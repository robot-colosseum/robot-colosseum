from typing import Dict, List, Optional

from numpy.typing import NDArray
from pyrep import PyRep
from pyrep.const import ObjectType

from colosseum.variations.variation import IVariation


class CameraPoseVariation(IVariation):
    """Camera pose variation, can change camera's pose in the simulation"""

    def __init__(
        self,
        pyrep: PyRep,
        name: Optional[str],
        targets_names: List[str],
        euler_range: List[NDArray] = [],
        position_range: List[NDArray] = [],
        seed: Optional[int] = None,
    ):
        """
        Creates a camera pose variation, using one config option from the user

        Parameters
        ----------
            pyrep: PyRep
                A handle to the pyrep simulation
            name: Optional[str]
                A unique identifier for this variation
            targets_names: List[str]
                A list of names for the Cameras in simulation to be controlled
            euler_range: NDArray
                The min. and max. ranges for the applied delta of orientation
            position_range: NDArray
                The min. and max. ranges for the applied delta of position
            seed: Optional[int]
                The seed used for any random number generators
        """
        super().__init__(
            pyrep, name, ObjectType.VISION_SENSOR, targets_names, seed=seed
        )

        self._modify_orientation: bool = len(euler_range) == 2
        self._modify_position: bool = len(position_range) == 2

        self._initial_poses: Dict[str, NDArray] = {}
        for name, camera in self._targets.items():
            self._initial_poses[name] = camera.get_pose()

        self._euler_range = euler_range
        self._position_range = position_range

    def randomize(self) -> None:
        for name, camera in self._targets.items():
            # Reset back to the initial pose before applying the deltas
            self._targets[name].set_pose(self._initial_poses[name])

            if self._modify_orientation:
                euler_delta = self._rng.uniform(
                    low=self._euler_range[0], high=self._euler_range[1]
                )
                current_euler = camera.get_orientation()
                new_euler = current_euler + euler_delta
                camera.set_orientation(new_euler)

            if self._modify_position:
                position_delta = self._rng.uniform(
                    low=self._position_range[0], high=self._position_range[1]
                )
                current_position = camera.get_position()
                new_position = current_position + position_delta
                camera.set_position(new_position)
