import os, fcntl
import subprocess
import asyncio
import threading as t
import multiprocessing as mp
import signal
import time

import cmds

from controller import Controller

from bleak import BleakClient

import numpy as np

from lights_emitter import LightsEmitter
from logger import LOGGER


DEVICE_ADDR = 'BE:FF:E5:00:5D:95'
CHAR_UUID = '0000fff3-0000-1000-8000-00805f9b34fb'


async def test_run_lights(controller, event):
	color = [255, 0, 255]
	color_prev = [0, 0, 0]		
	# lights = np.column_stack([np.linspace(color[i], color_prev[i], 10, dtype=int) for i in range(3)])
	lights = _init_light_values(0.6)
	while True:
		for vals in lights:
			if event.is_set():
				event.clear()
				LOGGER.info("Got signal")
				break
			await controller.send_cmd_char(cmds.set_rgb_color(*vals))

def beats_producer(event):
	process = subprocess.Popen(['DBNBeatTracker', 'online'], stdout=subprocess.PIPE, bufsize=0, close_fds=True)
	pstdout = process.stdout
	fd = pstdout.fileno()
	fl = fcntl.fcntl(fd, fcntl.F_GETFL)
	fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
	while True:
		try:
			line = process.stdout.readline()
			l_str = line.rstrip().decode('utf-8')
			LOGGER.info(l_str)
			event.set()
		except IOError:
			pass
		time.sleep(0.03)


async def main_loop(event):
	async with BleakClient(DEVICE_ADDR) as client:
		LOGGER.info(f"Connected: {client.is_connected}")
		controller = Controller(client, CHAR_UUID, WRITE_HANDLE)
		emitter = LightsEmitter(controller, exp_rate=0.7, init_color=[255, 0, 255])
		await controller.send_cmd_char(cmds.ON_SWITCH)
		# await test_run_lights(controller, event)
		await emitter.pulse_light(event)


def run(event):
	asyncio.run(main_loop(event))


if __name__ == '__main__':
	event = t.Event()
	lights = t.Thread(target=run, args=(event,))
	lights.daemon = True
	lights.start()
	beats_producer(event)

