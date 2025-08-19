import bpy
import bmesh
from bpy.types import Operator
from bpy.props import EnumProperty, BoolProperty, FloatProperty, IntProperty
from mathutils import Vector, Euler
from .utils import get_active_3d_view
import random
import string


# получение полигонов по количеству сторон
class PS_OT_select_polygons(Operator):
    bl_idname = 'mesh.ps_select_polygons'
    bl_label = 'Select Polygons'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'Select polygons by number of sides'

    polygon_type: EnumProperty(
        name='Type',
        items=[
            ('NGONS', 'N-Gons', 'Select polygons with more than 4 sides', '', 0),
            ('QUADS', 'Quads', 'Select polygons with exactly 4 sides', '', 1),
            ('TRIS', 'Tris', 'Select polygons with exactly 3 sides', '', 2),
            ],
            default='NGONS',
            )

    @classmethod
    def poll(cls, context):
        if context.active_object:
            return context.active_object.type == 'MESH'

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



class PS_OT_random_name(Operator): # установка случайного имени
    bl_idname = 'object.ps_random_name'
    bl_label = 'Set Random Name'
    bl_description = 'Sets a random name of 11 letterse'
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        ob = context.object
        return (context.active_object != None) and (ob.type == 'MESH') and (context.mode == 'OBJECT')


    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        for obj in selected_objects:
            new_name = ''.join(random.choices(string.ascii_letters, k=11))
            obj.name = new_name
        return {'FINISHED'}







class PS_OT_clear_dots(Operator):
    bl_idname = "mesh.ps_clear_dots"
    bl_label = "Clear Dots"
    bl_description="To Remove A Single Vertex"

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        vCount = 0

        uniques = context.selected_objects
        for obj in uniques:
            me = obj.data
            mesh = bmesh.from_edit_mesh(me)

            vDots = []
            for v in mesh.verts:
                if len(v.link_edges) < 1:
                    vDots.append(v)
                    vCount += 1

            bmesh.ops.delete(mesh, geom=vDots, context='VERTS')
            bmesh.update_edit_mesh(me)

        self.report({'INFO'}, "Clear Dots - " + str(vCount))
        return {'FINISHED'}



class PS_OT_remove_vertex_non_manifold(Operator):
    bl_idname = "mesh.ps_remove_vertex_non_manifold"
    bl_label = "Remove Non Manifold Vertex"
    bl_description="Remove Vertexes That Are Not Connected To Polygons"

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        vCount = 0

        uniques = context.selected_objects
        for obj in uniques:
            me = obj.data
            mesh = bmesh.from_edit_mesh(me)

            vDots = []
            for v in mesh.verts:
                if len(v.link_faces)<1:
                    vDots.append(v)
                    vCount += 1

            bmesh.ops.delete(mesh, geom=vDots, context='VERTS')
            bmesh.update_edit_mesh(me)

        self.report({'INFO'}, "Removed Vertexes - " + str(vCount))
        return {'FINISHED'}



class PS_OT_clear_materials(Operator):
    bl_idname = 'object.ps_clear_materials'
    bl_label = 'Clear Materials'
    bl_description = 'To Remove All Materials From The Object'
    bl_optios = {'REGISTER', 'UNDO'}

    #sceen: BoolProperty( name='Scene', default = False )

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        sel_objs = context.selected_objects
        for obj in sel_objs:
            obj.data.materials.clear()

        """ if self.sceen:
            for material in bpy.data.materials:
                material.user_clear()
                bpy.data.materials.remove(material) """
        return {'FINISHED'}



class PS_OT_clear_data(Operator):
    bl_idname = 'object.ps_clear_data'
    bl_label = 'Clear Data'
    bl_description = 'To Remove All Data From The Object'

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        #sel_objs = context.selected_objects.copy()
        #active_obj = context.active_object.copy()

        # deselect all objects
        #bpy.ops.object.select_all(action='DESELECT')

        sel_objs = context.selected_objects
        for obj in sel_objs:
            #obj.select_set(True)
            #context.view_layer.objects.active = obj

            # --- Clear Vertex Groups ---
            if len(obj.vertex_groups) > 0:
                for vg in obj.vertex_groups:
                    obj.vertex_groups.remove(vg)

            # --- Clear Shape Keys ---
            if obj.data.shape_keys is not None:
                if len(obj.data.shape_keys.key_blocks):
                    for sk in obj.data.shape_keys.key_blocks:
                        obj.shape_key_remove(sk)

            """ # --- Clear UV Maps ---
            if len(obj.data.uv_layers) > 0:
                for uv in obj.data.uv_layers:
                    obj.data.uv_layers.remove(uv) """

            # --- Clear Color Attributes ---
            if len(obj.data.color_attributes) > 0:
                for ca in obj.data.color_attributes:
                    obj.data.color_attributes.remove(ca)

            # --- Clear Face Maps ---
            if len(obj.face_maps) > 0:
                for fm in obj.face_maps:
                    obj.face_maps.remove(fm)

            # --- Clear Atrributes ---
            if len(obj.data.attributes) > 0:
                for at in obj.data.attributes:
                    obj.data.attributes.remove(at)


            """ # --- Clear Geometry Data ---
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.customdata_custom_splitnormals_clear()
            bpy.ops.mesh.customdata_bevel_weight_edge_clear()
            bpy.ops.mesh.customdata_bevel_weight_vertex_clear()
            bpy.ops.mesh.customdata_crease_edge_clear()
            bpy.ops.mesh.customdata_crease_vertex_clear()
            bpy.ops.object.mode_set(mode='OBJECT') """

            #obj.select_set(False)


        # select all objects
        """ for obj in sel_objs:
            obj.select_set(True) """
        #context.view_layer.objects.active = active_obj
        return {'FINISHED'}






