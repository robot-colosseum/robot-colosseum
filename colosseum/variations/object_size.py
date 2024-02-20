from __future__ import annotations

from typing import List, Optional, cast

from omegaconf import DictConfig
from pyrep import PyRep
from pyrep.const import ObjectType

from colosseum.pyrep.extensions.shape import ShapeExt
from colosseum.variations.utils import ScaleCfgMode, safeGetValue, sampleScale
from colosseum.variations.variation import IVariation


class ObjectSizeVariation(IVariation):
    """Variation in charge of changing objects' scales in the simulation"""

    VARIATION_ID = "object_size"

    @staticmethod
    def CreateFromConfig(
        pyrep: PyRep,
        name: Optional[str],
        targets_names: List[str],
        cfg: DictConfig,
    ) -> ObjectSizeVariation:
        """
        Factory function used to create an object size variation from a given
        configuration coming from yaml through OmegaConf
        """
        scale_list = safeGetValue(cfg, "scale_list", [])
        scale_range = safeGetValue(cfg, "scale_range", [])
        scale_same = safeGetValue(cfg, "scale_same", False)
        seed = safeGetValue(cfg, "seed", None)

        return ObjectSizeVariation(
            pyrep,
            name,
            targets_names,
            scale_range=scale_range,
            scale_list=scale_list,
            scale_same=scale_same,
            seed=seed,
        )

    def __init__(
        self,
        pyrep: PyRep,
        name: Optional[str],
        targets_names: List[str],
        scale_range: List[float] = [],
        scale_list: List[float] = [],
        scale_same: bool = False,
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
            scale_range: List[float]
                A list of two scale values, low and high, to sample scales from
            scale_list: List[float]
                A set of scale values to sample from
            scale_same: bool
                Whether all objects should be applied the same scale or not
            seed Optional[int]
                The seed used for any random number generators
        """
        super().__init__(
            pyrep, name, ObjectType.SHAPE, targets_names, seed=seed
        )

        self._config_mode = ScaleCfgMode.USE_DEFAULT_SCALE_RANGE
        self._scale_list = scale_list
        self._scale_range = (
            (scale_range[0], scale_range[1])
            if len(scale_range) == 2
            else (0.75, 1.25)
        )
        self._scale_same = scale_same

        if len(scale_list) < 1 and len(scale_range) < 1:
            self._config_mode = ScaleCfgMode.USE_DEFAULT_SCALE_RANGE
        elif len(scale_range) > 0:
            self._config_mode = ScaleCfgMode.USE_CUSTOM_SCALE_RANGE
        elif len(scale_list) > 0:
            self._config_mode = ScaleCfgMode.USE_CUSTOM_SCALE_VALUES

        for target_name, target_shape in self._targets.items():
            # Replace Shape with ShapeExt
            self._targets[target_name] = ShapeExt(target_shape.get_handle())

    def randomize(self) -> None:
        """
        Samples a random scale value and sets it to the appropriate object in
        the simulation. If scale_same is True, the same scale value is applied
        to all target objects
        """
        if self._scale_same:
            scale_value = sampleScale(
                self._config_mode,
                self._rng,
                scale_list=self._scale_list,
                scale_range=self._scale_range,
            )
            for _, shape_ext in self._targets.items():
                if scale_value is not None:
                    cast(ShapeExt, shape_ext).set_scale(scale_value)
        else:
            for _, shape_ext in self._targets.items():
                scale_value = sampleScale(
                    self._config_mode,
                    self._rng,
                    scale_list=self._scale_list,
                    scale_range=self._scale_range,
                )

                if scale_value is not None:
                    cast(ShapeExt, shape_ext).set_scale(scale_value)
