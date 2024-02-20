import argparse
import importlib
import os
import pprint
import readline
import shutil
import sys
import traceback

from pyrep import PyRep
from pyrep.const import RenderMode
from pyrep.objects.dummy import Dummy
from pyrep.objects.shape import Shape
from pyrep.robots.arms.panda import Panda
from pyrep.robots.end_effectors.panda_gripper import PandaGripper
from rlbench.backend import task
from rlbench.backend.const import TTT_FILE
from rlbench.backend.exceptions import (
    BoundaryError,
    DemoError,
    NoWaypointsError,
    WaypointError,
)
from rlbench.backend.robot import Robot
from rlbench.environment import DIR_PATH as RLBENCH_ROOT_PATH
from rlbench.observation_config import CameraConfig, ObservationConfig

from colosseum import ASSETS_FOLDER, TASKS_PY_FOLDER, TASKS_TTM_FOLDER
from colosseum.rlbench.extensions.scene import SceneExt

TASKS_PY_DIR = TASKS_PY_FOLDER
TASKS_TTM_DIR = TASKS_TTM_FOLDER

PATH_TO_DESIGN_TTT_FILE = os.path.join(RLBENCH_ROOT_PATH, TTT_FILE)
PATH_TO_TASK_TXT_TEMPLATE = os.path.join(ASSETS_FOLDER, "task_template.txt")


def print_fail(message, end="\n"):
    message = str(message)
    sys.stderr.write("\x1b[1;31m" + message.strip() + "\x1b[0m" + end)


def setup_list_completer():
    task_files = [
        t.replace(".py", "")
        for t in os.listdir(task.TASKS_PATH)
        if t != "__init__.py" and t.endswith(".py")
    ]

    def list_completer(_, state):
        line = readline.get_line_buffer()
        if not line:
            return [c + " " for c in task_files][state]

        else:
            return [c + " " for c in task_files if c.startswith(line)][state]

    readline.parse_and_bind("tab: complete")
    readline.set_completer(list_completer)


# ------------------------------------------------------------------------------
# Extend some of the original task_builder functionality


class InvalidTaskName(Exception):
    ...


def name_to_task_class(task_file: str):
    name = task_file.replace(".py", "")
    class_name = "".join([w[0].upper() + w[1:] for w in name.split("_")])
    try:
        mod = importlib.import_module(name)
        mod = importlib.reload(mod)
    except ModuleNotFoundError as e:
        raise InvalidTaskName(
            "The task file '%s' does not exist or cannot be compiled." % name
        ) from e
    try:
        task_class = getattr(mod, class_name)
    except AttributeError as e:
        raise InvalidTaskName(
            "Cannot find the class name '%s' in the file '%s'."
            % (class_name, name)
        ) from e
    return task_class


# ------------------------------------------------------------------------------


