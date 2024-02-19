import os

COLOSSEUM_ROOT = os.path.dirname(os.path.abspath(__file__))

TASKS_PY_FOLDER = os.path.join(COLOSSEUM_ROOT, "rlbench", "tasks")
TASKS_TTM_FOLDER = os.path.join(COLOSSEUM_ROOT, "rlbench", "task_ttms")

ASSETS_FOLDER = os.path.join(COLOSSEUM_ROOT, "assets")
ASSETS_TEXTURES_FOLDER = os.path.join(ASSETS_FOLDER, "textures")
ASSETS_MODELS_TTM_FOLDER = os.path.join(ASSETS_FOLDER, "models")
