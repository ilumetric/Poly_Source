import bpy
import bmesh
import random
import string
import mathutils
from bpy.types import Operator
from bpy.props import (
    EnumProperty,
    BoolProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty,
    StringProperty,
)
from mathutils import Vector, Euler
from math import radians, degrees, atan2, pi
from .utils import get_active_3d_view

# =====================================================================
# выбор полигонов
# =====================================================================

class PS_OT_select_polygons(Operator):
    """Select polygons by number of sides"""
    bl_idname = 'mesh.ps_select_polygons'
    bl_label = 'Select Polygons'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'Select faces by vertex count and switch to Edit Mode'

    polygon_type: EnumProperty(
        name='Type',
        description='Face type to select',
        items=[
            ('NGONS', 'N-Gons', 'Select polygons with more than 4 sides', '', 0),
            ('QUADS', 'Quads', 'Select polygons with exactly 4 sides', '', 1),
            ('TRIS', 'Tris', 'Select polygons with exactly 3 sides', '', 2),
        ],
        default='NGONS',
    )

    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return ob is not None and ob.type == 'MESH'

    def execute(self, context):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')

        if self.polygon_type == 'NGONS':
            bpy.ops.mesh.select_face_by_sides(number=4, type='GREATER')
        elif self.polygon_type == 'QUADS':
            bpy.ops.mesh.select_face_by_sides(number=4, type='EQUAL')
        elif self.polygon_type == 'TRIS':
            bpy.ops.mesh.select_face_by_sides(number=3, type='EQUAL')

        return {'FINISHED'}


# =====================================================================
# утилиты для объектов
# =====================================================================

class PS_OT_random_name(Operator):
    """Set random name for selected objects"""
    bl_idname = 'object.ps_random_name'
    bl_label = 'Set Random Name'
    bl_description = 'Assign a random 11-character name to each selected object'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return ob is not None and ob.type == 'MESH' and context.mode == 'OBJECT'

    def execute(self, context):
        selected_objects = context.selected_objects
        for obj in selected_objects:
            new_name = ''.join(random.choices(string.ascii_letters, k=11))
            obj.name = new_name
        return {'FINISHED'}


# =====================================================================
# очистка
# =====================================================================

class PS_OT_clear_dots(Operator):
    """Remove isolated vertices"""
    bl_idname = "mesh.ps_clear_dots"
    bl_label = "Clear Dots"
    bl_description = "Delete all vertices that have no connected edges"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        v_count = 0
        for obj in context.selected_objects:
            me = obj.data
            bm = bmesh.from_edit_mesh(me)

            v_dots = [v for v in bm.verts if len(v.link_edges) < 1]
            v_count += len(v_dots)

            bmesh.ops.delete(bm, geom=v_dots, context='VERTS')
            bmesh.update_edit_mesh(me)

        self.report({'INFO'}, "Clear Dots - " + str(v_count))
        return {'FINISHED'}


class PS_OT_remove_vertex_non_manifold(Operator):
    """Remove vertices not connected to any face"""
    bl_idname = "mesh.ps_remove_vertex_non_manifold"
    bl_label = "Remove Non Manifold Vertex"
    bl_description = "Delete vertices that are not connected to any polygon"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        v_count = 0
        for obj in context.selected_objects:
            me = obj.data
            bm = bmesh.from_edit_mesh(me)

            v_dots = [v for v in bm.verts if len(v.link_faces) < 1]
            v_count += len(v_dots)

            bmesh.ops.delete(bm, geom=v_dots, context='VERTS')
            bmesh.update_edit_mesh(me)

        self.report({'INFO'}, "Removed Vertices - " + str(v_count))
        return {'FINISHED'}


class PS_OT_del_long_faces(Operator):
    """Dissolve vertices based on edge angle threshold"""
    bl_idname = "mesh.ps_del_long_faces"
    bl_label = "Delete Long Faces"
    bl_description = "Dissolve vertices where adjacent edges form angles exceeding the specified threshold"
    bl_options = {'REGISTER', 'UNDO'}

    angle: FloatProperty(
        name='Angle',
        description='Angle threshold in degrees for vertex dissolution',
        default=168.0,
    )
    use_face_split: BoolProperty(
        name='Use Face Split',
        description='Split non-planar faces when dissolving vertices',
        default=False,
    )
    use_boundary_tear: BoolProperty(
        name='Use Boundary Tear',
        description='Allow splitting along boundary edges during dissolution',
        default=False,
    )
    selected: BoolProperty(
        name='Selected Faces',
        description='Only process vertices belonging to selected faces',
        default=False,
    )
    logics: EnumProperty(
        name='Logics',
        description='Comparison operator for the angle threshold',
        items=[
            ("GREATER_THAN", "Greater Than", "Dissolve when angle is greater than threshold"),
            ("NOT_EQUAL_TO", "Not Equal To", "Dissolve when angle is not equal to threshold"),
            ("EQUAL_TO", "Equal To", "Dissolve when angle is equal to threshold"),
            ("LESS_THAN", "Less Than", "Dissolve when angle is less than threshold"),
        ],
        default="GREATER_THAN",
    )

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        v_count = 0
        up = Vector((0, 0, 1))

        def edge_angle(e1, e2, face_normal):
            """вычисляет угол между двумя рёбрами, имеющими общую вершину"""
            b = set(e1.verts).intersection(e2.verts).pop()
            a = e1.other_vert(b).co - b.co
            c = e2.other_vert(b).co - b.co
            a.negate()
            axis = a.cross(c).normalized()
            if axis.length < 1e-5:
                return pi

            if axis.dot(face_normal) < 0:
                axis.negate()
            m = axis.rotation_difference(up).to_matrix().to_4x4()

            a = (m @ a).xy.normalized()
            c = (m @ c).xy.normalized()
            return pi - atan2(a.cross(c), a.dot(c))

        def check_angle(angle_val):
            """проверяет угол по выбранной логике"""
            if self.logics == 'GREATER_THAN':
                return degrees(angle_val) > self.angle
            elif self.logics == 'NOT_EQUAL_TO':
                return degrees(angle_val) != self.angle
            elif self.logics == 'EQUAL_TO':
                return degrees(angle_val) == self.angle
            elif self.logics == 'LESS_THAN':
                return degrees(angle_val) < self.angle
            return False

        for obj in context.selected_objects:
            me = obj.data
            bm = bmesh.from_edit_mesh(me)
            bm.verts.ensure_lookup_table()

            v_dots = []

            if self.selected:
                target_faces = [f for f in bm.faces if f.select]
            else:
                target_faces = list(bm.faces)

            for f in target_faces:
                edges = list(f.edges)
                edges.append(f.edges[0])

                for e1, e2 in zip(edges, edges[1:]):
                    angle_val = edge_angle(e1, e2, f.normal)

                    # находим общую вершину двух рёбер
                    e1_v0 = e1.verts[0]
                    e1_v1 = e1.verts[1]
                    e2_v0 = e2.verts[0]
                    e2_v1 = e2.verts[1]

                    if e1_v0 == e2_v0 or e1_v0 == e2_v1:
                        v = e1_v0
                    elif e1_v1 == e2_v0 or e1_v1 == e2_v1:
                        v = e1_v1
                    else:
                        continue

                    if check_angle(angle_val):
                        v_dots.append(v)
                        v_count += 1

            # удаляем дубликаты
            v_dots = list(set(v_dots))

            if v_dots:
                bmesh.ops.dissolve_verts(bm, verts=v_dots, use_face_split=self.use_face_split, use_boundary_tear=self.use_boundary_tear)
                bmesh.update_edit_mesh(me)

        self.report({'INFO'}, "Dissolved Vertices - " + str(v_count))
        return {'FINISHED'}


