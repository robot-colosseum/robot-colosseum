from __future__ import annotations

import os
import re
from typing import Dict, List, Optional, Set, Tuple, cast

from omegaconf import DictConfig
from pyrep import PyRep
from pyrep.const import ObjectType, TextureMappingMode

from colosseum import ASSETS_TEXTURES_FOLDER
from colosseum.pyrep.extensions.shape import ShapeExt
from colosseum.variations.utils import safeGetValue
from colosseum.variations.variation import IVariation


class ObjectTextureVariation(IVariation):
    """Variation in charge of changing objects' textures in the simulation"""

    VARIATION_ID = "object_texture"

    @staticmethod
    def CreateFromConfig(
        pyrep: PyRep,
        name: Optional[str],
        targets_names: List[str],
        cfg: DictConfig,
    ) -> ObjectTextureVariation:
        """
        Factory function used to create an object texture variation from a given
        configuration coming from yaml through OmegaConf
        """
        textures_folder = safeGetValue(cfg, "textures_folder", "")
        textures_filenames = safeGetValue(cfg, "textures_filenames", [])
        repeat_along_u = safeGetValue(cfg, "repeat_along_u", True)
        repeat_along_v = safeGetValue(cfg, "repeat_along_v", True)
        uv_scale = safeGetValue(cfg, "uv_scale", (1.0, 1.0))
        mapping_mode = TextureMappingMode(
            safeGetValue(cfg, "mapping_mode", TextureMappingMode.PLANE.value)
        )
        seed = safeGetValue(cfg, "seed", None)

        return ObjectTextureVariation(
            pyrep,
            name,
            targets_names,
            textures_folder=textures_folder,
            textures_filenames=textures_filenames,
            repeat_along_u=repeat_along_u,
            repeat_along_v=repeat_along_v,
            uv_scale=uv_scale,
            mapping_mode=mapping_mode,
            seed=seed,
        )

    def __init__(
        self,
        pyrep: PyRep,
        name: Optional[str],
        targets_names: List[str],
        textures_folder: str = ASSETS_TEXTURES_FOLDER,
        textures_filenames: List[str] = [],
        repeat_along_u: bool = True,
        repeat_along_v: bool = True,
        uv_scale: Tuple[float, float] = (1.0, 1.0),
        mapping_mode: TextureMappingMode = TextureMappingMode.PLANE,
        seed: Optional[int] = None,
    ):
        """
        Creates an object texture variation, using config options from the user

        Parameters
        ----------
            pyrep: PyRep
                A handle to the pyrep simulation
            name: str
                A unique identifier for this variation
            targets_names: List[str]
                A list of names for the objects in simulation to be controlled
            textures_folder: str
                A path to the folder containing the textures to be used
            textures_filenames: List[str]
                A list of texture filenames to be used (whitelist)
            repeat_along_u: bool
                Whether the texture should be repeated along the U axis
            repeat_along_v: bool
                Whether the texture should be repeated along the V axis
            uv_scale: Tuple[float, float]
                A tuple of two floats, representing the UV scaling to be applied
            mapping_mode: TextureMappingMode
                The texture mapping mode to be used
            seed Optional[int]
                The seed used for any random number generators
        """
        super().__init__(
            pyrep, name, ObjectType.SHAPE, targets_names, seed=seed
        )

        self._textures_folder: str = (
            textures_folder if textures_folder != "" else ASSETS_TEXTURES_FOLDER
        )

        self._textures_filenames_set: Set[str] = set(textures_filenames)
        self._repeat_along_u = repeat_along_u
        self._repeat_along_v = repeat_along_v
        self._uv_scale = uv_scale
        self._mapping_mode = mapping_mode

        self._textures_paths: List[str] = []
        self._textures_names: List[str] = []

        self._textures_filemap: Dict[str, str] = {}

        regex = re.compile("(.*jpg$)|(.*png$)")
        candidate_textures_names = [
            fname
            for fname in os.listdir(self._textures_folder)
            if regex.match(fname)
        ]

        # Check that candidates are in the whitelist (if any)
        valid_textures_names = []
        for candidate_tex_name in candidate_textures_names:
            if len(self._textures_filenames_set) < 1:
                valid_textures_names.append(candidate_tex_name)
            elif candidate_tex_name in self._textures_filenames_set:
                valid_textures_names.append(candidate_tex_name)

        for fname in valid_textures_names:
            texture_filepath = os.path.join(self._textures_folder, fname)
            # TODO(wilbert): use a better approach to getting the texture name
            texture_filename = fname.split(".")[0]
            self._textures_paths.append(texture_filepath)
            self._textures_names.append(texture_filename)
            self._textures_filemap[texture_filename] = texture_filepath

        for target_name, target_shape in self._targets.items():
            # Replace Shape with ShapeExt
            self._targets[target_name] = ShapeExt(target_shape.get_handle())

    def randomize(self) -> None:
        for _, shape_ext in self._targets.items():
            choice_name = self._rng.choice(self._textures_names)
            choice_fpath = self._textures_filemap[choice_name]
            texture_obj, choice_texture = self._pyrep.create_texture(
                choice_fpath
            )
            cast(ShapeExt, shape_ext).try_set_texture(
                choice_texture,
                mapping_mode=self._mapping_mode,
                uv_scaling=self._uv_scale,
                repeat_along_u=self._repeat_along_u,
                repeat_along_v=self._repeat_along_v,
            )
            texture_obj.remove()
