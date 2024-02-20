from __future__ import annotations

import warnings
from typing import List, Optional, cast

import numpy as np
from numpy.typing import NDArray
from omegaconf import DictConfig
from pyrep import PyRep
from pyrep.const import ObjectType
from pyrep.objects.shape import Shape

from colosseum.variations.utils import ColorCfgMode, safeGetValue, sampleColor
from colosseum.variations.variation import IVariation

DEFAULT_TABLE_NAME = "diningTable_visible"


class TableColorVariation(IVariation):
    """Table color variation, can change tabletop's color in simulation"""

    VARIATION_ID = "table_color"

    @staticmethod
    def CreateFromConfig(
        pyrep: PyRep,
        name: Optional[str],
        cfg: DictConfig,
    ) -> TableColorVariation:
        """
        Factory function used to create a table color variation from a given
        configuration coming from yaml through OmegaConf
        """
        color_names = safeGetValue(cfg, "color_names", [])
        color_list = safeGetValue(cfg, "color_list", [])
        color_range = safeGetValue(cfg, "color_range", [])
        seed = safeGetValue(cfg, "seed", None)

        return TableColorVariation(
            pyrep,
            name,
            color_names=color_names,
            color_list=color_list,
            color_range=color_range,
            seed=seed,
        )

    def __init__(
        self,
        pyrep: PyRep,
        name: Optional[str],
        color_names: List[str] = [],
        color_list: List[NDArray] = [],
        color_range: List[NDArray] = [],
        seed: Optional[int] = None,
    ):
        """
        Creates a variation that randomizes the color of the table top in sim.

        Parameters
        ----------
            pyrep: PyRep
                A handle to the pyrep simulation
            color_names: List[str]
                A list of names of colors to sample from (predefined color set)
            color_list: List[NDArray]
                A list of color values to sample from instead of the predefined
            color_range: List[NDArray]
                A list of two color values, low and high, to sample colors from
            seed Optional[int]
                The seed used for any random number generators
        """
        super().__init__(
            pyrep, name, ObjectType.SHAPE, [DEFAULT_TABLE_NAME], seed=seed
        )

        self._config_mode = ColorCfgMode.USE_RANDOM_FROM_LIBRARY
        self._color_names = color_names
        self._color_list = color_list
        self._color_range = (
            (color_range[0], color_range[1])
            if len(color_range) == 2
            else (np.zeros(3), np.ones(3))
        )

        # Keep a reference to the table for easier access
        self._table_shape = cast(Shape, self._targets[DEFAULT_TABLE_NAME])

        if (
            len(color_names) < 1
            and len(color_list) < 1
            and len(color_range) < 1
        ):
            self._config_mode = ColorCfgMode.USE_RANDOM_FROM_LIBRARY
        elif len(color_names) > 0:
            self._config_mode = ColorCfgMode.USE_CUSTOM_COLOR_NAMES
        elif len(color_list) > 0:
            self._config_mode = ColorCfgMode.USE_CUSTOM_COLOR_VALUES
        elif len(color_range) > 0:
            self._config_mode = ColorCfgMode.USE_CUSTOM_COLOR_RANGE

    def randomize(self) -> None:
        color_value = sampleColor(
            self._config_mode,
            self._rng,
            color_names=self._color_names,
            color_list=self._color_list,
            color_range=self._color_range,
        )

        if color_value is not None:
            self._applyColor(color_value)

    def _applyColor(self, color: NDArray) -> None:
        table_shape_parts = self._table_shape.ungroup()
        table_top_shape = table_shape_parts[0]
        table_top_shape.set_color(color.tolist())
        if self._pyrep is not None:
            self._table_shape = self._pyrep.group_objects(table_shape_parts)
        else:
            warnings.warn(
                "Tried to group shapes but don't have a handle to pyrep itself"
            )