# =====================================================================
# очистка материалов и данных
# =====================================================================

class PS_OT_clear_materials(Operator):
    """Remove all materials from selected objects"""
    bl_idname = 'object.ps_clear_materials'
    bl_label = 'Clear Materials'
    bl_description = 'Remove all material slots from selected objects'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        for obj in context.selected_objects:
            obj.data.materials.clear()
        return {'FINISHED'}


class PS_OT_clear_data(Operator):
    """Remove extra data from selected objects"""
    bl_idname = 'object.ps_clear_data'
    bl_label = 'Clear Data'
    bl_description = 'Remove vertex groups, shape keys, color attributes, and custom attributes from selected objects'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        for obj in context.selected_objects:
            if obj.type != 'MESH':
                continue

            # очистка групп вершин
            obj.vertex_groups.clear()

            # очистка shape keys
            if obj.data.shape_keys is not None:
                obj.shape_key_clear()

            # очистка color attributes (удаляем с конца, чтобы индексы не смещались)
            while len(obj.data.color_attributes) > 0:
                obj.data.color_attributes.remove(obj.data.color_attributes[0])

            # очистка кастомных атрибутов (некоторые могут быть защищены)
            removable = [at for at in obj.data.attributes if not at.is_internal]
            for at in reversed(removable):
                try:
                    obj.data.attributes.remove(at)
                except RuntimeError:
                    pass

        return {'FINISHED'}


# =====================================================================
# сброс трансформаций (object mode)
# =====================================================================

class PS_OT_reset_location_object(Operator):
    """Reset object location by axis"""
    bl_idname = "object.ps_reset_location_object"
    bl_label = "Reset Location"
    bl_description = "Reset location of selected objects per axis, or align to the 3D cursor"
    bl_options = {'REGISTER', 'UNDO'}

    axis: EnumProperty(
        name='Axis',
        description='Axis to reset',
        items=[
            ('X', 'X Axis', 'Reset X location', '', 0),
            ('Y', 'Y Axis', 'Reset Y location', '', 1),
            ('Z', 'Z Axis', 'Reset Z location', '', 2),
            ('ALL', 'All Axis', 'Reset location on all axes', '', 3),
            ('ALL_T', 'All Transform', 'Reset location, rotation, and scale', '', 4),
        ],
        default='ALL',
    )

    cursor: BoolProperty(
        name="Relative 3D Cursor",
        description="Align to the 3D cursor position instead of the world origin",
        default=False,
    )

    def execute(self, context):
        cursor = context.scene.cursor
        cur_l = cursor.location
        cur_e = cursor.rotation_euler

        for ob in context.selected_objects:
            if self.axis == 'X':
                ob.location.x = cur_l.x if self.cursor else 0.0
            elif self.axis == 'Y':
                ob.location.y = cur_l.y if self.cursor else 0.0
            elif self.axis == 'Z':
                ob.location.z = cur_l.z if self.cursor else 0.0
            elif self.axis == 'ALL':
                ob.location = cur_l.copy() if self.cursor else Vector()
            elif self.axis == 'ALL_T':
                ob.location = cur_l.copy() if self.cursor else Vector()
                ob.rotation_euler = cur_e.copy()
                ob.scale = Vector((1.0, 1.0, 1.0))

        return {'FINISHED'}


class PS_OT_reset_rotation_object(Operator):
    """Reset object rotation by axis"""
    bl_idname = 'object.ps_reset_rotation_object'
    bl_label = 'Reset Rotation'
    bl_description = "Reset rotation of selected objects per axis, or align to the 3D cursor"
    bl_options = {'REGISTER', 'UNDO'}

    axis: EnumProperty(
        name='Axis',
        description='Axis to reset',
        items=[
            ('X', 'X Axis', 'Reset X rotation', '', 0),
            ('Y', 'Y Axis', 'Reset Y rotation', '', 1),
            ('Z', 'Z Axis', 'Reset Z rotation', '', 2),
            ('ALL', 'All Axis', 'Reset rotation on all axes', '', 3),
        ],
        default='X',
    )

    cursor: BoolProperty(
        name="Relative 3D Cursor",
        description="Align to the 3D cursor orientation instead of zeroing out",
        default=False,
    )

    def execute(self, context):
        cursor_rot = context.scene.cursor.rotation_euler
        for ob in context.selected_objects:
            if self.axis == 'X':
                ob.rotation_euler[0] = cursor_rot[0] if self.cursor else 0.0
            elif self.axis == 'Y':
                ob.rotation_euler[1] = cursor_rot[1] if self.cursor else 0.0
            elif self.axis == 'Z':
                ob.rotation_euler[2] = cursor_rot[2] if self.cursor else 0.0
            elif self.axis == 'ALL':
                ob.rotation_euler = cursor_rot.copy() if self.cursor else Euler()

        return {'FINISHED'}