class LoadedTask(object):
    def __init__(self, pr: PyRep, scene: SceneExt, robot: Robot):
        self.pr = pr
        self.scene = scene
        self.robot = robot
        self.task = None
        self.task_class = None
        self.task_file = None
        self._variation_index = 0

    def _load_task_to_scene(self):
        assert self.pr is not None
        assert self.robot is not None
        assert self.task_file is not None
        assert self.task_class is not None

        self.scene.unload()
        self.task = self.task_class(
            self.pr, self.robot, self.task_file.replace(".py", "")
        )
        try:
            # Try and load the task
            self.scene.load(self.task)
        except FileNotFoundError:
            # The .ttt file must not exist
            handle = Dummy.create()
            handle.set_name(self.task_file.replace(".py", ""))
            handle.set_model(True)
            # Put the dummy at the centre of the workspace
            self.task.get_base().set_position(Shape("workspace").get_position())

    def _edit_new_task(self):
        task_file = input("What task would you like to edit?\n")
        task_file = task_file.strip(" ")
        if len(task_file) > 3 and task_file[-3:] != ".py":
            task_file += ".py"
        try:
            task_class = name_to_task_class(task_file)
        except:  # noqa: E722
            print(
                (
                    "There was no task named: {}. "
                    + "Would you like to create it?"
                ).format(task_file)
            )
            inp = input()
            if inp == "y":
                self._create_python_file(task_file)
                task_class = name_to_task_class(task_file)
            else:
                print("Please pick a defined task in that case.")
                task_class, task_file = self._edit_new_task()
        return task_class, task_file

    def _create_python_file(self, task_file: str):
        with open(PATH_TO_TASK_TXT_TEMPLATE, "r") as f:
            file_content = f.read()
        class_name = self._file_to_class_name(task_file)
        file_content = file_content % (class_name,)
        new_file_path = os.path.join(TASKS_PY_DIR, task_file)
        if os.path.isfile(new_file_path):
            raise RuntimeError("File already exists. Will not override this.")
        with open(new_file_path, "w+") as f:
            f.write(file_content)

    def _file_to_class_name(self, name):
        name = name.replace(".py", "")
        return "".join([w[0].upper() + w[1:] for w in name.split("_")])

    def reload_python(self):
        assert self.task_file is not None

        try:
            task_class = name_to_task_class(self.task_file)
        except Exception:
            print_fail("The python file could not be loaded!")
            traceback.print_exc()
            return None, None
        self.task = task_class(
            self.pr, self.robot, self.task_file.replace(".py", "")
        )
        self.scene.load(self.task)

    def new_task(self):
        self._variation_index = 0
        self.task_class, self.task_file = self._edit_new_task()
        self._load_task_to_scene()
        self.pr.step_ui()
        print("You are now editing: %s" % str(self.task_class))

    def reset_variation(self):
        self._variation_index = 0

    def new_variation(self):
        assert self.task is not None

        try:
            self._variation_index += 1
            descriptions = self.scene.init_episode(
                self._variation_index % self.task.variation_count(),
                max_attempts=10,
            )
            print("Task descriptions: ", descriptions)
        except (WaypointError, BoundaryError, Exception):
            traceback.print_exc()
        self.pr.step_ui()

    def new_episode(self):
        assert self.task is not None

        try:
            descriptions = self.scene.init_episode(
                self._variation_index % self.task.variation_count(),
                max_attempts=10,
            )
            print("Task descriptions: ", descriptions)
        except (WaypointError, BoundaryError, Exception):
            traceback.print_exc()
            self.scene.reset()
        self.pr.step_ui()

    def new_demo(self):
        assert self.task is not None

        try:
            self.scene.get_demo(False, randomly_place=False)
        except (WaypointError, NoWaypointsError, DemoError, Exception):
            traceback.print_exc()
        success, _ = self.task.success()
        if success:
            print("Demo was a success!")
        self.scene.reset()
        self.pr.step_ui()
        self.pr.step_ui()

    def save_task(self):
        assert self.task is not None
        assert self.task_file is not None

        ttm_path = os.path.join(
            TASKS_TTM_DIR, self.task_file.replace(".py", ".ttm")
        )
        self.task.get_base().save_model(ttm_path)
        print("Task saved to:", ttm_path)

    def rename(self):
        print("Enter new name (or q to abort).")
        inp = input()
        if inp == "q":
            return

        name = inp.replace(".py", "")
        python_file = name + ".py"

        # Change name of base
        assert self.task_file is not None
        handle = Dummy(self.task_file.replace(".py", ""))
        handle.set_name(name)

        # Change the class name
        old_file_path = os.path.join(TASKS_PY_DIR, self.task_file)
        old_class_name = self._file_to_class_name(self.task_file)
        new_class_name = self._file_to_class_name(name)
        with open(old_file_path, "r") as f:
            content = f.read()
        content = content.replace(old_class_name, new_class_name)
        with open(old_file_path, "w") as f:
            f.write(content)

        # Rename python task file
        new_file_path = os.path.join(TASKS_PY_DIR, python_file)
        os.rename(old_file_path, new_file_path)

        # Rename .ttt
        old_ttm_path = os.path.join(
            TASKS_TTM_DIR, self.task_file.replace(".py", ".ttm")
        )
        new_ttm_path = os.path.join(
            TASKS_TTM_DIR, python_file.replace(".py", ".ttm")
        )
        os.rename(old_ttm_path, new_ttm_path)

        self.task_file = python_file
        self.reload_python()
        self.save_task()
        print("Rename complete!")

    def duplicate_task(self):
        print("Enter new name for duplicate (or q to abort).")
        inp = input()
        if inp == "q":
            return

        name = inp.replace(".py", "")
        new_python_file = name + ".py"

        assert self.task_file is not None

        # Change the class name
        old_file_path = os.path.join(TASKS_PY_DIR, self.task_file)
        old_class_name = self._file_to_class_name(self.task_file)
        new_file_path = os.path.join(TASKS_PY_DIR, new_python_file)
        new_class_name = self._file_to_class_name(name)

        if os.path.isfile(new_file_path):
            print("File: %s already exists!" % new_file_path)
            return

        # Change name of base
        handle = Dummy(self.task_file.replace(".py", ""))
        handle.set_name(name)

        with open(old_file_path, "r") as f:
            content = f.read()
        content = content.replace(old_class_name, new_class_name)
        with open(new_file_path, "w") as f:
            f.write(content)

        # Rename .ttt
        old_ttm_path = os.path.join(
            TASKS_TTM_DIR, self.task_file.replace(".py", ".ttm")
        )
        new_ttm_path = os.path.join(
            TASKS_TTM_DIR, new_python_file.replace(".py", ".ttm")
        )
        shutil.copy(old_ttm_path, new_ttm_path)

        self.task_file = new_python_file
        self.reload_python()
        self.save_task()
        print("Duplicate complete!")


