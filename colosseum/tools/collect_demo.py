import os
import pickle

import hydra
import numpy as np
from omegaconf import DictConfig
from rlbench.action_modes.action_mode import MoveArmThenGripper
from rlbench.action_modes.arm_action_modes import JointVelocity
from rlbench.action_modes.gripper_action_modes import Discrete
from rlbench.backend import const

from colosseum import ASSETS_CONFIGS_FOLDER, TASKS_PY_FOLDER, TASKS_TTM_FOLDER
from colosseum.rlbench.extensions.environment import EnvironmentExt
from colosseum.rlbench.utils import (
    ObservationConfigExt,
    check_and_make,
    name_to_class,
    save_demo,
)


@hydra.main(
    config_path=ASSETS_CONFIGS_FOLDER,
    config_name="basketball_in_hoop.yaml",
    version_base=None,
)
def main(config: DictConfig) -> int:
    check_and_make(config.data.save_path)

    np.random.seed(config.env.seed)

    data_cfg, env_cfg = config.data, config.env

    task_class = name_to_class(config.env.task_name, TASKS_PY_FOLDER)
    assert (
        task_class is not None
    ), f"Can't get task-class for task {config.env.task_name}"

    rlbench_env = EnvironmentExt(
        action_mode=MoveArmThenGripper(
            arm_action_mode=JointVelocity(), gripper_action_mode=Discrete()
        ),
        obs_config=ObservationConfigExt(data_cfg),
        headless=True,
        path_task_ttms=TASKS_TTM_FOLDER,
        env_config=env_cfg,
    )

    rlbench_env.launch()

    task_env = rlbench_env.get_task(task_class)

    descriptions, _ = task_env.reset()

    # --------------------------------------------------------------------------
    variation_path = os.path.join(
        data_cfg.save_path,
        task_env.get_name(),
        const.VARIATIONS_FOLDER % 0,  # just grab the first  rlbench variation
    )

    check_and_make(variation_path)

    with open(
        os.path.join(variation_path, const.VARIATION_DESCRIPTIONS), "wb"
    ) as f:
        pickle.dump(descriptions, f)

    episodes_path = os.path.join(variation_path, const.EPISODES_FOLDER)
    check_and_make(episodes_path)

    abort_variation = False
    for ex_idx in range(data_cfg.episodes_per_task):
        print(f"Task: {task_env.get_name()} // Variation: 0 // Demo: {ex_idx}")

        attempts = 10
        while attempts > 0:
            try:
                # TODO: for now we do the explicit looping.
                (demo,) = task_env.get_demos(amount=1, live_demos=True)
            except Exception:
                attempts -= 1
                if attempts > 0:
                    continue
                print(
                    f"Failed with task {task_env.get_name()}, sample: {ex_idx}"
                )
                abort_variation = True
                break
            episode_path = os.path.join(
                episodes_path, const.EPISODE_FOLDER % ex_idx
            )
            save_demo(data_cfg, demo, episode_path)
            break
        if abort_variation:
            break

    rlbench_env.shutdown()
    # --------------------------------------------------------------------------

    return 0


if __name__ == "__main__":
    SystemExit(main())
