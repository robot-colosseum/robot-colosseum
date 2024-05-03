import warnings
from typing import Tuple, Union

from pyrep.backend.sim import simGetObjectInt32Parameter
from pyrep.backend.simConst import sim_shapeintparam_compound
from pyrep.const import ObjectType, TextureMappingMode
from pyrep.objects.shape import Shape
from pyrep.textures.texture import Texture

from colosseum.pyrep.extensions.sim import simSetObjectScale, simSetObjectsScale


class ShapeExt(Shape):
    """Shape class that extends the functionality provided by PyRep's Shape"""

    def __init__(self, name_or_handle: Union[str, int]):
        """
        Creates an extended shape object, given the handle or name of the object
        in the simulation

        Parameters
        ----------
            name_or_handle: Union[str, int]
                The name or handle of the object in the simulation
        """
        super().__init__(name_or_handle)

        self._obj_handle: int = self.get_handle()
        self._obj_name: str = self.get_name()
        self._obj_scale: float = 1.0

    def set_friction(self, value: float) -> None:
        """
        Updates the friction coefficient of this shape in the simulation

        Parameters
        ----------
            value: float
                The friction value to be updated
        """
        # TODO(wilbert): check according to the current physics engine in use
        self.set_bullet_friction(value)

    def get_friction(self) -> float:
        """Returns the current friction coefficient of this shape"""
        # TODO(wilbert): check according to the current physics engine in use
        return self.get_bullet_friction()

    def set_scale(self, scale: float) -> None:
        """
        Scales the shape by a given factor in all directions. The scale method
        depends on the nature of the shape, whether or not it's a model object.
        Model objects are scaled using a custom function from CoppeliaSim's API
        that scales recursively the object and all its children. Non-model
        objects are scaled only themselves (not recursively), but any dummies
        that it contains are relocated trying to match what the scale effect
        should actually be

        Parameters
        ----------
            scale: float
                The scaling factor to apply to the shape
        """
        desired_scale = scale
        current_scale = self._obj_scale
        scale_factor = desired_scale / current_scale
        if self.is_model():
            simSetObjectsScale([self._obj_handle], scale_factor)
        else:
            simSetObjectScale(self._obj_handle, scale_factor)
        self._obj_scale = desired_scale

        if not self.is_model():
            obj_init_pos = self.get_position()
            # Relocate the positions of the dummies (if any)
            dummies = self.get_objects_in_tree(object_type=ObjectType.DUMMY)
            vectors_rel_init = [
                (dummy.get_position() - obj_init_pos) for dummy in dummies
            ]
            for dummy, vec_init in zip(dummies, vectors_rel_init):
                scaled_vec = scale * vec_init
                dummy.set_position(obj_init_pos + scaled_vec)

    def get_scale(self) -> float:
        """Returns the current scale of the shape"""
        return self._obj_scale

    def try_set_texture(
        self,
        texture: Texture,
        mapping_mode: TextureMappingMode = TextureMappingMode.PLANE,
        repeat_along_u: bool = True,
        repeat_along_v: bool = True,
        uv_scaling: Tuple[float, float] = (1.0, 1.0),
    ):
        """
        This method tries to set a given texture to the shape, but it doesn't
        throw if the texture assignment fails. For the moment, this is the case
        for shapes that are compound shapes. In later versions of CoppeliaSim
        this issue is resolved, so we're just waiting for PyRep to be updated
        in the upstream repository

        """
        try:
            # Check if the shape is a compound shape
            is_compound = (
                simGetObjectInt32Parameter(
                    self._handle, sim_shapeintparam_compound
                )
                == 1
            )
            if is_compound:
                # TODO(wilbert): Disabling for now due to issue #28

                # # Ungroup the object, apply textures to children, and regroup
                # children_shapes = self.ungroup()
                # for shape in children_shapes:
                #     shape.set_texture(
                #         texture,
                #         mapping_mode,
                #         repeat_along_u=repeat_along_u,
                #         repeat_along_v=repeat_along_v,
                #         uv_scaling=uv_scaling,
                #     )
                # children_handles =
                #   [obj.get_handle() for obj in children_shapes]
                # self._handle = simGroupShapes(children_handles)

                # Do nothing for now, to not clutter with minor warnings
                pass

                # warnings.warn(
                #     "Tried applying texture to a compound shape, which"
                #     + " is not currently supported"
                # )
            else:
                self.set_texture(
                    texture,
                    mapping_mode,
                    repeat_along_u=repeat_along_u,
                    repeat_along_v=repeat_along_v,
                    uv_scaling=uv_scaling,
                )
        except RuntimeError:
            warnings.warn(
                "Might have tried setting a texture for a nested compound"
                + " shape, which is not yet supported in our extensions."
            )
