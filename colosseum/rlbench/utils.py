import abc
import importlib.util
import os
import pickle
import re
import sys
import warnings
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type

import numpy as np
from omegaconf import DictConfig
from PIL import Image
from pyrep.const import RenderMode
from pyrep.objects.dummy import Dummy
from pyrep.objects.vision_sensor import VisionSensor
from rlbench.backend import const, utils
from rlbench.backend.observation import Observation
from rlbench.backend.task import Task
from rlbench.demo import Demo
from rlbench.observation_config import ObservationConfig

from colosseum import TASKS_PY_FOLDER as DEFAULT_TASKS_PY_FOLDER
from colosseum.rlbench.extensions.environment import EnvironmentExt


@dataclass
class TaskInfo:
    task_name: str = field(default="")
    task_class: Optional[type] = field(default=None)
    task_path: str = field(default="")


def name_to_class(
    task_name: str, tasks_py_folder: str = DEFAULT_TASKS_PY_FOLDER
) -> Optional[type]:
    """
    Returns a class for the corresponding task located at the given folder

    Parameters
    ----------
        task_name: str
            The name of the task we want to use
        tasks_py_folder: str
            The folder where to find the tasks files

    Returns
    -------
        Optional[type]
            The class found for the requested task, otherwise None
    """
    task_filepath = os.path.join(tasks_py_folder, task_name) + ".py"
    class_name = "".join([w[0].upper() + w[1:] for w in task_name.split("_")])
    spec = importlib.util.spec_from_file_location(task_name, task_filepath)
    if spec is None or spec.loader is None:
        warnings.warn(
            f"Couldn't create spec for module {task_name} @ {task_filepath}"
        )
        return None

    module = importlib.util.module_from_spec(spec)
    sys.modules[task_name] = module
    try:
        spec.loader.exec_module(module)
    except FileNotFoundError:
        warnings.warn(f"No such taskfile {task_filepath}")
        return None

    try:
        task_class = getattr(module, class_name)
    except AttributeError:
        warnings.warn(
            f"Couldn't load class {class_name} from module @ {task_filepath}"
        )
        return None
    return task_class


def get_tasks_in_folder(
    tasks_py_folder: str = DEFAULT_TASKS_PY_FOLDER,
) -> List[TaskInfo]:
    """
    Returns a list of (task_name, task_class) pairs located in the given folder

    Parameters
    ----------
        tasks_py_folder: str
            The folder where to find the tasks files

    Returns
    -------
        List[Tuple[str, Optional[type]]]
    """
    regex = re.compile(r"^[a-z]+_[a-z_]+\.py$")
    tasks_files = [
        file for file in os.listdir(tasks_py_folder) if regex.match(file)
    ]

    return [
        TaskInfo(
            task_name=file[:-3],
            task_class=name_to_class(file[:-3], tasks_py_folder),
            task_path=os.path.abspath(os.path.join(tasks_py_folder, file)),
        )
        for file in tasks_files
    ]


