import bpy
from bpy.types import Operator
from bpy.props import BoolProperty, IntProperty


class PS_OT_cylinder_optimizer(Operator):
    """Optimize cylinder by selecting and dissolving edge loops"""
    bl_idname = "mesh.ps_cylinder_optimizer"
    bl_label = "Cylinder Optimizer"
    bl_description = "Reduce cylinder polygon count by dissolving selected edge loops. Select one longitudinal edge first"
    bl_options = {'REGISTER', 'UNDO'}

    skip: IntProperty(
        name="Deselected",
        description="Number of edge loops to skip between dissolved loops",
        min=1, default=1,
    )
    nth: IntProperty(
        name="Selected",
        description="Number of consecutive edge loops to select for dissolving",
        min=1, default=1,
    )
    offset: IntProperty(
        name="Offset",
        description="Offset the starting position of the selection pattern",
        default=0,
    )

    dissolve: BoolProperty(
        name="Dissolve Edges",
        description="Dissolve the selected edges after selection",
        default=True,
    )
    use_verts: BoolProperty(
        name="Dissolve Vertices",
        description="Also dissolve remaining vertices after edge dissolve",
        default=True,
    )
    use_face_split: BoolProperty(
        name="Face Split",
        description="Split non-planar faces during edge dissolve",
        default=False,
    )

    rounding: BoolProperty(
        name="Rounding Up",
        description="Round selected edge loops into a perfect circle instead of dissolving",
        default=False,
    )

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    @staticmethod
    def _circle(self, context):
        """выравнивает выбранные петли в окружность"""
        bpy.ops.mesh.loop_multi_select(ring=True)
        bpy.ops.mesh.loop_multi_select(ring=False)
        bpy.ops.mesh.looptools_circle(
            custom_radius=False, fit='best', flatten=True,
            influence=100, lock_x=False, lock_y=False, lock_z=False,
            radius=1, angle=0, regular=True,
        )

    @staticmethod
    def _optimizer(self, context):
        """оптимизирует цилиндр, удаляя лишние edge loops"""
        bpy.ops.ed.undo_push()
        bpy.ops.mesh.loop_multi_select(ring=True)
        bpy.ops.mesh.select_nth(skip=self.skip, nth=self.nth, offset=self.offset)
        bpy.ops.mesh.loop_multi_select(ring=False)
        if self.dissolve:
            bpy.ops.mesh.dissolve_edges(use_verts=self.use_verts, use_face_split=self.use_face_split)

    def execute(self, context):
        if self.rounding:
            self._circle(self, context)
        else:
            self._optimizer(self, context)
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        if not self.rounding:
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
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
