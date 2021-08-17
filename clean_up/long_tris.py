import bpy
import bmesh
from bpy.types import Operator
from bpy.props import BoolProperty, IntProperty, FloatProperty


class PS_OT_del_long_faces(Operator):
    bl_idname = "ps.del_long_faces"
    bl_label = "Delete Long Faces"
    #bl_description="To Remove A Single Vertex"

    angle: FloatProperty(default=120.0)

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
                vAngle = v.calc_edge_angle()
                if vAngle > self.angle:
                    vDots.append(v)
                    vCount += 1


            bmesh.ops.dissolve_verts(mesh, vDots, use_face_split=False, use_boundary_tear=False)
            #bmesh.ops.delete(mesh, geom=vDots, context='VERTS')
            bmesh.update_edit_mesh(me)
        
        self.report({'INFO'}, "Clear Dots - " + str(vCount))
        return {'FINISHED'}








classes = [
    PS_OT_del_long_faces,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)