# --- RESET
class PS_OT_reset_location_object(Operator):
    bl_idname = "object.ps_reset_location_object"
    bl_label = "Reset Location"
    """ bl_description = ("Reset All Transform\n"
                    "Location, Rotation, Scale") """
    bl_options = {'REGISTER', 'UNDO'}

    axis: EnumProperty(
        name='Axis',
        items=[
            ('X', 'X Axis', '', '', 0),
            ('Y', 'Y Axis', '', '', 1),
            ('Z', 'Z Axis', '', '', 2),
            ('ALL', 'All Axis', '', '', 3),
            ('ALL_T', 'All Tramsform', '', '', 4),
            ],
            default='ALL',
            )

    cursor: BoolProperty(name="Relative 3D Cursor", description = "Alignment Relative To The 3d Сursor.", default=False)

    def execute(self, context):
        cursor = context.scene.cursor
        cur_l = cursor.location
        cur_e = cursor.rotation_euler
        objs = context.selected_objects
        for ob in objs:
            if self.axis == 'X':
                if self.cursor:
                    ob.location.x = cur_l.x
                else:
                    ob.location.x = 0.0

            elif self.axis == 'Y':
                if self.cursor:
                    ob.location.y = cur_l.y
                else:
                    ob.location.y = 0.0

            elif self.axis == 'Z':
                if self.cursor:
                    ob.location.z = cur_l.z
                else:
                    ob.location.z = 0.0

            elif self.axis == 'ALL':
                if self.cursor:
                    ob.location = cur_l
                else:
                    ob.location = Vector()

            elif self.axis == 'ALL_T':
                if self.cursor:
                    ob.location = cur_l
                else:
                    ob.location = Vector()

                ob.rotation_euler = cur_e #Quaternion()
                ob.scale = Vector((1.0, 1.0, 1.0))

                #bpy.ops.object.location_clear(clear_delta=False)
                #bpy.ops.object.rotation_clear(clear_delta=False)
                #bpy.ops.object.scale_clear(clear_delta=False)

        return {'FINISHED'}



class PS_OT_reset_rotation_object(Operator):
    bl_idname = 'object.ps_reset_rotation_object'
    bl_label = 'Reset Rotation'
    bl_options = {'REGISTER', 'UNDO'}

    axis: EnumProperty(
        name='Axis',
        items=[
            ('X', 'X Axis', '', '', 0),
            ('Y', 'Y Axis', '', '', 1),
            ('Z', 'Z Axis', '', '', 2),
            ('ALL', 'All Axis', '', '', 3),
            ],
            default='X',
            )

    cursor: BoolProperty(name="Relative 3D Cursor", description = "Alignment Relative To The 3d Сursor.", default=False)

    def execute(self, context):
        cursor = context.scene.cursor.rotation_euler
        objs = context.selected_objects
        for ob in objs:
            if self.axis == 'X':
                if self.cursor:
                    ob.rotation_euler[0] = cursor[0]
                else:
                    ob.rotation_euler[0] = 0.0

            elif self.axis == 'Y':
                if self.cursor:
                    ob.rotation_euler[1] = cursor[1]
                else:
                    ob.rotation_euler[1] = 0.0

            elif self.axis == 'Z':
                if self.cursor:
                    ob.rotation_euler[2] = cursor[2]
                else:
                    ob.rotation_euler[2] = 0.0

            elif self.axis == 'ALL':
                if self.cursor:
                    ob.rotation_euler = cursor
                else:
                    ob.rotation_euler = Euler()

        return {'FINISHED'}



class PS_OT_reset_scale_object(Operator):
    bl_idname = 'object.ps_reset_scale_object'
    bl_label = 'Reset Scale'
    bl_options = {'REGISTER', 'UNDO'}

    axis: EnumProperty(
        name='Axis',
        items=[
            ('X', 'X Axis', '', '', 0),
            ('Y', 'Y Axis', '', '', 1),
            ('Z', 'Z Axis', '', '', 2),
            ('ALL', 'All Axis', '', '', 3),
            ],
            default='X',
            )

    def execute(self, context):
        objs = context.selected_objects
        for ob in objs:
            if self.axis == 'X':
                ob.scale[0] = 1.0

            elif self.axis == 'Y':
                ob.scale[1] = 1.0

            elif self.axis == 'Z':
                ob.scale[2] = 1.0

            elif self.axis == 'ALL':
                ob.scale = Vector((1.0, 1.0, 1.0))

        return {'FINISHED'}



