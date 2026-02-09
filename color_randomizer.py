import bpy
from bpy.types import Operator, PropertyGroup
from bpy.props import IntProperty, PointerProperty
from .utils.utils import get_addon_prefs


def set_name(self, context, obj):
    name = obj.name
    props = obj.random_color

    if props.color_idx == 0:
        props.color_idx += 1
    else:
        count = props.color_idx - 1
        prefix = "CR" + str(count) + "_"
        lenP = len(prefix)
        name = name[lenP:]

    obj.name = "CR" + str(props.color_idx) + "_" + name

    props.color_idx += 1


def del_prefix(self, context, obj):
    name = obj.name
    props = obj.random_color

    count = props.color_idx - 1
    prefix = "CR" + str(count) + "_"
    lenP = len(prefix)
    obj.name = name[lenP:]

    props.color_idx = 0


class PS_OT_set_color(Operator):
    """Add incremental color randomizer prefix to selected objects"""
    bl_idname = 'object.ps_set_color'
    bl_label = 'Object Color'
    bl_description = 'Add color randomizer prefix to selected objects for viewport color variation'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def execute(self, context):
        objects = context.selected_objects
        for obj in objects:
            props = obj.random_color
            if len(obj.name) >= 54 and props.color_idx == 0:
                self.report({'WARNING'}, f'The object name "{obj.name}" is too long! You need to reduce the name to at least 53 characters.')
                continue

            set_name(self, context, obj)
        return {'FINISHED'}


class PS_OT_del_prefix(Operator):
    """Remove color randomizer prefix from selected objects"""
    bl_idname = 'object.ps_del_prefix'
    bl_label = 'Delete Prefixes'
    bl_description = 'Remove color randomizer prefix from selected objects'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        objs = context.selected_objects
        return any(obj.random_color.color_idx != 0 for obj in objs)

    def execute(self, context):
        objects = context.selected_objects
        for obj in objects:
            props = obj.random_color
            if props.color_idx != 0:
                del_prefix(self, context, obj)
        return {'FINISHED'}


def button_in_header(self, context):
    props = get_addon_prefs()
    if props and getattr(props, 'b_color_randomizer', False):
        layout = self.layout
        row = layout.row(align=True)
        row.scale_x = 1.3
        row.operator('object.ps_set_color', text='', icon='COLOR')
        row.scale_x = 1.0
        row.operator('object.ps_del_prefix', text='', icon='X')


class PS_PG_color_store(PropertyGroup):
    """Per-object storage for color randomizer prefix index"""
    color_idx: IntProperty(
        name="Color Index",
        description="Current color randomizer prefix index for this object",
        default=0, max=999,
    )


classes = [
    PS_OT_set_color,
    PS_OT_del_prefix,
    PS_PG_color_store,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.random_color = PointerProperty(type=PS_PG_color_store)
    bpy.types.VIEW3D_HT_header.append(button_in_header)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Object.random_color
    bpy.types.VIEW3D_HT_header.remove(button_in_header)
