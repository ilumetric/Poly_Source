import os
import bpy
import bpy.utils.previews


preview_collections = {}


def register():
    global preview_collections
    pcoll = bpy.utils.previews.new()

    my_icons_dir = os.path.join(os.path.dirname(__file__), "icons")

    # --- ссылки
    pcoll.load("market_icon", os.path.join(my_icons_dir, "market.png"), 'IMAGE')
    pcoll.load("gumroad_icon", os.path.join(my_icons_dir, "gumroad.png"), 'IMAGE')
    pcoll.load("artstation_icon", os.path.join(my_icons_dir, "artstation.png"), 'IMAGE')

    # --- общие
    pcoll.load("ngon_icon", os.path.join(my_icons_dir, "ngon.png"), 'IMAGE')
    pcoll.load("quad_icon", os.path.join(my_icons_dir, "quad.png"), 'IMAGE')
    pcoll.load("tris_icon", os.path.join(my_icons_dir, "triangle.png"), 'IMAGE')
    pcoll.load("grid_icon", os.path.join(my_icons_dir, "grid.png"), 'IMAGE')
    pcoll.load("box_icon", os.path.join(my_icons_dir, "box.png"), 'IMAGE')
    pcoll.load("draw_icon", os.path.join(my_icons_dir, "draw.png"), 'IMAGE')
    pcoll.load("calculate_icon", os.path.join(my_icons_dir, "calculate.png"), 'IMAGE')
    pcoll.load("check_icon", os.path.join(my_icons_dir, "check.png"), 'IMAGE')

    # --- тулкит (оси, сброс)
    pcoll.load("fix_icon", os.path.join(my_icons_dir, "fix.png"), 'IMAGE')

    # --- булевые операции
    pcoll.load("bool_diff", os.path.join(my_icons_dir, "bool_diff.png"), 'IMAGE')
    pcoll.load("bool_union", os.path.join(my_icons_dir, "bool_union.png"), 'IMAGE')
    pcoll.load("bool_intersect", os.path.join(my_icons_dir, "bool_intersect.png"), 'IMAGE')
    pcoll.load("bool_slice", os.path.join(my_icons_dir, "bool_slice.png"), 'IMAGE')

    # --- прочие
    pcoll.load("tool", os.path.join(my_icons_dir, "tool.png"), 'IMAGE')
    pcoll.load("bevelSub", os.path.join(my_icons_dir, "bevelSub.png"), 'IMAGE')
    pcoll.load("180", os.path.join(my_icons_dir, "180.png"), 'IMAGE')
    pcoll.load("bevelW", os.path.join(my_icons_dir, "bevelW.png"), 'IMAGE')
    pcoll.load("creaseW", os.path.join(my_icons_dir, "creaseW.png"), 'IMAGE')
    pcoll.load("seam", os.path.join(my_icons_dir, "seam.png"), 'IMAGE')
    pcoll.load("sharp", os.path.join(my_icons_dir, "sharp.png"), 'IMAGE')

    preview_collections["main"] = pcoll


def unregister():
    global preview_collections
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
