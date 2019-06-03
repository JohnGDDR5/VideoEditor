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

class StripOperators(bpy.types.Operator):
    """Sets end frame to current frame"""
    bl_idname = "screen.strip_ops"
    bl_label = "Simple Object Operator"
    type = bpy.props.StringProperty(default="default")
    sub = bpy.props.StringProperty(default="default")
    #line = bpy.props.IntProperty(default=1, min=1)
    
    #Makes sure there is at least 1 strip selected in sequence editor
    @classmethod
    def poll(cls, context):
        return bpy.context.screen.scene.sequence_editor.active_strip is not None
    
    def execute(self, context):
        
        scene = bpy.context.scene
        data = bpy.data
        
        start = scene.frame_start
        end = scene.frame_end
        frameC = scene.frame_current
        
        screen = bpy.context.screen
        sequence_editor = screen.scene.sequence_editor
        
        list = []
        
        if self.type == "reverse":
            if self.sub == "strip":
                #Checks if there is at least 1 marker
                if sequence_editor.active_strip is not None:
                    active = sequence_editor.active_strip
                    
                    if active.use_reverse_frames == False:
                        active.use_reverse_frames = True
                    else:
                        active.use_reverse_frames = False
                    
                    startF = active.frame_final_start
                    channelC = active.channel
                    
                    print("-------------1")
                    print("StartF 1: "+str(startF))
                    print("Final Start 1: "+str(active.frame_final_start))
                    print("Frame Start 1: "+str(active.frame_start))
                    
                    #Hard Cut
                    active.animation_offset_start, active.animation_offset_end = active.animation_offset_end, active.animation_offset_start
                    #Soft Cut
                    active.frame_offset_start, active.frame_offset_end = active.frame_offset_end, active.frame_offset_start
                    
                    print("-------------2")
                    print("StartF 2: "+str(startF))
                    print("Final Start 2: "+str(active.frame_final_start))
                    print("Frame Start 2: "+str(active.frame_start))
                    
                    #active.frame_final_start = startF
                    active.frame_start += (active.frame_final_start*-1)+startF#+1
                    active.channel = channelC
                    print("-------------3")
                    print("StartF 3: "+str(startF))
                    print("Final Start 3: "+str(active.frame_final_start))
                    print("Frame Start 3: "+str(active.frame_start))
                    
                    print("-------------End")
                    
                    
                else:
                    print("No Active Strip")
            elif self.sub == "all":
                #Checks if there is at least 1 marker
                if len(markers) > 0:
                    for i in enumerate(markers):
                        i[1].select = True
                else:
                    print("No Markers in scene timeline")
                    
        elif self.type == "deselect":
            if self.sub == "all":
                pass
        else:
            print("Unrecognized .marker_ops's Type & Sub")
        
        return {'FINISHED'}

class MarkerOperators(bpy.types.Operator):
    """Sets end frame to current frame"""
    bl_idname = "screen.marker_ops"
    bl_label = "Simple Object Operator"
    type = bpy.props.StringProperty(default="default")
    sub = bpy.props.StringProperty(default="default")
    #line = bpy.props.IntProperty(default=1, min=1)
    
    #Makes sure there is at least 1 strip selected in sequence editor
    @classmethod
    def poll(cls, context):
        return len(bpy.context.scene.timeline_markers) > 0
    
    def execute(self, context):
        
        scene = bpy.context.scene
        data = bpy.data
        
        start = scene.frame_start
        end = scene.frame_end
        currentF = scene.frame_current
        
        markers = bpy.context.scene.timeline_markers
        
        list = []
        
        if self.type == "select":
            if self.sub == "currentFrame":
                #Checks if there is at least 1 marker
                if len(markers) > 0:
                    for i in enumerate(markers):
                        #If marker is in the current frame
                        if i[1].frame == currentF:
                            #Checks if marker is already selected or not to make it active
                            if i[1].select == False:
                                i[1].select = True
                            elif i[1].select == True:
                                i[1].select = False
                                i[1].select = True
                            break
                else:
                    print("No Markers in scene timeline")
            elif self.sub == "all":
                #Checks if there is at least 1 marker
                if len(markers) > 0:
                    for i in enumerate(markers):
                        i[1].select = True
                else:
                    print("No Markers in scene timeline")
                    
        elif self.type == "deselect":
            if self.sub == "all":
                #Checks if there is at least 1 marker
                if len(markers) > 0:
                    for i in enumerate(markers):
                        i[1].select = False
                else:
                    print("No Markers in scene timeline")
        else:
            print("Unrecognized .marker_ops's Type & Sub")
        
        return {'FINISHED'}
    
