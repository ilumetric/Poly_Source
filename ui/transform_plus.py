import bpy
import bmesh
from bpy.types import Panel, Operator
from bpy.props import EnumProperty
from ..utils.utils import get_addon_prefs


# --- маппинг осей к индексам ---
_AXIS_MAP_3 = {'X': 0, 'Y': 1, 'Z': 2}
_AXIS_MAP_4 = {'W': 0, 'X': 1, 'Y': 2, 'Z': 3}

# --- маппинг имён атрибутов bmesh ---
_EDGE_ATTR = {
    'BEVEL': 'bevel_weight_edge',
    'CREASE': 'crease_edge',
}
_VERT_ATTR = {
    'BEVEL': 'bevel_weight_vert',
    'CREASE': 'crease_vert',
}


# --- вспомогательные функции ---

def _toggle_bmesh_data(elements, layer):
    """переключает вес выделенных элементов между 0 и 1"""
    selected = [elem for elem in elements if elem.select]
    if not selected:
        return
    # если хоть один выделенный имеет вес > 0 — сбрасываем все, иначе устанавливаем 1
    has_weight = any(elem[layer] > 0.0 for elem in selected)
    new_value = 0.0 if has_weight else 1.0
    for elem in selected:
        elem[layer] = new_value


def _get_or_create_float_layer(bm_layers, attr_name, obj_data):
    """получает или создаёт float-слой bmesh"""
    if attr_name not in obj_data.attributes:
        return bm_layers.float.new(attr_name)
    return bm_layers.float.get(attr_name)


def _draw_transform_row(col, obj, prop_name, prop_index, axis_name,
                        lock_prop, lock_index, transform_type, default_value=0.0):
    """отрисовка строки трансформации с кнопкой сброса и замком"""
    row = col.row(align=True)
    row.prop(obj, prop_name, index=prop_index, text=axis_name)

    # кнопка сброса — показывается только если значение отличается от дефолтного
    current = getattr(obj, prop_name)[prop_index]
    if abs(current - default_value) > 1e-6:
        op = row.operator("object.ps_reset_transform_axis", text="", icon='LOOP_BACK')
        op.transform_type = transform_type
        op.axis = axis_name
    else:
        row.label(icon='BLANK1')

    row.separator(factor=0.2)

    # замок — lock_rotation_w не имеет индекса, остальные prop — массивы
    if lock_index is not None:
        row.prop(obj, lock_prop, index=lock_index, text='', emboss=False)
    else:
        row.prop(obj, lock_prop, text='', emboss=False)


# --- операторы ---

class PS_OT_copy_transform(Operator):
    bl_idname = "object.ps_copy_transform"
    bl_label = "Copy Transform to Clipboard"
    bl_description = "Copy the active object's transform to the clipboard"
    bl_options = {'REGISTER'}

    transform_type: EnumProperty(
        name="Transform Type",
        description="Type of transform to copy",
        items=[
            ('LOCATION', "Location", "Copy location"),
            ('ROTATION', "Rotation", "Copy rotation"),
            ('SCALE', "Scale", "Copy scale"),
        ],
        default='LOCATION',
    )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        obj = context.active_object
        t = self.transform_type

        if t == 'LOCATION':
            values = obj.location[:]
        elif t == 'ROTATION':
            if obj.rotation_mode == 'QUATERNION':
                values = obj.rotation_quaternion[:]
            elif obj.rotation_mode == 'AXIS_ANGLE':
                values = obj.rotation_axis_angle[:]
            else:
                values = obj.rotation_euler[:]
        else:
            values = obj.scale[:]

        transform_str = "({})".format(", ".join(f"{v:.5f}" for v in values))
        context.window_manager.clipboard = transform_str
        self.report({'INFO'}, f"{t.capitalize()} copied: {transform_str}")
        return {'FINISHED'}


