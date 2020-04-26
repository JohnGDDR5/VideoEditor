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

"""
bl_info = {
    "name": "Video Editor Script Tools",
    "description": "Simple strip tools for Blender",
    "author": "JohnGDDR5 (Juan Cardenas)",
    "version": (1, 0, 0), 
    "blender": (2, 80, 0),
    "location": "View3D > Tools > Rig",
    "warning": "Currently in development. Porting to Blender 2.8",
    "support": "COMMUNITY",
    "category": "Sequencer Video Editing"
}
"""

import bpy
        
from bpy.props import * #Basically to allow the use of BoolProperty .etc
from math import pi, radians
from mathutils import Matrix, Vector, Euler

from operator import itemgetter, attrgetter

class SEQUENCER_TOOLS_OT_strip_ops(bpy.types.Operator):
    """Operators for  Strips on Sequence Editor"""
    bl_idname = "sequencer_tools.strip_ops"
    bl_label = "Simple Object Operator"
    bl_options = {'REGISTER', 'UNDO'}
    type: bpy.props.StringProperty(default="default")
    sub: bpy.props.StringProperty(default="default")
    #line = bpy.props.IntProperty(default=1, min=1)
    
    #Makes sure there is at least 1 strip selected in sequence editor
    @classmethod
    def poll(cls, context):
        #return bpy.context.screen.scene.sequence_editor.active_strip is not None
        return bpy.context.scene.sequence_editor.active_strip is not None
    
    def execute(self, context):
        
        scene = bpy.context.scene
        data = bpy.data
        
        props = scene.SeqTools_Props
        
        start = scene.frame_start
        end = scene.frame_end
        frameC = scene.frame_current
        currentF = scene.frame_current
        
        markerScale = props.MarkerScale
        inlcudeMarkers = props.MarkerInclude
        markers = scene.timeline_markers
        
        screen = bpy.context.screen
        #sequence_editor = screen.scene.sequence_editor
        sequence_editor = scene.sequence_editor
        
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
                markerlist = []
                #Sequence Editor Strips for loops
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
                
                if inlcudeMarkers == True:
                    if self.sub == "afterCurrent":
                        for i in enumerate(markers):
                            if i[1].frame > currentF:
                                i[1].frame -= sub
                    elif self.sub == "afterCurrentSelected":
                        for i in enumerate(markers):
                            if i[1].frame > currentF:
                                if i[1].select == True:
                                    i[1].frame -= sub
            """if self.sub == "all":
                pass"""
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
            print("Unrecognized .strip_ops's Type & Sub")
            
        self.type = "default"
        self.sub = "default"
        
        return {'FINISHED'}