class PS_OT_reset_scale_object(Operator):
    """Reset object scale by axis"""
    bl_idname = 'object.ps_reset_scale_object'
    bl_label = 'Reset Scale'
    bl_description = "Reset scale of selected objects per axis to 1.0"
    bl_options = {'REGISTER', 'UNDO'}

    axis: EnumProperty(
        name='Axis',
        description='Axis to reset',
        items=[
            ('X', 'X Axis', 'Reset X scale to 1.0', '', 0),
            ('Y', 'Y Axis', 'Reset Y scale to 1.0', '', 1),
            ('Z', 'Z Axis', 'Reset Z scale to 1.0', '', 2),
            ('ALL', 'All Axis', 'Reset scale on all axes to 1.0', '', 3),
        ],
        default='X',
    )

    def execute(self, context):
        for ob in context.selected_objects:
            if self.axis == 'X':
                ob.scale[0] = 1.0
            elif self.axis == 'Y':
                ob.scale[1] = 1.0
            elif self.axis == 'Z':
                ob.scale[2] = 1.0
            elif self.axis == 'ALL':
                ob.scale = Vector((1.0, 1.0, 1.0))

        return {'FINISHED'}


# =====================================================================
# сброс трансформаций вершин (edit mode)
# =====================================================================

class PS_OT_reset_vertex_location(Operator):
    """Reset vertex location by axis"""
    bl_idname = 'mesh.ps_reset_vertex_location'
    bl_label = 'Reset Vertex Location'
    bl_description = "Move selected vertices to the object origin, 3D cursor, or world origin per axis"
    bl_options = {'REGISTER', 'UNDO'}

    axis: EnumProperty(
        name='Axis',
        description='Axis to reset',
        items=[
            ('X', 'X Axis', 'Reset vertex X position', '', 0),
            ('Y', 'Y Axis', 'Reset vertex Y position', '', 1),
            ('Z', 'Z Axis', 'Reset vertex Z position', '', 2),
            ('ALL', 'All Axis', 'Reset vertex position on all axes', '', 3),
        ],
        default='ALL',
    )

    pos: EnumProperty(
        name='Position',
        description='Target position for vertex reset',
        items=[
            ('OBJECT', 'Object', 'Reset relative to the object origin', '', 0),
            ('CURSOR', '3D Cursor', 'Reset to the 3D cursor position', '', 1),
            ('WORLD', 'World', 'Reset to the world origin', '', 2),
        ],
        default='OBJECT',
    )

    vi: BoolProperty(name='Vertex Individual', description='Move each vertex independently instead of preserving relative offsets', default=True)

    def execute(self, context):
        uniques = context.objects_in_mode_unique_data

        # получаем bmesh для каждого объекта
        bms = {}
        for ob in uniques:
            bms[ob] = bmesh.from_edit_mesh(ob.data)

        # вычисляем центр выделенных вершин
        verts = []
        for ob in uniques:
            verts.extend([v.co for v in bms[ob].verts if v.select])

        if len(verts) == 0:
            return {'CANCELLED'}

        center = sum(verts, Vector()) / len(verts)

        # смещение от центра для каждой вершины
        offsets = {}
        for ob in uniques:
            for v in bms[ob].verts:
                offsets[v] = center - v.co

        cursor = context.scene.cursor.location
        origin = Vector((0.0, 0.0, 0.0))

        for ob in uniques:
            inv_matrix = ob.matrix_world.inverted()
            for v in bms[ob].verts:
                if not v.select:
                    continue

                # целевая позиция в пространстве объекта
                if self.pos == 'CURSOR':
                    target = inv_matrix @ cursor
                elif self.pos == 'WORLD':
                    target = inv_matrix @ origin
                else:
                    target = origin

                offset = offsets[v] if not self.vi else Vector()

                if self.axis == 'X':
                    v.co.x = target[0] - offset[0]
                elif self.axis == 'Y':
                    v.co.y = target[1] - offset[1]
                elif self.axis == 'Z':
                    v.co.z = target[2] - offset[2]
                elif self.axis == 'ALL':
                    v.co = target - offset

            bmesh.update_edit_mesh(ob.data)

        return {'FINISHED'}


# =====================================================================
# передача трансформаций
# =====================================================================

class PS_OT_transfer_transform(Operator):
    """Transfer transformation from active to selected objects"""
    bl_idname = 'object.ps_transfer_transform'
    bl_label = 'Transfer Transform Data'
    bl_description = 'Copy location, rotation, and/or scale from the active object to all selected objects'
    bl_options = {'REGISTER', 'UNDO'}

    loc: BoolProperty(name='Location', description='Transfer location data', default=True)
    rot: BoolProperty(name='Rotation', description='Transfer rotation data', default=True)
    sca: BoolProperty(name='Scale', description='Transfer scale data', default=False)

    _copy_loc = None
    _copy_rot = None
    _copy_sca = None

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and context.active_object is not None

    def execute(self, context):
        for ob in context.selected_objects:
            if self.loc:
                ob.location = self._copy_loc
            if self.rot:
                ob.rotation_euler = self._copy_rot
            if self.sca:
                ob.scale = self._copy_sca
        return {'FINISHED'}

    def invoke(self, context, event):
        act = context.active_object
        self._copy_loc = act.location.copy()
        self._copy_rot = act.rotation_euler.copy()
        self._copy_sca = act.scale.copy()
        return self.execute(context)


# =====================================================================
# камера
# =====================================================================

class PS_OT_add_camera(Operator):
    """Add camera aligned to current view"""
    bl_idname = "object.ps_add_camera"
    bl_label = "Add Camera"
    bl_description = "Create a new camera and align it to the current 3D viewport view"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.object.camera_add()
        bpy.ops.view3d.camera_to_view()
        context.space_data.lock_camera = True
        return {'FINISHED'}


# =====================================================================
# материалы
# =====================================================================

class PS_OT_add_material(Operator):
    """Add default material to selected objects"""
    bl_idname = 'object.ps_add_material'
    bl_label = 'Add Material'
    bl_description = 'Create and assign a default PS Material to all selected objects'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mat = bpy.data.materials.get('PS Material')
        if mat is None:
            mat = bpy.data.materials.new(name='PS Material')

        for obj in context.selected_objects:
            obj.data.materials.append(mat)

        return {'FINISHED'}


# =====================================================================
# UE материал
# =====================================================================