def main() -> int:
    global TASKS_PY_DIR
    global TASKS_TTM_DIR

    setup_list_completer()

    # Get the paths to the directories for handling our resources --------------
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tasks_py_dir",
        default=TASKS_PY_DIR,
        required=False,
        type=str,
        help=(
            "Specify the directory where the .py files for tasks are "
            + "located. (default: {})"
        ).format(TASKS_PY_DIR),
    )
    parser.add_argument(
        "--tasks_ttm_dir",
        default="",
        required=False,
        type=str,
        help=(
            "Specify the directory where the .ttm files for tasks are "
            + "located. (default: {})"
        ).format(TASKS_TTM_DIR),
    )

    args = parser.parse_args()
    pprint.pprint(vars(args))

    TASKS_PY_DIR = args.tasks_py_dir
    TASKS_TTM_DIR = (
        args.tasks_ttm_dir
        if args.tasks_ttm_dir != ""
        else os.path.join(TASKS_PY_DIR, "..", "task_ttms")
    )

    # Add the directory to the tasks files to our path for importing
    sys.path.insert(0, TASKS_PY_DIR)
    # --------------------------------------------------------------------------

    pr = PyRep()
    pr.launch(PATH_TO_DESIGN_TTT_FILE, responsive_ui=True)
    pr.step_ui()

    robot = Robot(Panda(), PandaGripper())
    cam_config = CameraConfig(
        rgb=True, depth=False, mask=False, render_mode=RenderMode.OPENGL
    )
    obs_config = ObservationConfig()
    obs_config.set_all(False)
    obs_config.right_shoulder_camera = cam_config
    obs_config.left_shoulder_camera = cam_config
    obs_config.overhead_camera = cam_config
    obs_config.wrist_camera = cam_config
    obs_config.front_camera = cam_config

    scene = SceneExt(
        pr, robot, obs_config=obs_config, path_task_ttms=TASKS_TTM_DIR
    )
    loaded_task = LoadedTask(pr, scene, robot)

    print("  ,")
    print(" /(  ___________")
    print("|  >:===========`  Welcome to task builder!")
    print(" )(")
    print(' ""')

    loaded_task.new_task()

    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print("\n-----------------\n")
        print("The python file will be reloaded when simulation is restarted.")
        print("(q) to quit.")
        if pr.running:
            print("(+) stop the simulator")
            print("(v) for task variation.")
            print("(e) for episode of same variation.")
            print("(d) for demo.")
            print("(p) for running the sim for 100 steps (with rendering).")
        else:
            print("(!) to run task validator.")
            print("(+) run the simulator")
            print("(n) for new task.")
            print("(s) to save the .ttm")
            print("(r) to rename the task")
            print("(u) to duplicate/copy the task")

        inp = input()

        if inp == "q":
            break

        if pr.running:
            if inp == "+":
                pr.stop()
                pr.step_ui()
            elif inp == "p":
                [(pr.step(),) for _ in range(100)]
            elif inp == "d":
                loaded_task.new_demo()
            elif inp == "v":
                loaded_task.new_variation()
            elif inp == "e":
                loaded_task.new_episode()
        else:
            if inp == "+":
                loaded_task.reload_python()
                loaded_task.reset_variation()
                pr.start()
                pr.step_ui()
            elif inp == "n":
                inp = input("Do you want to save the current task first?\n")
                if inp == "y":
                    loaded_task.save_task()
                loaded_task.new_task()
            elif inp == "s":
                loaded_task.save_task()
            elif inp == "r":
                loaded_task.rename()
            elif inp == "u":
                loaded_task.duplicate_task()

    pr.stop()
    pr.shutdown()
    print("Done. Goodbye!")

    return 0


if __name__ == "__main__":
    SystemExit(main())
