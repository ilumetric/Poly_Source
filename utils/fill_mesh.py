import bmesh
import bpy
from bpy.types import Operator


class PS_OT_fill_mesh(Operator):
    """Fill mesh using convex hull from selected vertices"""
    bl_idname = 'mesh.ps_fill_mesh'
    bl_label = 'Fill Mesh'
    bl_description = 'Generate faces from selected vertices by computing a convex hull'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)

        bm_new = bmesh.new()
        bm_new.from_mesh(me, face_normals=True, use_shape_key=False)
        verts = [v for v in bm_new.verts if v.select]
        convex_hull = bmesh.ops.convex_hull(bm_new, input=verts, use_existing_faces=True)

        bm_new.verts.ensure_lookup_table()
        bm_new.edges.ensure_lookup_table()
        bm_new.faces.ensure_lookup_table()

        # извлекаем только новые грани из результата convex hull
        new_faces = [i for i in convex_hull['geom'] if isinstance(i, bmesh.types.BMFace)]

        for f_idx in new_faces:
            bm.faces.new([bm.verts[v.index] for v in f_idx.verts])

        bm_new.free()
        bmesh.update_edit_mesh(me)
        return {'FINISHED'}


classes = [
    PS_OT_fill_mesh,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
