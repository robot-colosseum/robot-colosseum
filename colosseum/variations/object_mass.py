from __future__ import annotations

import warnings
from enum import Enum
from typing import List, Optional, cast

import numpy as np
from omegaconf import DictConfig
from pyrep import PyRep
from pyrep.const import ObjectType
from pyrep.objects.shape import Shape

from colosseum.variations.utils import safeGetValue
from colosseum.variations.variation import IVariation


class MassConfigMode(Enum):
    # Invalid config mode
    INVALID_MODE = 0
    # Pick from a given set of mass values
    USE_CUSTOM_MASS_VALUES = 1
    # Pick from a min-max range of masses
    USE_CUSTOM_MASS_RANGE = 2


def sampleMass(
    mode: MassConfigMode,
    rng: np.random.Generator,
    mass_list: List[float] = [],
    mass_range: List[float] = [],
) -> Optional[float]:
    """
    Samples a random mass value using one of many options given by the user

    Parameters
    ----------
        mode: MassConfigMode
            The mode that will be used to sample mass values
        rng: np.random.Generator
            The random generator used to make the sampling process
        mass_list: List[float]
            A list of mass values which we can altentatively sample from
        mass_range: List[float]
            A list of two mass values that contain both low and high values
            to sample from using a uniform distribution

    Returns
    -------
        Optional[float]
            A mass value sampled at random, or None in the worst case if
            something went wrong during the sampling process
    """
    mass_value: Optional[float] = None
    if mode == MassConfigMode.USE_CUSTOM_MASS_VALUES:
        assert len(mass_list) > 0, "Must provide list of mass values"
        mass_value = rng.choice(mass_list)
    elif mode == MassConfigMode.USE_CUSTOM_MASS_RANGE:
        assert len(mass_range) == 2, "Mass range must be (low, high)"
        try:
            mass_value = rng.uniform(low=mass_range[0], high=mass_range[1])
        except ValueError:
            warnings.warn(
                " Something went wrong while using the given mass range",
                stacklevel=2,
            )

    return mass_value


class ObjectMassVariation(IVariation):
    """Variation in charge of changing objects' masses in the simulation"""

    VARIATION_ID = "object_mass"

    @staticmethod
    def CreateFromConfig(
        pyrep: PyRep,
        name: Optional[str],
        targets_names: List[str],
        cfg: DictConfig,
    ) -> ObjectMassVariation:
        """Factory function for creating variation obj out of yaml config"""
        mass_list = safeGetValue(cfg, "mass_list", [])
        mass_range = safeGetValue(cfg, "mass_range", [])
        mass_same = safeGetValue(cfg, "mass_same", False)
        seed = safeGetValue(cfg, "seed", None)

        return ObjectMassVariation(
            pyrep,
            name,
            targets_names,
            mass_list=mass_list,
            mass_range=mass_range,
            mass_same=mass_same,
            seed=seed,
        )

    def __init__(
        self,
        pyrep: PyRep,
        name: Optional[str],
        targets_names: List[str],
        mass_list: List[float],
        mass_range: List[float],
        mass_same: bool = False,
        seed: Optional[int] = None,
    ):
        """
        Creates an object mass variation, using config options from the user

        Parameters
        ----------
            pyrep: PyRep
                A handle to the pyrep simulation
            name: str
                A unique identifier for this variation
            targets_names: List[str]
                A list of names for the objects in simulation to be controlled
            mass_list: List[float]
                A set of mass values to sample from
            mass_range: List[float]
                A list of two mass values, low and high, to sample from
            seed Optional[int]
                The seed used for any random number generators
        """
        super().__init__(
            pyrep, name, ObjectType.SHAPE, targets_names, seed=seed
        )

        self._config_mode = MassConfigMode.USE_CUSTOM_MASS_VALUES
        self._mass_list = mass_list
        self._mass_range = mass_range
        self._mass_same = mass_same

        if len(mass_list) > 0:
            self._config_mode = MassConfigMode.USE_CUSTOM_MASS_VALUES
        elif len(mass_range) > 0:
            self._config_mode = MassConfigMode.USE_CUSTOM_MASS_RANGE
        else:
            self._config_mode = MassConfigMode.INVALID_MODE
            warnings.warn(
                "ObjectMassVariation> should pass valid args", stacklevel=2
            )

    def randomize(self) -> None:
        """
        Samples a random mass value and sets it to the appropriate objects
        in the simulation
        """
        if self._config_mode == MassConfigMode.INVALID_MODE:
            return

        if self._mass_same:
            mass_value = sampleMass(
                self._config_mode,
                self._rng,
                mass_list=self._mass_list,
                mass_range=self._mass_range,
            )
            for _, shape in self._targets.items():
                if mass_value is not None:
                    cast(Shape, shape).set_mass(mass_value)
        else:
            for _, shape in self._targets.items():
                mass_value = sampleMass(
                    self._config_mode,
                    self._rng,
                    mass_list=self._mass_list,
                    mass_range=self._mass_range,
                )

                if mass_value is not None:
                    cast(Shape, shape).set_mass(mass_value)