class PS_OT_locvert(Operator):
    bl_idname = 'mesh.ps_locvert'
    bl_label = 'Reset Vertex Location'
    bl_options = {'REGISTER', 'UNDO'} #, 'DEPENDS_ON_CURSOR'

    axis: EnumProperty(
        name='Axis',
        items=[
            ('X', 'X Axis', '', '', 0),
            ('Y', 'Y Axis', '', '', 1),
            ('Z', 'Z Axis', '', '', 2),
            ('ALL', 'All Axis', '', '', 3)],
            default='ALL',
            )

    pos: EnumProperty(
        name='Position',
        items=[
            ('OBJECT', 'Object', '', '', 0),
            ('CURSOR', '3D Cursor', '', '', 1),
            ('WORLD', 'World', '', '', 2),
            ],
            default='OBJECT',
            )

    vi: BoolProperty(name='Vertex Individual', description = ' ', default=True)


    def execute(self, context):
        uniques = context.objects_in_mode_unique_data

        # Selected Object(EDIT_MODE)
        bms = {}
        for ob in uniques:
            bms[ob] = bmesh.from_edit_mesh(ob.data)

        # ---
        l = Vector()
        v_g = []
        verts = []
        for ob in uniques:
            v_g.extend([ob.matrix_world @ v.co  for v in bms[ob].verts if v.select])
            verts.extend([v.co  for v in bms[ob].verts if v.select])

        if len(v_g) == 0:
            return {'CANCELLED'}
        else:
            l_g = sum(v_g, Vector()) / len(v_g)
            l = sum(verts, Vector()) / len(verts)

        vs_g = {} # DEL ??
        vs = {}
        for ob in uniques:
            for v in bms[ob].verts:
                vs_g[v] = l_g - v.co # DEL ??
                vs[v] = l - v.co
        # ---



        cursor = context.scene.cursor.location


        for ob in uniques:
            for v in bms[ob].verts:
                if v.select:
                    # --- X FIXME
                    if self.axis == 'X':
                        if self.pos == 'CURSOR': # TODO FIXME
                            if self.vi:
                                v.co.x = ( ob.matrix_world.inverted() @ cursor )[0]
                            else:
                                v.co.x = ( ob.matrix_world.inverted() @ cursor )[0] - vs[v][0]

                        elif self.pos == 'WORLD':
                            if self.vi:
                                v.co.x = ( ob.matrix_world.inverted() @ Vector((0.0, 0.0, 0.0)) )[0]
                            else:
                                v.co.x = ( ob.matrix_world.inverted() @ Vector((0.0, 0.0, 0.0)) )[0] - vs[v][0]

                        else:
                            if self.vi:
                                v.co.x = 0.0
                            else:
                                v.co.x = 0.0 - vs[v][0]

                    # --- Y FIXME
                    elif self.axis == 'Y':
                        if self.pos == 'CURSOR':
                            if self.vi:
                                v.co.y = ( ob.matrix_world.inverted() @ cursor )[1]
                            else:
                                v.co.y = ( ob.matrix_world.inverted() @ cursor )[1] - vs[v][1]

                        elif self.pos == 'WORLD':
                            if self.vi:
                                v.co.y = ( ob.matrix_world.inverted() @ Vector((0.0, 0.0, 0.0)) )[1]
                            else:
                                v.co.y = ( ob.matrix_world.inverted() @ Vector((0.0, 0.0, 0.0)) )[1] - vs[v][1]

                        else:
                            if self.vi:
                                v.co.y = 0.0
                            else:
                                v.co.y = 0.0 - vs[v][1]

                    # --- Z FIXME
                    elif self.axis == 'Z':
                        if self.pos == 'CURSOR':# TODO
                            if self.vi:
                                v.co.z = ( ob.matrix_world.inverted() @ cursor )[2]
                            else:
                                v.co.z = ( ob.matrix_world.inverted() @ cursor )[2] - vs[v][2]

                        elif self.pos == 'WORLD':
                            if self.vi:
                                v.co.z = ( ob.matrix_world.inverted() @ Vector((0.0, 0.0, 0.0)) )[2]
                            else:
                                #matrix_basis
                                #matrix_local
                                #matrix_parent_inverse
                                #matrix_world
                                loc = ob.matrix_world.inverted() @ Vector((0.0, 0.0, 0.0))
                                #v.co.z = loc[2] - vs[v][2]
                                v.co.z = loc[2]
                        else:
                            if self.vi:
                                v.co.z = 0.0
                            else:
                                v.co.z = 0.0 - vs[v][2]

                    # --- ALL
                    elif self.axis == 'ALL':
                        if self.pos == 'CURSOR':
                            if self.vi:
                                v.co = ob.matrix_world.inverted() @ cursor
                            else:
                                v.co = ( ob.matrix_world.inverted() @ cursor ) - vs[v]

                        elif self.pos == 'WORLD':
                            if self.vi:
                                v.co = ob.matrix_world.inverted() @ Vector((0.0, 0.0, 0.0))
                            else:
                                v.co = ( ob.matrix_world.inverted() @ Vector((0.0, 0.0, 0.0)) ) - vs[v]

                        else:
                            if self.vi:
                                v.co = Vector((0.0, 0.0, 0.0))
                            else:
                                v.co = Vector((0.0, 0.0, 0.0)) - vs[v]



        bmesh.update_edit_mesh(ob.data)

        return {'FINISHED'}



class PS_OT_transfer_transform(Operator): # --- Transfer Transform Data
    bl_idname = 'object.ps_transfer_transform'
    bl_label = 'Transfer Transform Data'
    bl_description = 'Transfer transformation data (location/rotation/scale) from the active object to the selected object.'
    bl_options = {'REGISTER', 'UNDO'}


    loc: BoolProperty(name='Location', description = 'Transferring location data', default=True)
    rot: BoolProperty(name='Rotation', description = 'Transferring rotation data.', default=True)
    sca: BoolProperty(name='Scale', description = 'Transferring scaling data.', default=False)

    act_obj: None
    copy_loc: None
    copy_rot: None
    copy_sca: None

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and context.active_object


    def execute(self, context):
        act_obj = context.active_object
        objs = context.selected_objects

        for ob in objs:
            if self.loc:
                ob.location = self.copy_loc
            if self.rot:
                ob.rotation_euler = self.copy_rot
            if self.sca:
                ob.scale = self.copy_sca
        return {'FINISHED'}


    def invoke(self, context, event):
        self.act_obj = context.active_object
        self.copy_loc = self.act_obj.location.copy()
        self.copy_rot = self.act_obj.rotation_euler.copy()
        self.copy_sca = self.act_obj.scale.copy()
        return self.execute(context)



class PS_OT_addcamera(Operator): # FIXME
    bl_idname = "object.ps_addcamera"
    bl_label = "Add Camera"
    bl_description = ("Add Camera \n"
                     "and align to view")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.object.camera_add()
        bpy.ops.view3d.camera_to_view()
        context.space_data.lock_camera = True
        return {'FINISHED'}



class PS_OT_add_material(Operator): # --- Add Material
    bl_idname = 'object.ps_add_material'
    bl_label = 'Add Material'
    bl_description = 'Auto Smooth Angle 180'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # --- Get material
        mat = bpy.data.materials.get( 'PS Material' )
        if mat is None:
            # --- Create material
            mat = bpy.data.materials.new( name = 'PS Material' )


        for obj in context.selected_objects:
            """ # Assign it to object
            if obj.data.materials:
                # assign to 1st material slot
                obj.data.materials[0] = mat
            else:
                # no slots """
            obj.data.materials.append(mat)

            """ if context.mode == 'EDIT_MESH':
                bpy.ops.object.material_slot_assign() """
        return {'FINISHED'}





