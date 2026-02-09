import bpy
import gpu
import bmesh
import math
from gpu_extras.batch import batch_for_shader
from bpy.types import Gizmo, GizmoGroup
from gpu import state
from .utils.utils import get_addon_prefs


UPDATE = False

if bpy.app.version >= (4, 0, 0):
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')

    # шейдер для точек с per-vertex цветами и поддержкой наложений (Vulkan)
    try:
        _pt_iface = gpu.types.GPUStageInterfaceInfo("pt_iface")
        _pt_iface.flat('VEC4', "vCol1")
        _pt_iface.flat('VEC4', "vCol2")

        _pt_info = gpu.types.GPUShaderCreateInfo()
        _pt_info.push_constant('MAT4', "ModelViewProjectionMatrix")
        _pt_info.push_constant('FLOAT', "pointSize")
        _pt_info.vertex_in(0, 'VEC3', "pos")
        _pt_info.vertex_in(1, 'VEC4', "col1")
        _pt_info.vertex_in(2, 'VEC4', "col2")
        _pt_info.vertex_out(_pt_iface)
        _pt_info.fragment_out(0, 'VEC4', "fragColor")
        _pt_info.vertex_source(
            "void main()\n"
            "{\n"
            "  gl_Position = ModelViewProjectionMatrix * vec4(pos, 1.0);\n"
            "  gl_PointSize = pointSize;\n"
            "  vCol1 = col1;\n"
            "  vCol2 = col2;\n"
            "}\n"
        )
        _pt_info.fragment_source(
            "void main()\n"
            "{\n"
            "  vec2 center = gl_PointCoord - vec2(0.5);\n"
            "  float dist = length(center);\n"
            "  if (dist > 0.5) discard;\n"
            "  float edge = smoothstep(0.45, 0.5, dist);\n"
            "  if (vCol2.a > 0.001) {\n"
            "    float split = smoothstep(-0.03, 0.03, center.x);\n"
            "    vec4 c = mix(vCol1, vCol2, split);\n"
            "    fragColor = vec4(c.rgb, c.a * (1.0 - edge));\n"
            "  } else {\n"
            "    fragColor = vec4(vCol1.rgb, vCol1.a * (1.0 - edge));\n"
            "  }\n"
            "}\n"
        )
        point_shader = gpu.shader.create_from_info(_pt_info)
        del _pt_info, _pt_iface
    except Exception:
        point_shader = None

    # шейдер для линий с контролем ширины (совместимость с Vulkan)
    try:
        _ln_info = gpu.types.GPUShaderCreateInfo()
        _ln_info.push_constant('MAT4', "ModelViewProjectionMatrix")
        _ln_info.push_constant('VEC4', "color")
        _ln_info.push_constant('FLOAT', "lineWidth")
        _ln_info.push_constant('VEC2', "viewportSize")
        _ln_info.vertex_in(0, 'VEC3', "pos")
        _ln_info.fragment_out(0, 'VEC4', "fragColor")
        _ln_info.vertex_source(
            "void main()\n"
            "{\n"
            "  gl_Position = ModelViewProjectionMatrix * vec4(pos, 1.0);\n"
            "}\n"
        )
        _ln_info.geometry_layout('LINES', 'TRIANGLE_STRIP', 4)
        _ln_info.geometry_source(
            "void main()\n"
            "{\n"
            "  vec4 p0 = gl_in[0].gl_Position;\n"
            "  vec4 p1 = gl_in[1].gl_Position;\n"
            "  vec2 ndc0 = p0.xy / p0.w;\n"
            "  vec2 ndc1 = p1.xy / p1.w;\n"
            "  vec2 diff = (ndc1 - ndc0) * viewportSize;\n"
            "  float len = length(diff);\n"
            "  if (len < 0.001) return;\n"
            "  vec2 screenDir = diff / len;\n"
            "  vec2 offset = vec2(-screenDir.y, screenDir.x) * (lineWidth * 0.5) / viewportSize;\n"
            "  gl_Position = vec4((ndc0 + offset) * p0.w, p0.z, p0.w);\n"
            "  EmitVertex();\n"
            "  gl_Position = vec4((ndc0 - offset) * p0.w, p0.z, p0.w);\n"
            "  EmitVertex();\n"
            "  gl_Position = vec4((ndc1 + offset) * p1.w, p1.z, p1.w);\n"
            "  EmitVertex();\n"
            "  gl_Position = vec4((ndc1 - offset) * p1.w, p1.z, p1.w);\n"
            "  EmitVertex();\n"
            "  EndPrimitive();\n"
            "}\n"
        )
        _ln_info.fragment_source(
            "void main()\n"
            "{\n"
            "  fragColor = color;\n"
            "}\n"
        )
        line_shader = gpu.shader.create_from_info(_ln_info)
        del _ln_info
    except Exception:
        line_shader = None
