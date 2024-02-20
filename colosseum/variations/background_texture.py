from __future__ import annotations

import os
import re
import warnings
from typing import Dict, List, Optional, Set, Tuple, cast

from omegaconf import DictConfig
from pyrep import PyRep
from pyrep.const import ObjectType, TextureMappingMode
from pyrep.objects.shape import Shape

from colosseum import ASSETS_TEXTURES_FOLDER
from colosseum.variations.utils import safeGetValue
from colosseum.variations.variation import IVariation

DEFAULT_WALLS_NAMES = ["Wall1", "Wall2", "Wall3", "Wall4"]

DEFAULT_TEXTURE_KWARGS = {
    "mapping_mode": TextureMappingMode.PLANE,
    "repeat_along_u": True,
    "repeat_along_v": True,
    "uv_scaling": [4.0, 4.0],
}


class BackgroundTextureVariation(IVariation):
    """
    Background texture variation, can change the walls' texture in simulation
    """

    VARIATION_ID = "background_texture"

    @staticmethod
    def CreateFromConfig(
        pyrep: PyRep,
        name: Optional[str],
        cfg: DictConfig,
    ) -> BackgroundTextureVariation:
        """
        Factory function used to create a background texture variation from a
        given configuration coming from yaml through OmegaConf
        """
        textures_folder = safeGetValue(cfg, "textures_folder", "")
        textures_filenames = safeGetValue(cfg, "textures_filenames", [])
        uv_scale = safeGetValue(cfg, "uv_scale", (1.0, 1.0))
        seed = safeGetValue(cfg, "seed", None)

        return BackgroundTextureVariation(
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
        Creates a background texture variation to randomize the walls' texture

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
            seed: Optional[int]
                The seed used for any random number generators
        """
        super().__init__(
            pyrep, name, ObjectType.SHAPE, DEFAULT_WALLS_NAMES, seed=seed
        )

        self._walls_shapes: List[Shape] = []
        self._textures_folder: str = (
            textures_folder if textures_folder != "" else ASSETS_TEXTURES_FOLDER
        )
        self._textures_filenames_set: Set[str] = set(textures_filenames)

        self._textures_paths: List[str] = []
        self._textures_names: List[str] = []

        self._textures_filemap: Dict[str, str] = {}

        self._uv_scale = uv_scale

        if len(self._targets) < 1:
            warnings.warn(
                "BackgroundTextureVariation > Couldn't find the "
                + "shape for the background walls with names "
                + f"{DEFAULT_WALLS_NAMES}"
            )
            return

        # Keep a reference to the walls for easier access
        self._walls_shapes = [
            cast(Shape, self._targets[wall_name])
            for wall_name in DEFAULT_WALLS_NAMES
        ]

        # Use textures_filenames if given by the user, otherwise assumme all
        # textures in the given directory are available
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
        Samples a random texture from the given folder, and applies it to all
        the walls that surround the scene, using the given uv_scaling
        """
        assert len(self._walls_shapes) > 0

        choice_name = self._rng.choice(self._textures_names)
        choice_fpath = self._textures_filemap[choice_name]
        if self._pyrep is not None:
            texture_obj, texture = self._pyrep.create_texture(choice_fpath)

            # Apply the texture to all walls ----------------------------------
            for wall_shape in self._walls_shapes:
                wall_shape.set_texture(texture, **DEFAULT_TEXTURE_KWARGS)
            # -----------------------------------------------------------------

            texture_obj.remove()
