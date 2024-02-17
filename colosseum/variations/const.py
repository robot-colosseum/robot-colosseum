from typing import Dict, List

import numpy as np
from numpy.typing import NDArray

COLORS_NAMES: List[str] = [
    "red",
    "maroon",
    "lime",
    "green",
    "blue",
    "navy",
    "yellow",
    "cyan",
    "magenta",
    "silver",
    "gray",
    "orange",
    "olive",
    "purple",
    "teal",
    "azure",
    "violet",
    "rose",
    "black",
    "white",
]

COLORS_MAP: Dict[str, NDArray] = {
    "red": np.array([1.0, 0.0, 0.0]),
    "maroon": np.array([0.5, 0.0, 0.0]),
    "lime": np.array([0.0, 1.0, 0.0]),
    "green": np.array([0.0, 0.5, 0.0]),
    "blue": np.array([0.0, 0.0, 1.0]),
    "navy": np.array([0.0, 0.0, 0.5]),
    "yellow": np.array([1.0, 1.0, 0.0]),
    "cyan": np.array([0.0, 1.0, 1.0]),
    "magenta": np.array([1.0, 0.0, 1.0]),
    "silver": np.array([0.75, 0.75, 0.75]),
    "gray": np.array([0.5, 0.5, 0.5]),
    "orange": np.array([1.0, 0.5, 0.0]),
    "olive": np.array([0.5, 0.5, 0.0]),
    "purple": np.array([0.5, 0.0, 0.5]),
    "teal": np.array([0, 0.5, 0.5]),
    "azure": np.array([0.0, 0.5, 1.0]),
    "violet": np.array([0.5, 0.0, 1.0]),
    "rose": np.array([1.0, 0.0, 0.5]),
    "black": np.array([0.0, 0.0, 0.0]),
    "white": np.array([1.0, 1.0, 1.0]),
}
