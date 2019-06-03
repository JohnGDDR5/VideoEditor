# ##### BEGIN GPL LICENSE BLOCK #####
#
# Render Rig for rendering a rig using custom bone curve objects as curves.
# Copyright (C) 2019 Juan Cardenas
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "RenderRig",
    "description": "Generates a renderable rig with custom bones",
    "author": "Juan Cardenas",
    "version": (1, 0), #internal v1.24.6
    "blender": (2, 79, 0),
    "location": "View3D > Tools > Rig",
    "warning": "Runs very slowly on high density rigs.",
    "support": "COMMUNITY",
    "category": "Rigging"
}

import bpy
        
from bpy.props import *
from math import pi, radians
from mathutils import Matrix, Vector, Euler

class PrintSomething(bpy.types.Operator):
    """Sets end frame to current frame"""
    bl_idname = "object.print_something"
    bl_label = "Simple Object Operator"
    #type = bpy.props.StringProperty(default="start")
    line = bpy.props.IntProperty(default=1, min=1)

    def execute(self, context):
        
        scene = bpy.context.scene
        data = bpy.data
        
        print("Something")
        
        return {'FINISHED'}
    
"""class PanelGroupArmatures(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="PanelGroupArmaturesName", default="PanelGroupArmatures")
    panelList = bpy.props.CollectionProperty(type=Panels)
    
class PanelGroups(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="PanelGroupName", default="PanelGroups")
    panelList = bpy.props.CollectionProperty(type=Panels)
    panelArmatures = bpy.props.CollectionProperty(type=PanelGroupArmatures)"""

def initSceneProperties(scn):
    #Custom Variables created in Scene Custom Prop data on run
   
    mlg1 = bpy.types.Scene.LayerToggle = BoolProperty(name="Boolean", description="Shadow Samples Toggle Button", default=False)
    scn["LayerToggle"] = False
    mlg2 = bpy.types.Scene.ScnLayersToggle = BoolVectorProperty(name="Boolean", description="Booleans if bone layers are on/off", size=32)
    scn["ScnLayersToggle"] = ([False]*32)
    mlg3 = bpy.types.Scene.PanelSettings = BoolProperty(name="Boolean", description="Booleans if bone layers are on/off", default=True)
    scn["PanelSettings"] = True
    mlg4 = bpy.types.Scene.ActiveResButtons = IntVectorProperty(name = "IntVector", description = "X & Y Vector for Custom Resolution's Aspect Ratio", size=2, default=(0,0))
    scn["ActiveResButtons"] = (0, 0)
    mlg5 = bpy.types.Scene.CustomResolutionX = IntProperty(name="Int", description="Custom Resolution for X", default= 1920, min=0, subtype="PIXEL")
    scn["CustomResolutionX"] = 1920
    
    return

#Need This When its not run as an AddOn
#initSceneProperties(bpy.context.scene)

# Menu UI Panel __________________________________________________

class CustomPanel(bpy.types.Panel):
    #A Custom Panel in Viewport
    bl_idname = "StripEdit"
    bl_label = "Strip Edit"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Edit Video"
    
    # draw function
    def draw(self, context):
                 
        layout = self.layout
        scn = context.scene
        
        col = layout.column()
        
        #Prints "Something" in Console        
        row = col.row(align=True)
        row.operator("object.print_something", text='Print Something')


# Register        
def register():  
    ut = bpy.utils
    
    ut.register_class(CustomPanel)
    ut.register_class(PrintSomething)
    #Note: register_manual_map isn't needed for an AddOn
    #ut.register_manual_map(initSceneProperties)
    
    #Note: Need to register Custom Scene Properites manually in register(), not in initSceneProperties(scn) for AddOn
    bpy.types.Scene.LayerToggle = BoolProperty(name="Boolean", description="Shadow Samples Toggle Button", default=False)
    bpy.types.Scene.ScnLayersToggle = BoolVectorProperty(name="Boolean", description="Booleans if bone layers are on/off", size=32)
    bpy.types.Scene.PanelSettings = BoolProperty(name="Boolean", description="Booleans if bone layers are on/off", default=True)
    bpy.types.Scene.ActiveResButtons = IntVectorProperty(name = "IntVector", description = "X & Y Vector for Custom Resolution's Aspect Ratio", size=2, default=(0,0))
    bpy.types.Scene.CustomResolutionX = IntProperty(name="Int", description="Custom Resolution for X", default= 1920, min=0, subtype="PIXEL")
    
    #Registers CollectionProperty in the Scene
    #ut.register_class(SelectListClass)
    #bpy.types.Scene.selectList = bpy.props.CollectionProperty(type=SelectListClass)
def unregister():
    ut = bpy.utils
    
    ut.unregister_class(CustomPanel)
    ut.unregister_class(PrintSomething)
    #Note: register_manual_map isn't needed for an AddOn
    #ut.unregister_manual_map(initSceneProperties)
    
    #Note: Need to manually delete Custom Scene Properites for AddOn
    del bpy.types.Scene.LayerToggle
    del bpy.types.Scene.ScnLayersToggle
    del bpy.types.Scene.PanelSettings
    del bpy.types.Scene.ActiveResButtons
    del bpy.types.Scene.CustomResolutionX
    
    #Unregister CollectionProperty
    #ut.unregister_class(SelectListClass)
    #del bpy.types.Scene.selectList
    
if __name__ == "__main__":
    register()
