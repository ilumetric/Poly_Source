import os
import bpy
import bpy.utils.previews


preview_collections = {}


def register():
    global preview_collections
    pcoll = bpy.utils.previews.new()

    my_icons_dir = os.path.join(os.path.dirname(__file__), "icons")

    # --- общие
    pcoll.load("ngon_icon", os.path.join(my_icons_dir, "ngon.png"), 'IMAGE')
    pcoll.load("quad_icon", os.path.join(my_icons_dir, "quad.png"), 'IMAGE')
    pcoll.load("tris_icon", os.path.join(my_icons_dir, "triangle.png"), 'IMAGE')
    pcoll.load("check_icon", os.path.join(my_icons_dir, "check.png"), 'IMAGE')

    # --- булевые операции
    pcoll.load("bool_diff", os.path.join(my_icons_dir, "bool_diff.png"), 'IMAGE')
    pcoll.load("bool_union", os.path.join(my_icons_dir, "bool_union.png"), 'IMAGE')
    pcoll.load("bool_intersect", os.path.join(my_icons_dir, "bool_intersect.png"), 'IMAGE')
    pcoll.load("bool_slice", os.path.join(my_icons_dir, "bool_slice.png"), 'IMAGE')

    preview_collections["main"] = pcoll


def unregister():
    global preview_collections
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
