import bpy
import bmesh
from bpy.types import Operator
from bpy.props import EnumProperty, BoolProperty, FloatProperty, IntProperty
from mathutils import Vector, Euler
from .utils import get_active_3d_view



# --- Get Polygons
class PS_OT_ngons_select(Operator):
    bl_idname = 'ps.ngons_select'
    bl_label = 'N-Gons Select'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'Number Of N-Gons. Click To Select'
             
    @classmethod
    def poll(cls, context):
        if context.active_object:
            return context.active_object.type == 'MESH'

    def execute(self, context):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_face_by_sides(number=4, type='GREATER')
        return {'FINISHED'}


class PS_OT_quads_select(Operator):
    bl_idname = 'ps.quads_select'
    bl_label = 'Quads Select'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'Number Of Quads. Click To Select'

    @classmethod
    def poll(cls, context):
        if context.active_object:
            return context.active_object.type == 'MESH'

    def execute(self, context):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_face_by_sides(number=4, type='EQUAL')
        return {'FINISHED'}


class PS_OT_tris_select(Operator):
    bl_idname = 'ps.tris_select'
    bl_label = 'Tris Select'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'Number Of Tris. Click To Select'

    @classmethod
    def poll(cls, context):
        if context.active_object:
            return context.active_object.type == 'MESH'
            
    def execute(self, context):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_face_by_sides(number=3, type='EQUAL')
        return {'FINISHED'}






class PS_OT_clear_dots(Operator):
    bl_idname = "ps.clear_dots"
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
    bl_idname = "ps.remove_vertex_non_manifold"
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
    bl_idname = 'ps.clear_materials'
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
    bl_idname = 'ps.clear_data'
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
    bl_idname = "ps.reset_location_object"
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
    bl_idname = 'ps.reset_rotation_object'
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
    bl_idname = 'ps.reset_scale_object'
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
    bl_idname = 'ps.locvert'
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



class PS_OT_autosmooth(Operator): # --- Auto Smooth 
    bl_idname = "ps.autosmooth"
    bl_label = "Angle 180"
    bl_description = "Auto Smooth Angle 180"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in context.selected_objects:
            obj.data.use_auto_smooth = True
            obj.data.auto_smooth_angle = 3.14159
        return {'FINISHED'} 



class PS_OT_transfer_transform(Operator): # --- Transfer Transform Data
    bl_idname = 'ps.transfer_transform'
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
    bl_idname = "ps.addcamera"
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
    bl_idname = 'ps.add_material'
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
    bl_idname = 'ps.fill_from_points'
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



class PS_OT_submod(Operator): # --- Modifieres Bevel And Subsurf
    bl_idname = "ps.submod"
    bl_label = "Add Subdivision And Bevel Modifier"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        nameB = "PS Bevel"
        nameS = "PS Subdivision"

        for obj in context.selected_objects:

            if obj.modifiers.get(nameB) is None:
                obj.modifiers.new(nameB, 'BEVEL')
                obj.modifiers[nameB].show_expanded = False
                obj.modifiers[nameB].profile = 1
                obj.modifiers[nameB].segments = 2
                obj.modifiers[nameB].limit_method = 'WEIGHT'

            if obj.modifiers.get(nameS) is None:
                obj.modifiers.new(nameS, 'SUBSURF')
                obj.modifiers[nameS].show_expanded = False
                obj.modifiers[nameS].levels = 3

        return {'FINISHED'} 



