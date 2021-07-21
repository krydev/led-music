import asyncio
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
        self.light_values = self._init_light_values()


    def _init_light_values(self):
        vals = []
        color = np.array(self.init_color)
        prev_color = np.zeros(3)
        while not np.array_equal(color[self.non_zero_inds], prev_color[self.non_zero_inds]):
            vals.append(color)
            prev_color = color
            color = np.array([int(c * self.exp_rate) + 1 for c in color])
        return np.array(vals)

    async def pulse_light(self, event):
        LOGGER.info("Starting pulsing")

        ind = 0
        while True:
            # reducing light intensity exponentially
            if event.is_set():
                ind = 0
                LOGGER.info("Received event signal. Resetting light")
                event.clear()
            color = self.light_values[ind]
            await self.controller.send_cmd_char(set_rgb_color(*color))
            LOGGER.info(f"Current color: {color}")
            ind = min(ind + 1, self.light_values.shape[0] - 1)
