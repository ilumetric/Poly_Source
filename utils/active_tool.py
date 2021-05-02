import bpy
from bl_ui.space_toolsystem_common import activate_by_id as activate_tool #FIXME проверить 
from bl_ui.space_toolsystem_toolbar import VIEW3D_PT_tools_active as view3d_tools



def active_tool():
    return view3d_tools.tool_active_from_context(bpy.context)












classes = []


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)