class PS_OT_fill_from_points(Operator):
    bl_idname = 'mesh.ps_fill_from_points'
    bl_label = 'Fill From Points'
    bl_options = {'REGISTER', 'UNDO'} #, 'DEPENDS_ON_CURSOR'


    #faces: BoolProperty(name='Faces', description = ' ', default=False)
    angle: FloatProperty(name='Angle', default=90.0)
    range_count: IntProperty(name='Range Count', default=1, min=1, max=100)

    def execute(self, context):
        from mathutils.geometry import tessellate_polygon, delaunay_2d_cdt
        import random
        import heapq
        from itertools import combinations
        from math import degrees, radians


        obj = context.object
        me = obj.data
        obj.update_from_editmode()
        bm = bmesh.from_edit_mesh(me)


        verts_old = [v for v in bm.verts]

        # Копируем вершины из исходного объекта
        verts = [bm.verts.new(v.co) for v in me.vertices]

        # --- удаление старых вершин
        for v in verts_old:
            bm.verts.remove(v)

        # Функция для расчета расстояния между двумя вершинами
        def calc_distance(vert1, vert2):
            return (vert1.co - vert2.co).length

        # Создаем минимальное остовное дерево
        # Используем кучу для оптимизации выбора минимального ребра
        edge_heap = []
        added_verts = set([verts[0]])
        for vert in verts[1:]:
            heapq.heappush(edge_heap, (calc_distance(verts[0], vert), 0, verts.index(vert)))

        while len(added_verts) < len(verts):
            dist, vert_from_idx, vert_to_idx = heapq.heappop(edge_heap)
            if verts[vert_to_idx] not in added_verts:
                added_verts.add(verts[vert_to_idx])
                bm.edges.new((verts[vert_from_idx], verts[vert_to_idx]))

                # Добавляем соседние ребра новой вершины в кучу
                for v_idx, vert in enumerate(verts):
                    if vert not in added_verts:
                        heapq.heappush(edge_heap, (calc_distance(verts[vert_to_idx], vert), vert_to_idx, v_idx))









            #
            """ for v in bm.verts:
                if len(v.link_edges) > 1:
                    edge0 = v.link_edges[0]
                    edge1 = v.link_edges[1]
                    vert0 = edge0.verts[0] if edge0.verts[0] in edge1.verts else edge0.verts[1]
                    vert1 = edge0.other_vert(vert0)
                    vert2 = edge1.other_vert(vert0)
                    vec0 = vert0.co - vert1.co
                    vec1 = vert0.co - vert2.co
                    angle = vec0.angle(vec1)
                    angle = angle if angle < radians(180) else (radians(360) - angle)
                    if angle <= radians(self.angle):
                        bmesh.ops.contextual_create(bm, geom=[vert0, vert1, vert2]) """



            """ def can_create_face(bm, verts):
                # Проверка на наличие существующих граней между вершинами
                existing_faces = set(frozenset(face.verts) for face in bm.faces)
                return not frozenset(verts) in existing_faces

            for _ in range(self.range_count):
                edge_pairs = []
                for v in bm.verts:
                    if len(v.link_edges) > 1:
                        boundary_edges = [e for e in v.link_edges if len(e.link_faces) <= 1]
                        for i, edge0 in enumerate(boundary_edges):
                            for edge1 in boundary_edges[i + 1:]:
                                edge_pairs.append((edge0, edge1, v))

                for edge0, edge1, common_vert in edge_pairs:
                    vert0 = edge0.other_vert(common_vert)
                    vert1 = edge1.other_vert(common_vert)
                    vec0 = common_vert.co - vert0.co
                    vec1 = common_vert.co - vert1.co
                    angle = vec0.angle(vec1)
                    if angle <= radians(self.angle):
                        if can_create_face(bm, [common_vert, vert0, vert1]):
                            bmesh.ops.contextual_create(bm, geom=[common_vert, vert0, vert1]) """








            bmesh.update_edit_mesh(me)





        return {'FINISHED'}





from bpy.props import (
    EnumProperty,
    BoolProperty,
    FloatProperty,
    IntProperty
)
from math import radians


