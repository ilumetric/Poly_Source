import bpy

from .headers import (
    header_panel,
    view_header_left_panel,
    view_header_right_panel,
    tool_panel,
)
from .panels import panels_classes
from .menus import (
    menus_classes,
    rmb_menu,
    preset_increment_angle,
    outliner_header_button,
)
from .transform_plus import transform_plus_classes


classes = panels_classes + menus_classes + transform_plus_classes

# оригинальная функция draw тулхедера для восстановления при unregister
_original_tool_header_draw = None


def register():
    global _original_tool_header_draw

    for cls in classes:
        bpy.utils.register_class(cls)

    # сохраняем оригинальный draw и заменяем своим
    _original_tool_header_draw = bpy.types.VIEW3D_HT_tool_header.draw
    bpy.types.VIEW3D_HT_tool_header.draw = tool_panel

    bpy.types.TOPBAR_HT_upper_bar.append(header_panel)
    bpy.types.VIEW3D_MT_editor_menus.append(view_header_left_panel)
    bpy.types.VIEW3D_HT_header.append(view_header_right_panel)
    bpy.types.VIEW3D_MT_editor_menus.append(rmb_menu)
    bpy.types.VIEW3D_MT_object_context_menu.prepend(rmb_menu)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.prepend(rmb_menu)

    bpy.types.OUTLINER_HT_header.append(outliner_header_button)
    bpy.types.VIEW3D_PT_snapping.append(preset_increment_angle)
    bpy.types.IMAGE_PT_snapping.append(preset_increment_angle)


def unregister():
    global _original_tool_header_draw

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    # восстанавливаем оригинальный draw тулхедера
    if _original_tool_header_draw is not None:
        bpy.types.VIEW3D_HT_tool_header.draw = _original_tool_header_draw
        _original_tool_header_draw = None

    bpy.types.TOPBAR_HT_upper_bar.remove(header_panel)
    bpy.types.VIEW3D_MT_editor_menus.remove(view_header_left_panel)
    bpy.types.VIEW3D_HT_header.remove(view_header_right_panel)
    bpy.types.VIEW3D_MT_editor_menus.remove(rmb_menu)
    bpy.types.VIEW3D_MT_object_context_menu.remove(rmb_menu)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.remove(rmb_menu)

    bpy.types.OUTLINER_HT_header.remove(outliner_header_button)
    bpy.types.VIEW3D_PT_snapping.remove(preset_increment_angle)
    bpy.types.IMAGE_PT_snapping.remove(preset_increment_angle)
