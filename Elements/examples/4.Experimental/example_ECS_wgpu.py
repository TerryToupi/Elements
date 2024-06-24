from random import random, randint
import wgpu
import glm
import numpy as np
import Elements.definitions as definitions

from Elements.pyGLV.GUI.Viewer import GLFWWindow
from Elements.pyGLV.GUI.Viewer import button_map 

from Elements.pyECSS.systems.wgpu_transform_system import TransformSystem
from Elements.pyECSS.systems.wgpu_camera_controller_system import CameraControllerSystem 
from Elements.pyECSS.systems.wgpu_camera_system import CameraSystem
from Elements.pyECSS.systems.wgpu_mesh_system import MeshSystem 
from Elements.pyECSS.systems.wpgu_shader_system import ShderSystem 

from Elements.pyECSS.wgpu_components import * 
from Elements.pyECSS.wgpu_entity import Entity 
from Elements.pyECSS.wgpu_time_manager import TimeStepManager
from Elements.pyGLV.GL.wpgu_scene import Scene 

from Elements.pyGLV.GUI.wgpu_renderer import Renderer
from Elements.pyGLV.GUI.Input_manager import InputManager 
from Elements.pyGLV.GUI.wgpu_gpu_controller import GpuController

from Elements.pyGLV.GL.wgpu_texture import TextureLib

canvas = GLFWWindow(windowHeight=800, windowWidth=1280, wgpu=True, windowTitle="Wgpu Example")
canvas.init()

width = canvas._windowWidth
height = canvas._windowHeight

# Create a wgpu device
adapter = wgpu.gpu.request_adapter(power_preference="high-performance")
device = adapter.request_device()
GpuController().set_adapter_device(device=device, adapter=adapter)

# Prepare present context
present_context = canvas.get_context()
render_texture_format = present_context.get_preferred_format(device.adapter)
present_context.configure(device=device, format=render_texture_format) 

InputManager().set_monitor(canvas)

TextureLib().make_texture(name="3x3", path=definitions.TEXTURE_DIR / "3x3.jpg") 
TextureLib().make_texture(name="grass", path=definitions.TEXTURE_DIR / "Texture_Grass.png") 
TextureLib().make_texture(name="Cauterizer", path=definitions.MODEL_DIR / "Cauterizer" / "cauterizer_low_01_Cauterizer_Blue_AlbedoTransparency.png")
TextureLib().make_texture(name="building", path=definitions.MODEL_DIR / "stronghold" / "textures" / "texture_building.jpeg")

camera = Scene().add_entity() 
Scene().add_component(camera, InfoComponent("main camera"))
Scene().add_component(camera, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1), static=False))
Scene().add_component(camera, CameraComponent(60, 16/9, 0.01, 500, 1.2, CameraComponent.Type.PERSPECTIVE))
Scene().add_component(camera, CameraControllerComponent())  
Scene().set_primary_cam(camera) 

cube = Scene().add_entity() 
Scene().add_component(cube, InfoComponent("Plane")) 
Scene().add_component(cube, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(0.1, 0.1, 0.1), static=True)) 
Scene().add_component(cube, MeshComponent(mesh_type=MeshComponent.Type.IMPORT, import_path=definitions.MODEL_DIR / "cube-sphere" / "cube.obj"))
Scene().add_component(cube, ShaderComponent(shader_path=definitions.SHADER_DIR / "WGPU" / "base_shader.wgsl")) 
Scene().add_component(cube, MaterialComponent()) 

cube2 = Scene().add_entity() 
Scene().add_component(cube2, InfoComponent("Plane2")) 
Scene().add_component(cube2, TransformComponent(glm.vec3(2, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1), static=True)) 
Scene().add_component(cube2, MeshComponent(mesh_type=MeshComponent.Type.IMPORT, import_path=definitions.MODEL_DIR / "cube-sphere" / "cube.obj"))
Scene().add_component(cube2, ShaderComponent(shader_path=definitions.SHADER_DIR / "WGPU" / "base_shader.wgsl")) 
Scene().add_component(cube2, MaterialComponent()) 

model = Scene().add_entity() 
Scene().add_component(model, InfoComponent("model")) 
Scene().add_component(model, TransformComponent(glm.vec3(-1, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1), static=True)) 
Scene().add_component(model, MeshComponent(mesh_type=MeshComponent.Type.IMPORT, import_path=definitions.MODEL_DIR / "Cauterizer" / "Cauterizer.obj"))
Scene().add_component(model, ShaderComponent(shader_path=definitions.SHADER_DIR / "WGPU" / "base_shader.wgsl")) 
Scene().add_component(model, MaterialComponent()) 

building = Scene().add_entity() 
Scene().add_component(building, InfoComponent("building")) 
Scene().add_component(building, TransformComponent(glm.vec3(0, 2, -4), glm.vec3(0, -90, 180), glm.vec3(0.01, 0.01, 0.01), static=True)) 
Scene().add_component(building, MeshComponent(mesh_type=MeshComponent.Type.IMPORT, import_path=definitions.MODEL_DIR / "stronghold" / "source" / "building.obj"))
Scene().add_component(building, ShaderComponent(shader_path=definitions.SHADER_DIR / "WGPU" / "base_shader.wgsl")) 
Scene().add_component(building, MaterialComponent()) 

Scene().add_system(TransformSystem([TransformComponent]))
Scene().add_system(CameraSystem([CameraComponent, TransformComponent]))
Scene().add_system(CameraControllerSystem([CameraControllerComponent, CameraComponent, TransformComponent])) 
Scene().add_system(MeshSystem([MeshComponent]))
Scene().add_system(ShderSystem([ShaderComponent]))


def set_base_shader_uniforms(ent:Entity, text_name:str):
    camera_ent:Entity = Scene().get_primary_cam()

    camera_comp: CameraComponent = Scene().get_component(camera_ent, CameraComponent)
    shader_comp: ShaderComponent = Scene().get_component(ent, ShaderComponent)
    plane_trans: TransformComponent = Scene().get_component(ent, TransformComponent)

    view = camera_comp.view
    projection = camera_comp.projection 
    model = plane_trans.world_matrix

    GpuController().set_uniform_value(
        shader_component=shader_comp, buffer_name="ubuffer", member_name="view", uniform_value=view, mat4x4f=True
    ) 
    GpuController().set_uniform_value(
        shader_component=shader_comp, buffer_name="ubuffer", member_name="projection", uniform_value=projection, mat4x4f=True
    ) 
    GpuController().set_uniform_value(
        shader_component=shader_comp, buffer_name="ubuffer", member_name="model", uniform_value=model, mat4x4f=True
    ) 
    GpuController().set_texture_sampler(
        shader_component=shader_comp, texture_name="myTexture", sampler_name="mySampler", texture=TextureLib().get_texture(name=text_name)
    )


Renderer().init(
    present_context=present_context,
    render_texture_format=render_texture_format,
    canvas_size=[width, height]
) 
while canvas._running:
    ts = TimeStepManager().update()  
    event = canvas.event_input_process(); 
    width = canvas._windowWidth
    height = canvas._windowHeight   
    Scene().update(event, ts)  

    set_base_shader_uniforms(cube, "3x3")
    set_base_shader_uniforms(cube2, "grass")
    set_base_shader_uniforms(model, "Cauterizer")
    set_base_shader_uniforms(building, "building")

    Renderer().render([1920, 1080]) 
    canvas.display()

canvas.shutdown()