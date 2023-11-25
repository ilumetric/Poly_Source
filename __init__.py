bl_info = {
    'name': 'Poly Source',
    "author": "Max Derksen, Oxicid",
    'version': (4, 0, 6),
    'blender': (4, 0, 0),
    'location': 'VIEW 3D > Top Bar',
    'category': '3D View',
}



from . import (
    preferences,
    ui,
    check,
    polycount,
    envira_grid,
    icons,
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
    preferences.register()
    
    ui.register()
    check.register()
    polycount.register()
    envira_grid.register()

    fill_mesh.register()
    ops.register()
    cylinder_optimizer.register()


    # --- Tool Kit
    cube.register()
    cylinder.register()


    # --- Clean Up
    long_tris.register()


def unregister():
    icons.unregister()
    preferences.unregister()

    ui.unregister()
    check.unregister()
    polycount.unregister()
    envira_grid.unregister()

    fill_mesh.unregister()
    ops.unregister()
    cylinder_optimizer.unregister()


    # --- Tool Kit
    cube.unregister()
    cylinder.unregister()


    # --- Clean Up
    long_tris.unregister()