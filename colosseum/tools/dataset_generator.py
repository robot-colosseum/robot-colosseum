from __future__ import annotations

import json
import os
import pickle
from multiprocessing import Manager, Process
from typing import Any, Dict, Optional, Type, cast

import hydra
import numpy as np
from omegaconf import DictConfig, OmegaConf
from rlbench.action_modes.action_mode import MoveArmThenGripper
from rlbench.action_modes.arm_action_modes import JointVelocity
from rlbench.action_modes.gripper_action_modes import Discrete
from rlbench.backend import const
from rlbench.backend.task import Task

from colosseum import (
    ASSETS_CONFIGS_FOLDER,
    ASSETS_JSON_FOLDER,
    TASKS_PY_FOLDER,
    TASKS_TTM_FOLDER,
)
from colosseum.rlbench.extensions.environment import EnvironmentExt
from colosseum.rlbench.utils import (
    ObservationConfigExt,
    check_and_make,
    name_to_class,
    save_demo,
)
from colosseum.variations.utils import safeGetValue

OmegaConf.register_new_resolver("eval", eval)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
COLLECTION_STRATEGY_CONFIG = os.path.join(
    CURRENT_DIR, "data_collection_strategy.json"
)

MAX_ATTEMPTS = 10
PROCESS_BUDGET = 5

# Index for the case of all rlbench variations mixed
RLBENCH_ALL_VARIATIONS_INDEX = 13
VARIATIONS_ALL_FOLDER = "all_variations"
# Index for the case of both rlbench and our variations all active
RLBENCH_EVERYTHING_INDEX = 15


class SaveCollectionState:
    def __init__(self, total_episodes: int = 0, save_path: str = ""):
        self.number_episodes = 0
        self.total_episodes = total_episodes
        self.save_path = save_path


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


