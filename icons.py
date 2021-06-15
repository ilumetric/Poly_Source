import bpy
import os
import bpy.utils.previews



preview_collections = {}


def register():
    global preview_collections
    # --- ICON
    pcoll = bpy.utils.previews.new()
    
    


    # --- GENERAL
    my_icons_dir = os.path.join(os.path.dirname(__file__), "icons") # если нужна диреектория "./toolkit/icons"

    # --- Links
    pcoll.load("update_icon", os.path.join(my_icons_dir, "update.png"), 'IMAGE')
    pcoll.load("market_icon", os.path.join(my_icons_dir, "market.png"), 'IMAGE')
    pcoll.load("gumroad_icon", os.path.join(my_icons_dir, "gumroad.png"), 'IMAGE')
    pcoll.load("artstation_icon", os.path.join(my_icons_dir, "artstation.png"), 'IMAGE')
    pcoll.load("discord_icon", os.path.join(my_icons_dir, "discord.png"), 'IMAGE')


    # --- General
    pcoll.load("ngon_icon", os.path.join(my_icons_dir, "ngon.png"), 'IMAGE')
    pcoll.load("quad_icon", os.path.join(my_icons_dir, "quad.png"), 'IMAGE')
    pcoll.load("tris_icon", os.path.join(my_icons_dir, "triangle.png"), 'IMAGE')

    pcoll.load("grid_icon", os.path.join(my_icons_dir, "grid.png"), 'IMAGE')
    pcoll.load("box_icon", os.path.join(my_icons_dir, "box.png"), 'IMAGE')
    pcoll.load("draw_icon", os.path.join(my_icons_dir, "draw.png"), 'IMAGE')
    pcoll.load("calculate_icon", os.path.join(my_icons_dir, "calculate.png"), 'IMAGE')
    pcoll.load("check_icon", os.path.join(my_icons_dir, "check.png"), 'IMAGE')

  
    # --- Add Objects
    pcoll.load("addOb", os.path.join(my_icons_dir, "add_ob.png"), 'IMAGE')
    pcoll.load("tube", os.path.join(my_icons_dir, "tube.png"), 'IMAGE')
    pcoll.load("cylinder", os.path.join(my_icons_dir, "cylinder.png"), 'IMAGE')
    pcoll.load("empty_mesh", os.path.join(my_icons_dir, "empty_mesh.png"), 'IMAGE')
    pcoll.load("cube", os.path.join(my_icons_dir, "cube.png"), 'IMAGE')


    # --- TOOL KIT
    pcoll.load("x_icon", os.path.join(my_icons_dir, "x.png"), 'IMAGE')
    pcoll.load("y_icon", os.path.join(my_icons_dir, "y.png"), 'IMAGE')
    pcoll.load("z_icon", os.path.join(my_icons_dir, "z.png"), 'IMAGE')

    pcoll.load("reset_icon", os.path.join(my_icons_dir, "reset.png"), 'IMAGE')
    pcoll.load("toselect_icon", os.path.join(my_icons_dir, "select.png"), 'IMAGE')
    #pcoll.load("resetrot_icon", os.path.join(my_icons_dir, "reset_rotation.png"), 'IMAGE')
    pcoll.load("fix_icon", os.path.join(my_icons_dir, "fix.png"), 'IMAGE')

    
    #old
    pcoll.load("tool", os.path.join(my_icons_dir, "tool.png"), 'IMAGE')
    pcoll.load("bevelSub", os.path.join(my_icons_dir, "bevelSub.png"), 'IMAGE')
    pcoll.load("180", os.path.join(my_icons_dir, "180.png"), 'IMAGE')
    pcoll.load("bevelW", os.path.join(my_icons_dir, "bevelW.png"), 'IMAGE')
    pcoll.load("creaseW", os.path.join(my_icons_dir, "creaseW.png"), 'IMAGE')

    preview_collections["main"] = pcoll

   
    
  







def unregister():
    global preview_collections
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()