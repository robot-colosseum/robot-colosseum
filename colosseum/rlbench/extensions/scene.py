import inspect
import os
import warnings
from typing import List

from omegaconf import DictConfig, ListConfig
from pyrep import PyRep
from pyrep.objects.object import Object
from rlbench.backend.robot import Robot
from rlbench.backend.scene import Scene
from rlbench.environment import Task
from rlbench.observation_config import ObservationConfig

from colosseum.variations.manager import VariationsManager

# If the user doesn't provide the location of .ttm files, use this as default
DEFAULT_PATH_TTMS = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "task_ttms"
)


class SceneExt(Scene):
    def __init__(
        self,
        pyrep: PyRep,
        robot: Robot,
        obs_config: ObservationConfig = ObservationConfig(),
        robot_setup: str = "panda",
        path_task_ttms: str = DEFAULT_PATH_TTMS,
        scene_config: DictConfig = DictConfig({}),
    ):
        """
        Creates a new SceneExt object, which updates the original Scene class
        from RLBench to include variations in the simulation.

        Parmaeters
        ----------
            pyrep: PyRep
                A handle to the pyrep simulation
            robot: Robot
                A handle to the robot used in the simulation
            obs_config: ObservationConfig
                The observation configuration that will be used to generate the
                observations of the simulation
            robot_setup: str
                An identifier of the robot setup used for this simulation
            path_task_ttms: str
                The path where the .ttm files of the tasks are located
            scene_config: DictConfig
                The configuration of the scene, which includes the factors that
                will be used to generate the variations in the simulation
        """
        super().__init__(pyrep, robot, obs_config, robot_setup)

        self._path_task_ttms: str = path_task_ttms
        factors_config: ListConfig = ListConfig([])
        if "factors" not in scene_config:
            warnings.warn(
                "SceneExt >>> given scene_cfg doesnt't contain any factors"
            )
        else:
            factors_config = scene_config.factors

        self._var_manager = VariationsManager(self.pyrep, factors_config)

    def load(self, task: Task) -> None:
        """
        Loads the task .ttm model into the simulation. This is done manually, as
        the previous implementation was hardcoded to always use the default path
        to .ttm files
        """
        # Load task manually (don't call task.load) ----------------------------
        if not Object.exists(task.name):
            ttm_file = os.path.join(self._path_task_ttms, f"{task.name}.ttm")
            if not os.path.isfile(ttm_file):
                raise FileNotFoundError(f"Couldn't find .ttm file {ttm_file}")

            task._base_object = self.pyrep.import_model(ttm_file)
        # ----------------------------------------------------------------------

        task.get_base().set_position(self._workspace.get_position())
        self._initial_task_state = task.get_state()
        self.task = task
        self._initial_task_pose = task.boundary_root().get_orientation()
        self._has_init_task = self._has_init_episode = False
        self._variation_index = 0

    def init_episode(
        self,
        index: int,
        randomly_place: bool = True,
        max_attempts: int = 5,
        place_demo: bool = False,
    ) -> List[str]:
        """
        Method called to initialize a new episode on every reset of the
        simulation. We also manage the setup for the variations in here
        """
        if not self._has_init_task:
            self._var_manager.on_init_task()
        self._var_manager.on_init_episode()

        # HACK: This is a workaround for the case of using RLBench from PerAct
        arg_count: int = len(inspect.signature(Scene.init_episode).parameters)
        if arg_count == 5:
            # Using implementation from RLBench upstream repo
            return super().init_episode(
                index,
                randomly_place,
                max_attempts,
                place_demo,  # type: ignore
            )
        else:
            # Using implementation from RLBench fork from PerAct
            return super().init_episode(index, randomly_place, max_attempts)

    def step(self):
        super().step()

        self._var_manager.on_step_episode()
