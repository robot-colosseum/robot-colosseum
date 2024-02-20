import hydra
from omegaconf import DictConfig
from rlbench.action_modes.action_mode import MoveArmThenGripper
from rlbench.action_modes.arm_action_modes import JointVelocity
from rlbench.action_modes.gripper_action_modes import Discrete

from colosseum import ASSETS_CONFIGS_FOLDER, TASKS_PY_FOLDER, TASKS_TTM_FOLDER
from colosseum.rlbench.extensions.environment import EnvironmentExt
from colosseum.rlbench.utils import ObservationConfigExt, name_to_class


@hydra.main(
    config_path=ASSETS_CONFIGS_FOLDER,
    config_name="basketball_in_hoop.yaml",
    version_base=None,
)
def main(cfg: DictConfig) -> int:
    task_name = cfg.env.task_name
    task_class = name_to_class(task_name, TASKS_PY_FOLDER)
    if task_class is None:
        return 1

    env = EnvironmentExt(
        action_mode=MoveArmThenGripper(
            arm_action_mode=JointVelocity(), gripper_action_mode=Discrete()
        ),
        obs_config=ObservationConfigExt(cfg.data),
        headless=False,
        path_task_ttms=TASKS_TTM_FOLDER,
        env_config=cfg.env,
    )
    env.launch()

    task_env = env.get_task(task_class)

    if task_env is not None:
        for i in range(cfg.data.episodes_per_task):
            print(f"Running episode {i+1} / {cfg.data.episodes_per_task}")
            _ = task_env.get_demos(1, live_demos=True)

    return 0


if __name__ == "__main__":
    SystemExit(main())