class ObservationConfigExt(ObservationConfig):
    def __init__(self, data: DictConfig):
        super().__init__()

        self.set_all_low_dim(True)
        self.set_all_high_dim(False)

        # Left shoulder camera settings ----------------------------------------
        self.left_shoulder_camera.rgb = (
            data.images.rgb and data.cameras.left_shoulder
        )
        self.left_shoulder_camera.depth = (
            data.images.depth and data.cameras.left_shoulder
        )
        self.left_shoulder_camera.mask = (
            data.images.mask and data.cameras.left_shoulder
        )
        self.left_shoulder_camera.point_cloud = (
            data.images.point_cloud and data.cameras.left_shoulder
        )
        self.left_shoulder_camera.image_size = data.image_size
        self.left_shoulder_camera.depth_in_meters = data.depth_in_meters
        self.left_shoulder_camera.masks_as_one_channel = (
            data.masks_as_one_channel
        )
        self.left_shoulder_camera.render_mode = (
            RenderMode.OPENGL3
            if data.renderer == "opengl3"
            else RenderMode.OPENGL
        )

        # Right shoulder camera settings ---------------------------------------
        self.right_shoulder_camera.rgb = (
            data.images.rgb and data.cameras.right_shoulder
        )
        self.right_shoulder_camera.depth = (
            data.images.depth and data.cameras.right_shoulder
        )
        self.right_shoulder_camera.mask = (
            data.images.mask and data.cameras.right_shoulder
        )
        self.right_shoulder_camera.point_cloud = (
            data.images.point_cloud and data.cameras.right_shoulder
        )
        self.right_shoulder_camera.image_size = data.image_size
        self.right_shoulder_camera.depth_in_meters = data.depth_in_meters
        self.right_shoulder_camera.masks_as_one_channel = (
            data.masks_as_one_channel
        )
        self.right_shoulder_camera.render_mode = (
            RenderMode.OPENGL3
            if data.renderer == "opengl3"
            else RenderMode.OPENGL
        )

        # Overhead camera settings ---------------------------------------------
        self.overhead_camera.rgb = data.images.rgb and data.cameras.overhead
        self.overhead_camera.depth = data.images.depth and data.cameras.overhead
        self.overhead_camera.mask = data.images.mask and data.cameras.overhead
        self.overhead_camera.point_cloud = (
            data.images.point_cloud and data.cameras.overhead
        )
        self.overhead_camera.image_size = data.image_size
        self.overhead_camera.depth_in_meters = data.depth_in_meters
        self.overhead_camera.masks_as_one_channel = data.masks_as_one_channel
        self.overhead_camera.render_mode = (
            RenderMode.OPENGL3
            if data.renderer == "opengl3"
            else RenderMode.OPENGL
        )

        # Wrist camera settings ------------------------------------------------
        self.wrist_camera.rgb = data.images.rgb and data.cameras.wrist
        self.wrist_camera.depth = data.images.depth and data.cameras.wrist
        self.wrist_camera.mask = data.images.mask and data.cameras.wrist
        self.wrist_camera.point_cloud = (
            data.images.point_cloud and data.cameras.wrist
        )
        self.wrist_camera.image_size = data.image_size
        self.wrist_camera.depth_in_meters = data.depth_in_meters
        self.wrist_camera.masks_as_one_channel = data.masks_as_one_channel
        self.wrist_camera.render_mode = (
            RenderMode.OPENGL3
            if data.renderer == "opengl3"
            else RenderMode.OPENGL
        )

        # Front camera settings ------------------------------------------------
        self.front_camera.rgb = data.images.rgb and data.cameras.front
        self.front_camera.depth = data.images.depth and data.cameras.front
        self.front_camera.mask = data.images.mask and data.cameras.front
        self.front_camera.point_cloud = (
            data.images.point_cloud and data.cameras.front
        )
        self.front_camera.image_size = data.image_size
        self.front_camera.depth_in_meters = data.depth_in_meters
        self.front_camera.masks_as_one_channel = data.masks_as_one_channel
        self.front_camera.depth_in_meters = data.depth_in_meters
        self.front_camera.masks_as_one_channel = data.masks_as_one_channel
        self.front_camera.render_mode = (
            RenderMode.OPENGL3
            if data.renderer == "opengl3"
            else RenderMode.OPENGL
        )


def check_and_make(folder: str) -> None:
    if not os.path.exists(folder):
        os.makedirs(folder)