class PS_OT_reset_transform_axis(Operator):
    bl_idname = "object.ps_reset_transform_axis"
    bl_label = "Reset Transform Axis"
    bl_description = "Reset a specific axis of the object's transform to its default value"
    bl_options = {'REGISTER', 'UNDO'}

    transform_type: EnumProperty(
        name="Transform Type",
        items=[
            ('LOCATION', "Location", "Reset location axis"),
            ('ROTATION', "Rotation", "Reset rotation axis"),
            ('SCALE', "Scale", "Reset scale axis"),
        ],
        default='LOCATION',
    )

    axis: EnumProperty(
        name="Axis",
        items=[
            ('X', "X", "X axis"),
            ('Y', "Y", "Y axis"),
            ('Z', "Z", "Z axis"),
            ('W', "W", "W axis (quaternion / axis-angle)"),
        ],
        default='X',
    )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        obj = context.active_object
        t = self.transform_type
        axis = self.axis

        if t == 'LOCATION':
            if axis not in _AXIS_MAP_3:
                return {'CANCELLED'}
            obj.location[_AXIS_MAP_3[axis]] = 0.0

        elif t == 'ROTATION':
            if obj.rotation_mode == 'QUATERNION':
                if axis not in _AXIS_MAP_4:
                    return {'CANCELLED'}
                idx = _AXIS_MAP_4[axis]
                obj.rotation_quaternion[idx] = 1.0 if axis == 'W' else 0.0
            elif obj.rotation_mode == 'AXIS_ANGLE':
                if axis not in _AXIS_MAP_4:
                    return {'CANCELLED'}
                obj.rotation_axis_angle[_AXIS_MAP_4[axis]] = 0.0
            else:
                if axis not in _AXIS_MAP_3:
                    return {'CANCELLED'}
                obj.rotation_euler[_AXIS_MAP_3[axis]] = 0.0

        elif t == 'SCALE':
            if axis not in _AXIS_MAP_3:
                return {'CANCELLED'}
            obj.scale[_AXIS_MAP_3[axis]] = 1.0

        self.report({'INFO'}, f"{axis} {t.lower()} reset")
        return {'FINISHED'}


class PS_OT_tp_edge_data(Operator):
    bl_idname = "mesh.ps_tp_edge_data"
    bl_label = "Mark Edge Data"
    bl_description = "Toggle bevel weight or crease for selected edges"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    mode: EnumProperty(
        name='Mode',
        items=[
            ('BEVEL', 'Bevel Weight', ''),
            ('CREASE', 'Crease Weight', ''),
        ],
        default='BEVEL',
    )

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        attr_name = _EDGE_ATTR[self.mode]
        for obj in context.objects_in_mode_unique_data:
            bm = bmesh.from_edit_mesh(obj.data)
            layer = _get_or_create_float_layer(bm.edges.layers, attr_name, obj.data)
            _toggle_bmesh_data(bm.edges, layer)
            bmesh.update_edit_mesh(obj.data)
        return {'FINISHED'}


class PS_OT_tp_vertex_data(Operator):
    bl_idname = "mesh.ps_tp_vertex_data"
    bl_label = "Mark Vertex Data"
    bl_description = "Toggle bevel weight or crease for selected vertices"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    mode: EnumProperty(
        name='Mode',
        items=[
            ('BEVEL', 'Bevel Weight', ''),
            ('CREASE', 'Crease Weight', ''),
        ],
        default='BEVEL',
    )

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        attr_name = _VERT_ATTR[self.mode]
        for obj in context.objects_in_mode_unique_data:
            bm = bmesh.from_edit_mesh(obj.data)
            layer = _get_or_create_float_layer(bm.verts.layers, attr_name, obj.data)
            _toggle_bmesh_data(bm.verts, layer)
            bmesh.update_edit_mesh(obj.data)
        return {'FINISHED'}


# --- панель ---

