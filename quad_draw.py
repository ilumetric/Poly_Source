import bpy


from gpu_extras.batch import batch_for_shader
from bpy.types import Operator, GizmoGroup, Gizmo
import bmesh






import bgl 

import gpu
from math import sin, cos, pi
from gpu.types import (
        GPUBatch,
        GPUVertBuf,
        GPUVertFormat,
    )
from mathutils import Matrix, Vector
import mathutils




# Shader
from .utils.shader import vs_uni, fs_uni, vs_sm, fs_sm
shader_uni = gpu.types.GPUShader(vs_uni, fs_uni)
shader_sm = gpu.types.GPUShader(vs_sm, fs_sm)


# Activate Tool
from .utils.active_tool import active_tool







# --- Retopology Tool
tools_ret = {
        "PS_tool.poly_quilt",
        "PS_tool.poly_quilt_poly",
        "PS_tool.poly_quilt_extrude",
        "PS_tool.poly_quilt_edgeloop",
        "PS_tool.poly_quilt_loopcut",
        "PS_tool.poly_quilt_knife",
        "PS_tool.poly_quilt_delete",
        "PS_tool.poly_quilt_brush",
        "PS_tool.poly_quilt_seam",
        "builtin.poly_build",
        }
#import time
def gpu_draw(self, context): # TODO
    

    if context.active_object != None and context.active_object.select_get() and context.mode == 'EDIT_MESH':
        
        props = context.preferences.addons[__package__].preferences

        theme = context.preferences.themes['Default']
        vertex_size = theme.view_3d.vertex_size

        

        # Color
        VA_Col = props.v_alone_color[0], props.v_alone_color[1], props.v_alone_color[2], props.v_alone_color[3]
        VE_Col = props.VE_color[0], props.VE_color[1], props.VE_color[2], props.VE_color[3]
        F_Col = props.F_color[0], props.F_color[1], props.F_color[2], props.opacity
        sel_Col = props.select_color[0], props.select_color[1], props.select_color[2], 1.0
        
        
        

        # добавить обработку сетки через bgl TODO
        
        tool_retopo = active_tool().idname in tools_ret # Retopology Tool
    

        

        

        is_perspective = context.region_data.is_perspective
        if is_perspective:
            z_bias = props.z_bias / 350
        else:
            z_bias = 1.0



        bgl.glEnable(bgl.GL_BLEND)
        bgl.glLineWidth(props.edge_width)
        bgl.glPointSize(vertex_size + props.verts_size)
        bgl.glCullFace(bgl.GL_BACK)



        if tool_retopo:
            shader = shader_uni
        else:
            shader = shader_sm


        view_mat = context.region_data.perspective_matrix
        shader.uniform_float("view_mat", view_mat)
        shader.uniform_float("Z_Bias", z_bias)
        
        

  
        
        


        if props.use_mod_ret:
            depsgraph = context.evaluated_depsgraph_get()


        #uniques = context.objects_in_mode_unique_data
        uniques = context.selected_objects
        for obj in uniques:
            if props.use_mod_ret:
                if len(obj.modifiers) > 0: 
                    depsgraph.update()

                ob_eval = obj.evaluated_get(depsgraph)
                me = ob_eval.to_mesh()
            
                bm = bmesh.new()
                bm.from_mesh(me, face_normals=True, use_shape_key=False)

                bm.verts.ensure_lookup_table()
                bm.edges.ensure_lookup_table()
                bm.faces.ensure_lookup_table()

            else:
                bm = bmesh.from_edit_mesh(obj.data)



            if len(bm.verts)<30000:
                if tool_retopo:
                    # только одиночные вертексы
                    vCo_one = [obj.matrix_world @ v.co for v in bm.verts] # if len(v.link_faces) < 1

                    with gpu.matrix.push_pop():
                        gpu.matrix.translate((0,0))
                        gpu.matrix.scale_uniform(1)

                        fmt = GPUVertFormat()
                        pos_id = fmt.attr_add(id="pos", comp_type='F32', len=3, fetch_mode='FLOAT')
                        vbo = GPUVertBuf(len=len(vCo_one), format=fmt)
                        vbo.attr_fill(id=pos_id, data=vCo_one)
                        batch = GPUBatch(type='POINTS', buf=vbo)
                        batch.program_set(shader)
                        shader.uniform_float("color", VA_Col)
                        batch.draw()



                else:
                    vertex_co = [obj.matrix_world @ v.co for v in bm.verts]
                    v_len = len(vertex_co)
                    vert_col = [VE_Col for i in range(v_len)]
                    # Окрашивание выделенных элементов
                    for i, vert in enumerate(bm.verts):
                        if len(vert.link_faces) < 1:
                            vert_col[i] = VA_Col

                        if vert.select:
                            #face_col[i] = select_color_f
                            vert_col[i] = sel_Col

                    with gpu.matrix.push_pop():
                        #gpu.matrix.translate(position)
                        #gpu.matrix.scale_uniform(radius)

                        fmt = GPUVertFormat()
                        pos_id = fmt.attr_add(id="pos", comp_type='F32', len=2, fetch_mode='FLOAT')
                        vbo = GPUVertBuf(len=len(vertex_co), format=fmt)
                        vbo.attr_fill(id=pos_id, data=vCo_one)
                        batch = GPUBatch(type='POINTS', buf=vbo)
                        batch.program_set(shader)
                        shader.uniform_float("color", VA_Col)
                        batch.draw()


