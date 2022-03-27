bl_info = {
    'name': 'Poly Source',
    "author": "Max Derksen",
    'version': (2, 1, 0),
    'blender': (3, 0, 0),
    'location': 'VIEW 3D > Top Bar',
    'category': 'Mesh',
}



from . import (
    preferences,
    retopology,
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
    empty_mesh,
)

from .toolkit import (
    tk_modifiers,
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
    retopology.register()
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
    empty_mesh.register()

    tk_modifiers.register()
    tk_panel.register()
    tk_scripts.register()


    # --- Clean Up
    long_tris.register()


def unregister():
    icons.unregister()
    preferences.unregister()

    ui.unregister()
    retopology.unregister()
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
    empty_mesh.unregister()

    tk_modifiers.unregister()
    tk_panel.unregister()
    tk_scripts.unregister()


    # --- Clean Up
    long_tris.unregister()