def save_demo(
    data_cfg: DictConfig,
    demo: Demo,
    example_path: str,
    variation: Optional[int] = None,
) -> None:
    # Save image data first, and then None the image data, and pickle
    left_shoulder_rgb_path = os.path.join(
        example_path, const.LEFT_SHOULDER_RGB_FOLDER
    )
    left_shoulder_depth_path = os.path.join(
        example_path, const.LEFT_SHOULDER_DEPTH_FOLDER
    )
    left_shoulder_mask_path = os.path.join(
        example_path, const.LEFT_SHOULDER_MASK_FOLDER
    )
    right_shoulder_rgb_path = os.path.join(
        example_path, const.RIGHT_SHOULDER_RGB_FOLDER
    )
    right_shoulder_depth_path = os.path.join(
        example_path, const.RIGHT_SHOULDER_DEPTH_FOLDER
    )
    right_shoulder_mask_path = os.path.join(
        example_path, const.RIGHT_SHOULDER_MASK_FOLDER
    )
    overhead_rgb_path = os.path.join(example_path, const.OVERHEAD_RGB_FOLDER)
    overhead_depth_path = os.path.join(
        example_path, const.OVERHEAD_DEPTH_FOLDER
    )
    overhead_mask_path = os.path.join(example_path, const.OVERHEAD_MASK_FOLDER)
    wrist_rgb_path = os.path.join(example_path, const.WRIST_RGB_FOLDER)
    wrist_depth_path = os.path.join(example_path, const.WRIST_DEPTH_FOLDER)
    wrist_mask_path = os.path.join(example_path, const.WRIST_MASK_FOLDER)
    front_rgb_path = os.path.join(example_path, const.FRONT_RGB_FOLDER)
    front_depth_path = os.path.join(example_path, const.FRONT_DEPTH_FOLDER)
    front_mask_path = os.path.join(example_path, const.FRONT_MASK_FOLDER)

    if data_cfg.images.rgb:
        if data_cfg.cameras.left_shoulder:
            check_and_make(left_shoulder_rgb_path)
        if data_cfg.cameras.right_shoulder:
            check_and_make(right_shoulder_rgb_path)
        if data_cfg.cameras.overhead:
            check_and_make(overhead_rgb_path)
        if data_cfg.cameras.wrist:
            check_and_make(wrist_rgb_path)
        if data_cfg.cameras.front:
            check_and_make(front_rgb_path)

    if data_cfg.images.depth:
        if data_cfg.cameras.left_shoulder:
            check_and_make(left_shoulder_depth_path)
        if data_cfg.cameras.right_shoulder:
            check_and_make(right_shoulder_depth_path)
        if data_cfg.cameras.overhead:
            check_and_make(overhead_depth_path)
        if data_cfg.cameras.wrist:
            check_and_make(wrist_depth_path)
        if data_cfg.cameras.front:
            check_and_make(front_depth_path)

    if data_cfg.images.mask:
        if data_cfg.cameras.left_shoulder:
            check_and_make(left_shoulder_mask_path)
        if data_cfg.cameras.right_shoulder:
            check_and_make(right_shoulder_mask_path)
        if data_cfg.cameras.overhead:
            check_and_make(overhead_mask_path)
        if data_cfg.cameras.wrist:
            check_and_make(wrist_mask_path)
        if data_cfg.cameras.front:
            check_and_make(front_mask_path)

    for i in range(len(demo)):
        obs = demo[i]

        if data_cfg.images.rgb:
            if data_cfg.cameras.left_shoulder:
                left_shoulder_rgb = Image.fromarray(obs.left_shoulder_rgb)
                left_shoulder_rgb.save(
                    os.path.join(left_shoulder_rgb_path, const.IMAGE_FORMAT % i)
                )
            if data_cfg.cameras.right_shoulder:
                right_shoulder_rgb = Image.fromarray(obs.right_shoulder_rgb)
                right_shoulder_rgb.save(
                    os.path.join(
                        right_shoulder_rgb_path, const.IMAGE_FORMAT % i
                    )
                )
            if data_cfg.cameras.overhead:
                overhead_rgb = Image.fromarray(obs.overhead_rgb)
                overhead_rgb.save(
                    os.path.join(overhead_rgb_path, const.IMAGE_FORMAT % i)
                )
            if data_cfg.cameras.wrist:
                wrist_rgb = Image.fromarray(obs.wrist_rgb)
                wrist_rgb.save(
                    os.path.join(wrist_rgb_path, const.IMAGE_FORMAT % i)
                )
            if data_cfg.cameras.front:
                front_rgb = Image.fromarray(obs.front_rgb)
                front_rgb.save(
                    os.path.join(front_rgb_path, const.IMAGE_FORMAT % i)
                )

        if data_cfg.images.depth:
            if data_cfg.cameras.left_shoulder:
                left_shoulder_depth = utils.float_array_to_rgb_image(
                    obs.left_shoulder_depth, scale_factor=const.DEPTH_SCALE
                )
                left_shoulder_depth.save(
                    os.path.join(
                        left_shoulder_depth_path, const.IMAGE_FORMAT % i
                    )
                )
            if data_cfg.cameras.right_shoulder:
                right_shoulder_depth = utils.float_array_to_rgb_image(
                    obs.right_shoulder_depth, scale_factor=const.DEPTH_SCALE
                )
                right_shoulder_depth.save(
                    os.path.join(
                        right_shoulder_depth_path, const.IMAGE_FORMAT % i
                    )
                )
            if data_cfg.cameras.overhead:
                overhead_depth = utils.float_array_to_rgb_image(
                    obs.overhead_depth, scale_factor=const.DEPTH_SCALE
                )
                overhead_depth.save(
                    os.path.join(overhead_depth_path, const.IMAGE_FORMAT % i)
                )
            if data_cfg.cameras.wrist:
                wrist_depth = utils.float_array_to_rgb_image(
                    obs.wrist_depth, scale_factor=const.DEPTH_SCALE
                )
                wrist_depth.save(
                    os.path.join(wrist_depth_path, const.IMAGE_FORMAT % i)
                )
            if data_cfg.cameras.front:
                front_depth = utils.float_array_to_rgb_image(
                    obs.front_depth, scale_factor=const.DEPTH_SCALE
                )
                front_depth.save(
                    os.path.join(front_depth_path, const.IMAGE_FORMAT % i)
                )

        if data_cfg.images.mask:
            if data_cfg.cameras.left_shoulder:
                left_shoulder_mask = Image.fromarray(
                    (obs.left_shoulder_mask * 255).astype(np.uint8)
                )
                left_shoulder_mask.save(
                    os.path.join(
                        left_shoulder_mask_path, const.IMAGE_FORMAT % i
                    )
                )

            if data_cfg.cameras.right_shoulder:
                right_shoulder_mask = Image.fromarray(
                    (obs.right_shoulder_mask * 255).astype(np.uint8)
                )
                right_shoulder_mask.save(
                    os.path.join(
                        right_shoulder_mask_path, const.IMAGE_FORMAT % i
                    )
                )

            if data_cfg.cameras.overhead:
                overhead_mask = Image.fromarray(
                    (obs.overhead_mask * 255).astype(np.uint8)
                )
                overhead_mask.save(
                    os.path.join(overhead_mask_path, const.IMAGE_FORMAT % i)
                )

            if data_cfg.cameras.wrist:
                wrist_mask = Image.fromarray(
                    (obs.wrist_mask * 255).astype(np.uint8)
                )
                wrist_mask.save(
                    os.path.join(wrist_mask_path, const.IMAGE_FORMAT % i)
                )

            if data_cfg.cameras.front:
                front_mask = Image.fromarray(
                    (obs.front_mask * 255).astype(np.uint8)
                )
                front_mask.save(
                    os.path.join(front_mask_path, const.IMAGE_FORMAT % i)
                )

        # We save the images separately, so set these to None for pickling.
        obs.left_shoulder_rgb = None
        obs.left_shoulder_depth = None
        obs.left_shoulder_point_cloud = None
        obs.left_shoulder_mask = None
        obs.right_shoulder_rgb = None
        obs.right_shoulder_depth = None
        obs.right_shoulder_point_cloud = None
        obs.right_shoulder_mask = None
        obs.overhead_rgb = None
        obs.overhead_depth = None
        obs.overhead_point_cloud = None
        obs.overhead_mask = None
        obs.wrist_rgb = None
        obs.wrist_depth = None
        obs.wrist_point_cloud = None
        obs.wrist_mask = None
        obs.front_rgb = None
        obs.front_depth = None
        obs.front_point_cloud = None
        obs.front_mask = None

    with open(os.path.join(example_path, const.LOW_DIM_PICKLE), "wb") as f:
        pickle.dump(demo, f)

    if variation is not None:
        with open(
            os.path.join(example_path, "variation_number.pkl"), "wb"
        ) as f:
            pickle.dump(variation, f)