def should_collect_task(
    collection_cfg: Dict[str, Any], spreadsheet_idx: int, idx_to_collect: int
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
    """
    idx_enabled = collection_cfg["strategy"][spreadsheet_idx]["enabled"]
    if idx_to_collect == -1:  # catch them all
        return idx_enabled
    else:
        return idx_enabled and (idx_to_collect == spreadsheet_idx)


def get_variation_name(
    collection_cfg: Dict[str, Any], spreadsheet_idx: int
) -> bool:
    return collection_cfg["strategy"][spreadsheet_idx]["variation_name"]


# TODO(wilbert): this is a hacky way to force the behavior we want :/, should
# be enought for now for this special case
def run_all_rlbench_variations(
    i: int,
    variation_name: str,
    results: Any,
    file_lock: Any,
    task: Type[Task],
    config: DictConfig,
) -> None:
    data_cfg, env_cfg = config.data, config.env

    np.random.seed(None)

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

    tasks_with_problems = results[i] = ""

    task_env = rlbench_env.get_task(task)

    variation_path = os.path.join(
        data_cfg.save_path,
        task_env.get_name() + f"_{i}",
    )
    check_and_make(variation_path)

    episodes_path = os.path.join(variation_path, const.EPISODES_FOLDER)
    check_and_make(episodes_path)

    use_save_states = safeGetValue(data_cfg, "use_save_states", False)
    save_state: Optional[SaveCollectionState] = None
    save_state_path = os.path.join(episodes_path, "save_state.pkl")
    if (
        os.path.exists(save_state_path)
        and os.path.isfile(save_state_path)
        and use_save_states
    ):
        with open(save_state_path, "rb") as fhandle:
            save_state = cast(SaveCollectionState, pickle.load(fhandle))
            print(
                f"Starting from save state in {save_state_path} with "
                + f"#episodes = {save_state.number_episodes}"
            )

    if save_state is None and use_save_states:
        save_state = SaveCollectionState(
            data_cfg.episodes_per_task, save_state_path
        )

    ex_start = save_state.number_episodes if save_state is not None else 0
    abort_variation = False
    for ex_idx in range(ex_start, data_cfg.episodes_per_task):
        var_idx = np.random.randint(task_env.variation_count())
        task_env.set_variation(var_idx)
        descriptions, _ = task_env.reset()

        print(
            "{}// Task: {} // Var: {} // RLBench-Var: {} // Demo: {}".format(
                i, task_env.get_name(), variation_name, var_idx, ex_idx
            )
        )

        attempts = safeGetValue(data_cfg, "max_attempts", MAX_ATTEMPTS)
        while attempts > 0:
            try:
                # TODO: for now we do the explicit looping.
                (demo,) = task_env.get_demos(amount=1, live_demos=True)
            except Exception as e:
                attempts -= 1
                if attempts > 0:
                    continue
                problem = (
                    f"Process {i} failed collecting task "
                    + f"{task_env.get_name()} (variation: 0, "
                    + f"example: {ex_idx}). Skipping "
                    + f"this task/variation.\n{str(e)}\n"
                )
                print(problem)
                tasks_with_problems += problem
                abort_variation = True
                break
            episode_path = os.path.join(
                episodes_path, const.EPISODE_FOLDER % ex_idx
            )
            with file_lock:
                save_demo(data_cfg, demo, episode_path, var_idx)
                if save_state is not None:
                    save_state.number_episodes += 1
                    with open(save_state.save_path, "wb") as fhandle:
                        pickle.dump(save_state, fhandle)

                with open(
                    os.path.join(episode_path, const.VARIATION_DESCRIPTIONS),
                    "wb",
                ) as f:
                    pickle.dump(descriptions, f)
            break
        if abort_variation:
            break

    results[i] = tasks_with_problems
    rlbench_env.shutdown()
    # --------------------------------------------------------------------------


def run(
    i: int,
    variation_name: str,
    results: Any,
    file_lock: Any,
    task: Type[Task],
    config: DictConfig,
):
    data_cfg, env_cfg = config.data, config.env

    np.random.seed(None)

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

    tasks_with_problems = results[i] = ""

    task_env = rlbench_env.get_task(task)

    variation_path = os.path.join(
        data_cfg.save_path,
        task_env.get_name() + f"_{i}",
        const.VARIATIONS_FOLDER % 0,
    )

    check_and_make(variation_path)

    descriptions, _ = task_env.reset()

    with open(
        os.path.join(variation_path, const.VARIATION_DESCRIPTIONS), "wb"
    ) as f:
        pickle.dump(descriptions, f)

    episodes_path = os.path.join(variation_path, const.EPISODES_FOLDER)
    check_and_make(episodes_path)

    save_state: Optional[SaveCollectionState] = None
    save_state_path = os.path.join(episodes_path, "save_state.pkl")
    use_save_states = safeGetValue(data_cfg, "use_save_states", False)
    if (
        os.path.exists(save_state_path)
        and os.path.isfile(save_state_path)
        and use_save_states
    ):
        with open(save_state_path, "rb") as fhandle:
            save_state = cast(SaveCollectionState, pickle.load(fhandle))
            print(
                f"Starting from save state in {save_state_path} with "
                + f"#episodes = {save_state.number_episodes}"
            )

    if save_state is None and use_save_states:
        save_state = SaveCollectionState(
            data_cfg.episodes_per_task, save_state_path
        )

    ex_start = save_state.number_episodes if save_state is not None else 0
    abort_variation = False
    for ex_idx in range(ex_start, data_cfg.episodes_per_task):
        print(
            "{}// Task: {} // Var: {} // RLBench-Var: {} // Demo: {}".format(
                i, task_env.get_name(), variation_name, 0, ex_idx
            )
        )

        attempts = safeGetValue(data_cfg, "max_attempts", MAX_ATTEMPTS)
        while attempts > 0:
            try:
                # TODO: for now we do the explicit looping.
                (demo,) = task_env.get_demos(amount=1, live_demos=True)
            except Exception as e:
                attempts -= 1
                if attempts > 0:
                    continue
                problem = (
                    f"Process {i} failed collecting task "
                    + f"{task_env.get_name()} (variation: 0, "
                    + f"example: {ex_idx}). Skipping "
                    + f"this task/variation.\n{str(e)}\n"
                )
                print(problem)
                tasks_with_problems += problem
                abort_variation = True
                break
            episode_path = os.path.join(
                episodes_path, const.EPISODE_FOLDER % ex_idx
            )
            with file_lock:
                save_demo(data_cfg, demo, episode_path)
                if save_state is not None:
                    save_state.number_episodes += 1
                    with open(save_state.save_path, "wb") as fhandle:
                        pickle.dump(save_state, fhandle)
            break
        if abort_variation:
            break

    results[i] = tasks_with_problems
    rlbench_env.shutdown()
    # --------------------------------------------------------------------------


@hydra.main(
    config_path=ASSETS_CONFIGS_FOLDER,
    config_name="basketball_in_hoop.yaml",
    version_base=None,
)
def main(base_cfg: DictConfig) -> int:
    # Get the data from the collection strategy file----------------------------
    collection_cfg_path: str = (
        os.path.join(ASSETS_JSON_FOLDER, base_cfg.env.task_name) + ".json"
    )
    collection_cfg: Optional[Any] = None
    with open(collection_cfg_path, "r") as fh:
        collection_cfg = json.load(fh)

    if collection_cfg is None:
        return 1

    if "strategy" not in collection_cfg:
        return 1
    # --------------------------------------------------------------------------

    # Check if the user wants to collect all variations (-1) or only one
    idx_to_collect = (
        base_cfg.data.idx_to_collect
        if "idx_to_collect" in base_cfg.data
        else -1
    )

    manager = Manager()

    result_dict = manager.dict()
    file_lock = manager.Lock()

    check_and_make(base_cfg.data.save_path)

    num_spreadsheet_idx = len(collection_cfg["strategy"])

    processes = [
        Process(
            target=(
                run
                if spreadsheet_idx != RLBENCH_ALL_VARIATIONS_INDEX
                and spreadsheet_idx != RLBENCH_EVERYTHING_INDEX
                else run_all_rlbench_variations
            ),
            args=(
                spreadsheet_idx,
                get_variation_name(collection_cfg, spreadsheet_idx),
                result_dict,
                file_lock,
                name_to_class(base_cfg.env.task_name, TASKS_PY_FOLDER),
                get_spreadsheet_config(
                    base_cfg,
                    collection_cfg,
                    spreadsheet_idx,
                ),
            ),
        )
        for spreadsheet_idx in range(num_spreadsheet_idx)
        if should_collect_task(collection_cfg, spreadsheet_idx, idx_to_collect)
    ]

    # while len(processes) > 0:
    #     active_processes = []
    #     for _ in range(PROCESS_BUDGET):
    #         if len(processes) > 0:
    #             active_processes.append(processes.pop())
    #     [t.start() for t in active_processes]
    #     [t.join() for t in active_processes]

    [t.start() for t in processes]
    [t.join() for t in processes]

    # print("Data collection done!")
    # for i in range(num_spreadsheet_idx):
    #     print(result_dict[i])

    return 0


if __name__ == "__main__":
    SystemExit(main())
