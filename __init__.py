bl_info = {
    'name': 'Poly Source',
    "author": "Max Derksen",
    'version': (1, 7, 1),
    'blender': (2, 93, 0),
    'location': 'VIEW 3D > Top Bar',
    'category': 'Mesh',
}



from . import (
    preferences,
    quad_draw,
    ui,
    check,
    polycount,
    envira_grid,
    icons,
)

from .utils import (
    active_tool,
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
    tk_panel,
    tk_scripts,
)


def register():
    icons.register()
    preferences.register()
    
    ui.register()
    quad_draw.register()
    check.register()
    polycount.register()
    envira_grid.register()

    active_tool.register()
    op.register()
    cylinder_optimizer.register()


    # --- Tool Kit
    cube.register()
    cylinder.register()
    empty_mesh.register()

    tk_panel.register()
    tk_scripts.register()


def unregister():
    icons.unregister()
    preferences.unregister()

    ui.unregister()
    quad_draw.unregister()
    check.unregister()
    polycount.unregister()
    envira_grid.unregister()

    active_tool.unregister()
    op.unregister()
    cylinder_optimizer.unregister()


    # --- Tool Kit
    cube.unregister()
    cylinder.unregister()
    empty_mesh.unregister()

    tk_panel.unregister()
    tk_scripts.unregister()