def get_variation_name(
    collection_cfg: Dict[str, Any], spreadsheet_idx: int
) -> str:
    """
    Returns the name of the variation (given by spreadsheet index)

    Parameters
    ----------
        collection_cfg : Dict[str, Any]
            The data collection strategy parsed from the JSON strategy file
        spreadsheet_idx : int
            The index in the spreadsheet to use for the current task variation

    Returns
    -------
        str
            The name of the variation (given by spreadsheet index)
    """
    return collection_cfg["strategy"][spreadsheet_idx]["variation_name"]


def should_collect_task(
    collection_cfg: Dict[str, Any], spreadsheet_idx: int
) -> bool:
    """
    Returns whether or not the variation (given by spreadsheet index) is enabled
    in the given collection strategy (given as a JSON object)

    Parameters
    ----------
        collection_cfg : Dict[str, Any]
            The data collection strategy parsed from the JSON strategy file
        spreadsheet_idx : int
            The index in the spreadsheet to use for the current task variation

    Returns
    -------
        bool
            Whether or not the variation is enabled
    """
    return collection_cfg["strategy"][spreadsheet_idx]["enabled"]


def get_spreadsheet_config(
    base_cfg: DictConfig, collection_cfg: Dict[str, Any], spreadsheet_idx: int
) -> DictConfig:
    """
    Creates a new config object based on a base configuration, updated with
    entries to match the options from the data collection strategy in JSON
    format for the given spreadsheet index.

    Parameters
    ----------
        base_cfg : DictConfig
            The base configuration for the current task
        collection_cfg : Dict[str, Any]
            The data collection strategy parsed from the JSON strategy file
        spreadsheet_idx : int
            The index in the spreadsheet to use for the current task variation

    Returns
    -------
        DictConfig
            The new configuration object with the updated options for this
            variation
    """
    spreadsheet_cfg = base_cfg.copy()

    collections_variation_cfg = collection_cfg["strategy"][spreadsheet_idx][
        "variations"
    ]
    for collection_var_cfg in collections_variation_cfg:
        var_type = collection_var_cfg["type"]
        var_name = collection_var_cfg["name"]
        var_enabled = collection_var_cfg["enabled"]
        for variation_cfg in spreadsheet_cfg.env.scene.factors:
            if variation_cfg.variation != var_type:
                continue
            else:
                if var_name == "any" or (
                    "name" in variation_cfg and variation_cfg.name == var_name
                ):
                    variation_cfg.enabled = var_enabled

    return spreadsheet_cfg


