from typing import List, Tuple

import numpy as np
from pyrep.objects.joint import Joint
from pyrep.objects.object import Object
from pyrep.objects.proximity_sensor import ProximitySensor
from pyrep.objects.shape import Shape
from rlbench.backend.conditions import DetectedCondition, JointCondition
from rlbench.backend.task import Task


class GetIceFromFridge(Task):
    def init_task(self) -> None:
        self._cup = Shape("cup")
        self._fridge = Shape("fridge_base")
        self._init_pose_cup_to_fridge = self._cup.get_pose(
            relative_to=self._fridge
        )

        self.register_graspable_objects([self._cup])
        self.register_success_conditions(
            [
                JointCondition(Joint("joint"), np.deg2rad(1)),
                DetectedCondition(self._cup, ProximitySensor("success")),
            ]
        )

    def init_episode(self, index: int) -> List[str]:
        self._cup.set_pose(
            self._init_pose_cup_to_fridge, relative_to=self._fridge
        )

        return [
            "get ice from fridge",
            "use the cup to get ice from the fridge",
            "pick up the cup and fill it with ice from the fridge",
            "push the cup up against the tongue of the ice dispenser to "
            + "retrieve ice from the fridge",
        ]

    def variation_count(self) -> int:
        return 1

    def boundary_root(self) -> Object:
        return Shape("fridge_root")

    def base_rotation_bounds(
        self,
    ) -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
        return (0.0, 0.0, -np.pi / 4), (0.0, 0.0, np.pi / 4)
