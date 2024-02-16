from typing import List, Tuple

from pyrep.objects.joint import Joint
from pyrep.objects.object import Object
from pyrep.objects.proximity_sensor import ProximitySensor
from pyrep.objects.shape import Shape
from rlbench.backend.conditions import DetectedCondition
from rlbench.backend.task import Task


class EmptyDishwasher(Task):
    def init_task(self) -> None:
        success_detector = ProximitySensor("success")
        self._plate = Shape("dishwasher_plate")
        self._tray = Shape("dishwasher_tray")
        self.register_graspable_objects([self._plate])
        self.register_success_conditions(
            [DetectedCondition(self._plate, success_detector, negated=True)]
        )

        self._jnt_door = Joint("dishwasher_door_joint")
        self._jnt_door_init = self._jnt_door.get_joint_position()

        self._jnt_tray = Joint("dishwasher_tray_joint")
        self._jnt_tray_init = self._jnt_tray.get_joint_position()

        self._init_relpose_plate_to_tray = self._plate.get_pose(
            relative_to=self._tray
        )

    def init_episode(self, index: int) -> List[str]:
        self._jnt_door.set_joint_position(self._jnt_door_init)
        self._jnt_tray.set_joint_position(self._jnt_tray_init)
        self._plate.set_pose(
            self._init_relpose_plate_to_tray, relative_to=self._tray
        )

        return [
            "empty the dishwasher",
            "take dishes out of dishwasher",
            "open the  dishwasher door, slide the rack out and remove the "
            + "dishes",
        ]

    def variation_count(self) -> int:
        return 1

    def base_rotation_bounds(
        self,
    ) -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
        return (0, 0, -3.14 / 2.0), (0, 0, 3.14 / 2.0)

    def boundary_root(self) -> Object:
        return Shape("boundary_root")