class PS_OT_add_subsurf_and_bevel(Operator):
    bl_idname = "object.ps_add_subsurf_and_bevel"
    bl_label = "Add Subdivision And Bevel"
    bl_description = ' '
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}


    # Bevel properties
    bevel_segments: IntProperty(
        name="Segments",
        default=2,
        min=1,
        max=10,
        description="Number of segments for the bevel"
    )

    bevel_width: FloatProperty(
        name="Width",
        default=0.02,
        min=0.0,
        max=1.0,
        description="Bevel width"
    )

    bevel_angle: FloatProperty(
        name="Angle",
        default=60.0,
        min=0.0,
        max=180.0,
        description="Bevel angle"
    )

    use_clamp_overlap: BoolProperty(
        name="Clamp Overlap",
        default=True,
        description="Clamp overlap of beveled edges/vertices"
    )

    # Subdivision properties
    subdivision_levels: IntProperty(
        name="Levels",
        default=3,
        min=0,
        max=6,
        description="Number of subdivision levels"
    )

    # Preset options
    preset_mode: EnumProperty(
        items=[
            ('DEFAULT', "Default", "Default preset with weight-based bevels"),
            ('WIDE', "Wide Bevel", "Wider bevels without overlap clamping"),
            ('ANGLE', "Angle Based", "Angle-based bevels")
        ],
        name="Preset",
        default='DEFAULT'
    )

    def apply_preset(self, context, mod_bevel):
        if self.preset_mode == 'DEFAULT':
            mod_bevel.width = 0.02
            mod_bevel.use_clamp_overlap = True
            mod_bevel.segments = self.bevel_segments
        elif self.preset_mode == 'WIDE':
            mod_bevel.width = 0.15
            mod_bevel.use_clamp_overlap = False
            mod_bevel.segments = self.bevel_segments
        elif self.preset_mode == 'ANGLE':
            mod_bevel.angle_limit = self.bevel_angle * 3.14159 / 180.0  # Convert to radians
            mod_bevel.width = self.bevel_width
            mod_bevel.use_clamp_overlap = self.use_clamp_overlap
            mod_bevel.segments = self.bevel_segments

    def has_bevel_weights(self, obj):
        if obj.type != 'MESH':
            return False

        # Check for the bevel_weight_edge attribute
        if not obj.data.attributes.get('bevel_weight_edge'):
            return False

        # Check if any edges have non-zero bevel weight
        bevel_weight_layer = obj.data.attributes['bevel_weight_edge']
        for value in bevel_weight_layer.data:
            if value.value > 0:
                return True

        return False

    def setup_bevel_modifier(self, obj, mod_name):
        # Get or create bevel modifier
        mod_bevel = obj.modifiers.get(mod_name)
        if mod_bevel is None:
            mod_bevel = obj.modifiers.new(mod_name, 'BEVEL')

        # Configure bevel modifier based on presence of bevel weights
        mod_bevel.show_expanded = False
        mod_bevel.profile = 1

        if self.has_bevel_weights(obj):
            mod_bevel.limit_method = 'WEIGHT'
        else:
            mod_bevel.limit_method = 'ANGLE'

        # Apply preset settings
        self.apply_preset(bpy.context, mod_bevel)

        return mod_bevel

    def setup_subdivision_modifier(self, obj, mod_name):
        # Get or create subdivision modifier
        mod_subd = obj.modifiers.get(mod_name)
        if mod_subd is None:
            mod_subd = obj.modifiers.new(mod_name, 'SUBSURF')

        # Configure subdivision modifier
        mod_subd.show_expanded = False
        mod_subd.levels = self.subdivision_levels

        return mod_subd

    def execute(self, context):
        nameB = "PS Bevel"
        nameS = "PS Subdivision"

        for obj in context.selected_objects:
            if obj.type == 'MESH':
                self.setup_bevel_modifier(obj, nameB)
                self.setup_subdivision_modifier(obj, nameS)

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
    bl_idname = "object.ps_triangulate"
    bl_label = "Triangulate"
    bl_description = "Triangulate Modifier"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        name = "PS Triangulate"

        for obj in context.selected_objects:
            if obj.modifiers.get(name) is None:
                obj.modifiers.new(name, 'TRIANGULATE')
                obj.modifiers[name].show_expanded = False

            obj.modifiers[name].quad_method = 'FIXED'
            obj.modifiers[name].ngon_method = 'BEAUTY'
            obj.modifiers[name].min_vertices = 4
            #if bpy.app.version < (4, 2, 0):
            obj.modifiers[name].keep_custom_normals = True

        return {'FINISHED'}


class TrisWeightedNormal(Operator):
    bl_idname = 'object.ps_tris_weighted_normal'
    bl_label = "Tris & Weighted Normal"
    bl_description = "Triangulate mesh and fix normals"
    bl_options = {'REGISTER', 'UNDO'}

    # Параметры для Weighted Normal модификатора
    weight: IntProperty(
        name="Weight",
        default=50,
        min=0,
        max=100,
        description="Weight for normal calculation"
    )

    mode: EnumProperty(
        name="Mode",
        items=[
            ('FACE_AREA', "Face Area", "Weight by face area"),
            ('CORNER_ANGLE', "Corner Angle", "Weight by corner angle"),
            ('FACE_ANGLE', "Face Angle", "Weight by face angle"),
        ],
        default='FACE_AREA',
        description="Weight calculation mode"
    )

    thresh: FloatProperty(
        name="Threshold",
        default=0.01,
        min=0.0,
        max=1.0,
        description="Threshold for normal calculation"
    )

    keep_sharp: BoolProperty(
        name="Keep Sharp",
        default=True,
        description="Keep sharp edges"
    )

    use_face_influence: BoolProperty(
        name="Use Face Influence",
        default=False,
        description="Use face influence for normal calculation"
    )

    def execute(self, context):
        tri_mod = "PS Triangulate"
        n_mod = "PS Weighted Normal"

        for obj in context.selected_objects:
            # Сглаживание нормалей
            bpy.ops.object.shade_smooth()

            # normal fix
            if obj.modifiers.get(n_mod) is None:
                obj.modifiers.new(n_mod, 'WEIGHTED_NORMAL')
                obj.modifiers[n_mod].show_expanded = False

            obj.modifiers[n_mod].mode = self.mode
            obj.modifiers[n_mod].weight = self.weight
            obj.modifiers[n_mod].thresh = self.thresh
            obj.modifiers[n_mod].keep_sharp = self.keep_sharp
            obj.modifiers[n_mod].use_face_influence = self.use_face_influence

            # triangulate
            if obj.modifiers.get(tri_mod) is None:
                obj.modifiers.new(tri_mod, 'TRIANGULATE')
                obj.modifiers[tri_mod].show_expanded = False
            obj.modifiers[tri_mod].quad_method = 'FIXED'
            obj.modifiers[tri_mod].ngon_method = 'BEAUTY'
            obj.modifiers[tri_mod].min_vertices = 4
            #if bpy.app.version < (4, 2, 0):
            obj.modifiers[tri_mod].keep_custom_normals = True

        return {'FINISHED'}


