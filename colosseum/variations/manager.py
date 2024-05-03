from typing import List, Optional

from omegaconf import ListConfig
from pyrep import PyRep

from colosseum.variations.background_texture import BackgroundTextureVariation
from colosseum.variations.camera_pose import CameraPoseVariation
from colosseum.variations.distractor_object import DistractorObjectVariation
from colosseum.variations.light_color import LightColorVariation
from colosseum.variations.object_color import ObjectColorVariation
from colosseum.variations.object_friction import ObjectFrictionVariation
from colosseum.variations.object_size import ObjectSizeVariation
from colosseum.variations.object_texture import ObjectTextureVariation
from colosseum.variations.table_color import TableColorVariation
from colosseum.variations.table_texture import TableTextureVariation
from colosseum.variations.utils import safeGetValue
from colosseum.variations.variation import IVariation


class VariationsManager:
    def __init__(
        self, pyrep: PyRep, factors_config: ListConfig = ListConfig([])
    ):
        self._pyrep: PyRep = pyrep
        self._variations: List[IVariation] = []
        self._factors_config: ListConfig = factors_config

    def on_init_task(self) -> None:
        self._variations.clear()

        for factor in self._factors_config:
            variation: Optional[IVariation] = None
            factor_type = safeGetValue(factor, "variation", None)
            factor_enabled = safeGetValue(factor, "enabled", True)
            factor_name = safeGetValue(factor, "name", None)
            targets = safeGetValue(factor, "targets", [])

            if factor_type == LightColorVariation.VARIATION_ID:
                variation = LightColorVariation.CreateFromConfig(
                    self._pyrep, factor_name, targets, factor
                )

            elif factor_type == ObjectColorVariation.VARIATION_ID:
                variation = ObjectColorVariation.CreateFromConfig(
                    self._pyrep, factor_name, targets, factor
                )

            elif factor_type == ObjectSizeVariation.VARIATION_ID:
                variation = ObjectSizeVariation.CreateFromConfig(
                    self._pyrep, factor_name, targets, factor
                )

            elif factor_type == ObjectTextureVariation.VARIATION_ID:
                variation = ObjectTextureVariation.CreateFromConfig(
                    self._pyrep, factor_name, targets, factor
                )

            elif factor_type == TableColorVariation.VARIATION_ID:
                variation = TableColorVariation.CreateFromConfig(
                    self._pyrep, factor_name, factor
                )

            elif factor_type == TableTextureVariation.VARIATION_ID:
                variation = TableTextureVariation.CreateFromConfig(
                    self._pyrep, factor_name, factor
                )

            elif factor_type == BackgroundTextureVariation.VARIATION_ID:
                variation = BackgroundTextureVariation.CreateFromConfig(
                    self._pyrep, factor_name, factor
                )

            elif factor_type == DistractorObjectVariation.VARIATION_ID:
                variation = DistractorObjectVariation.CreateFromConfig(
                    self._pyrep, factor_name, targets, factor
                )

            elif factor_type == CameraPoseVariation.VARIATION_ID:
                variation = CameraPoseVariation.CreateFromConfig(
                    self._pyrep, factor_name, targets, factor
                )
            elif factor_type == ObjectFrictionVariation.VARIATION_ID:
                variation = ObjectFrictionVariation.CreateFromConfig(
                    self._pyrep, factor_name, targets, factor
                )

            if variation is not None:
                variation.setEnable(factor_enabled)
                self._variations.append(variation)

    def on_init_episode(self) -> None:
        for variation in self._variations:
            if variation.enabled:
                variation.on_init_episode()

    def on_step_episode(self) -> None:
        for variation in self._variations:
            if variation.enabled:
                variation.on_step_episode()
