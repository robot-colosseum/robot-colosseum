from __future__ import annotations

from typing import List, Optional, cast

import numpy as np
from numpy.typing import NDArray
from omegaconf import DictConfig
from pyrep import PyRep
from pyrep.const import ObjectType
from pyrep.objects.light import Light

from colosseum.variations.utils import ColorCfgMode, safeGetValue, sampleColor
from colosseum.variations.variation import IVariation


class LightColorVariation(IVariation):
    """Light color variation, can change lights' colors in the simulation"""

    VARIATION_ID = "light_color"

    @staticmethod
    def CreateFromConfig(
        pyrep: PyRep,
        name: Optional[str],
        targets_names: List[str],
        cfg: DictConfig,
    ):
        """
        Factory function used to create a light color variation
        """
        color_names = safeGetValue(cfg, "color_names", [])
        color_list = safeGetValue(cfg, "color_list", [])
        color_range = safeGetValue(cfg, "color_range", [])
        color_same = safeGetValue(cfg, "color_same", True)
        seed = safeGetValue(cfg, "seed", None)

        return LightColorVariation(
            pyrep,
            name,
            targets_names,
            color_names=color_names,
            color_list=color_list,
            color_range=color_range,
            color_same=color_same,
            seed=seed,
        )

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
        Creates a light color variation, using one config. given by the user

        Parameters
        ----------
            pyrep: PyRep
                A handle to the pyrep simulation
            targets_names: List[str]
                A list of names for the lights in simulation to be controlled
            color_names: List[str]
                A list of names of colors to sample from (predefined color set)
            color_list: List[NDArray]
                A list of color values to sample from instead of the predefined
            color_range: List[NDArray]
                A list of two color values, low and high, to sample colors from
            color_same: bool
                Whether or not all lights controlled by this variation will
                have the same color for each
            seed Optional[int]
                The seed used for any random number generators
        """
        super().__init__(
            pyrep, name, ObjectType.LIGHT, targets_names, seed=seed
        )

        self._config_mode = ColorCfgMode.USE_RANDOM_FROM_LIBRARY
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
            self._config_mode = ColorCfgMode.USE_RANDOM_FROM_LIBRARY
        elif len(color_names) > 0:
            self._config_mode = ColorCfgMode.USE_CUSTOM_COLOR_NAMES
        elif len(color_list) > 0:
            self._config_mode = ColorCfgMode.USE_CUSTOM_COLOR_VALUES
        elif len(color_range) > 0:
            self._config_mode = ColorCfgMode.USE_CUSTOM_COLOR_RANGE

    def randomize(self) -> None:
        """
        Samples a random color and sets it to the associated lights in the
        simulation. Depending on the self._color_same parameter, all lights will
        receive the same color or not
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
                for _, light in self._targets.items():
                    self.apply(cast(Light, light), color_value)
        else:
            for _, light in self._targets.items():
                color_value = sampleColor(
                    self._config_mode,
                    self._rng,
                    color_names=self._color_names,
                    color_list=self._color_list,
                    color_range=self._color_range,
                )
                if color_value is not None:
                    self.apply(cast(Light, light), color_value)

    def apply(self, light: Light, color: NDArray) -> None:
        """
        Applies the given light color to the given light

        Parameters
        ----------
            light: Light
                The light object to be modified
            color: NDArray
                The color to be applied to the light
        """
        light.set_diffuse(color.tolist())
        light.set_specular(color.tolist())
