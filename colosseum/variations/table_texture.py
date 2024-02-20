from __future__ import annotations

import os
import re
from typing import Dict, List, Optional, Set, Tuple, cast

from omegaconf import DictConfig
from pyrep import PyRep
from pyrep.const import ObjectType, TextureMappingMode
from pyrep.objects.shape import Shape
from pyrep.textures.texture import Texture

from colosseum import ASSETS_TEXTURES_FOLDER
from colosseum.variations.utils import safeGetValue
from colosseum.variations.variation import IVariation

DEFAULT_TABLE_NAME = "diningTable_visible"

DEFAULT_TEXTURE_KWARGS = {
    "mapping_mode": TextureMappingMode.PLANE,
    "repeat_along_u": True,
    "repeat_along_v": True,
    "uv_scaling": [4.0, 4.0],
}


class TableTextureVariation(IVariation):
    """
    Table texture variation, can change the tabletop texture in the simulation
    """

    VARIATION_ID = "table_texture"

    @staticmethod
    def CreateFromConfig(
        pyrep: PyRep, name: Optional[str], cfg: DictConfig
    ) -> TableTextureVariation:
        """
        Factory function used to create a table texture variation from a given
        configuration coming from yaml through OmegaConf
        """
        textures_folder = safeGetValue(cfg, "textures_folder", "")
        textures_filenames = safeGetValue(cfg, "textures_filenames", [])
        uv_scale = safeGetValue(cfg, "uv_scale", (1.0, 1.0))
        seed = safeGetValue(cfg, "seed", None)

        return TableTextureVariation(
            pyrep,
            name,
            textures_folder=textures_folder,
            textures_filenames=textures_filenames,
            uv_scale=uv_scale,
            seed=seed,
        )

    def __init__(
        self,
        pyrep: PyRep,
        name: Optional[str],
        textures_folder: str = ASSETS_TEXTURES_FOLDER,
        textures_filenames: List[str] = [],
        uv_scale: Tuple[float, float] = (1.0, 1.0),
        seed: Optional[int] = None,
    ):
        """
        Creates a table-texture variation to randomize the tabletop texture

        Parameters
        ----------
            pyrep: PyRep
                A handle to the pyrep simulation
            name: str
                A unique identifier for this variation
            textures_folder: str
                A path to the folder containing the textures to be used
            textures_filenames: List[str]
                A list of texture filenames to be used (whitelist)
            uv_scale: Tuple[float, float]
                A tuple of two floats, representing the UV scaling to be applied
            seed: Optional[int]
                The seed used for any random number generators
        """
        super().__init__(
            pyrep, name, ObjectType.SHAPE, [DEFAULT_TABLE_NAME], seed=seed
        )

        self._table_shape: Optional[Shape] = None
        self._textures_folder: str = (
            textures_folder if textures_folder != "" else ASSETS_TEXTURES_FOLDER
        )
        self._textures_filenames_set: Set[str] = set(textures_filenames)

        self._textures_paths: List[str] = []
        self._textures_names: List[str] = []

        self._textures_filemap: Dict[str, str] = {}

        self._uv_scale = uv_scale

        # Keep a reference to the table for easier access
        if DEFAULT_TABLE_NAME in self._targets:
            self._table_shape = cast(Shape, self._targets[DEFAULT_TABLE_NAME])

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

    def randomize(self) -> None:
        """
        Samples a random texture from the given folder, and applies it to the
        table top using the given uv scaling
        """
        assert self._table_shape is not None

        choice_name = self._rng.choice(self._textures_names)
        choice_fpath = self._textures_filemap[choice_name]
        texture_obj, texture = self._pyrep.create_texture(choice_fpath)
        self._applyTexture(texture)
        texture_obj.remove()

    def _applyTexture(self, choice_texture: Texture) -> None:
        """
        Applies a given texture object to the table top

        Parameters
        ----------
            choice_texture: Texture
                The texture object to be applied to the table top
        """
        assert self._table_shape is not None

        texture_args = DEFAULT_TEXTURE_KWARGS.copy()
        texture_args["mapping_mode"] = TextureMappingMode.PLANE
        texture_args["uv_scaling"] = self._uv_scale

        table_shape_parts = self._table_shape.ungroup()
        # Only the first part contains the tabletop
        table_shape_parts[0].set_texture(choice_texture, **texture_args)
        self._table_shape = self._pyrep.group_objects(table_shape_parts)
