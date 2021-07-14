import asyncio
import numpy as np

from cmds import set_rgb_color
from controller import Controller


class LightsEmitter():
    """ Light pulsing functions """
    def __init__(self, controller: Controller, exp_rate: float, init_color: list):
        self.controller = controller
        self.exp_rate = 1 - exp_rate
        self.init_color = np.array(init_color, dtype=int)
        self.non_zero_inds = np.where(self.init_color != 0)[0]


    async def pulse_light(self, init_color: list=None):
        if init_color:
            self.init_color = init_color
            self.non_zero_inds = np.where(self.init_color != 0)[0]
        color = np.array(self.init_color)
        try:
            while True:
                await asyncio.sleep(0)
                # reducing light intensity exponentially
                # color_prev = color
                color = np.array([int(c**0.5)+1 for c in color])
                self.controller.send_cmd_char(set_rgb_color(*color))
                # for vals in np.column_stack([np.linspace(color[i], color_prev[i], 30, dtype=int) for i in range(3)]):
                #     self.controller.send_cmd(set_rgb_color(*vals))
                    # if np.random.randint(1, 5) == 3:
                    #     await asyncio.sleep(0)
                print(f"Current color: {color}")
        except asyncio.CancelledError:
            # reverse light
            print(f"Got cancel signal. Reversing light intensity")
            # self.controller.send_cmd(set_rgb_color(*self.init_color))
            # color = np.array([int(c*0.1) for c in self.init_color])
            # while not np.array_equal(color[self.non_zero_inds], self.init_color[self.non_zero_inds]):
            #     color = np.minimum(self.init_color, color*3)
            #     self.controller.send_cmd(set_rgb_color(*color))
            #     print(f"Current color: {color}")