class PS_OT_add_mirror_mod(Operator): # --- Modifieres Mirror
    
    bl_idname = "ps.add_mirror_mod"
    bl_label = "Mirror Modifier"
    bl_options = {'REGISTER', 'UNDO'}

    axis: EnumProperty(
        name='Axis',
        items=[
            ('X', 'X Axis', '', '', 0),
            ('Y', 'Y Axis', '', '', 1),
            ('Z', 'Z Axis', '', '', 2)],
            default='X',
            )

    uv_offset: BoolProperty(name="UV Offset", description = "Shift the UV to +1 to avoid overlaps.", default=True)
    show_on_cage: BoolProperty(name="On Cage", description = "Adjust edit cage to modifier result.", default=False)

    mirror_x: BoolProperty(name="Mirror X", description = "Mirror the U(X) texture coordinate around the flip offset point.", default=False)
    mirror_y: BoolProperty(name="Mirror Y", description = "Mirror the V(Y) texture coordinate around the flip offset point.", default=False)


    def execute(self, context):
        name = "PS Mirror"
       
        for obj in context.selected_objects:

            if obj.modifiers.get(name) is None:
                obj.modifiers.new(name, 'MIRROR')
                obj.modifiers[name].show_expanded = False
                obj.modifiers[name].use_axis[0] = False
         
            obj.modifiers[name].show_on_cage = self.show_on_cage

            if self.axis == 'X':
                obj.modifiers[name].use_axis[0] = True
                #obj.modifiers[name].use_bisect_axis[0] = True

            elif self.axis == 'Y':
                obj.modifiers[name].use_axis[1] = True
                #obj.modifiers[name].use_bisect_axis[1] = True

            elif self.axis == 'Z':
                obj.modifiers[name].use_axis[2] = True
                #obj.modifiers[name].use_bisect_axis[2] = True

            if self.uv_offset:
                obj.modifiers[name].offset_u = 1.0

            obj.modifiers[name].use_mirror_u = self.mirror_x
            obj.modifiers[name].use_mirror_v = self.mirror_y

        return {'FINISHED'} 



class PS_OT_triangulate(Operator): # --- Triangulate
    bl_idname = "ps.triangulate"
    bl_label = "Triangulate"
    bl_description = ("Triangulate Modifier")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        name = "PS Triangulate"
       
        for obj in context.selected_objects:
            if obj.modifiers.get(name) is None:
                obj.modifiers.new(name, 'TRIANGULATE')
                obj.modifiers[name].show_expanded = False

            obj.modifiers[name].quad_method = 'BEAUTY'
            obj.modifiers[name].ngon_method = 'BEAUTY'
            obj.modifiers[name].min_vertices = 4
            if bpy.app.version < (4, 2, 0):
                obj.modifiers[name].keep_custom_normals = False

        return {'FINISHED'} 



class PS_OT_solidify(Operator): # --- Solidify
    bl_idname = "ps.solidify"
    bl_label = "Solidify"
    bl_description = ("Solidify Modifier")
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



class PS_OT_normalfix(Operator): # --- Normal Fix
    bl_idname = "ps.normalfix"
    bl_label = "Normal fix"
    bl_description = ("Fix Weighted Normal \n"
                     "(Maya normals etc.)")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        name = "PS Weighted Normal"
       
        for obj in context.selected_objects:
            if obj.modifiers.get(name) is None:
                obj.modifiers.new(name, 'WEIGHTED_NORMAL')
                obj.modifiers[name].show_expanded = False

            obj.modifiers[name].keep_sharp = True
            obj.modifiers[name].weight = 50
            obj.modifiers[name].mode = 'FACE_AREA'
            obj.modifiers[name].thresh = 0.01
           
        return {'FINISHED'} 



class PS_OT_edge_data(Operator): # --- Bevel & Crease
    bl_idname = "ps.edge_data"
    bl_label = 'Mark'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    
    
    mode: EnumProperty(
        name='Mode',
        items=[
            ('BEVEL', 'Bevel Weight', '', '', 0),
            ('CREASE', 'Crease Weight', '', '', 1),
            ('SEAM', 'Seam', '', '', 2),
            ('SHARP', 'Sharp', '', '', 3),
            ],
            default='BEVEL',
            )


    @classmethod
    def poll(self, context):
        return context.mode == 'EDIT_MESH'


    def execute(self, context):
        for obj in context.objects_in_mode_unique_data:
            bm = bmesh.from_edit_mesh(obj.data)
            
            if self.mode == 'BEVEL':
                if 'bevel_weight_edge' not in obj.data.attributes:
                    bevel_edge = bm.edges.layers.float.new('bevel_weight_edge')
                else:
                    bevel_edge = bm.edges.layers.float.get('bevel_weight_edge')

                for edge in bm.edges:
                    if edge.select:
                        if edge[bevel_edge] > 0.0:
                            for e in bm.edges:
                                if e.select:
                                    e[bevel_edge] = 0.0
                            break
                        else:
                            edge[bevel_edge] = 1.0
           
            elif self.mode == 'CREASE':
                if 'crease_edge' not in obj.data.attributes:
                    crease_edge = bm.edges.layers.float.new('crease_edge')
                else:
                    crease_edge = bm.edges.layers.float.get('crease_edge')

                for edge in bm.edges:
                    if edge.select:
                        if edge[crease_edge] > 0.0:
                            for e in bm.edges:
                                if e.select:
                                    e[crease_edge] = 0.0
                            break
                        else:
                            edge[crease_edge] = 1.0

            elif self.mode == 'SEAM':
                for edge in bm.edges:
                    if edge.select:
                        if edge.seam:
                            for e in bm.edges:
                                if e.select:
                                    e.seam = False
                            break
                        else:
                            edge.seam = True

            elif self.mode == 'SHARP':
                for edge in bm.edges:
                    if edge.select:
                        if edge.smooth:
                            for e in bm.edges:
                                if e.select:
                                    e.smooth = False
                            break
                        else:
                            edge.smooth = True

            bmesh.update_edit_mesh(obj.data)
        return {'FINISHED'}