class SEQUENCER_TOOLS_OT_marker_ops(bpy.types.Operator):
    """Operators for Markers in scene timeline"""
    bl_idname = "sequencer_tools.marker_ops"
    bl_label = "Simple Object Operator"
    bl_options = {'REGISTER', 'UNDO'}

    type: bpy.props.StringProperty(default="default")
    sub: bpy.props.StringProperty(default="default")
    #line = bpy.props.IntProperty(default=1, min=1)
    
    #Makes sure there is at least 1 strip selected in sequence editor
    @classmethod
    def poll(cls, context):
        #return len(bpy.context.scene.timeline_markers) > 0
        return True
    
    def execute(self, context):
        
        scene = bpy.context.scene
        data = bpy.data
        
        props = scene.SeqTools_Props
        
        start = scene.frame_start
        end = scene.frame_end
        currentF = scene.frame_current
        
        markerScale = props.MarkerScale
        markerInt = props.MarkerInt
        
        markers = scene.timeline_markers
        
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
        elif self.type == "scale":
            
            #Checks if there is at least 1 marker
            if len(markers) > 0:
                #Allows for correct calculation
                markerScale = (markerScale-1)*-1
                
                #When MarkerScale isn't 1 or 0
                if props.MarkerScale != 1 and props.MarkerScale != 0:
                    for i in enumerate(markers):
                        if i[1].select == True:
                            frameDifference = currentF - i[1].frame
                            frameDifference *= markerScale
                            i[1].frame += int(frameDifference)
                elif props.MarkerScale == 0:
                    for i in enumerate(markers):
                        if i[1].select == True:
                            i[1].frame = currentF
                #No need to scale anything when they won't move at all
                else:
                    pass
        #This doesn't work MLG
        elif self.type == "active":
            if self.sub == "next":
                #Checks if there is at least 1 marker
                if len(markers) > 0:
                    #1st try
                    """
                    markerIndex = 0
                    #Selects Next Marker
                    for i in enumerate(markers):
                        if i[1].select == True:
                            markerIndex = i[0]
                            break
                        elif i[0] == len(markers)-1:
                            pass
                    
                    #Deselects all markers
                    for i in markers:
                        i.select = False
                    
                    #Selects Next Marker
                    if markerIndex != len(markers)-1:
                        markers[markerIndex+1].select = True
                    else:
                        markers[0].select = True
                    #break"""
                    #2nd try
                    """
                    markerIndex = 0
                    #indexList = []
                    #Appends all selected marker frames to frameList
                    frameList = []
                    for i in enumerate(markers):
                        if i[1].select == True:
                            #indexList.append(i[0])
                            frameList.append(i[1].frame)
                    #Finds minimum frame to find the index 
                    minimum = min(frameList)
                    
                    #Deselects all markers
                    for i in markers:
                        i.select = False
                    #Find which marker is at the minimum frame
                    for i in enumerate(markers):
                        if i[1].frame == minimum:
                            #Doesn't work since indexes aren't in range
                            markers[i[0]+1].select = True
                            #markerIndex = i[0]
                            break
                        elif i[0] == len(markers)-1:
                            #markers[0].select = True
                            pass
                    """
                    markerIndex = 0
                    indexList = []
                    #Appends all selected marker frames to frameList
                    frameList = []
                    for i in enumerate(markers):
                        #if i[1].select == True:
                        indexList.append(i[0])
                        frameList.append(i[1].frame)
                        #break
                    #Finds minimum frame to find the index 
                    #minimum = min(frameList)
                    
                    #Sorts the list
                    sort = sorted(frameList)
                    
                    #Deselects all markers
                    for i in markers:
                        i.select = False
                    #Find which marker is at the minimum frame
                    """for i in enumerate(markers):
                        if i[1].frame == minimum:
                            #Doesn't work since indexes aren't in range
                            markers[i[0]+1].select = True
                            #markerIndex = i[0]
                            break
                        elif i[0] == len(markers)-1:
                            #markers[0].select = True
                            pass"""
                    #Find which marker is at the minimum frame
                    for i in indexList:
                        print("I: "+str(i))
                        if markers[i].frame == sort[0]:
                            print("sort[0] : "+str(sort[0]))
                            if i != len(markers)-1:
                                print("indexList[i+1] : "+str(indexList[i+1]))
                                #Doesn't work since indexes aren't in range
                                markers[indexList[i+1]].select = True
                                #markerIndex = i[0]
                                break
                            else:
                                markers[0].select = True
                        #elif i == len(markers)-1:
                            #markers[0].select = True
                            #pass
                    
                else:
                    print("No Markers in scene timeline")
                
        elif self.type == "move":
            if self.sub == "add":
                for i in enumerate(markers):
                    if i[1].select == True:
                        i[1].frame += markerInt
            elif self.sub == "sub":
                for i in enumerate(markers):
                    if i[1].select == True:
                        i[1].frame -= markerInt
            
        else:
            print("Unrecognized .marker_ops's Type & Sub")
        
        return {'FINISHED'}
    