#from bpy.app.handlers import persistent, depsgraph_update_post
#@persistent
""" def update():
    print( len(depsgraph_update_post) )
    return True """

def PS_draw_bgl(self, context):
    #if context.area:
    if context.active_object != None and context.active_object.select_get() and context.mode == 'EDIT_MESH':
        #start_time = time.time()
        
        props = context.preferences.addons[__package__].preferences

        theme = context.preferences.themes['Default']
        vertex_size = theme.view_3d.vertex_size

        # Color
        VA_Col = props.v_alone_color[0], props.v_alone_color[1], props.v_alone_color[2], props.v_alone_color[3]
        VE_Col = props.VE_color[0], props.VE_color[1], props.VE_color[2], props.VE_color[3]
        F_Col = props.F_color[0], props.F_color[1], props.F_color[2], props.opacity
        sel_Col = props.select_color[0], props.select_color[1], props.select_color[2], 1.0
        


        
        
        

        bgl.glEnable(bgl.GL_BLEND)
        bgl.glLineWidth(props.edge_width)
        bgl.glPointSize(vertex_size + props.verts_size)
        bgl.glCullFace(bgl.GL_BACK)
        
        
        if props.xray_ret == False:
            bgl.glEnable(bgl.GL_DEPTH_TEST)
            bgl.glEnable(bgl.GL_CULL_FACE)


        if props.line_smooth:
            bgl.glEnable(bgl.GL_LINE_SMOOTH)

        
        #bgl.glDepthRange(0, 0.99999)
        #bgl.glDepthFunc(600)
        bgl.glDepthMask(False)

        

        

        is_perspective = context.region_data.is_perspective
        if is_perspective:
            z_bias = props.z_bias / 350
        else:
            z_bias = 1.0


        

        tool_retopo = active_tool().idname in tools_ret # Retopology Tools
        if tool_retopo:
            shader = shader_uni
        else:
            shader = shader_sm

        shader.bind()


        view_mat = context.region_data.perspective_matrix
        shader.uniform_float("view_mat", view_mat)
        shader.uniform_float("Z_Bias", z_bias)
        
        


        
        


        if props.use_mod_ret:
            depsgraph = context.evaluated_depsgraph_get()


        #uniques = context.objects_in_mode_unique_data
        uniques = context.selected_objects
        for obj in uniques:
            if props.use_mod_ret:
                if len(obj.modifiers) > 0: 
                    depsgraph.update()

                ob_eval = obj.evaluated_get(depsgraph)
                me = ob_eval.to_mesh()
            
                bm = bmesh.new()
                bm.from_mesh(me, face_normals=True, use_shape_key=False)

                bm.verts.ensure_lookup_table()
                bm.edges.ensure_lookup_table()
                bm.faces.ensure_lookup_table()

            else:
                bm = bmesh.from_edit_mesh(obj.data)



            if len(bm.verts)<30000:
                # Если выбран инструмент ретопологии
                if tool_retopo:
                    # все вертексы
                    vCo = [obj.matrix_world @ v.co for v in bm.verts]
                    loop_triangles = bm.calc_loop_triangles()
                    faces_indices = [[loop.vert.index for loop in looptris] for looptris in loop_triangles]

                    FACES = batch_for_shader(shader, 'TRIS', {"pos": vCo}, indices=faces_indices)
                    shader.uniform_float("color", F_Col)
                    FACES.draw(shader)




                    edges_ind = [e.index for e in bm.edges]
                    edges_cord = [obj.matrix_world @ v.co for i in edges_ind for v in bm.edges[i].verts]
                    
                    EDGES = batch_for_shader(shader, 'LINES', {"pos": edges_cord}) 
                    shader.uniform_float("color", VE_Col)
                    EDGES.draw(shader)




                    # только одиночные вертексы
                    vCo_one = [obj.matrix_world @ v.co for v in bm.verts if len(v.link_faces) < 1] #not v.is_manifold] (not v.is_manifold and v.is_wire)

                    VERTS = batch_for_shader(shader, 'POINTS', {"pos": vCo_one})
                    shader.uniform_float("color", VA_Col)
                    VERTS.draw(shader)
                    
                

                # Если выбраны обычные инструменты
                else:
                    # FACES
                    vertex_co = [obj.matrix_world @ v.co for v in bm.verts]
                    v_len = len(vertex_co)

                    loop_triangles = bm.calc_loop_triangles()
                    faces_indices = [[loop.vert.index for loop in looptris] for looptris in loop_triangles]

                    face_col = [F_Col for i in range(v_len)]
                    FACES = batch_for_shader(shader, 'TRIS', {"pos": vertex_co, "col": face_col}, indices=faces_indices)
                    FACES.draw(shader)


                    # EDGES & VERTICES
                    edges_ind = [e.index for e in bm.edges]
                    edges_cord = [obj.matrix_world @ v.co for i in edges_ind for v in bm.edges[i].verts]
    
                    edge_col = [VE_Col for i in range(len(edges_cord))]
                    vert_col = [VE_Col for i in range(v_len)]


                    # Окрашивание выделенных элементов
                    for i, vert in enumerate(bm.verts):
                        if len(vert.link_faces) < 1:
                            vert_col[i] = VA_Col

                        if vert.select:
                            #face_col[i] = select_color_f
                            vert_col[i] = sel_Col

                    for i, edge in enumerate(bm.edges):
                        if edge.select:
                            ind = i*2
                            ind2 = ind + 1
                            edge_col[ind] = sel_Col
                            edge_col[ind2] = sel_Col


                
                    EDGES = batch_for_shader(shader, 'LINES', {"pos": edges_cord, "col": edge_col})
                    VERTS = batch_for_shader(shader, 'POINTS', {"pos": vertex_co, "col": vert_col}) 
                
                    EDGES.draw(shader)
                    if context.tool_settings.mesh_select_mode[0]:
                        VERTS.draw(shader)
                    
            if props.use_mod_ret:     
                bm.free()
                
            
            

        if props.line_smooth:
            bgl.glDisable(bgl.GL_LINE_SMOOTH)
        
        bgl.glDisable(bgl.GL_DEPTH_TEST)
        bgl.glDisable(bgl.GL_CULL_FACE)
        bgl.glLineWidth(1)
        bgl.glPointSize(1)
        bgl.glDisable(bgl.GL_BLEND)  



        #end_time = time.time()
        #print(end_time-start_time)







