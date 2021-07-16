import subprocess
import asyncio
import cmds

from controller import Controller

from bleak import BleakClient, BleakScanner

import numpy as np

from lights_emitter import LightsEmitter
from logger import LOGGER

DEVICE_ADDR = 'BE:FF:E5:00:5D:95'
WRITE_HANDLE = '0008'
CHAR_UUID = '0000fff3-0000-1000-8000-00805f9b34fb'


async def test_run_lights(controller):
	while True:
		color = [255, 0, 255]
		color_prev = [0, 0, 0]
		for vals in np.column_stack([np.linspace(color[i], color_prev[i], 20, dtype=int) for i in range(3)]):
			await controller.send_cmd_char(cmds.set_rgb_color(*vals))


async def beats_producer(queue):
	process = await asyncio.create_subprocess_shell('DBNBeatTracker online', stdout=subprocess.PIPE)
	while True:
		# await asyncio.sleep(0)
		line = await process.stdout.readline()
		if line:
			l_str = line.decode('utf-8')
			await queue.put(l_str)
			await asyncio.sleep(0)
			LOGGER.info(l_str)

# async def beats_producer(queue):
# 	process = subprocess.Popen(['DBNBeatTracker', 'online'], stdout=subprocess.PIPE, bufsize=1)
# 	for line in iter(process.stdout.readline, b''):
# 		l_str = line.rstrip().decode('utf-8')
# 		await queue.put(l_str)
# 		await asyncio.sleep(0)
# 		LOGGER.info(l_str)


async def main_loop():
	async with BleakClient(DEVICE_ADDR) as client:
		LOGGER.info(f"Connected: {client.is_connected}")
		controller = Controller(client, CHAR_UUID)
		queue = asyncio.Queue(maxsize=1)
		emitter = LightsEmitter(controller, exp_rate=0.7, init_color=[255, 0, 255])
		await controller.send_cmd_char(cmds.ON_SWITCH)
		# await test_run_lights(controller)
		await asyncio.gather(beats_producer(queue), emitter.pulse_light(queue))
		# asyncio.ensure_future(lights_sync(emitter))



if __name__ == '__main__':
	asyncio.run(main_loop())
