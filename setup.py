from setuptools import setup

setup(
    package_data={
        "colosseum": [
            "rlbench/task_ttms/*.ttm",
            "assets/textures/*.jpg",
            "assets/textures/*.png",
            "assets/models/*.ttm",
        ],
    },
    entry_points={
        "console_scripts": [
            "visualize_task=colosseum.tools.visualize_task:main",
        ]
    },
)
