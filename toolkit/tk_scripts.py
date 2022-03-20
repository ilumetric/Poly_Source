import bpy
import bmesh 
import array
from mathutils import Matrix, Vector, Euler

from bpy.types import Operator, PropertyGroup
from bpy.props import EnumProperty, BoolProperty




#=======================================================RESET OBJECT=========================================================
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
    bl_options = {'REGISTER', 'UNDO', 'DEPENDS_ON_CURSOR' }

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
        
        vs_g = {}
        vs = {}
        for ob in uniques:
            for v in bms[ob].verts:
                vs_g[v] = l_g - v.co
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



# --- Modifieres Bevel And Subsurf
class PS_OT_submod(Operator):
    bl_idname = "ps.submod"
    bl_label = "Add Subdivision And Bevel Modifier"
    bl_options = {'REGISTER', 'UNDO'}

    
    def execute(self, context):
        
        nameB = "PS Bevel"
        nameS = "PS Subdivision"

        for obj in context.selected_objects:

            if obj.modifiers.get(nameB) is None:
                obj.modifiers.new(nameB, 'BEVEL')
         
                obj.modifiers[nameB].profile = 1
                obj.modifiers[nameB].segments = 2
                obj.modifiers[nameB].limit_method = 'WEIGHT'

            if obj.modifiers.get(nameS) is None:
                obj.modifiers.new(nameS, 'SUBSURF')
                obj.modifiers[nameS].levels = 3


        return {'FINISHED'} 



# --- Modifieres Mirror
class PS_OT_add_mirror_mod(Operator):
    
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
                obj.modifiers[name].use_axis[0] = False
         
            obj.modifiers[name].show_on_cage = self.show_on_cage

            if self.axis == 'X':
                obj.modifiers[name].use_axis[0] = True
                obj.modifiers[name].use_bisect_axis[0] = True

            elif self.axis == 'Y':
                obj.modifiers[name].use_axis[1] = True
                obj.modifiers[name].use_bisect_axis[1] = True

            elif self.axis == 'Z':
                obj.modifiers[name].use_axis[2] = True
                obj.modifiers[name].use_bisect_axis[2] = True

            if self.uv_offset:
                obj.modifiers[name].offset_u = 1.0

          
            obj.modifiers[name].use_mirror_u = self.mirror_x
            obj.modifiers[name].use_mirror_v = self.mirror_y

        return {'FINISHED'} 



# --- Auto Smooth 
class PS_OT_autosmooth(Operator):
    bl_idname = "ps.autosmooth"
    bl_label = "Angle 180"
    bl_description = "Auto Smooth Angle 180"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in context.selected_objects:
            obj.data.use_auto_smooth = True
            obj.data.auto_smooth_angle = 3.14159
        return {'FINISHED'} 



# --- Triangulate
class PS_OT_triangulate(Operator):
    bl_idname = "ps.triangulate"
    bl_label = "Triangulate"
    bl_description = ("Triangulate Modifier")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        name = "PS Triangulate"
       
        for obj in context.selected_objects:
            if obj.modifiers.get(name) is None:
                obj.modifiers.new(name, 'TRIANGULATE')



            obj.modifiers[name].quad_method = 'BEAUTY'
            obj.modifiers[name].ngon_method = 'BEAUTY'
            obj.modifiers[name].min_vertices = 4
            obj.modifiers[name].keep_custom_normals = False

        return {'FINISHED'} 



# --- Solidify
class PS_OT_solidify(Operator):
    bl_idname = "ps.solidify"
    bl_label = "Solidify"
    bl_description = ("Solidify Modifier")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        name = "PS Solidify"
       
        for obj in context.selected_objects:
            if obj.modifiers.get(name) is None:
                obj.modifiers.new(name, 'SOLIDIFY')



            obj.modifiers[name].solidify_mode = 'NON_MANIFOLD'
            obj.modifiers[name].nonmanifold_boundary_mode = 'FLAT'
            obj.modifiers[name].offset = 1
            obj.modifiers[name].nonmanifold_thickness_mode = 'EVEN'

        return {'FINISHED'} 



# --- Normal Fix
class PS_OT_normalfix(Operator):
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

            obj.modifiers[name].keep_sharp = True
            obj.modifiers[name].weight = 50
            obj.modifiers[name].mode = 'FACE_AREA'
            obj.modifiers[name].thresh = 0.01
           

        return {'FINISHED'} 



# --- Bevel & Crease
class PS_OT_edge_data(Operator):
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


    def execute(self, context):
        
        for obj in context.selected_objects:
            bm = bmesh.from_edit_mesh(obj.data)
            
            if self.mode == 'BEVEL':
                bw = bm.edges.layers.bevel_weight.verify()

                for edge in bm.edges:
                    if edge.select:
                        if edge[bw] > 0.0:
                            for e in bm.edges:
                                if e.select:
                                    e[bw] = 0.0
                            break
                        else:
                            edge[bw] = 1.0
           
            elif self.mode == 'CREASE':
                cw = bm.edges.layers.crease.verify()

                for edge in bm.edges:
                    if edge.select:
                        if edge[cw] > 0.0:
                            for e in bm.edges:
                                if e.select:
                                    e[cw] = 0.0
                            break
                        else:
                            edge[cw] = 1.0

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


        #dg = context.evaluated_depsgraph_get()
        #dg.update()
        #context.view_layer.update()
        #if context.area:
        #context.area.tag_redraw()
        return {'FINISHED'}




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










classes = [
    PS_OT_reset_location_object,
    PS_OT_reset_rotation_object,
    PS_OT_reset_scale_object,
    PS_OT_locvert,
    PS_OT_submod,
    PS_OT_autosmooth,
    PS_OT_triangulate,
    PS_OT_solidify,
    PS_OT_normalfix,
    PS_OT_addcamera,
    PS_OT_add_mirror_mod,
    PS_OT_edge_data,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

   
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)