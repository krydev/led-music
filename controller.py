from typing import Union

from pygatt import BLEDevice
from dataclasses import dataclass


@dataclass
class Controller:
	""" GATT BLE device controller class """
	device: BLEDevice
	write_handle: Union[int, str]
	uuid_char: str = None

	def __post_init__(self):
		self.write_handle = int(self.write_handle, 16)

	def send_cmd_handle(self, cmd_str):
		cmd_bytes = bytearray.fromhex(cmd_str)
		self.device.char_write_handle(self.write_handle, cmd_bytes, wait_for_response=False)

	def send_cmd_char(self, cmd_str):
		cmd_bytes = bytearray.fromhex(cmd_str)
		self.device.char_write(self.uuid_char, cmd_bytes, wait_for_response=False)