class SEQUENCER_TOOLS_OT_marker_to_current(bpy.types.Operator):
    """Sets active and closest marker to current frame"""
    bl_idname = "sequencer_tools.marker_to_current"
    bl_label = "Simple Object Operator"
    bl_options = {'REGISTER', 'UNDO'}
    
    #Makes sure there is at least 1 strip selected in sequence editor
    @classmethod
    def poll(cls, context):
        return len(bpy.context.scene.timeline_markers) > 0
    
    def execute(self, context):
        
        scene = bpy.context.scene
        
        props = scene.SeqTools_Props
        
        start = scene.frame_start
        end = scene.frame_end
        currentF = scene.frame_current
        
        markers = scene.timeline_markers
        list = []
        #List will have [0]=name, [1]=distance, [2]=boolean, [3]=index
            
        if len(markers) > 0:
            print("Greater than 0")
            print("CurrentF: " + str(currentF))
            for j, i in enumerate(scene.timeline_markers):
                
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
    
class SEQUENCER_TOOLS_OT_timeline_add(bpy.types.Operator):
    """Adds frame number set of Frameint"""
    bl_idname = "time.timeline_add"
    bl_label = "Simple Object Operator"
    type: bpy.props.StringProperty(default="add")
    bl_options = {'REGISTER', 'UNDO'}
    #timeline = bpy.props.StringProperty(default="start")

    def execute(self, context):
        
        scene = bpy.context.scene
        
        props = scene.SeqTools_Props
        
        timelineInt = props.TimelineInt[0]
        if props.TimelineBool == True:
            timelineInt = props.TimelineInt[1]
        #bool = scene.frameAddBool
        
        frameCurrent = scene.frame_current
        frameEnd = scene.frame_end
        frameStart = scene.frame_start
        
        #scene = bpy.context.scene
        
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

"""
def initSceneProperties(scn):
    #Custom Variables created in Scene Custom Prop data on run
   
    mlg1 = bpy.types.Scene.LayerToggle = BoolProperty(name="Boolean", description="Shadow Samples Toggle Button", default=False)
    scn["LayerToggle"] = False
    
    mlg2 = bpy.types.Scene.ScnLayersToggle = BoolVectorProperty(name="Boolean", description="Booleans if bone layers are on/off", size=32)
    scn["ScnLayersToggle"] = ([False]*32)
    
    mlg3 = bpy.types.Scene.TimelineBool = BoolProperty(name="Boolean", description="Booleans if bone layers are on/off", default=False)
    scn["TimelineBool"] = False
    
    mlg5 = bpy.types.Scene.TimelineInt = IntVectorProperty(name="IntVector", description="Add or Sub Current Frame", default= (24, 24) , min=0, size=2)
    scn["TimelineInt"] = (24, 24)
    
    mlg6 = bpy.types.Scene.MarkerScale = FloatProperty(name="Float", description="Scale location of selected markers", default= 1.0, min=0.0, soft_min=0.0, soft_max=5.0)
    scn["MarkerScale"] = 24
    
    mlg7 = bpy.types.Scene.MarkerInclude = BoolProperty(name="Boolean", description="If you want to include markers when moving with screen.strip_ops", default=False)
    scn["MarkerInclude"] = False
    
    mlg8 = bpy.types.Scene.MarkerInt = IntProperty(name="Int", description="Add or Sub Current Frame selected markers", default= 24, min=0)
    scn["MarkerInt"] = 24
    
    return

#Need This When its not run as an AddOn
initSceneProperties(bpy.context.scene)
"""

class SEQUENCER_TOOLS_props(bpy.types.PropertyGroup):
    #collections for custom Property Groups
    LayerToggle: BoolProperty(name="Boolean", description="Shadow Samples Toggle Button", default=False)
    
    ScnLayersToggle: BoolVectorProperty(name="Boolean", description="Booleans if bone layers are on/off", size=32, default=([False]*32))
    
    TimelineBool: BoolProperty(name="Boolean", description="Booleans if bone layers are on/off", default=False)
    
    TimelineInt: IntVectorProperty(name="IntVector", description="Add or Sub Current Frame", default= (24, 24) , min=0, size=2)
    
    MarkerScale: FloatProperty(name="Float", description="Scale location of selected markers", default= 24.0, min=0.0, soft_min=0.0, soft_max=5.0)
    
    MarkerInclude: BoolProperty(name="Boolean", description="If you want to include markers when moving with screen.strip_ops", default=False)
    
    MarkerInt: IntProperty(name="Int", description="Add or Sub Current Frame selected markers", default= 24, min=0)
    
    # END

