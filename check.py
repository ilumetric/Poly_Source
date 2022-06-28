import bpy, gpu, bmesh
from gpu_extras.batch import batch_for_shader
from bpy.types import Operator, Gizmo, GizmoGroup
from gpu import state


DIRT = False
shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')



def custom_batch(shader, type, content, indices=None):
    """
    shader
    type: 'POINTS', 'LINES', 'TRIS' or 'LINES_ADJ'
    
    """
    from gpu.types import (
        GPUBatch,
        GPUIndexBuf,
        GPUVertBuf,
    )

    for data in content.values():
        vbo_len = len(data)
        break
    else:
        raise ValueError("Empty 'content'")

    vbo_format = shader.format_calc()
    vbo = GPUVertBuf(vbo_format, vbo_len)

    for id, data in content.items():
        if len(data) != vbo_len:
            raise ValueError("Length mismatch for 'content' values")
        vbo.attr_fill(id, data)

    if indices is None:
        return GPUBatch(type=type, buf=vbo)
    else:
        ibo = GPUIndexBuf(type=type, seq=indices)
        return GPUBatch(type=type, buf=vbo, elem=ibo)


def check_draw(self, context):
    objs = context.selected_objects
    if len(objs) > 0:
        props = context.preferences.addons[__package__.split('.')[0]].preferences

        theme = context.preferences.themes['Default']
        vertex_size = theme.view_3d.vertex_size


        # --- Set
        state.blend_set('ALPHA')
        state.line_width_set(props.edge_width + 1)
        state.point_size_set(vertex_size + 5)

        if props.xray_che == False:
            state.depth_mask_set(False)
            state.face_culling_set('BACK')
            state.depth_test_set('LESS_EQUAL')


        shader.bind()
        
        
        # --- Color
        ngone_col = props.ngone_col
        tris_col = props.tris_col
        e_non_col = props.non_manifold_color
        e_pole_col = props.e_pole_col
        n_pole_col = props.n_pole_col
        f_pole_col = props.f_pole_col
        v_bound_col = props.bound_col
        v_alone_col = props.v_alone_color
        custom_col = props.custom_col

        if props.use_mod_che:
            depsgraph = context.evaluated_depsgraph_get()

     
        
        for obj in objs:
            if obj.type == 'MESH':

                me = obj.data
                if len(me.polygons) < 50000:

                    if context.mode == 'EDIT_MESH' and props.use_mod_che == False:
                        bm = bmesh.from_edit_mesh(obj.data)

                    else:
                        if props.use_mod_che:
                            if len(obj.modifiers) > 0: 
                                depsgraph.update()

                            ob_eval = obj.evaluated_get(depsgraph)
                            me = ob_eval.to_mesh()
                

                        bm = bmesh.new()
                        bm.from_mesh(me)

                        bm.verts.ensure_lookup_table()
                        bm.edges.ensure_lookup_table()
                        bm.faces.ensure_lookup_table()




                
                    
                    # --- N-Gone
                    if props.ngone:
                        ngone = []
                        for n in bm.faces:
                            if len(n.verts)>4:
                                ngone.append(n.index)
                        #print("ngone",ngone)
                                
                        copy = bm.copy()
                        copy.faces.ensure_lookup_table()
                        edge_n = [e for i in ngone for e in copy.faces[i].edges]

                        for e in copy.edges:
                            if not e in edge_n:
                                e.hide_set(True)

                        bmesh.ops.triangulate(copy, faces=copy.faces[:])

                        v_index = []
                        ngone_co = []
                        for f in copy.faces:
                            v_index.extend([v.index for v in f.verts if not f.hide])
                            ngone_co.extend([obj.matrix_world @ v.co for v in f.verts if not f.hide]) 

                        copy.free() # TODO может быть удалить ?

                        ngons_indices = []
                        ngons_indices.extend(list(range(0, len(v_index)))[v_i:v_i+3] for v_i in range(0, len(v_index), 3))
                        NGONE = batch_for_shader(shader, 'TRIS', {"pos": ngone_co}, indices=ngons_indices)
                        shader.uniform_float("color", ngone_col)
                        NGONE.draw(shader)
                        

                        

                    # --- Custom 
                    if props.custom_count:
                        custom_faces = []
                        for n in bm.faces:
                            if len(n.verts) == props.custom_count_verts:
                                custom_faces.append(n.index)
                        
                                
                        copy = bm.copy()
                        copy.faces.ensure_lookup_table()
                        edge_n = [e for i in custom_faces for e in copy.faces[i].edges]

                        for e in copy.edges:
                            if not e in edge_n:
                                e.hide_set(True)

                        bmesh.ops.triangulate(copy, faces=copy.faces[:])

                        v_index = []
                        custom_co = []
                        for f in copy.faces:
                            v_index.extend([v.index for v in f.verts if not f.hide])
                            custom_co.extend([obj.matrix_world @ v.co for v in f.verts if not f.hide]) 

                        copy.free() # TODO может быть удалить ?

                        custom_faces_indices = []
                        custom_faces_indices.extend(list(range(0, len(v_index)))[v_i:v_i+3] for v_i in range(0, len(v_index), 3))
                        CUSTOM = batch_for_shader(shader, 'TRIS', {"pos": custom_co}, indices=custom_faces_indices)
                        shader.uniform_float("color", custom_col)
                        CUSTOM.draw(shader)



                    if props.tris:
                        tris_co = [obj.matrix_world @ v.co for f in bm.faces for v in f.verts if len(f.verts)==3]
                        TRIS = batch_for_shader(shader, 'TRIS', {"pos": tris_co})
                        shader.uniform_float("color", tris_col)
                        TRIS.draw(shader)

                    
                    if props.non_manifold_check:
                        e_non_i = [e.index for e in bm.edges if not e.is_manifold]
                        e_non_co = [obj.matrix_world @ v.co for i in e_non_i for v in bm.edges[i].verts]
                        EDGES_NON = batch_for_shader(shader, 'LINES', {"pos": e_non_co})
                        shader.uniform_float("color", e_non_col)
                        EDGES_NON.draw(shader)


                    if props.e_pole: 
                        e_pole_co = [obj.matrix_world @ v.co for v in bm.verts if len(v.link_edges)==5]
                        E_POLE = batch_for_shader(shader, 'POINTS', {"pos": e_pole_co})
                        shader.uniform_float("color", e_pole_col) 
                        E_POLE.draw(shader)


                    if props.n_pole:
                        n_pole_co = [obj.matrix_world @ v.co for v in bm.verts if len(v.link_edges)==3]
                        N_POLE = batch_for_shader(shader, 'POINTS', {"pos": n_pole_co}) 
                        shader.uniform_float("color", n_pole_col) 
                        N_POLE.draw(shader)


                    if props.f_pole: 
                        f_pole_co = [obj.matrix_world @ v.co for v in bm.verts if len(v.link_edges)>5]
                        F_POLE = batch_for_shader(shader, 'POINTS', {"pos": f_pole_co})
                        shader.uniform_float("color", f_pole_col) 
                        F_POLE.draw(shader)


                    if props.v_bound:
                        v_bound_co = [obj.matrix_world @ v.co for v in bm.verts if v.is_boundary or not v.is_manifold]
                        V_BOUND = batch_for_shader(shader, 'POINTS', {"pos": v_bound_co,})
                        shader.uniform_float("color", v_bound_col) 
                        V_BOUND.draw(shader)
                    

                    if props.v_alone:
                        v_alone_co = [obj.matrix_world @ v.co for v in bm.verts if len(v.link_edges)<1]
                        V_ALONE = batch_for_shader(shader, 'POINTS', {"pos": v_alone_co})
                        shader.uniform_float("color", v_alone_col)
                        V_ALONE.draw(shader)




                    if props.use_mod_che:
                        bm.free()



        # --- Restore
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

    def test_select(self, context, location):
        if context.area.type == 'VIEW_3D':
            context.area.tag_redraw()
        return -1



class PS_GGT_check_group(GizmoGroup):
    
    bl_idname = 'PS_GGT_check_group'
    bl_label = "PS Draw"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'SHOW_MODAL_ALL'} #'DEPTH_3D' , 'TOOL_INIT', 'SELECT', , 'SCALE' , 'SHOW_MODAL_ALL' 'PERSISTENT', 
 

    """ @classmethod
    def poll(cls, context):
        settings = context.scene.PS_scene_set
        return settings.PS_check """
        

    def setup(self, context):
        mesh = self.gizmos.new(PS_GT_check.bl_idname)
        mesh.use_draw_modal = True
        self.mesh = mesh 


    """ def draw_prepare(self, context):
        settings = context.scene.PS_scene_set
        mesh = self.mesh
        if settings.PS_check == True:
            mesh.hide = False
        else:
            mesh.hide = True """






















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