class Solidify(Operator):
    bl_idname = 'object.ps_solidify'
    bl_label = "Solidify"
    bl_description = "Solidify Modifier"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        name = "PS Solidify"
        for obj in context.selected_objects:
            if obj.modifiers.get(name) is None:
                obj.modifiers.new(name, 'SOLIDIFY')
                obj.modifiers[name].show_expanded = False
            obj.modifiers[name].solidify_mode = 'NON_MANIFOLD'
            obj.modifiers[name].nonmanifold_boundary_mode = 'FLAT'
            obj.modifiers[name].offset = 1
            obj.modifiers[name].nonmanifold_thickness_mode = 'EVEN'
        return {'FINISHED'}


class SetEdgeData(Operator):
    bl_idname = 'mesh.ps_set_edge_data'
    bl_label = "Set Edge Data"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    bl_description = "Toggle edge data (Bevel/Cease/Seam/Sharp) for selected edges using booleans: if any selected edge has any chosen data -> clear all, else -> set all."

    do_bevel: BoolProperty(name='Bevel', default=False)
    do_crease: BoolProperty(name='Crease', default=False)
    do_seam: BoolProperty(name='Seam', default=False)
    do_sharp: BoolProperty(name='Sharp', default=False)

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    @classmethod
    def description(cls, context, properties):
        desc = "Toggle edge data"
        if properties.do_bevel:
            desc += " Bevel"
        if properties.do_crease:
            desc += " Crease"
        elif properties.do_seam:
            desc += " Seam"
        if properties.do_sharp:
            desc += " Sharp"
        desc += " for selected edges using booleans: if any selected edge has any chosen data -> clear all, else -> set all."
        return desc

    def execute(self, context):
        # проверяем, есть ли активные флаги; если нет — ничего не делаем
        if not any([self.do_bevel, self.do_crease, self.do_seam, self.do_sharp]):
            return {'CANCELLED'}

        uniques = list(context.objects_in_mode_unique_data)

        # первый проход: проверяем, присутствуют ли выбранные данные у каких-либо выделенных ребер
        any_has = False
        for obj in uniques:
            bm = bmesh.from_edit_mesh(obj.data)
            bevel_layer = bm.edges.layers.float.get('bevel_weight_edge') if self.do_bevel else None
            crease_layer = bm.edges.layers.float.get('crease_edge') if self.do_crease else None

            for edge in bm.edges:
                if not edge.select:
                    continue
                if self.do_bevel and bevel_layer and (edge[bevel_layer] > 0.0):
                    any_has = True
                    break
                if self.do_crease and crease_layer and (edge[crease_layer] > 0.0):
                    any_has = True
                    break
                if self.do_seam and edge.seam:
                    any_has = True
                    break
                if self.do_sharp and (edge.smooth is False):
                    any_has = True
                    break
            if any_has:
                break

        # второй проход: если что-то есть — выключаем, если пусто — включаем
        for obj in uniques:
            bm = bmesh.from_edit_mesh(obj.data)

            if any_has:
                # выключаем отмеченные опции
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
                # включаем отмеченные опции
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