# Menu UI Panel __________________________________________________

class SEQUENCER_TOOLS_PT_custom_panel1(bpy.types.Panel):
    #A Custom Panel in Viewport
    bl_idname = "SEQUENCER_TOOLS_PT_custom_panel1"
    bl_label = "Strip Edit"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Edit Video"
    
    # draw function
    def draw(self, context):
                 
        layout = self.layout
        
        scene = bpy.context.scene
        screen = bpy.context.screen
        
        props = scene.SeqTools_Props
        
        #New Stuff
        #bpy.context.scene.sequence_editor.active_strip

        #sequence_editor = screen.scene.sequence_editor
        sequence_editor = scene.sequence_editor
        currentF = scene.frame_current
        
        col = layout.column()
        #Current Frame
        #row = col.row(align=True)
        #row.label(text="Current Frame:")
        
        row = col.row(align=True)
        #if screen.scene.sequence_editor.active_strip is not None:
        if scene.sequence_editor.active_strip is not None:
            active_strip = sequence_editor.active_strip
            
            row.label(text="Strip Frames: "+str(active_strip.frame_final_duration))
            row = col.row(align=True)
            row.label(text="Start Frame: "+str(active_strip.frame_final_start))
            row = col.row(align=True)
            row.label(text="Current Frame Dif: "+str(active_strip.frame_final_start-currentF))
        else:
            row.label(text="Strip Frames: No Active Strip")
            row = col.row(align=True)
            row.label(text="Start Frame: No Active Strip")
            row = col.row(align=True)
            row.label(text="Current Frame Dif: No Active Strip")
        
        row = col.row(align=True)
        button = row.operator("time.timeline_add", text="", icon="ADD")
        button.type = "add"
        button = row.operator("time.timeline_add", text="", icon="REMOVE")
        button.type = "sub"
        if props.TimelineBool == False:
            row.prop(props, "TimelineInt", index=0, text="Add Frame")
        else:
            row.prop(props, "TimelineInt", index=1, text="Add Frame")
        row.prop(props, "TimelineBool", text="", icon="PREVIEW_RANGE")
        
        #Strip
        row = col.row(align=True)
        row.label(text="Strip:")
        
        #Reverse Strip    
        row = col.row(align=True)
        if sequence_editor.active_strip is not None:
            if sequence_editor.active_strip.use_reverse_frames == False:
                button = row.operator("sequencer_tools.strip_ops", text="Reverse Strip", icon="FILE_REFRESH")
            else:
                button = row.operator("sequencer_tools.strip_ops", text="UnReverse Strip", icon="FILE_REFRESH")
        else:
            button = row.operator("sequencer_tools.strip_ops", text="Reverse Strip", icon="FILE_REFRESH")
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
        
        row = col.row(align=True)
        row.label(text="Move Strips:")
        
        #Moves All Strips After Current Frame to Current Frame
        row = col.row(align=True)
        button = row.operator("sequencer_tools.strip_ops", text="All Left", icon="BACK")
        button.type = "move"
        button.sub = "afterCurrent"
        
        #Moves All Selected Strips After Current Frame to Current Frame
        #row = col.row(align=True)
        button = row.operator("sequencer_tools.strip_ops", text="Active", icon="BACK")
        button.type = "move"
        button.sub = "afterCurrentSelected"
        
        row.prop(props, "MarkerInclude", text="", icon="MARKER_HLT")
        
        #bpy.ops.sequencer.select(extend=False, linked_handle=False, left_right='NONE', linked_time=False)
        #Right
        row = col.row(align=True)
        row.label(text="Select Strips:")
        
        row = col.row(align=True)
        button = row.operator("sequencer.select", text="Right", icon="BACK")
        button.extend = False
        button.linked_handle = False
        button.linked_time = False
        button.left_right = "LEFT"
        
        button = row.operator("sequencer.select", text="Left", icon="FORWARD")
        button.extend = False
        button.linked_handle = False
        button.linked_time = False
        button.left_right = "RIGHT"
        
        #Markers
        row = col.row(align=True)
        row.label(text="Markers:")
        
        row = col.row(align=True)
        button = row.operator("sequencer_tools.marker_ops", text="", icon="ADD")
        button.type = "move"
        button.sub = "add"
        button = row.operator("sequencer_tools.marker_ops", text="", icon="REMOVE")
        button.type = "move"
        button.sub = "sub"
        row.prop(props, "MarkerInt", text="Marker")
        
        #Scale Markers
        row = col.row(align=True)
        button = row.operator("sequencer_tools.marker_ops", text="", icon="FULLSCREEN_ENTER")
        button.type = "scale"
        
        row.prop(props, "MarkerScale", text="Scale")
        
        
        row = col.row(align=True)
        button = row.operator("screen.marker_jump", text="Previous", icon="TRIA_LEFT")
        #row.operator("sequencer_tools.marker_jump", text="Previous", icon="TRIA_LEFT").next = False
        #row.operator("sequencer_tools.marker_jump", text="Previous", icon="TRIA_LEFT")
        button.next = False

        button = row.operator("screen.marker_jump", text="Next", icon="TRIA_RIGHT")
        button.next = True
        
        #Active
        """row = col.row(align=True)
        button = row.operator("sequencer_tools.marker_ops", text="Next", icon="TRIA_RIGHT")
        button.type = "active"
        button.sub = "next" """
        #button = row.operator("sequencer_tools.marker_ops", text="Previous", icon="REMOVE")
        #button.type = "active"
        #button.sub = "previous"
        
        #Select
        row = col.row(align=True)
        button = row.operator("sequencer_tools.marker_ops", text="Select Current Frame", icon="MARKER_HLT")
        button.type = "select"
        button.sub = "currentFrame"
        
        row = col.row(align=True)
        button = row.operator("sequencer_tools.marker_ops", text="Select All", icon="MARKER_HLT")
        button.type = "select"
        button.sub = "all"
        
        #row = col.row(align=True)
        button = row.operator("sequencer_tools.marker_ops", text="Unselect All", icon="MARKER")
        button.type = "deselect"
        button.sub = "all"
        
        row = col.row(align=True)
        button = row.operator("sequencer_tools.marker_to_current", text="Marker To Current", icon="MARKER_HLT")
        
        #End of SEQUENCER_TOOLS_PT_custom_panel11

classes = (
    SEQUENCER_TOOLS_PT_custom_panel1,
    SEQUENCER_TOOLS_OT_strip_ops,
    SEQUENCER_TOOLS_OT_marker_ops,
    SEQUENCER_TOOLS_OT_marker_to_current,
    SEQUENCER_TOOLS_OT_timeline_add,
    #initSceneProperties,

    SEQUENCER_TOOLS_props,
)

"""
def register():
    #ut = bpy.utils
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.Scene.SeqTools_Props = bpy.props.PointerProperty(type=SEQUENCER_TOOLS_props)
    
def unregister():
    #ut = bpy.utils
    #from bpy.utils import unregister_class
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    #Just incase to prevent an error
    if hasattr(bpy.types.Scene, "SeqTools_Props") == True:
        del bpy.types.Scene.SeqTools_Props
    
#register, unregister = bpy.utils.register_classes_factory(classes)
if __name__ == "__main__":
    register()

"""