class PS_PT_transform_plus(Panel):
    """Enhanced transform panel with inline axis reset and clipboard copy"""
    bl_label = "Transform +"
    bl_idname = "PS_PT_transform_plus"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'PS'

    @classmethod
    def poll(cls, context):
        if context.object is None:
            return False
        prefs = get_addon_prefs()
        return prefs is not None #and prefs.b_transform_plus

    def draw(self, context):
        layout = self.layout
        obj = context.object

        if context.mode == 'OBJECT':
            self._draw_object_mode(layout, obj)
        elif context.mode == 'EDIT_MESH':
            self._draw_edit_mode(layout)


        # старый подход TODO удалить
        box = layout.box()
        if context.mode == 'OBJECT':
            box.label(text='Reset Transform')
            box.scale_x = 1.3

            grid = box.grid_flow(columns=2, align=False)
            grid_sub = grid.grid_flow(columns=3, align=True)
            grid_sub.operator('object.ps_reset_location_object', text='X').axis = 'X'
            grid_sub.operator('object.ps_reset_location_object', text='Y').axis = 'Y'
            grid_sub.operator('object.ps_reset_location_object', text='Z').axis = 'Z'
            grid.operator('object.ps_reset_location_object', text='Location').axis = 'ALL'

            grid = box.grid_flow(columns=2, align=False)
            grid_sub = grid.grid_flow(columns=3, align=True)
            grid_sub.operator('object.ps_reset_rotation_object', text='X').axis = 'X'
            grid_sub.operator('object.ps_reset_rotation_object', text='Y').axis = 'Y'
            grid_sub.operator('object.ps_reset_rotation_object', text='Z').axis = 'Z'
            grid.operator('object.ps_reset_rotation_object', text='Rotation').axis = 'ALL'

            grid = box.grid_flow(columns=2, align=False)
            grid_sub = grid.grid_flow(columns=3, align=True)
            grid_sub.operator('object.ps_reset_scale_object', text='X').axis = 'X'
            grid_sub.operator('object.ps_reset_scale_object', text='Y').axis = 'Y'
            grid_sub.operator('object.ps_reset_scale_object', text='Z').axis = 'Z'
            grid.operator('object.ps_reset_scale_object', text='Scale').axis = 'ALL'

            box.operator("object.ps_reset_location_object", text='Reset All').axis = 'ALL_T'

        elif context.mode == 'EDIT_MESH':
            box.label(text='Reset Transform')
            box.scale_x = 1.3

            grid = box.grid_flow(columns=2, align=False)
            grid_sub = grid.grid_flow(columns=3, align=True)
            grid_sub.operator("mesh.ps_reset_vertex_location", text='X').axis = 'X'
            grid_sub.operator("mesh.ps_reset_vertex_location", text='Y').axis = 'Y'
            grid_sub.operator("mesh.ps_reset_vertex_location", text='Z').axis = 'Z'
            grid.operator("mesh.ps_reset_vertex_location", text='Location').axis = 'ALL'

    # --- объектный режим ---

    def _draw_object_mode(self, layout, obj):
        """отрисовка панели в объектном режиме"""
        # --- location ---
        col = layout.column()
        row = col.row()
        op = row.operator("object.ps_copy_transform", text="", icon='EMPTY_ARROWS', emboss=False)
        op.transform_type = 'LOCATION'
        row.label(text='Location:')

        col = col.column(align=True)
        for i, axis in enumerate('XYZ'):
            _draw_transform_row(col, obj, "location", i, axis,
                                "lock_location", i, 'LOCATION', 0.0)

        # --- rotation ---
        col = layout.column()
        row = col.row()
        op = row.operator("object.ps_copy_transform", text="", icon='ORIENTATION_GIMBAL', emboss=False)
        op.transform_type = 'ROTATION'
        row.label(text='Rotation:')
        sub_row = row.row()
        sub_row.prop(obj, "rotation_mode", text="")

        col = col.column(align=True)
        self._draw_rotation_rows(col, obj)

        # --- scale ---
        col = layout.column()
        row = col.row()
        op = row.operator("object.ps_copy_transform", text="", icon='FULLSCREEN_ENTER', emboss=False)
        op.transform_type = 'SCALE'
        row.label(text='Scale:')

        col = col.column(align=True)
        for i, axis in enumerate('XYZ'):
            _draw_transform_row(col, obj, "scale", i, axis,
                                "lock_scale", i, 'SCALE', 1.0)

    def _draw_rotation_rows(self, col, obj):
        """отрисовка строк ротации с учётом режима вращения"""
        if obj.rotation_mode == 'QUATERNION':
            # w — дефолт 1.0, отдельный lock_rotation_w
            _draw_transform_row(col, obj, "rotation_quaternion", 0, 'W',
                                "lock_rotation_w", None, 'ROTATION', 1.0)
            for i, axis in enumerate('XYZ'):
                _draw_transform_row(col, obj, "rotation_quaternion", i + 1, axis,
                                    "lock_rotation", i, 'ROTATION', 0.0)

        elif obj.rotation_mode == 'AXIS_ANGLE':
            # w (угол) — дефолт 0.0, отдельный lock_rotation_w
            _draw_transform_row(col, obj, "rotation_axis_angle", 0, 'W',
                                "lock_rotation_w", None, 'ROTATION', 0.0)
            for i, axis in enumerate('XYZ'):
                _draw_transform_row(col, obj, "rotation_axis_angle", i + 1, axis,
                                    "lock_rotation", i, 'ROTATION', 0.0)

        else:  # EULER
            for i, axis in enumerate('XYZ'):
                _draw_transform_row(col, obj, "rotation_euler", i, axis,
                                    "lock_rotation", i, 'ROTATION', 0.0)

    # --- режим редактирования ---

    def _draw_edit_mode(self, layout):
        """отрисовка панели в режиме редактирования"""
        layout.label(text="Vertex Data:")
        layout.operator("mesh.ps_tp_vertex_data", text="Vertex Bevel", icon='UV_SYNC_SELECT').mode = 'BEVEL'
        layout.operator("mesh.ps_tp_vertex_data", text="Vertex Crease", icon='UV_SYNC_SELECT').mode = 'CREASE'

        layout.label(text="Edge Data:")
        layout.operator("mesh.ps_tp_edge_data", text="Edge Bevel", icon='UV_SYNC_SELECT').mode = 'BEVEL'
        layout.operator("mesh.ps_tp_edge_data", text="Edge Crease", icon='UV_SYNC_SELECT').mode = 'CREASE'


transform_plus_classes = [
    PS_OT_copy_transform,
    PS_OT_reset_transform_axis,
    PS_OT_tp_edge_data,
    PS_OT_tp_vertex_data,
    PS_PT_transform_plus,
]
