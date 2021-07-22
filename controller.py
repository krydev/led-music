from bleak import BleakClient
from dataclasses import dataclass


@dataclass
class Controller:
	""" BleakClient controller class """
	client: BleakClient
	uuid_char: str

	async def send_cmd_char(self, cmd_str):
		cmd_bytes = bytearray.fromhex(cmd_str)
		await self.client.write_gatt_char(self.uuid_char, cmd_bytes)