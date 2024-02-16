from typing import List

from pyrep.objects.joint import Joint
from rlbench.backend.conditions import JointCondition
from rlbench.backend.task import Task


class CloseLaptopLid(Task):
    def init_task(self) -> None:
        self._jnt_base = Joint("joint")
        self._init_pos = self._jnt_base.get_joint_position()

        self.register_success_conditions([JointCondition(self._jnt_base, 1.79)])

    def init_episode(self, index: int) -> List[str]:
        self._jnt_base.set_joint_position(self._init_pos)

        return ["close laptop lid", "close the laptop", "shut the laptop lid"]

    def variation_count(self) -> int:
        return 1