# TODO
class PS_OT_unreal_material(Operator):
    bl_idname = "ps.unreal_material"
    bl_label = "UE Material"
    bl_options = {'REGISTER', 'UNDO'}

    # Panel properties
    base_color_texture: bpy.props.BoolProperty(name="Base Color Texture", default=True)
    rgb_mask_texture: bpy.props.BoolProperty(name="RGB Mask Texture", default=True)
    normal_map_texture: bpy.props.BoolProperty(name="Normal Map Texture", default=True)
    alpha_texture: bpy.props.BoolProperty(name="Alpha Texture", default=False)
    #invert_normal_g: bpy.props.BoolProperty(name="Invert G Channel in Normal Map", default=True)

    #base_color_texture_path: bpy.props.StringProperty(name="Base Color Texture Path", subtype='FILE_PATH')
    #rgb_mask_texture_path: bpy.props.StringProperty(name="RGB Mask Texture Path", subtype='FILE_PATH')
    #normal_map_texture_path: bpy.props.StringProperty(name="Normal Map Texture Path", subtype='FILE_PATH')
    #alpha_texture_path: bpy.props.StringProperty(name="Alpha Texture Path", subtype='FILE_PATH')

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(self, "base_color_texture")
        #row.prop(self, "base_color_texture_path")

        row = layout.row()
        row.prop(self, "rgb_mask_texture")
        #row.prop(self, "rgb_mask_texture_path")

        row = layout.row()
        row.prop(self, "normal_map_texture")
        #row.prop(self, "normal_map_texture_path")

        row = layout.row()
        row.prop(self, "alpha_texture")
        #row.prop(self, "alpha_texture_path")




    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        material = self.create_material()
        self.apply_material_to_selected(material, context)
        bpy.context.space_data.shading.color_type = 'TEXTURE'
        return {'FINISHED'}

    """ def load_texture(self, mat, file_path):
        tex_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
        if file_path != '':
            tex_node.image = bpy.data.images.load(file_path)
        return tex_node """

    def create_material(self):
        mat = bpy.data.materials.new(name="PS_UE_Material")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get('Principled BSDF')
        bsdf.location = (0, 500)

        if self.base_color_texture:
            tex_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
            tex_node.name = 'Base Color Texture'
            tex_node.label = 'Base Color Texture'
            tex_node.location = (-400, 400)
            #tex_node = self.load_texture(mat, self.base_color_texture_path)
            mat.node_tree.links.new(bsdf.inputs['Base Color'], tex_node.outputs['Color'])

        if self.rgb_mask_texture:
            tex_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
            tex_node.name = 'RGB Mask Texture'
            tex_node.label = 'RGB Mask Texture'
            tex_node.location = (-400, 200)
            #tex_node.color_space = 'None-Color'
            #tex_node = self.load_texture(mat, self.rgb_mask_texture_path)
            separate_rgb_node = mat.node_tree.nodes.new('ShaderNodeSeparateColor')
            separate_rgb_node.mode = 'RGB'
            mat.node_tree.links.new(separate_rgb_node.inputs['Color'], tex_node.outputs['Color'])
            mat.node_tree.links.new(bsdf.inputs['Roughness'], separate_rgb_node.outputs[0])
            mat.node_tree.links.new(bsdf.inputs['Metallic'], separate_rgb_node.outputs[1])
            #mat.node_tree.links.new(bsdf.inputs['Ambient Occlusion'], separate_rgb_node.outputs['B'])

        if self.normal_map_texture:
            tex_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
            tex_node.name = 'Normal Map Texture'
            tex_node.label = 'Normal Map Texture'
            tex_node.location = (-400, 0)
            #tex_node.color_space = 'None-Color'
            #tex_node = self.load_texture(mat, self.normal_map_texture_path)
            
            # Создание ноды Separate XYZ
            separate_xyz_node = mat.node_tree.nodes.new('ShaderNodeSeparateXYZ')
            mat.node_tree.links.new(separate_xyz_node.inputs['Vector'], tex_node.outputs['Color'])

            # Создание ноды Invert для инвертирования канала Y
            invert_node = mat.node_tree.nodes.new('ShaderNodeInvert')
            mat.node_tree.links.new(invert_node.inputs['Color'], separate_xyz_node.outputs['Y'])

            # Создание ноды Combine XYZ
            combine_xyz_node = mat.node_tree.nodes.new('ShaderNodeCombineXYZ')
            mat.node_tree.links.new(combine_xyz_node.inputs['X'], separate_xyz_node.outputs['X'])
            mat.node_tree.links.new(combine_xyz_node.inputs['Y'], invert_node.outputs['Color'])
            mat.node_tree.links.new(combine_xyz_node.inputs['Z'], separate_xyz_node.outputs['Z'])

            # Создание ноды Normal Map
            normal_map_node = mat.node_tree.nodes.new('ShaderNodeNormalMap')
            normal_map_node.space = 'TANGENT'
            mat.node_tree.links.new(normal_map_node.inputs['Color'], combine_xyz_node.outputs['Vector'])

            # Соединение ноды Normal Map с Principled BSDF
            mat.node_tree.links.new(bsdf.inputs['Normal'], normal_map_node.outputs['Normal'])


        if self.alpha_texture:
            tex_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
            tex_node.name = 'Alpha Texture'
            tex_node.label = 'Alpha Texture'
            tex_node.location = (-400, 200)
            #tex_node = self.load_texture(mat, self.alpha_texture_path)
            mat.node_tree.links.new(bsdf.inputs['Alpha'], tex_node.outputs['Color'])

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
    bl_idname = "ps.bool_difference"
    bl_label = "Bool Difference"
    bl_description = ("Subtract selected objects from active object \n"
                      "• Shift+LMB - Do not delete Bool Object \n"
                      "• Ctrl+LMB - Brush mode")
    bl_options = {"REGISTER", "UNDO"}
    mode = "DIFFERENCE"