class timelineAdd(bpy.types.Operator):
    """Adds frame number set of Frameint"""
    bl_idname = "time.timeline_add"
    bl_label = "Simple Object Operator"
    type = bpy.props.StringProperty(default="add")
    #timeline = bpy.props.StringProperty(default="start")

    def execute(self, context):
        
        scene = bpy.context.scene
        
        timelineInt = scene.TimelineInt[0]
        if bpy.context.scene.TimelineBool == True:
            timelineInt = scene.TimelineInt[1]
        #bool = scene.frameAddBool
        
        frameCurrent = bpy.context.scene.frame_current
        frameEnd = scene.frame_end
        frameStart = scene.frame_start
        
        scene = bpy.context.scene
        
        #Current Frame
        #if self.timeline == "current":
        if self.type == "add":
            scene.frame_current += timelineInt
        elif self.type == "sub":
            scene.frame_current -= timelineInt
        elif self.type == "multiply":
            scene.frame_current *= timelineInt
            
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
    mlg3 = bpy.types.Scene.TimelineBool = BoolProperty(name="Boolean", description="Booleans if bone layers are on/off", default=False)
    scn["TimelineBool"] = False
    """mlg4 = bpy.types.Scene.ActiveResButtons = IntVectorProperty(name = "IntVector", description = "X & Y Vector for Custom Resolution's Aspect Ratio", size=2, default=(0,0))
    scn["ActiveResButtons"] = (0, 0)"""
    mlg5 = bpy.types.Scene.TimelineInt = IntVectorProperty(name="IntVector", description="Add or Sub Current Frame", default= (24, 24) , min=0, size=2)
    scn["TimelineInt"] = (24, 24)
    
    return

#Need This When its not run as an AddOn
initSceneProperties(bpy.context.scene)

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
        scene = bpy.context.scene
        screen = bpy.context.screen
        sequence_editor = bpy.context.screen.scene.sequence_editor
        
        col = layout.column()
        #Current Frame
        row = col.row(align=True)
        row.label(text="Current Frame:")
        row = col.row(align=True)
        button = row.operator("time.timeline_add", text="", icon="ZOOMIN")
        button.type = "add"
        button = row.operator("time.timeline_add", text="", icon="ZOOMOUT")
        button.type = "sub"
        if scene.TimelineBool == False:
            row.prop(scene, "TimelineInt", index=0, text="Frame")
        else:
            row.prop(scene, "TimelineInt", index=1, text="Frame")
        row.prop(scene, "TimelineBool", text="", icon="PREVIEW_RANGE")
        
        #Strip
        row = col.row(align=True)
        row.label(text="Strip:")
        row = col.row(align=True)
        if bpy.context.screen.scene.sequence_editor.active_strip is not None:
            active_strip = sequence_editor.active_strip
            row.label(text="Frame Length: "+str(active_strip.frame_final_duration))
        else:
            row.label(text="Frame Length: No Active Strip")
        
        #Reverse Strip    
        row = col.row(align=True)
        if sequence_editor.active_strip is not None:
            if sequence_editor.active_strip.use_reverse_frames == False:
                button = row.operator("screen.strip_ops", text="Reverse Strip", icon="FILE_REFRESH")
            else:
                button = row.operator("screen.strip_ops", text="UnReverse Strip", icon="FILE_REFRESH")
        else:
            button = row.operator("screen.strip_ops", text="Reverse Strip", icon="FILE_REFRESH")
        button.type = "reverse"
        button.sub = "strip"
        
        row = col.row(align=True)
        button = row.operator("sequencer.strip_jump", text="Previous", icon="TRIA_LEFT")
        button.next = False
        button.center = False
        
        button = row.operator("sequencer.strip_jump", text="Next", icon="TRIA_RIGHT")
        button.next = True
        button.center = False
        
        row = col.row(align=True)
        button = row.operator("sequencer.strip_jump", text="Center", icon="ARROW_LEFTRIGHT")
        button.next = True
        button.center = True
        
        #Markers
        row = col.row(align=True)
        row.label(text="Markers:")
        row = col.row(align=True)
        row.operator("screen.marker_jump", text="Previous", icon="TRIA_LEFT").next = False
        row.operator("screen.marker_jump", text="Next", icon="TRIA_RIGHT").next = True
        
        row = col.row(align=True)
        button = row.operator("screen.marker_ops", text="Select Current Frame", icon="MARKER_HLT")
        button.type = "select"
        button.sub = "currentFrame"
        
        row = col.row(align=True)
        button = row.operator("screen.marker_ops", text="Select All", icon="MARKER_HLT")
        button.type = "select"
        button.sub = "all"
        
        #row = col.row(align=True)
        button = row.operator("screen.marker_ops", text="Unselect All", icon="MARKER")
        button.type = "deselect"
        button.sub = "all"
        
        #End of CustomPanel1

# Register        
def register():  
    ut = bpy.utils
    
    ut.register_class(CustomPanel)
    ut.register_class(StripOperators)
    ut.register_class(MarkerOperators)
    ut.register_class(timelineAdd)
    #Note: register_manual_map isn't needed for an AddOn
    ut.register_manual_map(initSceneProperties)
    
    #Registers CollectionProperty in the Scene
    #ut.register_class(SelectListClass)
    #bpy.types.Scene.selectList = bpy.props.CollectionProperty(type=SelectListClass)
def unregister():
    ut = bpy.utils
    
    ut.unregister_class(CustomPanel)
    ut.unregister_class(StripOperators)
    ut.unregister_class(MarkerOperators)
    ut.unregister_class(timelineAdd)
    #Note: register_manual_map isn't needed for an AddOn
    ut.unregister_manual_map(initSceneProperties)
    
    #Unregister CollectionProperty
    #ut.unregister_class(SelectListClass)
    #del bpy.types.Scene.selectList
    
if __name__ == "__main__":
    register()
