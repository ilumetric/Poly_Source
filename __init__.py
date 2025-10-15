bl_info = {
    'name': 'Poly Source',
    "author": "Max Derksen",
    'version': (5, 0, 5),
    'blender': (4, 2, 0),
    'location': 'VIEW 3D > Top Bar',
    'category': '3D View',
}



from . import (
    camera_sync,
    preferences,
    ui,
    check,
    color_randomizer,
    polycount,
    envira_grid,
    icons,
    wire_for_selected,
)

from .utils import (
    fill_mesh,
    cylinder_optimizer,
    ops,
)


# --- Tool Kit
from .add_object import (
    cube,
    cylinder,
)


# --- Clean Up
from .clean_up import (
    long_tris,
)



def register():
    icons.register()
    ops.register()
    preferences.register()
    
    camera_sync.register()
    ui.register()
    check.register()
    color_randomizer.register()
    polycount.register()
    envira_grid.register()
    wire_for_selected.register()



    fill_mesh.register()
    
    cylinder_optimizer.register()


    # --- Tool Kit
    cube.register()
    cylinder.register()


    # --- Clean Up
    long_tris.register()


def unregister():
    
    

    camera_sync.unregister()
    ui.unregister()
    check.unregister()
    color_randomizer.unregister()
    polycount.unregister()
    envira_grid.unregister()
    wire_for_selected.unregister()

    fill_mesh.unregister()
    
    cylinder_optimizer.unregister()


    # --- Tool Kit
    cube.unregister()
    cylinder.unregister()


    # --- Clean Up
    long_tris.unregister()

    preferences.unregister()
    ops.unregister()
    icons.unregister()