import abc
import warnings
from typing import Dict, List, Optional

from numpy.random import default_rng
from pyrep import PyRep
from pyrep.const import ObjectType
from pyrep.objects.object import Object


class IVariation(abc.ABC):
    """Interface for variation factors in the simulation."""

    DEFAULT_VARIATION_NAME = "variation"
    DEFAULT_VARIATION_COUNT = 0

    def __init__(
        self,
        pyrep: PyRep,
        name: Optional[str] = None,
        targets_type: ObjectType = ObjectType.SHAPE,
        targets_names: List[str] = [],
        seed: Optional[int] = None,
    ):
        """
        Creates a variation that affects the given targets in simulation

        Parameters
        ----------
            pyrep: PyRep
                A handle to the pyrep simulation
            targets_type: ObjectType
                The type of the objects this variation is in charge of
            targets_names: List[str]
                A list of names for the objects in simulation to be controlled
        """
        self._pyrep = pyrep
        if name is None:
            self._name = "{def_name}-{def_count}".format(
                def_name=IVariation.DEFAULT_VARIATION_NAME,
                def_count=IVariation.DEFAULT_VARIATION_COUNT,
            )
            self.DEFAULT_VARIATION_COUNT += 1
        else:
            self._name = name
        self._seed = seed
        self._targets_type = targets_type
        self._targets_names = targets_names

        self._rng = default_rng(self._seed)
        self._enabled = False

        objects_available = self._pyrep.get_objects_in_tree(
            object_type=self._targets_type
        )

        self._targets: Dict[str, Object] = {
            obj.get_name(): obj
            for obj in objects_available
            if obj.get_name() in self._targets_names
        }

        if len(self._targets) < 1:
            warnings.warn(
                "IVariation > couldn't find any related targets in "
                + f"the simulation. Targets names were: {targets_names}"
            )

        self._enabled = True

    def setEnable(self, value: bool) -> None:
        """
        Enable or disable the variation factor in the simulation

        Parameters
        ----------
            value: bool
                The value to set the enabled flag to
        """
        self._enabled = value

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def name(self) -> str:
        return self._name

    @abc.abstractmethod
    def randomize(self) -> None:
        """
        Apply the factor's effect into the targets in the simulation
        """
        ...

    def on_init_episode(self) -> None:
        """
        Called when the episode is initialized
        """
        if self._enabled:
            self.randomize()

    def on_step_episode(self) -> None:
        """
        Called when the simulation is advanced one step
        """
        pass
