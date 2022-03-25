import bpy
import bmesh
from bpy.types import Operator
from bpy.props import EnumProperty, BoolProperty


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
                obj.modifiers[nameB].show_expanded = False
                obj.modifiers[nameB].profile = 1
                obj.modifiers[nameB].segments = 2
                obj.modifiers[nameB].limit_method = 'WEIGHT'

            if obj.modifiers.get(nameS) is None:
                obj.modifiers.new(nameS, 'SUBSURF')
                obj.modifiers[nameS].show_expanded = False
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
                obj.modifiers[name].show_expanded = False
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
                obj.modifiers[name].show_expanded = False

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
                obj.modifiers[name].show_expanded = False

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
                obj.modifiers[name].show_expanded = False

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


classes = [
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