class PS_OT_unreal_material(Operator):
    """Create Unreal Engine-style material with PBR textures"""
    bl_idname = 'object.ps_unreal_material'
    bl_label = "UE Material"
    bl_description = "Create an Unreal Engine-style PBR material from texture maps and apply it to selected objects"
    bl_options = {'REGISTER', 'UNDO'}

    base_color_texture: StringProperty(
        name="Base Color Texture",
        description="Path to Base Color texture",
        default="",
        subtype='FILE_PATH',
    )
    mask_texture: StringProperty(
        name="Mask Texture",
        description="Path to Mask texture (RGB: R-Roughness, G-Metallic, B-AO)",
        default="",
        subtype='FILE_PATH',
    )
    normal_texture: StringProperty(
        name="Normal Texture",
        description="Path to Normal texture",
        default="",
        subtype='FILE_PATH',
    )
    emissive_texture: StringProperty(
        name="Emissive Texture",
        description="Path to Emissive texture (red channel used)",
        default="",
        subtype='FILE_PATH',
    )
    emissive_color: FloatVectorProperty(
        name="Emissive Color",
        subtype='COLOR',
        default=(1.0, 1.0, 1.0),
        min=0.0, max=1.0,
        description="Color multiplier for emissive texture",
    )
    emissive_intensity: FloatProperty(
        name="Emissive Intensity",
        default=1.0,
        description="Intensity for emission (set to BSDF's Emission Strength)",
    )
    apply_to_active: BoolProperty(
        name="Apply to Active Material",
        default=False,
        description="If enabled, re-build nodes in the active material instead of creating a new one",
    )

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "base_color_texture")
        layout.prop(self, "mask_texture")
        layout.prop(self, "normal_texture")
        layout.prop(self, "emissive_texture")
        layout.prop(self, "emissive_color")
        layout.prop(self, "emissive_intensity")
        layout.prop(self, "apply_to_active")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        if self.apply_to_active:
            active_obj = context.active_object
            if not active_obj:
                self.report({'ERROR'}, "No active object found")
                return {'CANCELLED'}
            mat = active_obj.active_material
            if not mat:
                self.report({'ERROR'}, "Active object has no active material")
                return {'CANCELLED'}
            if not mat.use_nodes:
                mat.use_nodes = True
            result = self._build_material_tree(mat)
            if result is None:
                return {'CANCELLED'}
        else:
            mat = bpy.data.materials.new(name="PS_UE_Material")
            mat.use_nodes = True
            result = self._build_material_tree(mat)
            if result is None:
                return {'CANCELLED'}
            self._apply_material_to_selected(mat, context)

        if context.area and context.area.type == 'VIEW_3D':
            context.space_data.shading.color_type = 'TEXTURE'
        return {'FINISHED'}

    def _build_material_tree(self, mat):
        """строит дерево нод для UE-подобного материала"""
        nt = mat.node_tree
        nodes = nt.nodes
        links = nt.links
        for node in list(nodes):
            nodes.remove(node)

        output_node = nodes.new('ShaderNodeOutputMaterial')
        output_node.location = (600, 0)

        bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.location = (300, 0)
        links.new(bsdf.outputs['BSDF'], output_node.inputs['Surface'])

        # --- Base Color ---
        base_color_node = None
        if self.base_color_texture:
            try:
                base_color_img = bpy.data.images.load(self.base_color_texture)
            except Exception:
                self.report({'ERROR'}, f"Could not load Base Color texture: {self.base_color_texture}")
                return None
            base_color_node = nodes.new('ShaderNodeTexImage')
            base_color_node.image = base_color_img
            base_color_node.name = "Base Color Texture"
            base_color_node.label = "Base Color Texture"
            base_color_node.location = (-400, 300)
            base_color_node.interpolation = 'Smart'
            base_color_node.extension = 'REPEAT'
            links.new(bsdf.inputs['Base Color'], base_color_node.outputs['Color'])

        # --- Mask (RGB: R-Roughness, G-Metallic, B-AO) ---
        if self.mask_texture:
            try:
                mask_img = bpy.data.images.load(self.mask_texture)
            except Exception:
                self.report({'ERROR'}, f"Could not load Mask texture: {self.mask_texture}")
                return None
            mask_node = nodes.new('ShaderNodeTexImage')
            mask_node.image = mask_img
            mask_node.name = "Mask Texture"
            mask_node.label = "Mask Texture"
            mask_node.location = (-400, 0)
            mask_node.image.colorspace_settings.name = 'Non-Color'
            mask_node.interpolation = 'Closest'
            mask_node.extension = 'REPEAT'

            separate_mask = nodes.new('ShaderNodeSeparateColor')
            separate_mask.location = (-200, 0)
            links.new(separate_mask.inputs['Color'], mask_node.outputs['Color'])
            links.new(bsdf.inputs['Roughness'], separate_mask.outputs['Red'])
            links.new(bsdf.inputs['Metallic'], separate_mask.outputs['Green'])

            # смешиваем Base Color с AO (Blue-канал)
            if base_color_node:
                for link in list(nt.links):
                    if link.from_socket == base_color_node.outputs['Color'] and link.to_socket == bsdf.inputs['Base Color']:
                        nt.links.remove(link)
                mix_ao = nodes.new('ShaderNodeMixRGB')
                mix_ao.blend_type = 'MULTIPLY'
                mix_ao.inputs['Fac'].default_value = 1.0
                mix_ao.location = (0, 300)
                links.new(mix_ao.inputs[1], base_color_node.outputs['Color'])
                links.new(mix_ao.inputs[2], separate_mask.outputs['Blue'])
                links.new(bsdf.inputs['Base Color'], mix_ao.outputs['Color'])

        # --- Normal (с инвертированием зелёного канала для UE) ---
        if self.normal_texture:
            try:
                normal_img = bpy.data.images.load(self.normal_texture)
            except Exception:
                self.report({'ERROR'}, f"Could not load Normal texture: {self.normal_texture}")
                return None
            normal_tex = nodes.new('ShaderNodeTexImage')
            normal_tex.image = normal_img
            normal_tex.name = "Normal Texture"
            normal_tex.label = "Normal Texture"
            normal_tex.location = (-400, -300)
            normal_tex.image.colorspace_settings.name = 'Non-Color'
            normal_tex.interpolation = 'Smart'
            normal_tex.extension = 'REPEAT'

            separate_normal = nodes.new('ShaderNodeSeparateColor')
            separate_normal.location = (-200, -300)
            links.new(separate_normal.inputs['Color'], normal_tex.outputs['Color'])

            invert_green = nodes.new('ShaderNodeMath')
            invert_green.operation = 'SUBTRACT'
            invert_green.inputs[0].default_value = 1.0
            invert_green.location = (0, -300)
            links.new(invert_green.inputs[1], separate_normal.outputs['Green'])

            combine_normal = nodes.new('ShaderNodeCombineColor')
            combine_normal.location = (200, -300)
            links.new(combine_normal.inputs['Red'], separate_normal.outputs['Red'])
            links.new(combine_normal.inputs['Green'], invert_green.outputs['Value'])
            links.new(combine_normal.inputs['Blue'], separate_normal.outputs['Blue'])

            normal_map = nodes.new('ShaderNodeNormalMap')
            normal_map.location = (400, -300)
            normal_map.space = 'TANGENT'
            links.new(normal_map.inputs['Color'], combine_normal.outputs['Color'])
            links.new(bsdf.inputs['Normal'], normal_map.outputs['Normal'])

        # --- Emissive ---
        if self.emissive_texture:
            try:
                emissive_img = bpy.data.images.load(self.emissive_texture)
            except Exception:
                self.report({'ERROR'}, f"Could not load Emissive texture: {self.emissive_texture}")
                return None
            emissive_tex = nodes.new('ShaderNodeTexImage')
            emissive_tex.image = emissive_img
            emissive_tex.name = "Emissive Texture"
            emissive_tex.label = "Emissive Texture"
            emissive_tex.location = (-400, -600)
            emissive_tex.image.colorspace_settings.name = 'Non-Color'
            emissive_tex.interpolation = 'Smart'
            emissive_tex.extension = 'REPEAT'

            separate_emissive = nodes.new('ShaderNodeSeparateColor')
            separate_emissive.location = (-200, -600)
            links.new(separate_emissive.inputs['Color'], emissive_tex.outputs['Color'])

            emissive_color_node = nodes.new('ShaderNodeRGB')
            emissive_color_node.location = (-200, -700)
            emissive_color_node.outputs[0].default_value = (
                self.emissive_color[0], self.emissive_color[1], self.emissive_color[2], 1.0
            )

            multiply_emissive = nodes.new('ShaderNodeMixRGB')
            multiply_emissive.blend_type = 'MULTIPLY'
            multiply_emissive.inputs['Fac'].default_value = 1.0
            multiply_emissive.location = (0, -600)
            links.new(multiply_emissive.inputs[1], emissive_color_node.outputs['Color'])
            links.new(multiply_emissive.inputs[2], separate_emissive.outputs['Red'])

            links.new(bsdf.inputs['Emission Color'], multiply_emissive.outputs['Color'])
            bsdf.inputs['Emission Strength'].default_value = self.emissive_intensity

        return mat

    def _apply_material_to_selected(self, material, context):
        """назначает материал всем выделенным mesh-объектам"""
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                if not obj.data.materials:
                    obj.data.materials.append(material)
                else:
                    obj.data.materials[0] = material


