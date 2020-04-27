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


import bpy
        
from bpy.props import * #Basically to allow the use of BoolProperty .etc
from math import pi, radians
from mathutils import Matrix, Vector, Euler

from operator import itemgetter, attrgetter

class SEQUENCER_TOOLS_props(bpy.types.PropertyGroup):
    #collections for custom Property Groups
    toggle_layer: BoolProperty(name="Boolean", description="Shadow Samples Toggle Button", default=False)
    
    toggle_layers_scene: BoolVectorProperty(name="Boolean", description="Booleans if bone layers are on/off", size=32, default=([False]*32))
    
    toggle_2nd_add_frames: BoolProperty(name="Boolean", description="Booleans if bone layers are on/off", default=False)
    
    add_frames: IntVectorProperty(name="IntVector", description="Add or Sub Current Frame", default= (24, 24) , min=0, size=2)
    
    marker_scale: FloatProperty(name="Float", description="Scale location of selected markers", default= 24.0, min=0.0, soft_min=0.0, soft_max=5.0)
    
    markers_include: BoolProperty(name="Boolean", description="If you want to include markers when moving with screen.strip_ops", default=False)
    
    add_frames_marker: IntProperty(name="Int", description="Add or Sub Current Frame selected markers", default= 24, min=0)
    
    # END

class StripBlock():
    count = 0
    
    def __init__(self):
        self.strips = []
        self.start = 0
        self.end = 0
        
        type(self).count += 1
        
    def __del__(self):
        type(self).count -= 1

    def length(self):
        return len(self.strips)

    def append(self, object):
        self.strips.append(object )

    def extend(self, object):
        self.strips.extend(object )

    #Takes a parameter, if not, then it will use last object inside self.strips
    def update_range(self, strip_ob=None):
        #Object should be a Strip that uses
        #this function is to reuse code
        def calculating(strip_ob):
            if self.start != 0 and self.end != 0:
                if strip_ob.frame_final_start < self.start:
                    self.start = strip_ob.frame_final_start

                if strip_ob.frame_final_end > self.end:
                    self.end = strip_ob.frame_final_end
            else:
                self.start = strip_ob.frame_final_start
                self.end = strip_ob.frame_final_end

        if strip_ob != None:
            calculating(strip_ob)
        else:
            if self.length() > 0:
                calculating(self.strips[-1] )
            else:
                pass
    # Checks if Strips are ontop of the block, if it overlaps it.
    def is_between_range(self, strip_ob):
        is_between = False

        if self.start <= strip_ob.frame_final_start:
            if self.end >= strip_ob.frame_final_start:
                #is_between = True
                return True

        if self.end >= strip_ob.frame_final_end:
            if self.start <= strip_ob.frame_final_end:
                #is_between = True
                return True
        #is_between = self.start <= strip_ob.frame_final_start and self.end >= strip_ob.frame_final_end
        return False

    def sort_strips(self):
        #Sorts the strips in order
        self.strips.sort(key=lambda strip: strip.frame_final_start)

