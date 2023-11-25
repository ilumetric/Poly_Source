import bpy, gpu, bmesh
from gpu_extras.batch import batch_for_shader
from bpy.types import Operator, Gizmo, GizmoGroup
from gpu import state




UPDATE = False
DIRT = False
shader = gpu.shader.from_builtin('UNIFORM_COLOR')





ngone_co = []
ngons_indices = []
tris_co = []
custom_co = []
custom_faces_indices = []
e_non_co = []
e_pole_co = []
n_pole_co = []
f_pole_co = []
v_bound_co = []
v_alone_co = []
ngone_idx = []
e_non_idx = []
custom_faces_idx = []

def check_draw(self, context):
    props = context.preferences.addons[__package__].preferences
    settings = context.scene.PS_scene_set
    theme = context.preferences.themes['Default']
    edge_width = theme.view_3d.edge_width
    vertex_size = theme.view_3d.vertex_size

    state.blend_set('ALPHA')
    state.line_width_set(edge_width + 1)
    state.point_size_set(vertex_size + 5)
    
    if not settings.xray_for_check:
        state.depth_mask_set(False)
        state.face_culling_set('BACK')
        state.depth_test_set('LESS_EQUAL')

    shader.bind()

    if settings.ngone:
        NGONE = batch_for_shader(shader, 'TRIS', {"pos": ngone_co}, indices=ngons_indices)
        shader.uniform_float("color", props.ngone_col)
        NGONE.draw(shader)

    if settings.tris:
        TRIS = batch_for_shader(shader, 'TRIS', {"pos": tris_co})
        shader.uniform_float("color", props.tris_col)
        TRIS.draw(shader)

    if settings.custom_count:
        CUSTOM = batch_for_shader(shader, 'TRIS', {"pos": custom_co}, indices=custom_faces_indices)
        shader.uniform_float("color", props.custom_col)
        CUSTOM.draw(shader)

    if settings.non_manifold_check:
        EDGES_NON = batch_for_shader(shader, 'LINES', {"pos": e_non_co})
        shader.uniform_float("color", props.non_manifold_color)
        EDGES_NON.draw(shader)

    if settings.e_pole:
        E_POLE = batch_for_shader(shader, 'POINTS', {"pos": e_pole_co})
        shader.uniform_float("color", props.e_pole_col) 
        E_POLE.draw(shader)

    if settings.n_pole:
        N_POLE = batch_for_shader(shader, 'POINTS', {"pos": n_pole_co}) 
        shader.uniform_float("color", props.n_pole_col) 
        N_POLE.draw(shader)

    if settings.f_pole:
        F_POLE = batch_for_shader(shader, 'POINTS', {"pos": f_pole_co})
        shader.uniform_float("color", props.f_pole_col) 
        F_POLE.draw(shader)

    if settings.v_bound:
        V_BOUND = batch_for_shader(shader, 'POINTS', {"pos": v_bound_co})
        shader.uniform_float("color", props.bound_col) 
        V_BOUND.draw(shader)

    if settings.v_alone:
        V_ALONE = batch_for_shader(shader, 'POINTS', {"pos": v_alone_co})
        shader.uniform_float("color", props.v_alone_color)
        V_ALONE.draw(shader)

    state.depth_mask_set(True)
    state.depth_test_set('NONE')
    state.face_culling_set('NONE')
    state.point_size_set(3.0)
    state.line_width_set(1.0)
    state.blend_set('NONE') 

    


class PS_GT_check(Gizmo):
    bl_idname = 'PS_GT_check'

    def draw(self, context):
        check_draw(self, context)

    """ def test_select(self, context, location):
        if context.area.type == 'VIEW_3D':
            context.area.tag_redraw()
        return -1 """