# =====================================================================
# модификаторы
# =====================================================================

class PS_OT_add_subsurf_and_bevel(Operator):
    """Add bevel and subdivision modifiers"""
    bl_idname = "object.ps_add_subsurf_and_bevel"
    bl_label = "Add Subdivision And Bevel"
    bl_description = 'Add crease-based bevel with subdivision surface modifiers to selected objects'
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    bevel_segments: IntProperty(
        name="Segments", default=2, min=1, max=10,
        description="Number of segments for the bevel",
    )
    bevel_width: FloatProperty(
        name="Width", default=0.02, min=0.0, max=1.0,
        description="Bevel width",
    )
    bevel_angle: FloatProperty(
        name="Angle", default=60.0, min=0.0, max=180.0,
        description="Bevel angle",
    )
    use_clamp_overlap: BoolProperty(
        name="Clamp Overlap", default=True,
        description="Clamp overlap of beveled edges/vertices",
    )
    subdivision_levels: IntProperty(
        name="Levels", default=3, min=0, max=6,
        description="Number of subdivision levels",
    )
    preset_mode: EnumProperty(
        items=[
            ('DEFAULT', "Default", "Default preset with weight-based bevels"),
            ('WIDE', "Wide Bevel", "Wider bevels without overlap clamping"),
            ('ANGLE', "Angle Based", "Angle-based bevels"),
        ],
        name="Preset",
        default='DEFAULT',
    )

    def _apply_preset(self, mod_bevel):
        """применяет пресет к модификатору bevel"""
        if self.preset_mode == 'DEFAULT':
            mod_bevel.width = 0.02
            mod_bevel.use_clamp_overlap = True
            mod_bevel.segments = self.bevel_segments
        elif self.preset_mode == 'WIDE':
            mod_bevel.width = 0.15
            mod_bevel.use_clamp_overlap = False
            mod_bevel.segments = self.bevel_segments
        elif self.preset_mode == 'ANGLE':
            mod_bevel.angle_limit = radians(self.bevel_angle)
            mod_bevel.width = self.bevel_width
            mod_bevel.use_clamp_overlap = self.use_clamp_overlap
            mod_bevel.segments = self.bevel_segments

    def _has_bevel_weights(self, obj):
        """проверяет наличие bevel weights на рёбрах"""
        if obj.type != 'MESH':
            return False
        bevel_layer = obj.data.attributes.get('bevel_weight_edge')
        if not bevel_layer:
            return False
        return any(value.value > 0 for value in bevel_layer.data)

    def _setup_bevel(self, obj, mod_name):
        """настраивает модификатор bevel"""
        mod = obj.modifiers.get(mod_name) or obj.modifiers.new(mod_name, 'BEVEL')
        mod.show_expanded = False
        mod.profile = 1
        mod.limit_method = 'WEIGHT' if self._has_bevel_weights(obj) else 'ANGLE'
        self._apply_preset(mod)
        return mod

    def _setup_subdivision(self, obj, mod_name):
        """настраивает модификатор subdivision"""
        mod = obj.modifiers.get(mod_name) or obj.modifiers.new(mod_name, 'SUBSURF')
        mod.show_expanded = False
        mod.levels = self.subdivision_levels
        return mod

    def execute(self, context):
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                self._setup_bevel(obj, "PS Bevel")
                self._setup_subdivision(obj, "PS Subdivision")
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "preset_mode")
        layout.separator()

        box = layout.box()
        box.label(text="Bevel Settings:")
        box.prop(self, "bevel_segments")
        if self.preset_mode == 'ANGLE':
            box.prop(self, "bevel_angle")
            box.prop(self, "bevel_width")
            box.prop(self, "use_clamp_overlap")

        box = layout.box()
        box.label(text="Subdivision Settings:")
        box.prop(self, "subdivision_levels")