class SEQUENCER_TOOLS_OT_move_strips(bpy.types.Operator):
    """Operators for moving Strips on Sequence Editor"""
    bl_idname = "sequencer_tools.move_strips"
    bl_label = "Move selected Strips in Sequence Editor"
    bl_options = {'REGISTER', 'UNDO'}

    type: bpy.props.StringProperty(default="default")
    sub: bpy.props.StringProperty(default="default")
    #line = bpy.props.IntProperty(default=1, min=1)
    
    #Makes sure there is at least 1 strip selected in sequence editor
    @classmethod
    def poll(cls, context):
        #return bpy.context.screen.scene.sequence_editor.active_strip is not None
        #return bpy.context.scene.sequence_editor.active_strip is not None
        return True
    
    def execute(self, context):
        
        scene = bpy.context.scene
        data = bpy.data
        
        props = scene.SeqTools_Props

        sequence_editor = scene.sequence_editor
        
        selected_strips = [strip for strip in sequence_editor.sequences if strip.select]

        print(str(selected_strips) )
        if len(selected_strips) > 0:
            
            if len(selected_strips) > 1:

                first = StripBlock()
                #first.update_range(selected_strips[0] )
                first.append(selected_strips[0] )
                first.update_range()

                selected_strips.remove(selected_strips[0] )

                strip_blocks = []
                strip_blocks.append(first )
                
                ## 2nd
                for strip in selected_strips:
                    strip_start = strip.frame_final_start
                    strip_end = strip.frame_final_end
                    ## 1st
                    for block in strip_blocks:
                        
                        if strip_start >= block.start:
                            if block.end >= strip_start:
                                if strip_end > block.end:
                                    block.append(strip )
                                    block.update_range()
                                else:
                                    block.append(strip )
                            else:
                                block_new = None

                                #Checks if strip is between an existing block, to not create a new one
                                for j in strip_blocks:
                                    if j.is_between_range(strip ):
                                        block_new = j
                                        j.append(strip )
                                        j.update_range()

                                        #strip_blocks.append(block_new )
                                        break
                                #Creates a new StripBlock if strip wasn't between any existing ones 
                                if block_new == None:
                                    block_new = StripBlock()
                                    block_new.append(strip )
                                    block_new.update_range()

                                    strip_blocks.append(block_new )

                                break
                
                #Sorts the blocks in order
                strip_blocks.sort(key=lambda block: block.end)

                for i in enumerate(strip_blocks):
                    print("%d: [%d, %d], count: %d" % (i[0], i[1].start, i[1].end, i[1].length()) )
                
                ## This merges strip_blocks together if they are touching each other
                previous = strip_blocks[0]

                for i in strip_blocks[1:]:
                    if i.start == previous.end:
                        previous.extend(i.strips )
                        
                        previous.end = i.end

                        strip_blocks.remove(i )
                    else:
                        previous = i

                for i in enumerate(strip_blocks):
                    print("%d: [%d, %d], count: %d" % (i[0], i[1].start, i[1].end, i[1].length()) )

                ## Now I just need to sort the strips inside the strip blocks.

            else:
                print("Only 1 Strip Selected")
        else:
            print("No Strips Selected")
            
        self.type = "default"
        self.sub = "default"
        
        return {'FINISHED'}        

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
        
        marker_scale = props.marker_scale
        inlcudeMarkers = props.markers_include
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
        
        marker_scale = props.marker_scale
        add_frames_marker = props.add_frames_marker
        
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
                marker_scale = (marker_scale-1)*-1
                
                #When marker_scale isn't 1 or 0
                if props.marker_scale != 1 and props.marker_scale != 0:
                    for i in enumerate(markers):
                        if i[1].select == True:
                            frameDifference = currentF - i[1].frame
                            frameDifference *= marker_scale
                            i[1].frame += int(frameDifference)
                elif props.marker_scale == 0:
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
                        strip.select = False

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
                        i[1].frame += add_frames_marker
            elif self.sub == "sub":
                for i in enumerate(markers):
                    if i[1].select == True:
                        i[1].frame -= add_frames_marker
            
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
        #return len(bpy.context.scene.timeline_markers) > 0
        return True
    
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
                if strip.select == True:
                    print(str(strip.name)+": "+str(strip.frame) +" "+ str(strip.select))
                    #Gets the distance of the selected marker to current frame
                    distance = strip.frame - currentF
                    list.append([strip.name, distance, strip.select, j])
                    
                    if strip.frame >= currentF:
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
    bl_options = {'REGISTER', 'UNDO'}

    type: bpy.props.StringProperty(default="add")
    
    #timeline = bpy.props.StringProperty(default="start")

    def execute(self, context):
        
        scene = bpy.context.scene
        
        props = scene.SeqTools_Props
        
        add_frames = props.add_frames[0]
        if props.toggle_2nd_add_frames == True:
            add_frames = props.add_frames[1]
        #bool = scene.frameAddBool
        
        frameCurrent = scene.frame_current
        frameEnd = scene.frame_end
        frameStart = scene.frame_start
        
        #scene = bpy.context.scene
        
        #Current Frame
        #if self.timeline == "current":
        if self.type == "add":
            scene.frame_current += add_frames
        elif self.type == "sub":
            scene.frame_current -= add_frames
        elif self.type == "multiply":
            scene.frame_current *= add_frames
            
        return {'FINISHED'}
    