class PS_GGT_check_group(GizmoGroup):
    bl_idname = 'PS_GGT_check_group'
    bl_label = "PS Draw"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'PERSISTENT', 'SHOW_MODAL_ALL'} #'DEPTH_3D' , 'TOOL_INIT', 'SELECT', , 'SCALE' , 'SHOW_MODAL_ALL' 'PERSISTENT', 
 

    @classmethod
    def poll(cls, context):
        settings = context.scene.PS_scene_set
        return settings.PS_check
        
    def setup(self, context):
        self.mesh = self.gizmos.new(PS_GT_check.bl_idname)
        self.mesh.use_draw_modal = True
        self.mesh.hide_select = True

    def refresh(self, context):
        global ngone_co, ngons_indices, tris_co, custom_co, custom_faces_indices, e_non_co, e_pole_co, n_pole_co, f_pole_co, v_bound_co, v_alone_co, ngone_idx, e_non_idx, custom_faces_idx

        ngone_co = []
        ngons_indices = []
        tris_co = []
        custom_co = []
        custom_faces_indices = []
        e_non_co = []
        e_pole_co = []
        n_pole_co = []
        f_pole_co = []
        v_bound_co = []
        v_alone_co = []
        ngone_idx = []
        e_non_idx = []
        custom_faces_idx = []

        objs = [obj for obj in context.selected_objects if obj.type == 'MESH' and len(obj.data.polygons) < 50000]
        if not objs:
            return
        depsgraph = context.evaluated_depsgraph_get()

        settings = context.scene.PS_scene_set
        for obj in objs:
            if context.mode == 'EDIT_MESH':
                bm = bmesh.from_edit_mesh(obj.data)
            else:
                bm = bmesh.new()
                bm.from_mesh(obj.evaluated_get(depsgraph).data if settings.use_mod_che and obj.modifiers else obj.data)
                bm.verts.ensure_lookup_table()
                bm.edges.ensure_lookup_table()
                bm.faces.ensure_lookup_table()

            # --- N-Gone
            if settings.ngone:
                for n in bm.faces:
                    if len(n.verts)>4:
                        ngone_idx.append(n.index)
                        
                copy = bm.copy()
                copy.faces.ensure_lookup_table()
                edge_n = [e for i in ngone_idx for e in copy.faces[i].edges]

                for e in copy.edges:
                    if not e in edge_n:
                        e.hide_set(True)

                bmesh.ops.triangulate(copy, faces=copy.faces[:])

                v_index = []
                for f in copy.faces:
                    v_index.extend([v.index for v in f.verts if not f.hide])
                    ngone_co.extend([obj.matrix_world @ v.co for v in f.verts if not f.hide]) 

                copy.free() # TODO может быть удалить ?

                ngons_indices.extend(list(range(0, len(v_index)))[v_i:v_i+3] for v_i in range(0, len(v_index), 3))

            
            # --- Custom 
            if settings.custom_count:
                for n in bm.faces:
                    if len(n.verts) == settings.custom_count_verts:
                        custom_faces_idx.append(n.index)
                
                        
                copy = bm.copy()
                copy.faces.ensure_lookup_table()
                edge_n = [e for i in custom_faces_idx for e in copy.faces[i].edges]

                for e in copy.edges:
                    if not e in edge_n:
                        e.hide_set(True)

                bmesh.ops.triangulate(copy, faces=copy.faces[:])

                v_index = []
                
                for f in copy.faces:
                    v_index.extend([v.index for v in f.verts if not f.hide])
                    custom_co.extend([obj.matrix_world @ v.co for v in f.verts if not f.hide]) 

                copy.free() # TODO может быть удалить ?

                custom_faces_indices.extend(list(range(0, len(v_index)))[v_i:v_i+3] for v_i in range(0, len(v_index), 3))


            if settings.tris:
                tris_co = [obj.matrix_world @ v.co for f in bm.faces if len(f.verts) == 3 for v in f.verts]
            

            if settings.non_manifold_check:
                e_non_idx = [e.index for e in bm.edges if not e.is_manifold]
                e_non_co = [obj.matrix_world @ v.co for i in e_non_idx for v in bm.edges[i].verts]
            
            
            if settings.e_pole: 
                e_pole_co = [obj.matrix_world @ v.co for v in bm.verts if len(v.link_edges)==5]
            
            
            if settings.n_pole:
                n_pole_co = [obj.matrix_world @ v.co for v in bm.verts if len(v.link_edges)==3]
            
            
            if settings.f_pole:
                f_pole_co = [obj.matrix_world @ v.co for v in bm.verts if len(v.link_edges)>5]
            
            
            if settings.v_bound:
                v_bound_co = [obj.matrix_world @ v.co for v in bm.verts if v.is_boundary or not v.is_manifold]
            
            
            if settings.v_alone:
                v_alone_co = [obj.matrix_world @ v.co for v in bm.verts if len(v.link_edges)<1]
            
            if context.mode != 'EDIT_MESH':
                bm.free()

        #print('refresh')

    def draw_prepare(self, context):
        global UPDATE
        if UPDATE:
            self.refresh(context)
            UPDATE = False
        
        






















classes = [
    PS_GT_check,
    PS_GGT_check_group,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

   
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)