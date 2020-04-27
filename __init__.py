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

import bpy

import ast # For string to dictionary evaluations

#Imports Blender Properties ex. BoolProperty
from bpy.props import *

#from . backup_objects_addon_b2_80_v1_0_1 import classes
from . video_editor_script_v1_0 import (
    SEQUENCER_TOOLS_props,
    
    SEQUENCER_TOOLS_OT_move_strips,
    SEQUENCER_TOOLS_OT_strip_ops,
    SEQUENCER_TOOLS_OT_marker_ops,
    SEQUENCER_TOOLS_OT_marker_to_current,
    SEQUENCER_TOOLS_OT_timeline_add,

    SEQUENCER_TOOLS_PT_custom_panel1,
)

#print("classes"+str(classes) )
#Yes, I had to do this or else it would not register correctly
classes = (
    SEQUENCER_TOOLS_props,
    
    SEQUENCER_TOOLS_OT_move_strips,
    SEQUENCER_TOOLS_OT_strip_ops,
    SEQUENCER_TOOLS_OT_marker_ops,
    SEQUENCER_TOOLS_OT_marker_to_current,
    SEQUENCER_TOOLS_OT_timeline_add,

    SEQUENCER_TOOLS_PT_custom_panel1,
)

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
