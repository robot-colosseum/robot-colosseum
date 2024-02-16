from typing import List, Tuple

import numpy as np
from pyrep.objects.joint import Joint
from rlbench.backend.conditions import JointCondition
from rlbench.backend.task import Task


class CloseBox(Task):
    def init_task(self) -> None:
        self._jnt_box = Joint("box_joint")
        self._init_pos = self._jnt_box.get_joint_position()

        self.register_success_conditions([JointCondition(self._jnt_box, 2.6)])

    def init_episode(self, index: int) -> List[str]:
        self._jnt_box.set_joint_position(self._init_pos)

        return [
            "close box",
            "close the lid on the box",
            "shut the box",
            "shut the box lid",
        ]

    def variation_count(self) -> int:
        return 1

    def base_rotation_bounds(
        self,
    ) -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
        return (0, 0, -np.pi / 8), (0, 0, np.pi / 8)
