from __future__ import annotations

import os
import re
import warnings
from typing import Dict, List, Optional, Set

from numpy.typing import NDArray
from omegaconf import DictConfig
from pyrep import PyRep
from pyrep.const import ObjectType
from pyrep.objects.object import Object
from pyrep.objects.shape import Shape
from rlbench.backend.exceptions import BoundaryError
from rlbench.backend.spawn_boundary import SpawnBoundary

from colosseum import ASSETS_MODELS_TTM_FOLDER
from colosseum.rlbench.extensions.spawn_boundary import SpawnBoundaryExt
from colosseum.variations.utils import safeGetValue
from colosseum.variations.variation import IVariation


class DistractorObjectVariation(IVariation):
    """
    Distractor object variation, can spawn distractor objects in the simulation
    """

    VARIATION_ID = "distractor_object"

    @staticmethod
    def CreateFromConfig(
        pyrep: PyRep,
        name: Optional[str],
        targets_names: List[str],
        cfg: DictConfig,
    ) -> DistractorObjectVariation:
        """
        Factory function used to create a distractor object variation from a
        given configuration coming from yaml through OmegaConf
        """
        obj_ttm_folder = safeGetValue(cfg, "objects_folder", "")
        obj_ttm_whitelist = safeGetValue(cfg, "objects_filenames", [])
        num_objs_to_spawn = safeGetValue(cfg, "num_objects", 1)
        num_steps_to_wait = safeGetValue(cfg, "num_steps_wait", 0)
        shapes_to_handle = safeGetValue(cfg, "shapes_to_handle", [])
        seed = safeGetValue(cfg, "seed", None)

        return DistractorObjectVariation(
            pyrep,
            name,
            targets_names,
            obj_ttm_folder=obj_ttm_folder,
            obj_ttm_whitelist=obj_ttm_whitelist,
            num_objs_to_spawn=num_objs_to_spawn,
            num_steps_to_wait=num_steps_to_wait,
            shapes_to_handle=shapes_to_handle,
            seed=seed,
        )

    def __init__(
        self,
        pyrep: PyRep,
        name: Optional[str],
        targets_names: List[str],
        obj_ttm_folder: str = ASSETS_MODELS_TTM_FOLDER,
        obj_ttm_whitelist: List[str] = [],
        num_objs_to_spawn: int = 1,
        num_steps_to_wait: int = 0,
        shapes_to_handle: List[str] = [],
        seed: Optional[int] = None,
    ):
        """
        Creates a variation that spawns an object randomly in the scene

        Parameters
        ----------
        pyrep: PyRep
            A handle to the pyrep simulation
        name: Optional[str]
            A unique identifier for this variation
        targets_names: List[str]
            A list of names of the valid shapes that define the spawn regions
        obj_ttm_folder: str
            The folder where the models of the objects are located
        obj_ttm_whitelist: List[str]
            A list of objects that can be used for this variation
        num_objs_to_spawn: int
            The number of objects to be spawned each time we use this variation
        num_steps_to_wait: int
            The number of steps to wait until the spawning process is executed
        shapes_to_handle: List[str]
            A list of object names to handle within the spawn boundary
        seed Optional[int]
                The seed used for any random number generators
        """
        super().__init__(
            pyrep, name, ObjectType.SHAPE, targets_names, seed=seed
        )

        self._num_objs_to_spawn: int = num_objs_to_spawn
        self._num_steps_to_wait: int = num_steps_to_wait
        self._num_steps_waiting: int = 0
        self._waiting: bool = self._num_steps_to_wait > 0

        self._obj_ttm_folder: str = (
            obj_ttm_folder if obj_ttm_folder != "" else ASSETS_MODELS_TTM_FOLDER
        )
        self._obj_filenames_set: Set[str] = set(obj_ttm_whitelist)
        self._shapes_to_handle: List[Shape] = [
            Shape(name) for name in shapes_to_handle
        ]
        self._shapes_to_handle_init_pose: List[NDArray] = []
        for shape in self._shapes_to_handle:
            self._shapes_to_handle_init_pose.append(shape.get_pose())

        self._models_paths: List[str] = []
        self._models_names: List[str] = []

        self._models_filemap: Dict[str, str] = {}

        self._spawn_boundary: Optional[SpawnBoundary] = None

        self._spawn_models: List[Optional[Object]] = []

        self._ready: bool = False

        if len(self._targets) < 1:
            warnings.warn(
                f"Couldn't find any spawn boundary with names {targets_names}"
            )
            return

        regex = re.compile("(.*ttm$)")
        candidate_models_filenames = [
            fname
            for fname in os.listdir(self._obj_ttm_folder)
            if regex.match(fname)
        ]

        # Check that candidates are in the whitelist (if any)
        valid_models_names = []
        for candidate_obj_name in candidate_models_filenames:
            if len(self._obj_filenames_set) < 1:
                valid_models_names.append(candidate_obj_name)
            elif candidate_obj_name in self._obj_filenames_set:
                valid_models_names.append(candidate_obj_name)

        for fname in valid_models_names:
            model_filepath = os.path.join(self._obj_ttm_folder, fname)
            # TODO(wilbert): use a better approach to getting the texture name
            model_filename = fname.split(".")[0]
            self._models_paths.append(model_filepath)
            self._models_names.append(model_filename)
            self._models_filemap[model_filename] = model_filepath

        boundaries = [boundary for _, boundary in self._targets.items()]
        self._spawn_boundary = SpawnBoundaryExt(boundaries)
        self._ready = True

    def on_init_episode(self) -> None:
        if self._num_steps_to_wait < 1:
            super().on_init_episode()
        else:
            self._waiting = self._num_steps_to_wait > 0
            self._num_steps_waiting = 0

    def on_step_episode(self) -> None:
        if self._waiting:
            self._num_steps_waiting += 1
            if self._num_steps_waiting >= self._num_steps_to_wait:
                self._waiting = False
                self.randomize()

    def randomize(self) -> None:
        """
        Spawns a new object from the models folder into one of the selected
        spawn areas.
        """
        if not self._ready:
            return

        if self._spawn_boundary is None:
            return

        self._spawn_boundary.clear()
        self.remove_models()
        # Sample one oodel from the list of models available
        for _ in range(self._num_objs_to_spawn):
            choice_name = self._rng.choice(self._models_names)
            choice_fpath = self._models_filemap[choice_name]
            choice_model = self._pyrep.import_model(choice_fpath)
            try:
                self._spawn_boundary.sample(
                    choice_model,
                    ignore_collisions=False,
                    min_distance=0.05,
                    min_rotation=(0.0, 0.0, 0.0),
                    max_rotation=(0.0, 0.0, 0.0),
                )
            except BoundaryError:
                warnings.warn(
                    "Couldn't place the object within the boundary of any spawn"
                )
            except RuntimeError:
                pass  # There's an internal error due to objsInTree in PyRep
            spawn_position = choice_model.get_position()
            choice_model_bbox = choice_model.get_model_bounding_box()
            choice_model_height = choice_model_bbox[5] - choice_model_bbox[4]
            spawn_position[2] += choice_model_height * 0.5
            choice_model.set_position(spawn_position)

            self._spawn_models.append(choice_model)

        # Handle shapes passed for the variation to manage
        for shape, shape_init_pose in zip(
            self._shapes_to_handle, self._shapes_to_handle_init_pose
        ):
            try:
                shape.set_pose(shape_init_pose)
                self._spawn_boundary.sample(
                    shape,
                    ignore_collisions=False,
                    min_distance=0.05,
                    min_rotation=(0.0, 0.0, 0.0),
                    max_rotation=(0.0, 0.0, 0.0),
                )
            except BoundaryError:
                pass
            except RuntimeError:
                pass

    def remove_models(self) -> None:
        """
        Removes all models spawned by this variation that are still part of the
        simulation.
        """
        while len(self._spawn_models) > 0:
            model = self._spawn_models.pop()
            if model is not None:
                model.remove()
