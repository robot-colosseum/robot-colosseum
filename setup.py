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
            "task_builder=colosseum.tools.task_builder:main",
            "visualize_task=colosseum.tools.visualize_task:main",
            "dataset_generator=colosseum.tools.dataset_generator:main",
        ]
    },
)
