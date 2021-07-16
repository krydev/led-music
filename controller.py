from typing import Union

from bleak import BleakClient
from dataclasses import dataclass


@dataclass
class Controller:
	""" BleakClient controller class """
	client: BleakClient
	uuid_char: str
	write_handle: Union[int, str] = None

	def __post_init__(self):
		if self.write_handle:
			self.write_handle = int(self.write_handle, 16)

	async def send_cmd_handle(self, cmd_str):
		cmd_bytes = bytearray.fromhex(cmd_str)
		await self.client.write_gatt_descriptor(self.write_handle, cmd_bytes)

	async def send_cmd_char(self, cmd_str):
		cmd_bytes = bytearray.fromhex(cmd_str)
		await self.client.write_gatt_char(self.uuid_char, cmd_bytes, response=True)