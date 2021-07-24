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


# async def test_run_lights(controller, beat_event):
# 	color = [255, 0, 255]
# 	color_prev = [0, 0, 0]
# 	# lights = np.column_stack([np.linspace(color[i], color_prev[i], 10, dtype=int) for i in range(3)])
# 	lights = _init_light_values(0.6)
# 	while True:
# 		for vals in lights:
# 			if beat_event.is_set():
# 				beat_event.clear()
# 				LOGGER.info("Got signal")
# 				break
# 			await controller.send_cmd_char(cmds.set_rgb_color(*vals))

def beats_producer(beat_event):
	process = subprocess.Popen(['DBNBeatTracker', 'online'], stdout=subprocess.PIPE, bufsize=0, close_fds=True)
	pstdout = process.stdout
	fd = pstdout.fileno()
	fl = fcntl.fcntl(fd, fcntl.F_GETFL)
	fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
	while not process.poll():
		try:
			line = process.stdout.readline()
			l_str = line.rstrip().decode('utf-8')
			LOGGER.info(l_str)
			beat_event.set()
		except IOError:
			time.sleep(0.02)


async def main_loop(beat_event, stop_event):
	async with BleakClient(DEVICE_ADDR) as client:
		LOGGER.info(f"Connected: {client.is_connected}")
		controller = Controller(client, CHAR_UUID)
		init_color = [130, 0, 140]
		emitter = LightsEmitter(controller, exp_rate=0.4, init_color=init_color)
		await controller.send_cmd_char(cmds.ON_SWITCH)
		await controller.send_cmd_char(cmds.set_rgb_color(*init_color))
		# await test_run_lights(controller, beat_event)
		while not stop_event.is_set():
			await emitter.pulse_light(beat_event)


def run(beat_event, stop_event):
	asyncio.run(main_loop(beat_event, stop_event))


if __name__ == '__main__':
	stop_event = t.Event()
	beat_event = t.Event()
	lights = t.Thread(target=run, args=(beat_event, stop_event))
	lights.daemon = True
	lights.start()
	try:
		beats_producer(beat_event)
	except (KeyboardInterrupt, SystemExit):
		stop_event.set()
		lights.join()