class PS_OT_bool_union(Operator, PS_Boolean):
    bl_idname = "ps.bool_union"
    bl_label = "Bool Union"
    bl_description = ("Combine selected objects \n"
                      "• Shift+LMB - Do not delete Bool Object \n"
                      "• Ctrl+LMB - Brush mode")
    bl_options = {"REGISTER", "UNDO"}
    mode = "UNION"


class PS_OT_bool_intersect(Operator, PS_Boolean):
    bl_idname = "ps.bool_intersect"
    bl_label = "Bool Intersect"
    bl_description = ("Keep only intersecting geometry \n"
                      "• Shift+LMB - Do not delete Bool Object \n"
                      "• Ctrl+LMB - Brush mode")
    bl_options = {"REGISTER", "UNDO"}
    mode = "INTERSECT"


class PS_OT_bool_slice(Operator, PS_Boolean):
    bl_idname = "ps.bool_slice"
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
    bl_idname = "ps.distribute_objects"
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
    PS_OT_ngons_select,
    PS_OT_tris_select,
    PS_OT_quads_select,

    PS_OT_clear_dots,
    PS_OT_remove_vertex_non_manifold,
    PS_OT_clear_materials,
    PS_OT_clear_data,

    PS_OT_reset_location_object,
    PS_OT_reset_rotation_object,
    PS_OT_reset_scale_object,
    PS_OT_locvert,
    #PS_OT_autosmooth,
    PS_OT_transfer_transform,
    PS_OT_addcamera,
    PS_OT_add_material,
    PS_OT_fill_from_points,
    PS_OT_submod,
    PS_OT_add_mirror_mod,
    PS_OT_triangulate,
    PS_OT_solidify,
    PS_OT_normalfix,
    PS_OT_edge_data,

    PS_OT_unreal_material,

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