class ICameraMotion(abc.ABC):
    def __init__(self, cam: VisionSensor):
        self.cam = cam
        self._prev_pose: np.ndarray = cam.get_pose()

    @abc.abstractmethod
    def step(self) -> None:
        ...

    def save_pose(self) -> None:
        self._prev_pose = self.cam.get_pose()

    def restore_pose(self) -> None:
        self.cam.set_pose(self._prev_pose)


class CircleCameraMotion(ICameraMotion):
    def __init__(self, cam: VisionSensor, origin: Dummy, speed: float):
        super().__init__(cam)
        self.origin = origin
        self.speed = speed

    def step(self) -> None:
        self.origin.rotate([0, 0, self.speed])


class TaskRecorder:
    def __init__(self, env: EnvironmentExt, cam_motion: ICameraMotion, fps=30):
        self._env = env
        self._cam_motion = cam_motion
        self._fps = fps
        self._snaps = []
        self._current_snaps = []

    def take_snap(self, _: Observation) -> None:
        self._cam_motion.step()
        self._current_snaps.append(
            (self._cam_motion.cam.capture_rgb() * 255.0).astype(np.uint8)
        )

    def record_task(self, task_class: Type[Task]) -> bool:
        task_env = self._env.get_task(task_class)
        self._cam_motion.save_pose()
        while True:
            try:
                (demo,) = task_env.get_demos(
                    amount=1,
                    live_demos=True,
                    callable_each_step=self.take_snap,
                    max_attempts=1,
                )
                break
            except RuntimeError:
                self._cam_motion.restore_pose()
                self._current_snaps = []
        self._snaps.extend(self._current_snaps)
        self._current_snaps = []
        return True

    def save_snaps(self, path: str) -> None:
        print("Saving snaps ...")
        if len(self._snaps) < 1:
            return

        for i, snap in enumerate(self._snaps):
            Image.fromarray(snap).save(
                os.path.join(path, const.IMAGE_FORMAT % i)
            )

    def save_video(self, path: str) -> None:
        print("Converting to video ...")
        try:
            import cv2
        except ImportError:
            warnings.warn("Couldn't import cv2, skipping video creation")
            return

        video = cv2.VideoWriter(
            path,
            cv2.VideoWriter_fourcc("m", "p", "4", "v"),  # type: ignore
            self._fps,
            tuple(self._cam_motion.cam.get_resolution()),
        )
        for image in self._snaps:
            video.write(cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        video.release()
        self._snaps = []
