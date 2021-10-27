import asyncio
import math
import time

import numpy as np

from cmds import set_rgb_color
from controller import Controller
from logger import LOGGER


class LightsEmitter():
    """ Light pulsing functions """
    def __init__(self, controller: Controller, init_color: list):
        self.controller = controller
        self.init_color = np.array(init_color, dtype=int)


    async def pulse_light(self, r, g, b):
        LOGGER.info("Starting pulsing")
        await self.controller.send_cmd_char(set_rgb_color(r, g, b))