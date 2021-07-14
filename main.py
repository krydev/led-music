import subprocess
import asyncio

import pygatt
import cmds

from controller import Controller
from lights_emitter import LightsEmitter

import numpy as np

DEVICE_ADD = 'BE:FF:E5:00:5D:95'
WRITE_HANDLE = '0008'
CHAR_UUID = '0000fff4-0000-1000-8000-00805f9b34fb'


def test_run_lights(controller):
	while True:
		color = [255, 0, 255]
		color_prev = [0, 0, 0]
		for vals in np.column_stack([np.linspace(color[i], color_prev[i], 20, dtype=int) for i in range(3)]):
			controller.send_cmd_char(cmds.set_rgb_color(*vals))

async def main_loop(emitter):
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


if __name__ == '__main__':
	adapter = pygatt.GATTToolBackend()

	try:
		adapter.start()
		device = adapter.connect(DEVICE_ADD)
		controller = Controller(device, WRITE_HANDLE, CHAR_UUID)
		controller.send_cmd_char(cmds.ON_SWITCH)
		test_run_lights(controller)
		# emitter = LightsEmitter(controller, exp_rate=0.4, init_color=[255, 0, 255])
		# run_app = asyncio.ensure_future(main_loop(emitter))
		# event_loop = asyncio.get_event_loop()
		# event_loop.run_forever()
	finally:
		adapter.stop()
