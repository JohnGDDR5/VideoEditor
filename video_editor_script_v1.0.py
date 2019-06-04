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
    """Operators for  Strips on Sequence Editor"""
    bl_idname = "screen.strip_ops"
    bl_label = "Simple Object Operator"
    bl_options = {'REGISTER', 'UNDO'}
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
        #bpy.context.screen.scene.sequence_editor.active_strip
        list = []
        
        if self.type == "reverse":
            if self.sub == "all":
                #Checks if there is at least 1 marker
                if len(markers) > 0:
                    for i in enumerate(markers):
                        i[1].select = True
                else:
                    print("No Markers in scene timeline")
            elif self.sub == "strip":
                #Checks if there is at least an active strip
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
                    
        elif self.type == "deselect":
            if self.sub == "all":
                pass
        elif self.type == "move":
            #if self.sub == "afterCurrent":
            #Checks if there is at least an active strip
            if sequence_editor.active_strip is not None:
                active = sequence_editor.active_strip
                
                list = []
                listStart = []
                striplist = []
                if self.sub == "afterCurrent":
                    for i in enumerate(sequence_editor.sequences_all):
                        if i[1].frame_final_start > frameC:
                            list.append(i)
                            #print("1: "+str(i[1]))
                        else:
                            pass
                elif self.sub == "afterCurrentSelected":
                    for i in enumerate(sequence_editor.sequences_all):
                        if i[1].frame_final_start > frameC and i[1].select == True:
                            list.append(i)
                            #print("1: "+str(i[1]))
                        else:
                            pass
                #Appends the frame each strip in "list" starts in    
                for i in list:
                    listStart.append(i[1].frame_final_start)
                    
                #Gets the minimum index appended to "list" variable
                minimum = int(min(listStart))
                #The ammount to subtract for every strip on the left of the current frame
                sub = minimum-frameC#sequence_editor.sequences_all[minimum].frame_final_start-frameC
                
                for i in list:
                    if i[1].frame_final_start > frameC:
                        channel = i[1].channel
                        i[1].frame_start -= sub#(i[1].frame_final_start-frameC)
                        i[1].channel = channel
                    else:
                        pass
            #pass
            """elif self.sub == "afterCurrentActive":
                #Checks if there is at least an active strip
                if sequence_editor.active_strip is not None:
                    active = sequence_editor.active_strip
                    
                    list = []
                    
                    for i in enumerate(sequence_editor.sequences_all):
                        if i[1].frame_final_start > frameC and i[1].select == True:
                            list.append(i[0])
                        else:
                            pass
                    #Gets the minimum index appended to "list" variable
                    minimum = int(min(list))
                    #The ammount to subtract for every strip on the left of the current frame
                    sub = sequence_editor.sequences_all[minimum].frame_final_start-frameC
                    
                    for i in enumerate(sequence_editor.sequences_all):
                        if i[1].frame_final_start > frameC:
                            channel = i[1].channel
                            i[1].frame_start -= sub#(i[1].frame_final_start-frameC)
                            i[1].channel = channel
                        else:
                            pass
                pass"""
        else:
            print("Unrecognized .marker_ops's Type & Sub")
        
        return {'FINISHED'}

class MarkerOperators(bpy.types.Operator):
    """Operators for Markers in scene timeline"""
    bl_idname = "screen.marker_ops"
    bl_label = "Simple Object Operator"
    bl_options = {'REGISTER', 'UNDO'}
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
    
class MarkerToCurrent(bpy.types.Operator):
    """Sets active and closest marker to current frame"""
    bl_idname = "screen.marker_to_current"
    bl_label = "Simple Object Operator"
    bl_options = {'REGISTER', 'UNDO'}
    
    #Makes sure there is at least 1 strip selected in sequence editor
    @classmethod
    def poll(cls, context):
        return len(bpy.context.scene.timeline_markers) > 0
    
    def execute(self, context):
        
        scene = bpy.context.scene
        start = scene.frame_start
        end = scene.frame_end
        currentF = scene.frame_current
        
        markers = bpy.context.scene.timeline_markers
        list = []
        #List will have [0]=name, [1]=distance, [2]=boolean, [3]=index
            
        if len(markers) > 0:
            print("Greater than 0")
            print("CurrentF: " + str(currentF))
            for j, i in enumerate(bpy.context.scene.timeline_markers):
                
                #Checks if a marker is selected
                if i.select == True:
                    print(str(i.name)+": "+str(i.frame) +" "+ str(i.select))
                    #Gets the distance of the selected marker to current frame
                    distance = i.frame - currentF
                    list.append([i.name, distance, i.select, j])
                    
                    if i.frame >= currentF:
                        break
            
            #Checks if there is more than one selected marker
            if len(list) > 1:
                #There will always only be one index after the current frame if there is one or more selected after the current frame
                index = list[-1][3]
                #Checks if last marker distance is greater or less than current frame
                if list[-1][1] > 0:
                    #Checks which marker distance is closer to the current frame
                    if abs(list[-1][1]) < abs(list[-2][1]):
                        scene.timeline_markers[index].frame = currentF
                    else:
                        scene.timeline_markers[list[-2][3]].frame = currentF
                elif list[-1][1] < 0:
                    scene.timeline_markers[index].frame = currentF
            elif len(list) == 1:
                
                scene.timeline_markers[list[0][3]].frame = currentF
            else:
                print("No Markers Selected")
                pass
                
        else:
            print("select a marker")
        
        return {'FINISHED'}
    
class timelineAdd(bpy.types.Operator):
    """Adds frame number set of Frameint"""
    bl_idname = "time.timeline_add"
    bl_label = "Simple Object Operator"
    type = bpy.props.StringProperty(default="add")
    bl_options = {'REGISTER', 'UNDO'}
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
        
        #Moves All Strips After Current Frame to Current Frame
        row = col.row(align=True)
        button = row.operator("screen.strip_ops", text="Left Strips", icon="BACK")
        button.type = "move"
        button.sub = "afterCurrent"
        
        #Moves All Selected Strips After Current Frame to Current Frame
        #row = col.row(align=True)
        button = row.operator("screen.strip_ops", text="Active Strips", icon="BACK")
        button.type = "move"
        button.sub = "afterCurrentSelected"
        
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
        
        row = col.row(align=True)
        button = row.operator("screen.marker_to_current", text="Marker To Current", icon="MARKER_HLT")
        
        #End of CustomPanel1

# Register        
def register():  
    ut = bpy.utils
    
    ut.register_class(CustomPanel)
    ut.register_class(StripOperators)
    ut.register_class(MarkerOperators)
    ut.register_class(MarkerToCurrent)
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
    ut.unregister_class(MarkerToCurrent)
    ut.unregister_class(timelineAdd)
    #Note: register_manual_map isn't needed for an AddOn
    ut.unregister_manual_map(initSceneProperties)
    
    #Unregister CollectionProperty
    #ut.unregister_class(SelectListClass)
    #del bpy.types.Scene.selectList
    
if __name__ == "__main__":
    register()
