import bpy, gpu, bmesh
from gpu_extras.batch import batch_for_shader
from bpy.types import Operator, Gizmo, GizmoGroup
from gpu import state
from .utils.utils import get_addon_prefs
import math
from mathutils import Vector


UPDATE = False
DIRT = False


if bpy.app.version >= (4, 0, 0):
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
else:
    shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')



def get_object_screen_size(obj, context):
    # Получаем размер объекта на экране
    camera = context.scene.camera
    if not camera:
        return 1.0  # Если камеры нет, возвращаем 1

    # Получаем углы ограничивающего бокса в пространстве видового экрана
    bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    screen_coords = [camera.matrix_world.inverted() @ corner for corner in bbox_corners]
    screen_coords = [corner for corner in screen_coords if corner.z > 0]  # Отбрасываем точки за камерой

    if not screen_coords:
        return 1.0  # Если объект за камерой, возвращаем 1

    # Находим максимальное расстояние между точками на экране
    max_distance = max([(a - b).length for a in screen_coords for b in screen_coords])
    return max_distance

def analyze_edges_adaptive(obj, bm, context, base_size, curvature_threshold):
    edges_to_draw = []

    # Получаем размер объекта на экране
    screen_size = get_object_screen_size(obj, context)

    # Получаем размер ограничивающего бокса объекта
    bbox_size = max(obj.dimensions)

    # Вычисляем адаптивный множитель на основе размера объекта и его видимого размера
    size_factor = (bbox_size / base_size) * (1 / screen_size)

    bm.normal_update()

    for edge in bm.edges:
        # Получаем координаты вершин ребра в мировом пространстве
        v1_world = obj.matrix_world @ edge.verts[0].co
        v2_world = obj.matrix_world @ edge.verts[1].co

        # Рассчитываем длину ребра в мировом пространстве
        edge_length_world = (v2_world - v1_world).length

        # Адаптивная длина ребра
        adaptive_length = edge_length_world * size_factor

        # Рассчитываем кривизну
        if len(edge.link_faces) == 2:
            face1, face2 = edge.link_faces
            angle = math.degrees(face1.normal.angle(face2.normal))
            curvature = angle / adaptive_length
        else:
            curvature = 0

        # Проверяем, превышает ли кривизна пороговое значение
        if curvature > curvature_threshold:
            edges_to_draw.extend([v1_world, v2_world])

        # Также отмечаем рёбра, которые слишком длинные или короткие относительно базового размера
        if adaptive_length > base_size * 2 or adaptive_length < base_size * 0.5:
            edges_to_draw.extend([v1_world, v2_world])

    return edges_to_draw




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
elongated_tris_co = []
edges_curvature = []


def check_draw(self, context):
    props = get_addon_prefs()
    if not props:
        return
    settings = context.scene.poly_source
    theme = context.preferences.themes['Default']
    vertex_size = theme.view_3d.vertex_size



    state.blend_set('ALPHA')
    state.line_width_set(props.line_width)
    state.point_size_set(props.point_width)

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

    if settings.elongated_tris:
        LINES = batch_for_shader(shader, 'LINES', {"pos": elongated_tris_co})
        shader.uniform_float("color", props.elongated_tris_col)
        LINES.draw(shader)

    """ if settings.analyze_edges_curvature:
        LINES = batch_for_shader(shader, 'LINES', {"pos": edges_curvature})
        shader.uniform_float("color", props.elongated_tris_col)
        LINES.draw(shader) """



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
        settings = context.scene.poly_source
        return settings.PS_check

    def setup(self, context):
        self.mesh = self.gizmos.new(PS_GT_check.bl_idname)
        self.mesh.use_draw_modal = True
        self.mesh.hide_select = True

    def refresh(self, context):
        global ngone_co, ngons_indices, tris_co, custom_co, custom_faces_indices, e_non_co, e_pole_co, n_pole_co, f_pole_co, v_bound_co, v_alone_co, ngone_idx, e_non_idx, custom_faces_idx, elongated_tris_co

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
        elongated_tris_co = []
        edges_curvature = []


        objs = [obj for obj in context.selected_objects if obj.type == 'MESH' and len(obj.data.polygons) < 50000]
        if not objs:
            return
        depsgraph = context.evaluated_depsgraph_get()

        settings = context.scene.poly_source
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

            if settings.elongated_tris or settings.tris:
                #tris_co = [obj.matrix_world @ v.co for f in bm.faces if len(f.verts) == 3 for v in f.verts]
                for f in bm.faces:
                    if len(f.verts) == 3:
                        verts = [obj.matrix_world @ v.co for v in f.verts]

                        if settings.tris:
                            tris_co.extend(verts)

                        if settings.elongated_tris:
                            a, b, c = (verts[0] - verts[1]).length, (verts[1] - verts[2]).length, (verts[2] - verts[0]).length
                            longest_side = max(a, b, c)
                            s = (a + b + c) / 2
                            area = math.sqrt(s * (s - a) * (s - b) * (s - c))
                            shortest_height = 2 * area / longest_side

                            if longest_side / shortest_height > settings.elongated_aspect_ratio:
                                # добавляем пары вершин для трёх рёбер треугольника
                                elongated_tris_co.extend([verts[0], verts[1], verts[1], verts[2], verts[2], verts[0]])


            """ # Анализ выделенных рёбер
            if settings.analyze_edges_curvature:
                edges_curvature.extend(analyze_edges_adaptive(
                    obj,
                    bm,
                    context,
                    settings.base_edge_size,
                    settings.adaptive_curvature_threshold
                )) """

            if context.mode != 'EDIT_MESH':
                bm.free()


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