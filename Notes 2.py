
## Purpose of these Notes is to basically make a way for removing gaps in selected sequences, sequences overlapping each other are considered "together" and won't count as gaps.
## The only gaps counted are gaps where there are no sequences at all, ex. where you deleted a part of a sequence

## Active Strips
bpy.context.scene.sequence_editor.active_strip
bpy.data.scenes['Scene'].sequence_editor.sequences_all["MetaStrip.018"]

## All Sequences
bpy.context.scene.sequence_editor.sequences
bpy.data.scenes['Scene']...sequences

## Iterate through them
bpy.context.scene.sequence_editor.sequences[0]
bpy.data.scenes['Scene'].sequence_editor.sequences_all["MetaStrip.007"]

## Is selected?
bpy.context.scene.sequence_editor.sequences[0].select
True

## How to select all selected strips, since it isn't exposed in Blender's python
selected_strips = [i for i in bpy.context.scene.sequence_editor.sequences if i.select]

## Start
bpy.context.scene.sequence_editor.active_strip.frame_final_start
478

## End
bpy.context.scene.sequence_editor.active_strip.frame_final_end
603