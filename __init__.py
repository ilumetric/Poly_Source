bl_info = {
    'name': 'Poly Source',
    "author": "Max Derksen",
    'version': (1, 6, 2),
    'blender': (2, 83, 0),
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
)

from .utils import (
    active_tool,
    op,
    cylinder_optimizer,
)



def register():
    preferences.register()
    
    ui.register()
    quad_draw.register()
    check.register()
    polycount.register()
    envira_grid.register()

    active_tool.register()
    op.register()
    cylinder_optimizer.register()



def unregister():
    preferences.unregister()

    ui.unregister()
    quad_draw.unregister()
    check.unregister()
    polycount.unregister()
    envira_grid.unregister()

    active_tool.unregister()
    op.unregister()
    cylinder_optimizer.unregister()