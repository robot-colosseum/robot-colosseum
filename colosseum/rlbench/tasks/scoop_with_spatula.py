from typing import List

from pyrep.objects.proximity_sensor import ProximitySensor
from pyrep.objects.shape import Shape
from rlbench.backend.conditions import DetectedCondition, GraspedCondition
from rlbench.backend.task import Task


class ScoopWithSpatula(Task):
    def init_task(self) -> None:
        self._spatula = Shape("scoop_with_spatula_spatula")
        self._cuboid = Shape("Cuboid")
        self._sensor = ProximitySensor("success")
        self.register_graspable_objects([self._spatula])
        self.register_success_conditions(
            [
                DetectedCondition(self._cuboid, ProximitySensor("success")),
                GraspedCondition(self.robot.gripper, self._spatula),
            ]
        )

        self._init_relpose_spatula_to_cuboid = self._spatula.get_pose(
            relative_to=self._cuboid
        )
        self._init_relpose_cuboid_to_sensor = self._cuboid.get_pose(
            relative_to=self._sensor
        )

    def init_episode(self, index: int) -> List[str]:
        self._cuboid.set_pose(
            self._init_relpose_cuboid_to_sensor, relative_to=self._sensor
        )
        self._spatula.set_pose(
            self._init_relpose_spatula_to_cuboid, relative_to=self._cuboid
        )

        return [
            "scoop up the cube and lift it with the spatula",
            "scoop up the block and lift it with the spatula",
            "use the spatula to scoop the cube and lift it",
            "use the spatula to scoop the block and lift it",
            "pick up the cube using the spatula",
            "pick up the block using the spatula",
        ]

    def variation_count(self) -> int:
        return 1
