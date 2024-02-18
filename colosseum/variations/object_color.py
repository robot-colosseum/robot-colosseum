from typing import List, Optional, cast

import numpy as np
from numpy.typing import NDArray
from pyrep import PyRep
from pyrep.const import ObjectType
from pyrep.objects.shape import Shape

from colosseum.variations.utils import ColorConfigMode, sampleColor
from colosseum.variations.variation import IVariation


class ObjectColorVariation(IVariation):
    """Object color variation, can change objects' color in the simulation"""

    def __init__(
        self,
        pyrep: PyRep,
        name: Optional[str],
        targets_names: List[str],
        color_names: List[str] = [],
        color_list: List[NDArray] = [],
        color_range: List[NDArray] = [],
        color_same: bool = False,
        seed: Optional[int] = None,
    ):
        """
        Creates an object color variation, using one config option from the user

        Parameters
        ----------
            pyrep: PyRep
                A handle to the pyrep simulation
            name: str
                A unique identifier for this variation
            targets_names: List[str]
                The list of shapes in the simulation we want to change colors
            color_names: List[str]
                A list of names of colors to sample from. These names must be
                a subset of the names defined in colosseum.variations.const
            color_list: List[NDArray]
                A list of color values to sample from. These are used instead of
                the color names if given
            color_range: List[NDArray]
                The low and high RGB values to sample from uniformly. These are
                used instead of all other if given
            color_same: bool
                Whether all objects should have the same color or not
            seed: int
                The seed used to initialize the internal random number generator
        """
        super().__init__(
            pyrep, name, ObjectType.SHAPE, targets_names, seed=seed
        )

        self._config_mode = ColorConfigMode.USE_RANDOM_FROM_LIBRARY
        self._color_names = color_names
        self._color_list = color_list
        self._color_range = (
            (color_range[0], color_range[1])
            if len(color_range) == 2
            else (np.zeros(3), np.ones(3))
        )
        self._color_same = color_same

        if (
            len(color_names) < 1
            and len(color_list) < 1
            and len(color_range) < 1
        ):
            self._config_mode = ColorConfigMode.USE_RANDOM_FROM_LIBRARY
        elif len(color_names) > 0:
            self._config_mode = ColorConfigMode.USE_CUSTOM_COLOR_NAMES
        elif len(color_list) > 0:
            self._config_mode = ColorConfigMode.USE_CUSTOM_COLOR_VALUES
        elif len(color_range) > 0:
            self._config_mode = ColorConfigMode.USE_CUSTOM_COLOR_RANGE

    def randomize(self) -> None:
        """
        Samples a random color and sets it to the objects in the simulation.
        Depending on the self._color_scame parameter, all objects will receive
        the same color or different colors otherwise if the parameter is false
        """
        if self._color_same:
            color_value = sampleColor(
                self._config_mode,
                self._rng,
                color_names=self._color_names,
                color_list=self._color_list,
                color_range=self._color_range,
            )

            if color_value is not None:
                for _, shape in self._targets.items():
                    cast(Shape, shape).set_color(color_value.tolist())
        else:
            for _, shape in self._targets.items():
                color_value = sampleColor(
                    self._config_mode,
                    self._rng,
                    color_names=self._color_names,
                    color_list=self._color_list,
                    color_range=self._color_range,
                )

                if color_value is not None:
                    cast(Shape, shape).set_color(color_value.tolist())