class PS_OT_triangulate(Operator):
    """Add triangulate modifier"""
    bl_idname = "object.ps_triangulate"
    bl_label = "Triangulate"
    bl_description = "Add a triangulate modifier to selected objects with optimized quad splitting"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        name = "PS Triangulate"
        for obj in context.selected_objects:
            if obj.type != 'MESH':
                continue
            mod = obj.modifiers.get(name) or obj.modifiers.new(name, 'TRIANGULATE')
            mod.show_expanded = False
            mod.quad_method = 'FIXED'
            mod.ngon_method = 'BEAUTY'
            mod.min_vertices = 4
            mod.keep_custom_normals = True
        return {'FINISHED'}


class PS_OT_tris_weighted_normal(Operator):
    """Add triangulate and weighted normal modifiers"""
    bl_idname = 'object.ps_tris_weighted_normal'
    bl_label = "Tris & Weighted Normal"
    bl_description = "Add triangulate and weighted normal modifiers with smooth shading to selected objects"
    bl_options = {'REGISTER', 'UNDO'}

    weight: IntProperty(
        name="Weight", default=50, min=0, max=100,
        description="Weight for normal calculation",
    )
    mode: EnumProperty(
        name="Mode",
        items=[
            ('FACE_AREA', "Face Area", "Weight by face area"),
            ('CORNER_ANGLE', "Corner Angle", "Weight by corner angle"),
            ('FACE_ANGLE', "Face Angle", "Weight by face angle"),
        ],
        default='FACE_AREA',
        description="Weight calculation mode",
    )
    thresh: FloatProperty(
        name="Threshold", default=0.01, min=0.0, max=1.0,
        description="Threshold for normal calculation",
    )
    keep_sharp: BoolProperty(
        name="Keep Sharp", default=True,
        description="Keep sharp edges",
    )
    use_face_influence: BoolProperty(
        name="Use Face Influence", default=False,
        description="Use face influence for normal calculation",
    )

    def execute(self, context):
        tri_name = "PS Triangulate"
        wn_name = "PS Weighted Normal"

        # применяем smooth shading один раз для всех выделенных объектов
        bpy.ops.object.shade_smooth()

        for obj in context.selected_objects:
            if obj.type != 'MESH':
                continue

            # weighted normal модификатор
            mod_wn = obj.modifiers.get(wn_name) or obj.modifiers.new(wn_name, 'WEIGHTED_NORMAL')
            mod_wn.show_expanded = False
            mod_wn.mode = self.mode
            mod_wn.weight = self.weight
            mod_wn.thresh = self.thresh
            mod_wn.keep_sharp = self.keep_sharp
            mod_wn.use_face_influence = self.use_face_influence

            # triangulate модификатор
            mod_tri = obj.modifiers.get(tri_name) or obj.modifiers.new(tri_name, 'TRIANGULATE')
            mod_tri.show_expanded = False
            mod_tri.quad_method = 'FIXED'
            mod_tri.ngon_method = 'BEAUTY'
            mod_tri.min_vertices = 4
            mod_tri.keep_custom_normals = True

        return {'FINISHED'}


class PS_OT_solidify(Operator):
    """Add solidify modifier"""
    bl_idname = 'object.ps_solidify'
    bl_label = "Solidify"
    bl_description = "Add a non-manifold solidify modifier to selected objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        name = "PS Solidify"
        for obj in context.selected_objects:
            if obj.type != 'MESH':
                continue
            mod = obj.modifiers.get(name) or obj.modifiers.new(name, 'SOLIDIFY')
            mod.show_expanded = False
            mod.solidify_mode = 'NON_MANIFOLD'
            mod.nonmanifold_boundary_mode = 'FLAT'
            mod.offset = 1
            mod.nonmanifold_thickness_mode = 'EVEN'
        return {'FINISHED'}


# =====================================================================
# данные рёбер (seam, sharp, bevel, crease)
# =====================================================================

class PS_OT_set_edge_data(Operator):
    """Toggle edge data for selected edges"""
    bl_idname = 'mesh.ps_set_edge_data'
    bl_label = "Set Edge Data"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    bl_description = "Toggle edge attributes (Bevel Weight, Crease, Seam, Sharp) on selected edges"

    do_bevel: BoolProperty(name='Bevel', default=False)
    do_crease: BoolProperty(name='Crease', default=False)
    do_seam: BoolProperty(name='Seam', default=False)
    do_sharp: BoolProperty(name='Sharp', default=False)

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    @classmethod
    def description(cls, context, properties):
        parts = []
        if properties.do_bevel:
            parts.append("Bevel")
        if properties.do_crease:
            parts.append("Crease")
        if properties.do_seam:
            parts.append("Seam")
        if properties.do_sharp:
            parts.append("Sharp")
        return f"Toggle {' '.join(parts)} for selected edges"

    def execute(self, context):
        if not any([self.do_bevel, self.do_crease, self.do_seam, self.do_sharp]):
            return {'CANCELLED'}

        uniques = list(context.objects_in_mode_unique_data)

        # первый проход: проверяем, есть ли данные у выделенных рёбер
        any_has = False
        for obj in uniques:
            bm = bmesh.from_edit_mesh(obj.data)
            bevel_layer = bm.edges.layers.float.get('bevel_weight_edge') if self.do_bevel else None
            crease_layer = bm.edges.layers.float.get('crease_edge') if self.do_crease else None

            for edge in bm.edges:
                if not edge.select:
                    continue
                if self.do_bevel and bevel_layer and edge[bevel_layer] > 0.0:
                    any_has = True
                    break
                if self.do_crease and crease_layer and edge[crease_layer] > 0.0:
                    any_has = True
                    break
                if self.do_seam and edge.seam:
                    any_has = True
                    break
                if self.do_sharp and not edge.smooth:
                    any_has = True
                    break
            if any_has:
                break

        # второй проход: переключаем значения
        for obj in uniques:
            bm = bmesh.from_edit_mesh(obj.data)

            if any_has:
                # выключаем
                bevel_layer = bm.edges.layers.float.get('bevel_weight_edge') if self.do_bevel else None
                crease_layer = bm.edges.layers.float.get('crease_edge') if self.do_crease else None
                for e in bm.edges:
                    if not e.select:
                        continue
                    if self.do_bevel and bevel_layer:
                        e[bevel_layer] = 0.0
                    if self.do_crease and crease_layer:
                        e[crease_layer] = 0.0
                    if self.do_seam:
                        e.seam = False
                    if self.do_sharp:
                        e.smooth = True
            else:
                # включаем
                bevel_layer = None
                crease_layer = None
                if self.do_bevel:
                    bevel_layer = bm.edges.layers.float.get('bevel_weight_edge')
                    if bevel_layer is None:
                        bevel_layer = bm.edges.layers.float.new('bevel_weight_edge')
                if self.do_crease:
                    crease_layer = bm.edges.layers.float.get('crease_edge')
                    if crease_layer is None:
                        crease_layer = bm.edges.layers.float.new('crease_edge')
                for e in bm.edges:
                    if not e.select:
                        continue
                    if self.do_bevel:
                        e[bevel_layer] = 1.0
                    if self.do_crease:
                        e[crease_layer] = 1.0
                    if self.do_seam:
                        e.seam = True
                    if self.do_sharp:
                        e.smooth = False

            bmesh.update_edit_mesh(obj.data)
        return {'FINISHED'}


