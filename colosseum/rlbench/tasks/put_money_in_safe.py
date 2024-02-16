from typing import List, Tuple

import numpy as np
from pyrep.objects.dummy import Dummy
from pyrep.objects.proximity_sensor import ProximitySensor
from pyrep.objects.shape import Shape
from rlbench.backend.conditions import Condition, DetectedCondition, NothingGrasped
from rlbench.backend.spawn_boundary import SpawnBoundary
from rlbench.backend.task import Task

NUM_SHELVES_IN_SAFE = 3


class PutMoneyInSafe(Task):
    def init_task(self) -> None:
        self.index_dic = {0: "bottom", 1: "middle", 2: "top"}
        self.money = Shape("dollar_stack")
        self.money_boundary = Shape("dollar_stack_boundary")
        self.register_graspable_objects([self.money])
        self.success_conditions: List[Condition] = [
            NothingGrasped(self.robot.gripper)
        ]

        self._init_relpose_money_to_boundary = self.money.get_pose(
            relative_to=self.money_boundary
        )

    def init_episode(self, index: int) -> List[str]:
        self.money.set_pose(
            self._init_relpose_money_to_boundary,
            relative_to=self.money_boundary,
        )

        self.target_shelf = index
        w4 = Dummy("waypoint4")
        target_dummy_name = "dummy_shelf" + str(self.target_shelf)
        target_pos_dummy = Dummy(target_dummy_name)
        target_pos = target_pos_dummy.get_position()
        w4.set_position(target_pos, reset_dynamics=False)

        self.success_detector = ProximitySensor(
            ("success_detector" + str(self.target_shelf))
        )

        while len(self.success_conditions) > 1:
            self.success_conditions.pop()

        self.success_conditions.append(
            DetectedCondition(self.money, self.success_detector)
        )
        self.register_success_conditions(self.success_conditions)

        b = SpawnBoundary([self.money_boundary])
        b.sample(
            self.money,
            min_rotation=(0.00, 0.00, 0.00),
            max_rotation=(0.00, 0.00, +0.5 * np.pi),
        )

        return [
            "put the money away in the safe on the %s shelf"
            % self.index_dic[index],
            "leave the money on the %s shelf on the safe"
            % self.index_dic[index],
            "place the stack of bank notes on the %s shelf of the safe"
            % self.index_dic[index],
        ]

    def variation_count(self) -> int:
        return NUM_SHELVES_IN_SAFE

    def base_rotation_bounds(
        self,
    ) -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
        return (0.0, 0.0, 0.0), (0.0, 0.0, +0.5 * np.pi)
