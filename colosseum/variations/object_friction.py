from __future__ import annotations

import warnings
from enum import Enum
from typing import List, Optional, cast

import numpy as np
from omegaconf import DictConfig
from pyrep import PyRep
from pyrep.const import ObjectType

from colosseum.pyrep.extensions.shape import ShapeExt
from colosseum.variations.utils import safeGetValue
from colosseum.variations.variation import IVariation


class FrictionConfigMode(Enum):
    # Sample using value  from a list of possible friction values
    USE_CUSTOM_FRICTION_VALUES = 1
    # Sample a random value within a custom range
    USE_CUSTOM_FRICTION_RANGE = 2


def sampleFriction(
    mode: FrictionConfigMode,
    rng: np.random.Generator,
    friction_list: List[float] = [],
    friction_range: List[float] = [],
) -> Optional[float]:
    """
    Samples a random friction value using one of many options given by the user

    Parameters
    ----------
        mode: FrictionConfigMode
            The mode that will be used to sample friction values
        rng: np.random.Generator
            The random generator used to make the sampling process
        friction_list: List[float]
            A list of friction values which we can altentatively sample from
        friction_range: List[float]
            A list of two friction values that contain both low and high values
            to sample from using a uniform distribution

    Returns
    -------
        Optional[float]
            A friction value sampled at random, or None in the worst case if
            something went wrong during the sampling process
    """
    friction_value: Optional[float] = None
    if mode == FrictionConfigMode.USE_CUSTOM_FRICTION_VALUES:
        assert len(friction_list) > 0, "Must provide list of friction values"
        friction_value = rng.choice(friction_list)
    elif mode == FrictionConfigMode.USE_CUSTOM_FRICTION_RANGE:
        assert len(friction_range) == 2, "Friction range must be (low, high)"
        try:
            friction_value = rng.uniform(
                low=friction_range[0], high=friction_range[1]
            )
        except ValueError:
            warnings.warn(
                "Something went wrong while using the"
                + f" given friction ranges. Range is '{friction_range}'",
                stacklevel=2,
            )

    return friction_value


class ObjectFrictionVariation(IVariation):
    """Variation in charge of changing objects' friction in the simulation"""

    VARIATION_ID = "object_friction"

    @staticmethod
    def CreateFromConfig(
        pyrep: PyRep,
        name: Optional[str],
        targets_names: List[str],
        cfg: DictConfig,
    ) -> ObjectFrictionVariation:
        """Factory function for creating variation obj out of yaml config"""
        friction_list = safeGetValue(cfg, "friction_list", [])
        friction_range = safeGetValue(cfg, "friction_range", [])
        friction_same = safeGetValue(cfg, "friction_same", False)
        seed = safeGetValue(cfg, "seed", None)

        return ObjectFrictionVariation(
            pyrep,
            name,
            targets_names,
            friction_list=friction_list,
            friction_range=friction_range,
            friction_same=friction_same,
            seed=seed,
        )

    def __init__(
        self,
        pyrep: PyRep,
        name: Optional[str],
        targets_names: List[str],
        friction_list: List[float] = [],
        friction_range: List[float] = [],
        friction_same: bool = False,
        seed: Optional[int] = None,
    ):
        """
        Creates an object size variation, using config options from the user

        Parameters
        ----------
            pyrep: PyRep
                A handle to the pyrep simulation
            name: str
                A unique identifier for this variation
            targets_names: List[str]
                A list of names for the objects in simulation to be controlled
            friction_list: List[float]
                A set of friction values to sample from
            friction_range: List[float]
                A list of two friction values, low and high, to sample from
            friction_same: bool
                Whether all objects should be applied the same friction or not
            seed Optional[int]
                The seed used for any random number generators
        """
        super().__init__(
            pyrep, name, ObjectType.SHAPE, targets_names, seed=seed
        )

        self._config_mode = FrictionConfigMode.USE_CUSTOM_FRICTION_VALUES
        self._friction_list = friction_list
        self._friction_range = friction_range
        self._friction_same = friction_same

        if len(friction_list) > 0:
            self._config_mode = FrictionConfigMode.USE_CUSTOM_FRICTION_VALUES
        elif len(friction_range) > 0:
            self._config_mode = FrictionConfigMode.USE_CUSTOM_FRICTION_RANGE

        for target_name, target_shape in self._targets.items():
            # Replace Shape with ShapeExt
            self._targets[target_name] = ShapeExt(target_shape.get_handle())

    def randomize(self) -> None:
        """
        Samples a random friction value and sets it to the appropriate objects
        in the simulation
        """
        if self._friction_same:
            friction_value = sampleFriction(
                self._config_mode,
                self._rng,
                friction_list=self._friction_list,
                friction_range=self._friction_range,
            )
            for _, shape_ext in self._targets.items():
                if friction_value is not None:
                    cast(ShapeExt, shape_ext).set_friction(friction_value)
        else:
            for _, shape_ext in self._targets.items():
                friction_value = sampleFriction(
                    self._config_mode,
                    self._rng,
                    friction_list=self._friction_list,
                    friction_range=self._friction_range,
                )

                if friction_value is not None:
                    cast(ShapeExt, shape_ext).set_friction(friction_value)
