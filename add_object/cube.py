import bpy
from bpy.types import Operator
import bmesh

from bpy_extras.object_utils import AddObjectHelper, object_data_add
from bpy.props import (
    BoolProperty,
    BoolVectorProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty,
)


def add_box(width, height, depth):
    """
    This function takes inputs and returns vertex and face arrays.
    no actual mesh data creation is done here.
    """

    verts = [
        (+1.0, +1.0, 0.0),
        (+1.0, -1.0, 0.0),
        (-1.0, -1.0, 0.0),
        (-1.0, +1.0, 0.0),
        (+1.0, +1.0, +2.0),
        (+1.0, -1.0, +2.0),
        (-1.0, -1.0, +2.0),
        (-1.0, +1.0, +2.0),
    ]

    faces = [
        (0, 1, 2, 3),
        (4, 7, 6, 5),
        (0, 4, 5, 1),
        (1, 5, 6, 2),
        (2, 6, 7, 3),
        (4, 0, 3, 7),
    ]

    # apply size
    for i, v in enumerate(verts):
        verts[i] = v[0] * width, v[1] * depth, v[2] * height

    return verts, faces



class PS_OT_create_cube(Operator, AddObjectHelper):
    bl_idname = 'ps.create_cube'
    bl_label = 'Create Cube'
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
 
    subdivide: IntProperty(
        name="Subdivide",
        description="Subdivide Box",
        min=0,
        default=4,
    )


    width: FloatProperty(
        name="Width",
        description="Box Width",
        min=0.01, max=100.0,
        default=1.0,
    )
    height: FloatProperty(
        name="Height",
        description="Box Height",
        min=0.01, max=100.0,
        default=1.0,
    )
    depth: FloatProperty(
        name="Depth",
        description="Box Depth",
        min=0.01, max=100.0,
        default=1.0,
    )
    layers: BoolVectorProperty(
        name="Layers",
        description="Object Layers",
        size=20,
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    # generic transform props
    align_items = (
        ('WORLD', "World", "Align the new object to the world"),
        ('VIEW', "View", "Align the new object to the view"),
        ('CURSOR', "3D Cursor", "Use the 3D cursor orientation for the new object")
    )
    align: EnumProperty(
        name="Align",
        items=align_items,
        default='WORLD',
        update=AddObjectHelper.align_update_callback,
    )
    location: FloatVectorProperty(
        name="Location",
        subtype='TRANSLATION',
    )
    rotation: FloatVectorProperty(
        name="Rotation",
        subtype='EULER',
    )


    def execute(self, context):
        verts_loc, faces = add_box(self.width, self.height, self.depth)

        me = bpy.data.meshes.new("Box")

        bm = bmesh.new()

        for v_co in verts_loc:
            bm.verts.new(v_co)

        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()

        for f_idx in faces:
            bm.faces.new([bm.verts[i] for i in f_idx])



        bmesh.ops.subdivide_edges(
                                bm,
                                edges = bm.edges,
                                cuts = self.subdivide,
                                use_grid_fill=True,
                                ) #  edges, smooth, smooth_falloff, fractal, along_normal, cuts, seed, custom_patterns, edge_percents, quad_corner_type, use_grid_fill, use_single_edge, use_only_quads, use_sphere, use_smooth_even


        bm.to_mesh(me)
        me.update()

        # add the mesh as an object into the scene with this utility module
        object_data_add(context, me, operator=self)

        return {'FINISHED'}


    def draw(self, context):
        layout = self.layout

        layout.prop(self, "subdivide")
      

        layout.separator()
        layout.prop(self, "width", text='X - Width')
        layout.prop(self, "depth", text='Y - Width')
        layout.prop(self, "height", text='Z - Width')
    
    
        layout.separator()
        layout.prop(self, "align")
        layout.prop(self, "location")
        layout.prop(self, "rotation")




classes = [
    PS_OT_create_cube,
    ]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls) 