else:
    shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
    point_shader = None
    line_shader = None


# данные для отрисовки гизмо
ngone_co = []
ngons_indices = []
tris_co = []
custom_co = []
custom_faces_indices = []
e_non_co = []
ngone_idx = []
e_non_idx = []
custom_faces_idx = []
elongated_tris_co = []

# unified данные для точек (per-vertex цвета)
point_pos = []
point_col1 = []
point_col2 = []

# счётчики для статистики
v_alone_count = 0
v_bound_count = 0
e_pole_count = 0
n_pole_count = 0
f_pole_count = 0


def check_draw(self, context):
    """отрисовка результатов проверки меша"""
    props = get_addon_prefs()
    if not props:
        return
    settings = context.scene.poly_source

    state.blend_set('ALPHA')

    if not settings.xray_for_check:
        state.depth_mask_set(False)
        state.face_culling_set('BACK')
        state.depth_test_set('LESS_EQUAL')

    # --- грани (TRIS) — стандартный шейдер ---
    shader.bind()

    if settings.ngone and ngone_co:
        batch = batch_for_shader(shader, 'TRIS', {"pos": ngone_co}, indices=ngons_indices)
        shader.uniform_float("color", props.ngone_col)
        batch.draw(shader)

    if settings.tris and tris_co:
        batch = batch_for_shader(shader, 'TRIS', {"pos": tris_co})
        shader.uniform_float("color", props.tris_col)
        batch.draw(shader)

    if settings.custom_count and custom_co:
        batch = batch_for_shader(shader, 'TRIS', {"pos": custom_co}, indices=custom_faces_indices)
        shader.uniform_float("color", props.custom_col)
        batch.draw(shader)

    # отключаем face culling для линий и точек (quad-линии из geometry shader)
    state.face_culling_set('NONE')

    # --- рёбра (LINES) ---
    if line_shader:
        line_shader.bind()
        mvp = gpu.matrix.get_projection_matrix() @ gpu.matrix.get_model_view_matrix()
        line_shader.uniform_float("ModelViewProjectionMatrix", mvp)
        line_shader.uniform_float("lineWidth", props.line_width)
        region = context.region
        line_shader.uniform_float("viewportSize", (float(region.width), float(region.height)))
        _ls = line_shader
    else:
        state.line_width_set(props.line_width)
        _ls = shader

    if settings.non_manifold_check and e_non_co:
        batch = batch_for_shader(_ls, 'LINES', {"pos": e_non_co})
        _ls.uniform_float("color", props.non_manifold_color)
        batch.draw(_ls)

    if settings.elongated_tris and elongated_tris_co:
        batch = batch_for_shader(_ls, 'LINES', {"pos": elongated_tris_co})
        _ls.uniform_float("color", props.elongated_tris_col)
        batch.draw(_ls)

    # --- вершины (POINTS) — единый draw call с per-vertex цветами ---
    if point_pos:
        if point_shader:
            state.program_point_size_set(True)
            point_shader.bind()
            mvp = gpu.matrix.get_projection_matrix() @ gpu.matrix.get_model_view_matrix()
            point_shader.uniform_float("ModelViewProjectionMatrix", mvp)
            point_shader.uniform_float("pointSize", props.point_width)
            batch = batch_for_shader(point_shader, 'POINTS', {
                "pos": point_pos,
                "col1": point_col1,
                "col2": point_col2,
            })
            batch.draw(point_shader)
        else:
            # fallback для OpenGL — рисуем все точки одним цветом
            state.point_size_set(props.point_width)
            batch = batch_for_shader(shader, 'POINTS', {"pos": point_pos})
            shader.uniform_float("color", (1.0, 1.0, 0.0, 1.0))
            batch.draw(shader)

    # восстанавливаем состояние GPU
    if point_shader:
        state.program_point_size_set(False)
    state.depth_mask_set(True)
    state.depth_test_set('NONE')
    state.face_culling_set('NONE')
    state.point_size_set(3.0)
    state.line_width_set(1.0)
    state.blend_set('NONE')


