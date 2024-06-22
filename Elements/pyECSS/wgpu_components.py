import glm  
import wgpu

from enum import Enum 
from pathlib import Path
from assertpy import assert_that

class Component(object):  
    def __init__(self):
        self.is_active = True;

class InfoComponent(Component):
    def __init__(self, tag:str): 
        self.tag = tag

class TransformComponent(Component):
    def __init__(self, translation: glm.vec3, rotation: glm.vec3, scale: glm.vec3, static=False):
        self.translation = translation
        self.rotation = rotation
        self.scale = scale

        self.local_matrix = glm.mat4(1.0)
        self.world_matrix = glm.mat4(1.0)
        self.quaternion = glm.quat()

        self.static = static 
    
    def get_world_position(self) -> glm.vec3:
        return (self.world_matrix * glm.vec4(self.translation, 1.0)).xyz 
    
class CameraComponent(Component):
    class Type(Enum):
        PERSPECTIVE = 1
        ORTHOGRAPHIC = 2

    def __init__(self, fov, aspect_ratio, near, far, zoom_level, type: Type, primary = True):
        self.zoom_level = zoom_level
        self.fov = fov
        self.near = near
        self.far = far
        self.aspect_ratio = aspect_ratio
        self.type: CameraComponent.Type = type 
        self.projection = None

        self.view = glm.mat4(1.0)
        if type is CameraComponent.Type.ORTHOGRAPHIC:
            self.projection = glm.ortho(-self.aspect_ratio * self.zoom_level, self.aspect_ratio * self.zoom_level, -self.zoom_level, self.zoom_level, self.near, self.far)
        elif type is CameraComponent.Type.PERSPECTIVE:
            self.projection = glm.perspective(glm.radians(self.fov), self.aspect_ratio, self.near, self.far) 
        else:
            assert_that(self.projection).is_not_none() 
            
        self.view_projection = glm.mat4(1.0)

class CameraControllerComponent(Component):
    def __init__(self, movement_speed = 3.5, mouse_sensitivity = 1.25):
        self.front = glm.vec3(0.0, 0.0, 1.0)
        self.right = glm.vec3(1.0, 0.0, 0.0)
        self.up = glm.vec3(0.0, 1.0, 0.0)
        self.world_up = glm.vec3(0.0, 1.0, 0.0)
        self.yaw = -90.0
        self.pitch = 0.0
        self.movement_speed = movement_speed
        self.mouse_sensitivity = mouse_sensitivity
        self.zoom = 45.0
        self.prev_mouse_x = 0.0
        self.prev_mouse_y = 0.0 

class MeshComponent(Component): 
    class Type(Enum): 
        STATIC = 1
        IMPORT = 2 

    class Buffers(Enum):
        VERTEX = "a_vertices"
        INDEX = "a_indices"
        UV = "a_uvs"
        NORMAL = "a_normals"
        COLOR = "a_colors" 
        TANGENT = "a_tangents"
        BITANGENT = "a_bytangents"
    
    def __init__(self, mesh_type:Type, import_path=None): 
        self.vertices = None 
        self.indices = None
        self.uvs = None
        self.normals = None  
        self.Tangents = None 
        self.Bitangents = None 
        self.type = mesh_type 
        self.import_path = import_path
        self.buffer_map = {}
        self.vertices_num = None
        self.indices_num = None
  
class RenderExclusiveComponent(Component):
    def __init__(self):
        self.active = True 

class ShaderComponent(Component): 
    def __init__(self, shader_path:Path):
        assert_that(shader_path).is_not_none()

        self.pipeline_layout = None 
        self.bind_group_layouts: list = []  
        self.bind_group_layouts_entries = [[]]
        self.shader_module = None 
        self.shader_path = shader_path
        self.shader_code = None
        self.uniform_buffers = None
        self.uniform_gpu_buffers = {} 
        self.read_only_storage_buffers = None
        self.read_only_storage_gpu_buffers = {}
        self.other_uniform = None 
        self.attributes = None 
        self.attributes_layout = None 

class MaterialComponent(Component):
    def __init__(self, primitive=None, color_blend=None):

        self.pipeline = None  
        self.primitive = None
        self.color_blend = None

        if primitive is None:
            self.primitive = {
                "topology": wgpu.PrimitiveTopology.triangle_list,
                "front_face": wgpu.FrontFace.ccw,
                "cull_mode": wgpu.CullMode.none,
            } 
        else: 
            self.primitive = primitive 

        if color_blend is None:
            self.color_blend = { 
                "blend": {
                    "alpha": (
                        wgpu.BlendFactor.one,
                        wgpu.BlendFactor.zero,
                        wgpu.BlendOperation.add,
                    ),
                    "color": (
                        wgpu.BlendFactor.one,
                        wgpu.BlendFactor.zero,
                        wgpu.BlendOperation.add,
                    ),
                },
            } 
        else: 
            self.color_blend = color_blend