import asyncio
import math
import time

import numpy as np

from cmds import set_rgb_color
from controller import Controller
from logger import LOGGER


class LightsEmitter():
    """ Light pulsing functions """
    def __init__(self, controller: Controller, exp_rate: float, init_color: list):
        self.controller = controller
        self.exp_rate = exp_rate
        self.init_color = np.array(init_color, dtype=int)
        self.non_zero_inds = np.where(self.init_color != 0)[0]
        self.light_values = self._init_light_values(10)


    def _init_light_values(self, num_vals):
        vals = []
        for i in range(num_vals):
            color = (self.init_color * math.exp(-self.exp_rate*i)).astype(int)
            vals.append(color)
        return np.array(vals)

    async def pulse_light(self, event):
        LOGGER.info("Starting pulsing")
        await self.controller.send_cmd_char(set_rgb_color(*self.init_color))
        while True:
            event.wait()
            LOGGER.info("Received event signal. Resetting light")
            event.clear()
            for color in self.light_values:
                await self.controller.send_cmd_char(set_rgb_color(*color))
                LOGGER.info(f"Current color: {color}")
            # Reversing back
            for color in self.light_values[-2::-1]:
                await self.controller.send_cmd_char(set_rgb_color(*color))
                LOGGER.info(f"Current color: {color}")
                # time.sleep(0.01)