class PS_GT_check(Gizmo):
    """Mesh check overlay gizmo"""
    bl_idname = 'PS_GT_check'

    def draw(self, context):
        check_draw(self, context)


class PS_GGT_check_group(GizmoGroup):
    """Mesh check overlay gizmo group"""
    bl_idname = 'PS_GGT_check_group'
    bl_label = "PS Draw"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'PERSISTENT', 'SHOW_MODAL_ALL'}

    @classmethod
    def poll(cls, context):
        settings = context.scene.poly_source
        return settings.show_check

    def setup(self, context):
        self.mesh = self.gizmos.new(PS_GT_check.bl_idname)
        self.mesh.use_draw_modal = True
        self.mesh.hide_select = True

    def refresh(self, context):
        global ngone_co, ngons_indices, tris_co, custom_co, custom_faces_indices
        global e_non_co, ngone_idx, e_non_idx, custom_faces_idx, elongated_tris_co
        global point_pos, point_col1, point_col2
        global v_alone_count, v_bound_count, e_pole_count, n_pole_count, f_pole_count

        # сброс всех списков
        ngone_co = []
        ngons_indices = []
        tris_co = []
        custom_co = []
        custom_faces_indices = []
        e_non_co = []
        ngone_idx = []
        e_non_idx = []
        custom_faces_idx = []
        elongated_tris_co = []
        point_pos = []
        point_col1 = []
        point_col2 = []
        v_alone_count = 0
        v_bound_count = 0
        e_pole_count = 0
        n_pole_count = 0
        f_pole_count = 0

        objs = [obj for obj in context.selected_objects if obj.type == 'MESH' and len(obj.data.polygons) < 50000]
        if not objs:
            return

        depsgraph = context.evaluated_depsgraph_get()
        settings = context.scene.poly_source

        for obj in objs:
            if context.mode == 'EDIT_MESH' and obj.mode == 'EDIT':
                bm = bmesh.from_edit_mesh(obj.data)
            else:
                bm = bmesh.new()
                mesh_data = obj.evaluated_get(depsgraph).data if settings.use_modifiers and obj.modifiers else obj.data
                bm.from_mesh(mesh_data)
                bm.verts.ensure_lookup_table()
                bm.edges.ensure_lookup_table()
                bm.faces.ensure_lookup_table()

            # n-gone
            if settings.ngone:
                # локальные индексы граней текущего объекта
                obj_ngone_idx = [n.index for n in bm.faces if len(n.verts) > 4]
                ngone_idx.extend(obj_ngone_idx)

                if obj_ngone_idx:
                    copy = bm.copy()
                    copy.faces.ensure_lookup_table()
                    edge_n = set(e for i in obj_ngone_idx for e in copy.faces[i].edges)

                    for e in copy.edges:
                        if e not in edge_n:
                            e.hide_set(True)

                    bmesh.ops.triangulate(copy, faces=copy.faces[:])

                    offset = len(ngone_co)
                    v_count = 0
                    for f in copy.faces:
                        if not f.hide:
                            ngone_co.extend([obj.matrix_world @ v.co for v in f.verts])
                            v_count += len(f.verts)

                    copy.free()
                    ngons_indices.extend(
                        [offset + vi, offset + vi + 1, offset + vi + 2] for vi in range(0, v_count, 3)
                    )

            # кастомный подсчёт
            if settings.custom_count:
                # локальные индексы граней текущего объекта
                obj_custom_idx = [n.index for n in bm.faces if len(n.verts) == settings.custom_count_verts]
                custom_faces_idx.extend(obj_custom_idx)

                if obj_custom_idx:
                    copy = bm.copy()
                    copy.faces.ensure_lookup_table()
                    edge_n = set(e for i in obj_custom_idx for e in copy.faces[i].edges)

                    for e in copy.edges:
                        if e not in edge_n:
                            e.hide_set(True)

                    bmesh.ops.triangulate(copy, faces=copy.faces[:])

                    offset = len(custom_co)
                    v_count = 0
                    for f in copy.faces:
                        if not f.hide:
                            custom_co.extend([obj.matrix_world @ v.co for v in f.verts])
                            v_count += len(f.verts)

                    copy.free()
                    custom_faces_indices.extend(
                        [offset + vi, offset + vi + 1, offset + vi + 2] for vi in range(0, v_count, 3)
                    )

            # non-manifold рёбра
            if settings.non_manifold_check:
                obj_non_idx = [e.index for e in bm.edges if not e.is_manifold]
                e_non_idx.extend(obj_non_idx)
                e_non_co.extend([obj.matrix_world @ v.co for i in obj_non_idx for v in bm.edges[i].verts])

            # unified проверка вершин с детекцией наложений
            any_vert = (settings.e_pole or settings.n_pole or settings.f_pole
                        or settings.v_bound or settings.v_alone)
            if any_vert:
                props = get_addon_prefs()
                if props:
                    # предвычисляем цвета (один раз, не в цикле)
                    check_alone = settings.v_alone
                    check_bound = settings.v_bound
                    check_e = settings.e_pole
                    check_n = settings.n_pole
                    check_f = settings.f_pole
                    col_alone = tuple(props.v_alone_color) if check_alone else None
                    col_bound = tuple(props.bound_col) if check_bound else None
                    col_e = tuple(props.e_pole_col) if check_e else None
                    col_n = tuple(props.n_pole_col) if check_n else None
                    col_f = tuple(props.f_pole_col) if check_f else None
                    no_col = (0.0, 0.0, 0.0, 0.0)
                    matrix = obj.matrix_world

                    for v in bm.verts:
                        colors = []
                        ec = len(v.link_edges)

                        if check_alone and ec < 1:
                            v_alone_count += 1
                            colors.append(col_alone)
                        if check_bound and (v.is_boundary or not v.is_manifold):
                            v_bound_count += 1
                            colors.append(col_bound)
                        if check_e and ec == 5:
                            e_pole_count += 1
                            colors.append(col_e)
                        if check_n and ec == 3:
                            n_pole_count += 1
                            colors.append(col_n)
                        if check_f and ec > 5:
                            f_pole_count += 1
                            colors.append(col_f)

                        if colors:
                            point_pos.append(matrix @ v.co)
                            point_col1.append(colors[0])
                            point_col2.append(colors[1] if len(colors) > 1 else no_col)

            # треугольники и вытянутые треугольники
            if settings.elongated_tris or settings.tris:
                for f in bm.faces:
                    if len(f.verts) == 3:
                        verts = [obj.matrix_world @ v.co for v in f.verts]

                        if settings.tris:
                            tris_co.extend(verts)

                        if settings.elongated_tris:
                            a = (verts[0] - verts[1]).length
                            b = (verts[1] - verts[2]).length
                            c = (verts[2] - verts[0]).length
                            longest_side = max(a, b, c)
                            s = (a + b + c) / 2
                            area = math.sqrt(max(0, s * (s - a) * (s - b) * (s - c)))
                            if area > 0:
                                shortest_height = 2 * area / longest_side
                                if longest_side / shortest_height > settings.elongated_aspect_ratio:
                                    elongated_tris_co.extend([
                                        verts[0], verts[1],
                                        verts[1], verts[2],
                                        verts[2], verts[0],
                                    ])

            if not (context.mode == 'EDIT_MESH' and obj.mode == 'EDIT'):
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
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
