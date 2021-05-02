bl_info = {
    'name': 'Poly Source',
    "author": "Max Derksen",
    'version': (1, 6, 1),
    'blender': (2, 83, 0),
    'location': 'VIEW 3D > Top Bar',
    'category': 'Mesh',
}



from . import (
    preferences,
    op,
    quad_draw,
    ui,
    check,
    polycount,
    envira_grid,
)

from .utils import (
    active_tool,
)



def register():
    preferences.register()
    
    op.register()
    ui.register()
    quad_draw.register()
    check.register()
    polycount.register()
    envira_grid.register()

    active_tool.register()




def unregister():
    preferences.unregister()

    op.unregister()
    ui.unregister()
    quad_draw.unregister()
    check.unregister()
    polycount.unregister()
    envira_grid.unregister()

    active_tool.unregister()