# =====================================================================
# булевые операции
# =====================================================================

class PS_BooleanBase:
    """базовый миксин для булевых операций"""
    keep_bool_obj: BoolProperty(
        name="Keep Bool Object",
        description="Do not delete the boolean operand object after the operation",
        default=False,
    )
    brush_mode: BoolProperty(
        name="Brush Mode",
        description="Keep the boolean modifier live instead of applying it immediately",
        default=False,
    )

    BOOLEAN_SOLVER = "EXACT"

    @classmethod
    def poll(cls, context):
        active = context.active_object
        return (
            context.mode == 'OBJECT'
            and active is not None
            and active.type == 'MESH'
            and len(context.selected_objects) >= 2
        )

    def _validate_selection(self, context):
        active = context.active_object
        if active is None or active.type != 'MESH':
            self.report({'ERROR'}, "Active object must be a mesh")
            return None, None

        operands = [ob for ob in context.selected_objects if ob != active and ob.type == 'MESH']
        if not operands:
            self.report({'ERROR'}, "Select at least one mesh operand")
            return None, None

        return active, operands

    def objects_prepare(self):
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        for ob in bpy.context.selected_objects:
            if ob.type != "MESH":
                ob.select_set(False)

        # Preserve existing modifier stacks: for boolean ops we only need
        # unique mesh datablocks, not a full convert/apply pass.
        for ob in bpy.context.selected_objects:
            if ob.type != 'MESH':
                continue
            if ob.data.users > 1:
                ob.data = ob.data.copy()

    def mesh_selection(self, ob, select_action):
        obj = bpy.context.active_object
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_all(action=select_action)
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.context.view_layer.objects.active = obj

    def boolean_operation(self):
        obj, obs = self._validate_selection(bpy.context)
        if obj is None:
            return {'CANCELLED'}

        obj.select_set(False)

        self.mesh_selection(obj, "DESELECT")
        for ob in obs:
            self.mesh_selection(ob, "SELECT")
            self.boolean_mod(obj, ob, self.mode)
        obj.select_set(True)
        return {'FINISHED'}

    def boolean_mod(self, obj, ob, mode, ob_delete=True):
        md = obj.modifiers.new("PS Boolean", "BOOLEAN")
        md.show_viewport = self.brush_mode
        md.operation = mode
        md.object = ob
        if hasattr(md, "solver"):
            md.solver = self.BOOLEAN_SOLVER
        if hasattr(md, "use_hole_tolerant"):
            md.use_hole_tolerant = True

        # Boolean modifiers are created at the end of the stack by default,
        # which is exactly what we need for "on top of visible result" behavior.
        context_override = {
            'object': obj,
            'active_object': obj,
            'selected_objects': [obj],
            'selected_editable_objects': [obj],
        }

        if not self.brush_mode:
            with bpy.context.temp_override(**context_override):
                bpy.ops.object.modifier_apply(modifier=md.name)
            if not self.keep_bool_obj:
                bpy.data.objects.remove(ob)
        else:
            ob.display_type = 'BOUNDS'

    def execute(self, context):
        self.objects_prepare()
        return self.boolean_operation()

    def invoke(self, context, event):
        self.keep_bool_obj = event.shift
        self.brush_mode = event.ctrl
        if not self.poll(context):
            self.report({"ERROR"}, "Object mode with at least two mesh objects is required")
            return {"CANCELLED"}
        return self.execute(context)


class PS_OT_bool_difference(Operator, PS_BooleanBase):
    bl_idname = "object.ps_bool_difference"
    bl_label = "Bool Difference"
    bl_description = ("Subtract selected objects from the active object\n"
                      "\u2022 Shift+LMB \u2014 Keep the boolean operand object\n"
                      "\u2022 Ctrl+LMB \u2014 Non-destructive brush mode")
    bl_options = {"REGISTER", "UNDO"}
    mode = "DIFFERENCE"


class PS_OT_bool_union(Operator, PS_BooleanBase):
    bl_idname = "object.ps_bool_union"
    bl_label = "Bool Union"
    bl_description = ("Merge selected objects into the active object\n"
                      "\u2022 Shift+LMB \u2014 Keep the boolean operand object\n"
                      "\u2022 Ctrl+LMB \u2014 Non-destructive brush mode")
    bl_options = {"REGISTER", "UNDO"}
    mode = "UNION"


class PS_OT_bool_intersect(Operator, PS_BooleanBase):
    bl_idname = "object.ps_bool_intersect"
    bl_label = "Bool Intersect"
    bl_description = ("Keep only the overlapping volume between active and selected objects\n"
                      "\u2022 Shift+LMB \u2014 Keep the boolean operand object\n"
                      "\u2022 Ctrl+LMB \u2014 Non-destructive brush mode")
    bl_options = {"REGISTER", "UNDO"}
    mode = "INTERSECT"


class PS_OT_bool_slice(Operator, PS_BooleanBase):
    bl_idname = "object.ps_bool_slice"
    bl_label = "Bool Slice"
    bl_description = ("Cut the active object into two parts along the selected objects\n"
                      "\u2022 Shift+LMB \u2014 Keep the boolean operand object\n"
                      "\u2022 Ctrl+LMB \u2014 Non-destructive brush mode")
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        space_data = get_active_3d_view()
        if space_data is None:
            return {"CANCELLED"}

        is_local_view = bool(space_data.local_view)
        active, operands = self._validate_selection(context)
        if active is None:
            return {'CANCELLED'}

        self.objects_prepare()

        ob1 = active
        ob1.select_set(False)
        self.mesh_selection(ob1, "DESELECT")

        ob1_copy = None
        for ob2 in operands:
            self.mesh_selection(ob2, "SELECT")

            ob1_copy = ob1.copy()
            ob1_copy.data = ob1.data.copy()

            for coll in ob1.users_collection:
                coll.objects.link(ob1_copy)

            if is_local_view:
                ob1_copy.local_view_set(space_data, True)

            self.boolean_mod(ob1, ob2, "DIFFERENCE", ob_delete=False)
            self.boolean_mod(ob1_copy, ob2, "INTERSECT")
            ob1_copy.select_set(True)

        if ob1_copy is not None:
            context.view_layer.objects.active = ob1_copy
        return {"FINISHED"}


