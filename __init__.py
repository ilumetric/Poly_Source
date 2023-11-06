bl_info = {
    'name': 'Poly Source',
    "author": "Max Derksen, Oxicid",
    'version': (3, 1, 0),
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
    active_tool,
    fill_mesh,
    op,
    cylinder_optimizer,
)


# --- Tool Kit
from .add_object import (
    cube,
    cylinder,
)

from .toolkit import (
    tk_panel,
    tk_scripts,
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

    active_tool.register()
    fill_mesh.register()
    op.register()
    cylinder_optimizer.register()


    # --- Tool Kit
    cube.register()
    cylinder.register()

    tk_panel.register()
    tk_scripts.register()


    # --- Clean Up
    long_tris.register()


def unregister():
    icons.unregister()
    preferences.unregister()

    ui.unregister()
    check.unregister()
    polycount.unregister()
    envira_grid.unregister()

    active_tool.unregister()
    fill_mesh.unregister()
    op.unregister()
    cylinder_optimizer.unregister()


    # --- Tool Kit
    cube.unregister()
    cylinder.unregister()

    tk_panel.unregister()
    tk_scripts.unregister()


    # --- Clean Up
    long_tris.unregister()