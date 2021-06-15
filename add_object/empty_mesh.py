import bpy
from bpy.types import Operator
from bpy_extras.object_utils import AddObjectHelper, object_data_add




class PS_OT_create_empty_mesh(Operator, AddObjectHelper):
    bl_idname = 'ps.create_empty_mesh'
    bl_label = 'Create Empty Mesh'
    bl_options = {"REGISTER", "UNDO"}
 

    def execute(self, context):
        me = bpy.data.meshes.new("Empty Mesh")
        me.from_pydata([], [], [])
        

        # useful for development when the mesh may be invalid.
        # mesh.validate(verbose=True)
        object_data_add(context, me, operator=self)
        
        
        return {'FINISHED'}

    

classes = [
    PS_OT_create_empty_mesh,
    ]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls) 