import subprocess
import asyncio
import logging
import cmds

from controller import Controller
from lights_emitter import LightsEmitter
from bleak import BleakClient, BleakScanner

import numpy as np

DEVICE_ADDR = 'BE:FF:E5:00:5D:95'
WRITE_HANDLE = '0008'
CHAR_UUID = '0000fff3-0000-1000-8000-00805f9b34fb'


async def test_run_lights(controller):
	await controller.send_cmd_char(cmds.ON_SWITCH)
	while True:
		color = [255, 0, 255]
		color_prev = [0, 0, 0]
		for vals in np.column_stack([np.linspace(color[i], color_prev[i], 20, dtype=int) for i in range(3)]):
			await controller.send_cmd_char(cmds.set_rgb_color(*vals))


async def lights_sync(emitter):
	process = await asyncio.create_subprocess_shell('DBNBeatTracker online', stdout=subprocess.PIPE)
	lights_task = asyncio.ensure_future(emitter.pulse_light())
	while True:
		await asyncio.sleep(0)
		line = await process.stdout.readline()
		if line:
			lights_task.cancel()
			await lights_task
			lights_task = asyncio.ensure_future(emitter.pulse_light())
			print(line.decode('utf-8'))


async def main_loop(debug):
	log = logging.getLogger(__name__)
	if debug:
		import sys

		log.setLevel(logging.DEBUG)
		h = logging.StreamHandler(sys.stdout)
		h.setLevel(logging.DEBUG)
		log.addHandler(h)
	async with BleakClient(DEVICE_ADDR) as client:
		log.info(f"Connected: {client.is_connected}")
		controller = Controller(client, CHAR_UUID)
		emitter = LightsEmitter(controller, exp_rate=0.4, init_color=[255, 0, 255])
		await test_run_lights(controller)
		# await lights_sync(emitter)


if __name__ == '__main__':
	event_loop = asyncio.get_event_loop()
	event_loop.set_debug(True)
	event_loop.run_until_complete(main_loop(debug=True))