class UnrealMaterial(Operator):
    bl_idname = 'object.ps_unreal_material'
    bl_label = "UE Material"
    bl_options = {'REGISTER', 'UNDO'}

    # Свойства для указания путей к текстурам
    base_color_texture: bpy.props.StringProperty(
        name="Base Color Texture",
        description="Path to Base Color texture",
        default="",
        subtype='FILE_PATH'
    )
    mask_texture: bpy.props.StringProperty(
        name="Mask Texture",
        description="Path to Mask texture (RGB: R-Roughness, G-Metallic, B-AO)",
        default="",
        subtype='FILE_PATH'
    )
    normal_texture: bpy.props.StringProperty(
        name="Normal Texture",
        description="Path to Normal texture",
        default="",
        subtype='FILE_PATH'
    )
    emissive_texture: bpy.props.StringProperty(
        name="Emissive Texture",
        description="Path to Emissive texture (red channel used)",
        default="",
        subtype='FILE_PATH'
    )

    # Дополнительные параметры для эмиссивного канала
    emissive_color: bpy.props.FloatVectorProperty(
        name="Emissive Color",
        subtype='COLOR',
        default=(1.0, 1.0, 1.0),
        min=0.0, max=1.0,
        description="Color multiplier for emissive texture"
    )
    emissive_intensity: bpy.props.FloatProperty(
        name="Emissive Intensity",
        default=1.0,
        description="Intensity for emission (set to BSDF's Emission Strength)"
    )

    # Флажок: применять к активному материалу
    apply_to_active: bpy.props.BoolProperty(
        name="Apply to Active Material",
        default=False,
        description="If enabled, re-build nodes in the active material instead of creating a new one"
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
            # Применяем изменения к активному материалу
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
            result = self.build_material_tree(mat)
            if result is None:
                return {'CANCELLED'}
        else:
            # Создаём новый материал и назначаем всем выделенным объектам типа MESH
            mat = bpy.data.materials.new(name="PS_UE_Material")
            mat.use_nodes = True
            result = self.build_material_tree(mat)
            if result is None:
                return {'CANCELLED'}
            self.apply_material_to_selected(mat, context)

        # Переключаем 3D-вид в режим отображения текстур (если применимо)
        if context.area and context.area.type == 'VIEW_3D':
            context.space_data.shading.color_type = 'TEXTURE'
        return {'FINISHED'}

    def build_material_tree(self, mat):
        # Очистка всех существующих нод
        nt = mat.node_tree
        nodes = nt.nodes
        links = nt.links
        for node in list(nodes):
            nodes.remove(node)

        # Создаем базовые ноды: Material Output и Principled BSDF
        output_node = nodes.new('ShaderNodeOutputMaterial')
        output_node.location = (600, 0)

        bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.location = (300, 0)
        links.new(bsdf.outputs['BSDF'], output_node.inputs['Surface'])

        # --- Base Color Texture ---
        base_color_node = None
        if self.base_color_texture:
            try:
                base_color_img = bpy.data.images.load(self.base_color_texture)
            except Exception as e:
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

        # --- Mask Texture (RGB: R-Roughness, G-Metallic, B-AO) ---
        if self.mask_texture:
            try:
                mask_img = bpy.data.images.load(self.mask_texture)
            except Exception as e:
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

            separate_mask = nodes.new('ShaderNodeSeparateRGB')
            separate_mask.location = (-200, 0)
            links.new(separate_mask.inputs['Image'], mask_node.outputs['Color'])

            links.new(bsdf.inputs['Roughness'], separate_mask.outputs['R'])
            links.new(bsdf.inputs['Metallic'], separate_mask.outputs['G'])

            # Если Base Color задан – смешиваем его с AO (B-канал)
            if base_color_node:
                # Удаляем прямое соединение Base Color → BSDF
                for link in list(nt.links):
                    if link.from_socket == base_color_node.outputs['Color'] and link.to_socket == bsdf.inputs['Base Color']:
                        nt.links.remove(link)
                mix_ao = nodes.new('ShaderNodeMixRGB')
                mix_ao.blend_type = 'MULTIPLY'
                mix_ao.inputs['Fac'].default_value = 1.0
                mix_ao.location = (0, 300)
                links.new(mix_ao.inputs[1], base_color_node.outputs['Color'])
                links.new(mix_ao.inputs[2], separate_mask.outputs['B'])
                links.new(bsdf.inputs['Base Color'], mix_ao.outputs['Color'])

        # --- Normal Texture (с инвертированием зелёного канала) ---
        if self.normal_texture:
            try:
                normal_img = bpy.data.images.load(self.normal_texture)
            except Exception as e:
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

            separate_normal = nodes.new('ShaderNodeSeparateRGB')
            separate_normal.location = (-200, -300)
            links.new(separate_normal.inputs['Image'], normal_tex.outputs['Color'])

            invert_green = nodes.new('ShaderNodeMath')
            invert_green.operation = 'SUBTRACT'
            invert_green.inputs[0].default_value = 1.0
            invert_green.location = (0, -300)
            links.new(invert_green.inputs[1], separate_normal.outputs['G'])

            combine_normal = nodes.new('ShaderNodeCombineRGB')
            combine_normal.location = (200, -300)
            links.new(combine_normal.inputs['R'], separate_normal.outputs['R'])
            links.new(combine_normal.inputs['G'], invert_green.outputs['Value'])
            links.new(combine_normal.inputs['B'], separate_normal.outputs['B'])

            normal_map = nodes.new('ShaderNodeNormalMap')
            normal_map.location = (400, -300)
            normal_map.space = 'TANGENT'
            links.new(normal_map.inputs['Color'], combine_normal.outputs['Image'])
            links.new(bsdf.inputs['Normal'], normal_map.outputs['Normal'])

        # --- Emissive Texture ---
        if self.emissive_texture:
            try:
                emissive_img = bpy.data.images.load(self.emissive_texture)
            except Exception as e:
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

            separate_emissive = nodes.new('ShaderNodeSeparateRGB')
            separate_emissive.location = (-200, -600)
            links.new(separate_emissive.inputs['Image'], emissive_tex.outputs['Color'])

            # Берем только красный канал и умножаем его на выбранный цвет
            emissive_color_node = nodes.new('ShaderNodeRGB')
            emissive_color_node.location = (-200, -700)
            emissive_color_node.outputs[0].default_value = (self.emissive_color[0],
                                                            self.emissive_color[1],
                                                            self.emissive_color[2],
                                                            1.0)

            multiply_emissive = nodes.new('ShaderNodeMixRGB')
            multiply_emissive.blend_type = 'MULTIPLY'
            multiply_emissive.inputs['Fac'].default_value = 1.0
            multiply_emissive.location = (0, -600)
            links.new(multiply_emissive.inputs[1], emissive_color_node.outputs['Color'])
            links.new(multiply_emissive.inputs[2], separate_emissive.outputs['R'])

            # Подключаем результат к Emission входу BSDF и задаем интенсивность через Emission Strength
            links.new(bsdf.inputs['Emission'], multiply_emissive.outputs['Color'])
            bsdf.inputs['Emission Strength'].default_value = self.emissive_intensity

        return mat

    def apply_material_to_selected(self, material, context):
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                if not obj.data.materials:
                    obj.data.materials.append(material)
                else:
                    obj.data.materials[0] = material



# --- Bool Tool
# part of the functionality of the standard addon in blender 'Bool Tool' is taken as a basis
# TODO add the ability to work in Brush mode with multiple objects
class PS_Boolean:
    keep_bool_obj: BoolProperty(default=False)
    brush_mode: BoolProperty(default=False)

    def objects_prepare(self):
        for ob in bpy.context.selected_objects:
            if ob.type != "MESH":
                ob.select_set(False)
        bpy.ops.object.make_single_user(object=True, obdata=True)
        bpy.ops.object.convert(target="MESH")

    def mesh_selection(self, ob, select_action):
        obj = bpy.context.active_object

        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.mode_set(mode="EDIT")

        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_all(action=select_action)

        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.context.view_layer.objects.active = obj

    def boolean_operation(self):
        obj = bpy.context.active_object
        obj.select_set(False)
        obs = bpy.context.selected_objects

        self.mesh_selection(obj, "DESELECT")

        for ob in obs:
            self.mesh_selection(ob, "SELECT")
            self.boolean_mod(obj, ob, self.mode)

        obj.select_set(True)

    def boolean_mod(self, obj, ob, mode, ob_delete=True):
        md = obj.modifiers.new("PS Boolean", "BOOLEAN")
        md.show_viewport = self.brush_mode
        md.operation = mode
        md.object = ob

        if self.brush_mode is False:
            context_override = {'object': obj}
            with bpy.context.temp_override(**context_override):
                bpy.ops.object.modifier_apply(modifier=md.name)

            if self.keep_bool_obj is False: # ob_delete
                bpy.data.objects.remove(ob)
        else:
            ob.display_type = 'BOUNDS'


    def execute(self, context):
        self.objects_prepare()
        self.boolean_operation()
        return {"FINISHED"}

    def invoke(self, context, event):
        if event.shift:
            self.keep_bool_obj = True
        else:
            self.keep_bool_obj = False
        if event.ctrl:
            self.brush_mode = True
        else:
            self.brush_mode = False
        if len(context.selected_objects) < 2:
            self.report({"ERROR"}, "At least two objects must be selected")
            return {"CANCELLED"}
        return self.execute(context)


class PS_OT_bool_difference(Operator, PS_Boolean):
    bl_idname = "object.ps_bool_difference"
    bl_label = "Bool Difference"
    bl_description = ("Subtract selected objects from active object \n"
                      "• Shift+LMB - Do not delete Bool Object \n"
                      "• Ctrl+LMB - Brush mode")
    bl_options = {"REGISTER", "UNDO"}
    mode = "DIFFERENCE"


class PS_OT_bool_union(Operator, PS_Boolean):
    bl_idname = "object.ps_bool_union"
    bl_label = "Bool Union"
    bl_description = ("Combine selected objects \n"
                      "• Shift+LMB - Do not delete Bool Object \n"
                      "• Ctrl+LMB - Brush mode")
    bl_options = {"REGISTER", "UNDO"}
    mode = "UNION"


class PS_OT_bool_intersect(Operator, PS_Boolean):
    bl_idname = "object.ps_bool_intersect"
    bl_label = "Bool Intersect"
    bl_description = ("Keep only intersecting geometry \n"
                      "• Shift+LMB - Do not delete Bool Object \n"
                      "• Ctrl+LMB - Brush mode")
    bl_options = {"REGISTER", "UNDO"}
    mode = "INTERSECT"


class PS_OT_bool_slice(Operator, PS_Boolean):
    bl_idname = "object.ps_bool_slice"
    bl_label = "Bool Slice"
    bl_description = ("Slice active object along the selected objects \n"
                      "• Shift+LMB - Do not delete Bool Object \n"
                      "• Ctrl+LMB - Brush mode")

    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        space_data = get_active_3d_view()
        if space_data is not None:
            is_local_view = bool(space_data.local_view)
            self.objects_prepare()

            ob1 = context.active_object
            ob1.select_set(False)
            self.mesh_selection(ob1, "DESELECT")

            for ob2 in context.selected_objects:

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

            context.view_layer.objects.active = ob1_copy

        return {"FINISHED"}














import mathutils

class PS_OT_Distribute_Objects(Operator):
    bl_idname = "object.ps_distribute_objects"
    bl_label = "Distribute Objects (TEST)"
    bl_description = "Translate selected objects with spacing adjusted to their sizes"
    bl_options = {'REGISTER', 'UNDO'}

    expose_factor: bpy.props.FloatProperty(
        name="Expose Factor",
        description="Object spacing factor (from 0 to 1)",
        min=0.0,
        max=1.0,
        default=1.0,
    )

    _objects_data = None  # Временное хранилище для данных объектов

    def execute(self, context):
        if self._objects_data is None:
            objects = context.selected_objects
            if not objects:
                self.report({'WARNING'}, "No objects selected")
                return {'CANCELLED'}

            # Вычисляем ширины объектов и их начальные и конечные позиции
            widths = []
            objects_data = []
            total_width = 0.0
            padding = 0.1  # Отступ между объектами

            for obj in objects:
                bbox = [obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box]
                min_x = min([v.x for v in bbox])
                max_x = max([v.x for v in bbox])
                width = max_x - min_x
                widths.append(width)
                total_width += width + padding  # Добавляем отступы между объектами

            total_width -= padding  # Убираем отступ после последнего объекта

            # Начальная позиция для размещения объектов
            current_x = -total_width / 2.0  # Центрируем объекты относительно исходной позиции

            for i, obj in enumerate(objects):
                width = widths[i]

                initial_position = obj.location.copy()

                # Вычисляем конечную позицию
                final_position = initial_position.copy()
                final_position.x = current_x + width / 2.0
                final_position.y = initial_position.y  # Оставляем Y без изменений
                final_position.z = initial_position.z  # Оставляем Z без изменений

                # Сохраняем данные объекта
                objects_data.append({
                    'object': obj,
                    'initial_position': initial_position,
                    'final_position': final_position
                })

                current_x += width + padding  # Переходим к следующей позиции

            self._objects_data = objects_data

        # Применяем раздвижение объектов на основе expose_factor
        for data in self._objects_data:
            obj = data['object']
            initial_position = data['initial_position']
            final_position = data['final_position']
            obj.location = initial_position.lerp(final_position, self.expose_factor)

        return {'FINISHED'}

    def invoke(self, context, event):
        self._objects_data = None  # Сбрасываем данные при каждом вызове
        #wm = context.window_manager
        return self.execute(context) #wm.invoke_props_popup(self, event)

    """ def draw(self, context):
        layout = self.layout
        layout.prop(self, "expose_factor", slider=True) """




classes = [
    PS_OT_select_polygons,
    PS_OT_random_name,

    PS_OT_clear_dots,
    PS_OT_remove_vertex_non_manifold,
    PS_OT_clear_materials,
    PS_OT_clear_data,

    PS_OT_reset_location_object,
    PS_OT_reset_rotation_object,
    PS_OT_reset_scale_object,
    PS_OT_locvert,
    PS_OT_transfer_transform,
    PS_OT_addcamera,
    PS_OT_add_material,
    PS_OT_fill_from_points,
    PS_OT_add_subsurf_and_bevel,
    PS_OT_triangulate,
    TrisWeightedNormal,
    Solidify,
    SetEdgeData,

    UnrealMaterial,

    PS_OT_bool_difference,
    PS_OT_bool_union,
    PS_OT_bool_intersect,
    PS_OT_bool_slice,

    PS_OT_Distribute_Objects,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)