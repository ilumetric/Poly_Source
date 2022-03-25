import bpy
import bmesh
from mathutils import Vector, Euler
from bpy.types import Operator
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


classes = [
    PS_OT_reset_location_object,
    PS_OT_reset_rotation_object,
    PS_OT_reset_scale_object,
    PS_OT_locvert,
    PS_OT_autosmooth,
    PS_OT_transfer_transform,
    PS_OT_addcamera,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)