import bpy
import bmesh
from bpy.types import Operator
from bpy.props import BoolProperty


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



classes = [
    PS_OT_clear_dots,
    PS_OT_remove_vertex_non_manifold,
    PS_OT_clear_materials,
    PS_OT_clear_data,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)