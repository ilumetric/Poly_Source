import bpy
from bpy.types import Operator
from bpy.props import BoolProperty, IntProperty



class PS_OT_cylinder_optimizer(Operator):
    bl_idname = "ps.cylinder_optimizer"
    bl_label = "Cylinder Optimizer"
    bl_description="Select one longitudinal edge from the cylinder. (Works only with cylinders that have the correct geometry)" # TODO
    bl_options = {'REGISTER', 'UNDO'}


    skip: IntProperty(name="Deselected", min=1, default=1)
    nth: IntProperty(name="Selected", min=1, default=1)
    offset: IntProperty(name="Offset", default=0)
    
    dissolve: BoolProperty(name="Dissolve Edges", default=True)
    use_verts: BoolProperty(name="Dissolve Vertices", default=True)
    use_face_split: BoolProperty(name="Face Split", default=False)


    rounding: BoolProperty(name="Rounding Up", default=False)

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    @staticmethod
    def circle(self, context):
        bpy.ops.mesh.loop_multi_select(ring=True)
        bpy.ops.mesh.loop_multi_select(ring=False)

        bpy.ops.mesh.looptools_circle(custom_radius=False, fit='best', flatten=True, influence=100, lock_x=False, lock_y=False, lock_z=False, radius=1, angle=0, regular=True)



    @staticmethod
    def optimizer(self, context):
        bpy.ops.ed.undo_push()

        bpy.ops.mesh.loop_multi_select(ring=True)
        bpy.ops.mesh.select_nth(skip=self.skip, nth=self.nth, offset=self.offset)
        bpy.ops.mesh.loop_multi_select(ring=False)

        if self.dissolve:
            bpy.ops.mesh.dissolve_edges(use_verts=self.use_verts, use_face_split=self.use_face_split)


    def execute(self, context):
        if self.rounding:
            self.circle(self, context)
        else:
            self.optimizer(self, context)

        #self.report({'INFO'}, "Clear Dots - " + str(vCount))
        return {'FINISHED'}


    def draw(self, context):

        layout = self.layout
        if self.rounding == False:
            layout.prop(self, 'skip')
            layout.prop(self, 'nth')
            layout.prop(self, 'offset')

            layout.prop(self, 'dissolve')
            if self.dissolve:
                layout.prop(self, 'use_verts')
                layout.prop(self, 'use_face_split')














classes = [
    PS_OT_cylinder_optimizer,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)