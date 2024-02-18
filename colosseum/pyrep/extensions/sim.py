from typing import List

from pyrep.backend._sim_cffi import ffi, lib
from pyrep.backend.sim import _check_return, simImportMesh, simReleaseBuffer


def simSetObjectScale(shape_handle: int, scale: float) -> None:
    ret = lib.simScaleObject(shape_handle, scale, scale, scale, 0)
    _check_return(ret)


def simGetObjectScale(shape_handle: int) -> float:
    return lib.simGetObjectSizeFactor(shape_handle)


def simSetObjectsScale(objects_handles: List[int], scale: float) -> None:
    handles = ffi.new("int[]", objects_handles)
    ret = lib.simScaleObjects(handles, len(objects_handles), scale, False)
    _check_return(ret)


def simGetConvexHullShape(pathAndFilename):
    vertices, _, _ = simImportMesh(0, pathAndFilename, 0, False, 1.0)

    outVertices = ffi.new("float **")
    outVerticesCount = ffi.new("int *")
    outIndices = ffi.new("int **")
    outIndicesCount = ffi.new("int *")
    ret = lib.simGetQHull(
        vertices[0],
        len(vertices[0]),
        outVertices,
        outVerticesCount,
        outIndices,
        outIndicesCount,
        0,
        ffi.NULL,
    )
    _check_return(ret)

    mesh_options = 3
    mesh_shading_angle = 20.0 * 3.1415 / 180.0
    handle = lib.simCreateMeshShape(
        mesh_options,
        mesh_shading_angle,
        outVertices[0],
        outVerticesCount[0],
        outIndices[0],
        outIndicesCount[0],
        ffi.NULL,
    )

    simReleaseBuffer(ffi.cast("char *", outVertices[0]))
    simReleaseBuffer(ffi.cast("char *", outIndices[0]))
    return handle


def simGetShapeTextureIdNoThrow(objectHandle):
    """Returns the texture ID, and -1 otherwise (instead of throwing)"""
    return lib.simGetShapeTextureId(objectHandle)


def simGetShapeGeomInfo(shapeHandle):
    geom_int_data = ffi.new("int[5]")
    geom_float_data = ffi.new("float[5]")
    ret = lib.simGetShapeGeomInfo(
        shapeHandle, geom_int_data, geom_float_data, ffi.NULL
    )

    return ret, list(geom_int_data), list(geom_float_data)


def simExportMesh(shapeHandle: int, fileFormat: int, filepath: str) -> None:
    # --------------------------------------------------------------------------
    # Get the mesh data of this shape

    outVertices = ffi.new("float **")
    outVerticesCount = ffi.new("int *")
    outIndices = ffi.new("int **")
    outIndicesCount = ffi.new("int *")
    outNormals = ffi.new("float **")

    ret = lib.simGetShapeMesh(
        shapeHandle,
        outVertices,
        outVerticesCount,
        outIndices,
        outIndicesCount,
        outNormals,
    )

    _check_return(ret)

    # --------------------------------------------------------------------------
    # Feed the data into the exportMesh function

    ret = lib.simExportMesh(
        fileFormat,
        filepath.encode("ascii"),
        0,
        1.0,
        1,
        outVertices,
        outVerticesCount,
        outIndices,
        outIndicesCount,
        ffi.NULL,
        ffi.NULL,
    )
    _check_return(ret)
    simReleaseBuffer(ffi.cast("char *", outVertices[0]))
    simReleaseBuffer(ffi.cast("char *", outIndices[0]))
    simReleaseBuffer(ffi.cast("char *", outNormals[0]))
