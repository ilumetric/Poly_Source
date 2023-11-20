import bpy
import bmesh
from bpy.types import Operator
from bpy.props import EnumProperty, BoolProperty, FloatProperty, IntProperty
from mathutils import Vector, Euler




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
            obj.data.use_auto_smooth = True
            obj.data.auto_smooth_angle = 3.14159
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
    PS_OT_autosmooth,
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
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)