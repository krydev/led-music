import asyncio
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


    async def pulse_light(self, queue, init_color: list=None):
        # if init_color:
        #     self.init_color = init_color
        #     self.non_zero_inds = np.where(self.init_color != 0)[0]
        LOGGER.info("Starting pulsing")
        color = np.array(self.init_color)
        color_prev = np.zeros(3)
        while True:
            # reducing light intensity exponentially
            # color_prev = color
            try:
                l = queue.get_nowait()
                color = np.array(self.init_color)
                LOGGER.info(l)
                await self.controller.send_cmd_char(set_rgb_color(*color))
                queue.task_done()
            except asyncio.QueueEmpty:
                color = np.array([int(c * self.exp_rate) + 1 for c in color])
                LOGGER.info("Queue empty. Pulsing light meanwhile")
                await self.controller.send_cmd_char(set_rgb_color(*color))
            # color_prev = color
            # for vals in np.column_stack([np.linspace(color_prev[i], color[i], 20, dtype=int) for i in range(3)]):
            #     await self.controller.send_cmd_char(set_rgb_color(*vals))
                LOGGER.info(f"Current color: {color}")
            await asyncio.sleep(0)
            # await self.controller.send_cmd_char(set_rgb_color(*self.init_color))
            # color = np.array([int(c*0.1) for c in self.init_color])
            # while not np.array_equal(color[self.non_zero_inds], self.init_color[self.non_zero_inds]):
            #     color = np.minimum(self.init_color, color*3)
            #     self.controller.send_cmd(set_rgb_color(*color))
            #     print(f"Current color: {color}")