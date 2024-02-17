import warnings
from enum import Enum
from typing import Any, List, Optional, Tuple

import numpy as np
from numpy.typing import NDArray
from omegaconf import DictConfig

from colosseum.variations.const import COLORS_MAP, COLORS_NAMES


class ColorConfigMode(Enum):
    # Pick from a fixed set of color values from colosseum.variations.const
    USE_RANDOM_FROM_LIBRARY = 0
    # Similar to the previous one, but use only the names that the user provides
    USE_CUSTOM_COLOR_NAMES = 1
    # Pick from a given set of color values instead of the library
    USE_CUSTOM_COLOR_VALUES = 2
    # Use ranges to pick values from instead of using a fixed set of colors
    USE_CUSTOM_COLOR_RANGE = 3


def sampleColor(
    mode: ColorConfigMode,
    rng: np.random.Generator,
    color_names: List[str] = [],
    color_list: List[NDArray] = [],
    color_range: Tuple[NDArray, NDArray] = (np.zeros(3), np.ones(3)),
) -> Optional[NDArray]:
    """
    Samples a random color using one of many options given by the user

    Parameters
    ----------
        mode: ColorConfigMode
            The mode that will be used to sample colors
        rng: np.random.Generator
            The random generator used to make the sampling process
        color_names: List[str]
            The list of color names names used to sample from, used only if
            using the USE_CUSTOM_COLOR_NAMES mode
        color_list: List[NDArray]
            The list of RGB values to sample from, used only if using the
            USE_CUSTOM_COLOR_VALUES mode
        color_range: Tuple[NDArray, NDArray]
            Both the minimum and maximum RGB values to sample from, used only
            if using the USE_CUSTOM_COLOR_RANGE mode

    Returns
    -------
        Optional[NDArray]
            A color sampled at random, or None in the worst case if something
            went wrong during the sampling process
    """
    color_value: Optional[NDArray] = None
    if mode == ColorConfigMode.USE_RANDOM_FROM_LIBRARY:
        color_value = COLORS_MAP[rng.choice(COLORS_NAMES)]
    elif mode == ColorConfigMode.USE_CUSTOM_COLOR_NAMES:
        assert len(color_names) > 0, "Not enough color names provided"
        color_name = rng.choice(color_names)
        if color_name not in COLORS_MAP:
            warnings.warn(
                (
                    "Tried to pick a color name ('{}') that is not"
                    + " in the default colors library"
                ).format(color_name)
            )
        else:
            color_value = COLORS_MAP[color_name]
    elif mode == ColorConfigMode.USE_CUSTOM_COLOR_VALUES:
        assert len(color_list) > 0, "Not enough colors provided in list"
        color_value = rng.choice(color_list)
    elif mode == ColorConfigMode.USE_CUSTOM_COLOR_RANGE:
        assert len(color_range) == 2, "Color range must be in format (low,high)"
        try:
            color_value = rng.uniform(low=color_range[0], high=color_range[1])
        except ValueError:
            warnings.warn(
                "Something went wrong while using the"
                + f" given color ranges. Range given is '{color_range}'"
            )

    return color_value


class ScaleConfigMode(Enum):
    # Sample a random value from a list of possible scale factors
    USE_CUSTOM_SCALE_VALUES = 0
    # Sample a random value within a custom range
    USE_CUSTOM_SCALE_RANGE = 1


def sampleScale(
    mode: ScaleConfigMode,
    rng: np.random.Generator,
    scale_list: List[float] = [],
    scale_range: Tuple[float, float] = (0.75, 1.25),
) -> Optional[float]:
    """
    Samples a random scale value using one of many options given by the user

    Parameters
    ----------
        mode: ScaleConfigMode
            The mode that will be used to sample scale values
        rng: np.random.Generator
            The random generator used to make the sampling process
        scale_list: List[float]
            The list of scale values from which to sample from, used only if
            using the USE_CUSTOM_SCALE_VALUES mode
        scale_range: Tuple[float, float]
            The minimum and maximum scale values to sample from, used only if
            using the USE_CUSTOM_SCALE_RANGE mode

    Returns
    -------
        Optional[float]
            A scale value sampled at random, or None in the worst case if
            something went wrong during the sampling process
    """
    scale_value: Optional[float] = None
    if mode == ScaleConfigMode.USE_CUSTOM_SCALE_VALUES:
        assert len(scale_list) > 0, "Not enough scales provided in list"
        scale_value = rng.choice(scale_list)
    elif mode == ScaleConfigMode.USE_CUSTOM_SCALE_RANGE:
        assert len(scale_range) == 2, "Scale range must be in format (low,high)"
        try:
            scale_value = rng.uniform(low=scale_range[0], high=scale_range[1])
        except ValueError:
            warnings.warn(
                "Something went wrong while using the"
                + f" given scale ranges. Range is '{scale_range}'"
            )

    return scale_value


def safeGetValue(config: DictConfig, key: str, default: Any) -> Any:
    """
    Returns the value for a given key from a given config structure, or the
    given default if the key wasn't found in the config struct.

    Parameters
    ----------
        config: DictConfig
            The config structure from which to extract a key value
        key: str
            The key we want from the given config structure
        default: Any
            The value returned if the key was not found in the config structure

    Returns
    -------
        Any
            The value for the requested key, or the given default if not found
    """
    return config[key] if key in config else default