# =====================================================================
# распределение объектов
# =====================================================================

class PS_OT_distribute_objects(Operator):
    """Distribute selected objects with spacing"""
    bl_idname = "object.ps_distribute_objects"
    bl_label = "Distribute Objects"
    bl_description = "Evenly distribute selected objects along the X axis with spacing based on their bounding box sizes"
    bl_options = {'REGISTER', 'UNDO'}

    expose_factor: FloatProperty(
        name="Expose Factor",
        description="Object spacing factor (from 0 to 1)",
        min=0.0, max=1.0, default=1.0,
    )

    _objects_data = None

    def execute(self, context):
        if self._objects_data is None:
            objects = context.selected_objects
            if not objects:
                self.report({'WARNING'}, "No objects selected")
                return {'CANCELLED'}

            widths = []
            objects_data = []
            total_width = 0.0
            padding = 0.1

            for obj in objects:
                bbox = [obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box]
                min_x = min(v.x for v in bbox)
                max_x = max(v.x for v in bbox)
                width = max_x - min_x
                widths.append(width)
                total_width += width + padding

            total_width -= padding
            current_x = -total_width / 2.0

            for i, obj in enumerate(objects):
                width = widths[i]
                initial_position = obj.location.copy()
                final_position = initial_position.copy()
                final_position.x = current_x + width / 2.0
                objects_data.append({
                    'object': obj,
                    'initial_position': initial_position,
                    'final_position': final_position,
                })
                current_x += width + padding

            self._objects_data = objects_data

        # применяем интерполяцию на основе expose_factor
        for data in self._objects_data:
            obj = data['object']
            obj.location = data['initial_position'].lerp(data['final_position'], self.expose_factor)

        return {'FINISHED'}

    def invoke(self, context, event):
        self._objects_data = None
        return self.execute(context)


# =====================================================================
# пресет угла инкремента
# =====================================================================

class PS_OT_set_increment_angle(Operator):
    """Set snap rotation angle increment"""
    bl_idname = 'scene.ps_set_increment_angle'
    bl_label = 'Set Increment Angle'
    bl_options = {'REGISTER', 'INTERNAL'}

    angle: IntProperty(
        name='Angle',
        description='Angle preset value in degrees',
        default=45,
    )
    target: StringProperty(
        name='Target',
        description='Name of the tool_settings attribute to set',
        default='snap_angle_increment_3d',
    )

    @classmethod
    def description(cls, context, properties):
        return f"Set rotation snap angle to {properties.angle}°"

    def execute(self, context):
        setattr(context.scene.tool_settings, self.target, radians(self.angle))
        return {'FINISHED'}


# =====================================================================
# заполнение меша из точек
# =====================================================================

class PS_OT_fill_from_points(Operator):
    """Build mesh from selected points using minimum spanning tree"""
    bl_idname = 'mesh.ps_fill_from_points'
    bl_label = 'Fill From Points'
    bl_description = 'Connect selected vertices into a mesh using the minimum spanning tree algorithm'
    bl_options = {'REGISTER', 'UNDO'}

    angle: FloatProperty(
        name='Angle',
        description='Connection angle threshold in degrees',
        default=90.0,
    )
    range_count: IntProperty(
        name='Range Count',
        description='Number of nearest neighbor connections to consider',
        default=1, min=1, max=100,
    )

    def execute(self, context):
        import heapq

        obj = context.object
        me = obj.data
        obj.update_from_editmode()
        bm = bmesh.from_edit_mesh(me)

        verts_old = [v for v in bm.verts]

        # копируем вершины из исходного объекта
        verts = [bm.verts.new(v.co) for v in me.vertices]

        # удаляем старые вершины
        for v in verts_old:
            bm.verts.remove(v)

        def calc_distance(vert1, vert2):
            return (vert1.co - vert2.co).length

        # строим минимальное остовное дерево (алгоритм Прима)
        edge_heap = []
        added_verts = {verts[0]}
        for vert in verts[1:]:
            heapq.heappush(edge_heap, (calc_distance(verts[0], vert), 0, verts.index(vert)))

        while len(added_verts) < len(verts):
            dist, vert_from_idx, vert_to_idx = heapq.heappop(edge_heap)
            if verts[vert_to_idx] not in added_verts:
                added_verts.add(verts[vert_to_idx])
                bm.edges.new((verts[vert_from_idx], verts[vert_to_idx]))

                for v_idx, vert in enumerate(verts):
                    if vert not in added_verts:
                        heapq.heappush(edge_heap, (calc_distance(verts[vert_to_idx], vert), vert_to_idx, v_idx))

            bmesh.update_edit_mesh(me)

        return {'FINISHED'}


# =====================================================================
# регистрация
# =====================================================================

classes = [
    # выбор полигонов
    PS_OT_select_polygons,

    # утилиты объектов
    PS_OT_random_name,

    # очистка
    PS_OT_clear_dots,
    PS_OT_remove_vertex_non_manifold,
    PS_OT_clear_materials,
    PS_OT_clear_data,
    PS_OT_del_long_faces,

    # сброс трансформаций
    PS_OT_reset_location_object,
    PS_OT_reset_rotation_object,
    PS_OT_reset_scale_object,
    PS_OT_reset_vertex_location,
    PS_OT_transfer_transform,

    # камера
    PS_OT_add_camera,

    # материалы
    PS_OT_add_material,
    PS_OT_unreal_material,

    # модификаторы
    PS_OT_add_subsurf_and_bevel,
    PS_OT_triangulate,
    PS_OT_tris_weighted_normal,
    PS_OT_solidify,

    # данные рёбер
    PS_OT_set_edge_data,

    # булевые операции
    PS_OT_bool_difference,
    PS_OT_bool_union,
    PS_OT_bool_intersect,
    PS_OT_bool_slice,

    # распределение
    PS_OT_distribute_objects,

    # заполнение
    PS_OT_fill_from_points,

    # пресет угла инкремента
    PS_OT_set_increment_angle,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
