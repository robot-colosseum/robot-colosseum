from typing import List

import numpy as np
from pyrep.objects.object import Object
from rlbench.backend.exceptions import BoundaryError
from rlbench.backend.spawn_boundary import SpawnBoundary


class SpawnBoundaryExt(SpawnBoundary):
    def __init__(
        self,
        boundaries: List[Object],
        use_boundary_as_init_location: bool = True,
    ):
        """
        Extension of SpawnBoundary, which allows to use the coordinates of the
        selected boundary as initial coordinates for the object to be located.

        Parameters
        ----------
        boundaries: List[Object]
            The list of boundary objects used for sampling.
        use_boundary_as_init_location: bool
            A flag used to indicate whether or not use the coordinates of the
            sampled boundary for the sampled object.
        """
        super().__init__(boundaries)

        self._use_boundary_as_init_location = use_boundary_as_init_location

    def sample(
        self,
        obj: Object,
        ignore_collisions=False,
        min_rotation=(0.0, 0.0, -3.14),
        max_rotation=(0.0, 0.0, 3.14),
        min_distance=0.01,
    ) -> None:
        collision_fails = boundary_fails = self.MAX_SAMPLES
        while collision_fails > 0 and boundary_fails > 0:
            sampled_boundary = np.random.choice(
                self._boundaries, p=self._probabilities
            )
            if self._use_boundary_as_init_location:
                obj.set_position(sampled_boundary._boundary.get_position())
            result = sampled_boundary.add(
                obj, ignore_collisions, min_rotation, max_rotation, min_distance
            )
            if result == -1:
                boundary_fails -= 1
            elif result == -2:
                collision_fails -= 1
            elif result == -3:
                boundary_fails -= 1
            else:
                break
        if boundary_fails <= 0:
            raise BoundaryError(
                "Could not place within boundary."
                + "Perhaps the object is too big for it?"
            )
        elif collision_fails <= 0:
            raise BoundaryError(
                "Could not place the object within the boundary due to "
                + "collision with other objects in the boundary."
            )
