import math
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
from microphone import AudioHandler

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


def interp_rgb_exp(start: np.array, stop:np.array, exp_rate: float):
	assert len(start) == len(stop)
	reverse = False
	if start.max() < stop.max():
		reverse = True
		start, stop = stop, start
	vals = [start]
	i = 1
	init_color = np.copy(start)
	non_zero_inds = np.where(init_color != 0)[0]
	while np.all(start[non_zero_inds] > stop[non_zero_inds]):
		start = (init_color * math.exp(-exp_rate * i)).astype(int)
		vals.append(start)
		i+=1
	vals.append(stop)
	if reverse:
		return np.array(vals[-1::-1])
	return np.array(vals)

def interp_rgb(start: np.array, stop:np.array, size):
	assert len(start) == len(stop)
	return np.column_stack([np.linspace(start[i], stop[i], size, dtype=int) for i in range(len(start))])


async def main_loop():
	async with BleakClient(DEVICE_ADDR) as client:
		LOGGER.info(f"Connected: {client.is_connected}")
		controller = Controller(client, CHAR_UUID)
		init_color = np.array([100, 0, 100], dtype=np.int)
		prev_color = init_color
		# emitter = LightsEmitter(controller, init_color=init_color)
		await controller.send_cmd_char(cmds.ON_SWITCH)
		await controller.send_cmd_char(cmds.set_rgb_color(*init_color))

		audio = AudioHandler()
		audio.start()  # open the the stream
		while (audio.stream.is_active()):
			data = audio.stream.read(audio.CHUNK, exception_on_overflow=False)
			# audio.stream.read(audio.stream.get_read_available(), exception_on_overflow=False)
			t = time.time()
			onset_strength, beats = audio.callback(data)
			t = time.time()
			for beat in beats:
				new_color = (init_color * onset_strength[beat]).astype(int)
				if not np.array_equal(new_color, prev_color):
					print("Detected beat")
					seq = interp_rgb_exp(np.copy(prev_color), np.copy(new_color), 0.6)
					for color_vals in seq:
						print(color_vals)
						await controller.send_cmd_char(cmds.set_rgb_color(*color_vals))
					# print("Reversing")
					# for color_vals in seq[-1::-1]:
					# 	await controller.send_cmd_char(cmds.set_rgb_color(*color_vals))
				prev_color = np.copy(new_color)
		audio.stop()



if __name__ == '__main__':
	asyncio.run(main_loop())
