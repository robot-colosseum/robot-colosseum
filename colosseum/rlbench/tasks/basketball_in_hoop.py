from typing import List, Tuple

import numpy as np
from pyrep.objects.object import Object
from pyrep.objects.proximity_sensor import ProximitySensor
from pyrep.objects.shape import Shape
from rlbench.backend.conditions import DetectedCondition
from rlbench.backend.task import Task


class BasketballInHoop(Task):
    def init_task(self):
        self._ball = Shape("ball")
        self._hoop = Shape("basket_ball_hoop_respondable")

        self._init_pose_ball_to_hoop = self._ball.get_pose(
            relative_to=self._hoop
        )

        self.register_graspable_objects([self._ball])
        self.register_success_conditions(
            [DetectedCondition(self._ball, ProximitySensor("success"))]
        )

    def init_episode(self, index: int) -> List[str]:
        self._ball.set_pose(
            self._init_pose_ball_to_hoop, relative_to=self._hoop
        )

        return [
            "put the ball in the hoop",
            "play basketball",
            "shoot the ball through the net",
            "pick up the basketball and put it in the hoop",
            "throw the basketball through the hoop",
            "place the basket ball through the hoop",
        ]

    def variation_count(self) -> int:
        return 1

    def base_rotation_bounds(
        self,
    ) -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
        return (0, 0, -np.pi / 4), (0, 0, np.pi / 4)

    def boundary_root(self) -> Object:
        return Shape("basket_boundary_root")