"""class PanelGroupArmatures(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="PanelGroupArmaturesName", default="PanelGroupArmatures")
    panelList = bpy.props.CollectionProperty(type=Panels)
    
class PanelGroups(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="PanelGroupName", default="PanelGroups")
    panelList = bpy.props.CollectionProperty(type=Panels)
    panelArmatures = bpy.props.CollectionProperty(type=PanelGroupArmatures)"""


# Menu UI Panel __________________________________________________

class SEQUENCER_TOOLS_PT_custom_panel1(bpy.types.Panel):
    #A Custom Panel in Viewport
    bl_idname = "SEQUENCER_TOOLS_PT_custom_panel1"
    bl_label = "Strip Tools"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Strip Tools"
    
    # draw function
    def draw(self, context):
                 
        layout = self.layout
        
        scene = bpy.context.scene
        #screen = bpy.context.screen
        
        props = scene.SeqTools_Props
        
        #New Stuff
        #bpy.context.scene.sequence_editor.active_strip

        #sequence_editor = screen.scene.sequence_editor
        sequence_editor = scene.sequence_editor
        
        col = layout.column()

        row = col.row(align=True)
        row.operator("sequencer_tools.move_strips", text="Remove Spaces", icon="ADD")

        row = col.row(align=True)
        row.label(text="Frame")

        row = col.row(align=True)
        button = row.operator("time.timeline_add", text="", icon="ADD")
        button.type = "add"
        button = row.operator("time.timeline_add", text="", icon="REMOVE")
        button.type = "sub"
        if props.toggle_2nd_add_frames == False:
            row.prop(props, "add_frames", index=0, text="Add Frame")
        else:
            row.prop(props, "add_frames", index=1, text="Add Frame")
        row.prop(props, "toggle_2nd_add_frames", text="", icon="PREVIEW_RANGE")
        
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
        #button.next = False
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
        
        row.prop(props, "markers_include", text="", icon="MARKER_HLT")
        
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
        
        col.separator()

        #Markers
        row = col.row(align=True)
        row.label(text="Marker Frames")
        
        row = col.row(align=True)
        button = row.operator("sequencer_tools.marker_ops", text="", icon="ADD")
        button.type = "move"
        button.sub = "add"

        button = row.operator("sequencer_tools.marker_ops", text="", icon="REMOVE")
        button.type = "move"
        button.sub = "sub"

        row.prop(props, "add_frames_marker", text="Frames")
        
        #Scale Markers
        row = col.row(align=True)
        button = row.operator("sequencer_tools.marker_ops", text="", icon="FULLSCREEN_ENTER")
        button.type = "scale"
        
        row.prop(props, "marker_scale", text="Scale")

        row = col.row(align=True)
        row.label(text="Frame to Marker")

        row = col.row(align=True)
        button = row.operator("screen.marker_jump", text="Previous", icon="TRIA_LEFT")
        button.next = False

        button = row.operator("screen.marker_jump", text="Next", icon="TRIA_RIGHT")
        button.next = True
        

        row = col.row(align=True)
        row.label(text="Select Markers")

        #Select
        row = col.row(align=True)
        button = row.operator("sequencer_tools.marker_ops", text="In Current Frame", icon="MARKER_HLT")
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
        button = row.operator("sequencer_tools.marker_to_current", text="Marker To Frame", icon="MARKER_HLT")
        
        #End of SEQUENCER_TOOLS_PT_custom_panel11

classes = (
    SEQUENCER_TOOLS_props,
    
    SEQUENCER_TOOLS_OT_move_strips,
    SEQUENCER_TOOLS_OT_strip_ops,
    SEQUENCER_TOOLS_OT_marker_ops,
    SEQUENCER_TOOLS_OT_marker_to_current,
    SEQUENCER_TOOLS_OT_timeline_add,

    SEQUENCER_TOOLS_PT_custom_panel1,
)