#----------------------------------------------- FROM GIZMO TODO
class PS_GT_draw(Gizmo):
    bl_idname = "ps.draw"

    def draw(self, context):
        gpu_draw(self, context)
        #PS_draw_bgl(self, context)

    def setup(self):
        self.use_draw_modal = False
        #self.select = True
        #self.hide_select = True
        #self.group = PS_GGT_draw_group.bl_idname


    def test_select(self, context, location):
        if context.area.type == 'VIEW_3D':
            context.area.tag_redraw()
        return -1



class PS_GGT_draw_group(GizmoGroup):
    
    bl_idname = "PS_GGT_draw_mesh"
    bl_label = "PS Draw"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'PERSISTENT'} #'DEPTH_3D' , 'TOOL_INIT', 'SELECT', , 'SCALE' , 'SHOW_MODAL_ALL'
 

    @classmethod
    def poll(cls, context):
        props = context.preferences.addons[__package__.split(".")[0]].preferences
        return props.draw_
        

    def setup(self, context):
        mesh = self.gizmos.new(PS_GT_draw.bl_idname)
        self.mesh = mesh 


    def draw_prepare(self, context):
        props = context.preferences.addons[__package__.split(".")[0]].preferences

        mesh = self.mesh
        if props.draw_:
            mesh.hide = False
        else:
            mesh.hide = True

















#----------------------------------------------- STANDART
class PS_OT_draw_mesh(Operator):
    bl_idname = "ps.draw_mesh"
    bl_label = "Draw Mesh Advance"


    def modal(self, context, event):
        settings = context.scene.ps_set_
        #props = bpy.context.preferences.addons[__package__.split(".")[0]].preferences
        
        
        """ if context.area:
            #print('2222')
            context.area.tag_redraw() """

               
        if settings.retopo_mode == False:
            bpy.types.SpaceView3D.draw_handler_remove(self._ps_PS_draw, 'WINDOW')
            return {'FINISHED'}
            

    
        return {'PASS_THROUGH'}


    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D': # PS_draw_bgl
            args = (self, context)
            self._ps_PS_draw= bpy.types.SpaceView3D.draw_handler_add(PS_draw_bgl, args, 'WINDOW', 'POST_VIEW')
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "Area Type Not 'VIEW_3D'")
            return {'CANCELLED'} 







classes = [
    PS_GT_draw,
    PS_GGT_draw_group,
    PS_OT_draw_mesh,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

   
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)