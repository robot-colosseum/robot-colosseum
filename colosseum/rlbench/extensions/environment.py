import inspect
import os
import warnings
from typing import Optional

from omegaconf import DictConfig
from pyrep import PyRep
from pyrep.robots.arms.panda import Panda
from rlbench.action_modes.action_mode import ActionMode
from rlbench.backend.const import TTT_FILE
from rlbench.backend.robot import Robot
from rlbench.backend.scene import Scene
from rlbench.const import SUPPORTED_ROBOTS
from rlbench.environment import DIR_PATH, Environment
from rlbench.observation_config import ObservationConfig
from rlbench.sim2real.domain_randomization import (
    DynamicsRandomizationConfig,
    RandomizeEvery,
    VisualRandomizationConfig,
)
from rlbench.sim2real.domain_randomization_scene import DomainRandomizationScene

from colosseum.rlbench.extensions.scene import SceneExt

# If the user doesn't provide the location of .ttm files, use this as default
DEFAULT_PATH_TTMS = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "task_ttms"
)


class EnvironmentExt(Environment):
    def __init__(
        self,
        action_mode: ActionMode,
        dataset_root: str = "",
        obs_config: ObservationConfig = ObservationConfig(),
        headless: bool = False,
        static_positions: bool = False,
        robot_setup: str = "panda",
        randomize_every: Optional[RandomizeEvery] = None,
        use_variations: bool = True,
        frequency: int = 1,
        vis_random_config: Optional[VisualRandomizationConfig] = None,
        dyn_random_config: Optional[DynamicsRandomizationConfig] = None,
        attach_grasped_objects: bool = True,
        shaped_rewards: bool = False,
        path_task_ttms: str = DEFAULT_PATH_TTMS,
        env_config: DictConfig = DictConfig({}),
    ):
        # HACK: This is a workaround for the case of using RLBench from PerAct
        arg_count: int = len(inspect.signature(Environment.__init__).parameters)
        if arg_count == 12:
            # Using implementation from RLBench fork from PerAct
            super().__init__(
                action_mode,
                dataset_root,
                obs_config,
                headless,
                static_positions,
                robot_setup,
                randomize_every,  # type: ignore
                frequency,
                vis_random_config,  # type: ignore
                dyn_random_config,  # type: ignore
                attach_grasped_objects,
            )
        elif arg_count == 13:
            # Using implementation from RLBench upstream repo
            super().__init__(
                action_mode,
                dataset_root,
                obs_config,
                headless,
                static_positions,
                robot_setup,
                randomize_every,  # type: ignore
                frequency,
                vis_random_config,  # type: ignore
                dyn_random_config,  # type: ignore
                attach_grasped_objects,
                shaped_rewards,  # type: ignore
            )
        else:
            raise RuntimeError(
                "Unexpected number of arguments in Environment.__init__"
            )

        self._path_task_ttms: str = path_task_ttms
        self._use_variations: bool = use_variations
        self._env_config: DictConfig = env_config

    def launch(self) -> None:
        if self._pyrep is not None:
            raise RuntimeError("Already called launch!")
        self._pyrep = PyRep()
        self._pyrep.launch(
            os.path.join(DIR_PATH, TTT_FILE), headless=self._headless
        )

        arm_class, gripper_class, _ = SUPPORTED_ROBOTS[self._robot_setup]

        if self._robot_setup != "panda":
            panda_arm = Panda()
            panda_pos = panda_arm.get_position()
            panda_arm.remove()
            arm_path = os.path.join(
                DIR_PATH, "robot_ttms", self._robot_setup + ".ttm"
            )
            self._pyrep.import_model(arm_path)
            arm, gripper = arm_class(), gripper_class()
            arm.set_position(panda_pos)
        else:
            arm, gripper = arm_class(), gripper_class()

        self._robot = Robot(arm, gripper)
        # Use our extensions instead of the vanilla version -------------------
        if self._randomize_every is None:
            if self._use_variations:
                scene_config = DictConfig({})
                if "scene" not in self._env_config:
                    warnings.warn(
                        "There is no scene config data in the given env config"
                    )
                else:
                    scene_config = self._env_config.scene

                self._scene = SceneExt(
                    self._pyrep,
                    self._robot,
                    obs_config=self._obs_config,
                    robot_setup=self._robot_setup,
                    path_task_ttms=self._path_task_ttms,
                    scene_config=scene_config,
                )
            else:
                self._scene = Scene(
                    self._pyrep,
                    self._robot,
                    self._obs_config,
                    self._robot_setup,
                )
        else:
            self._scene = DomainRandomizationScene(
                self._pyrep,
                self._robot,
                self._obs_config,
                self._robot_setup,
                self._randomize_every,
                self._frequency,
                self._visual_randomization_config,
                self._dynamics_randomization_config,
            )
        # ---------------------------------------------------------------------
        self._action_mode.arm_action_mode.set_control_mode(self._robot)
