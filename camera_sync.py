import bpy
from bpy.types import Operator
from .utils.utils import get_addon_prefs


class PS_OT_lock_camera_transforms(Operator):
    """Toggle transform locks on the active camera"""
    bl_idname = 'object.ps_lock_camera_transforms'
    bl_label = 'Lock Camera Transforms'
    bl_description = 'Toggle location, rotation, and scale locks on the active camera'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj is not None and obj.type == 'CAMERA'

    def execute(self, context):
        selected_obj = context.object
        any_locked = any(selected_obj.lock_location) or any(selected_obj.lock_rotation) or any(selected_obj.lock_scale)
        new_lock_status = not any_locked
        for i in range(3):
            selected_obj.lock_location[i] = new_lock_status
            selected_obj.lock_rotation[i] = new_lock_status
            selected_obj.lock_scale[i] = new_lock_status
        status = "locked" if new_lock_status else "unlocked"
        self.report({'INFO'}, f"Transforms {status} for the selected camera.")
        return {'FINISHED'}


def button_in_header(self, context):
    props = get_addon_prefs()
    if props and getattr(props, 'b_camera_sync', False):
        active_object = context.object
        layout = self.layout
        row = layout.row(align=True)
        row.enabled = active_object is not None and active_object.type == 'CAMERA'
        is_camera_view = context.space_data.region_3d.view_perspective == 'CAMERA'

        if bpy.app.version >= (4, 2, 0):
            row.operator("view3d.view_camera", text="", icon='VIEW_CAMERA' if is_camera_view else 'VIEW_CAMERA_UNSELECTED')
            row.prop(context.space_data, "lock_camera", text="", icon='VIEW_LOCKED' if context.space_data.lock_camera else 'VIEW_UNLOCKED')
        else:
            row.operator("view3d.view_camera", text="", icon='VIEW_CAMERA' if is_camera_view else 'OUTLINER_DATA_CAMERA')
            row.prop(context.space_data, "lock_camera", text="", icon='KEYINGSET')
        if active_object is not None:
            any_locked = any(active_object.lock_location) or any(active_object.lock_rotation) or any(active_object.lock_scale)
        else:
            any_locked = False
        row.operator("object.ps_lock_camera_transforms", text="", icon='LOCKED' if any_locked else 'UNLOCKED')


classes = [
    PS_OT_lock_camera_transforms,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_HT_header.append(button_in_header)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bpy.types.VIEW3D_HT_header.remove(button_in_header)
