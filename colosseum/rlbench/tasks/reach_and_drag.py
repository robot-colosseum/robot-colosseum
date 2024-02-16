from typing import List

from pyrep.objects.proximity_sensor import ProximitySensor
from pyrep.objects.shape import Shape
from rlbench.backend.conditions import DetectedCondition
from rlbench.backend.task import Task
from rlbench.const import colors


class ReachAndDrag(Task):
    def init_task(self) -> None:
        self.stick = Shape("stick")
        self.register_graspable_objects([self.stick])
        self.cube = Shape("cube")
        self.target = Shape("target0")

        self._init_relpose_cube_to_target = self.cube.get_pose(
            relative_to=self.target
        )
        self._init_relpose_stick_to_cube = self.stick.get_pose(
            relative_to=self.cube
        )

    def init_episode(self, index: int) -> List[str]:
        self.cube.set_pose(
            self._init_relpose_cube_to_target, relative_to=self.target
        )
        self.stick.set_pose(
            self._init_relpose_stick_to_cube, relative_to=self.cube
        )

        self.register_success_conditions(
            [DetectedCondition(self.cube, ProximitySensor("success0"))]
        )
        color_name, color_rgb = colors[index]
        self.target.set_color(color_rgb)
        return [
            "use the stick to drag the cube onto the %s target" % color_name,
            (
                "pick up the stick and use it to push or pull the cube "
                + "onto the %s target"
            )
            % color_name,
            "drag the block towards the %s square on the table top"
            % color_name,
            (
                "grasping the stick by one end, pick it up and use the its "
                "other end to move the block onto the %s target"
            )
            % color_name,
        ]

    def variation_count(self) -> int:
        return len(colors)
