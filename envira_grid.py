import bpy
import gpu
import math
from gpu_extras.batch import batch_for_shader
from bpy.types import GizmoGroup, Gizmo
from gpu import state
from .utils.utils import get_addon_prefs


def generate_grid():
    """
    генерирует координаты внутренней сетки, ограниченной основной рамкой

    - каждая ячейка имеет заданный пользователем размер (в сантиметрах)
    - сетка размещается внутри основной рамки (unit_x / unit_y или 1x1, если включено)
    - выравнивание может быть по центру или от угла +X +Y

    возвращает:
        list: плоский список кортежей координат для батча 'LINES' (v1, v2, v1, v2, ...)
    """
    settings = bpy.context.scene.poly_source

    # работаем в сантиметрах; переводим в метры только при формировании координат
    x_outer_cm = max(0.0, abs(settings.unit_x))
    if settings.one2one:
        y_outer_cm = x_outer_cm
    else:
        y_outer_cm = max(0.0, abs(settings.unit_y))

    cell_size_cm = max(0.0001, abs(settings.grid_cell_size))
    z_pos = settings.offset_z / 100.0

    # габариты рамки в метрах
    half_x = (x_outer_cm / 100.0) / 2.0
    half_y = (y_outer_cm / 100.0) / 2.0

    # количество целых ячеек, помещающихся внутрь рамки
    num_cells_x = int(max(0, math.floor((x_outer_cm + 1e-6) / cell_size_cm)))
    num_cells_y = int(max(0, math.floor((y_outer_cm + 1e-6) / cell_size_cm)))

    vertical_positions = []
    horizontal_positions = []

    if settings.grid_align_center:
        # центрирование: одинаковые отступы по краям
        if num_cells_x >= 1:
            remainder_x_cm = x_outer_cm - num_cells_x * cell_size_cm
            left_margin_x_cm = remainder_x_cm / 2.0
            first_x_cm = -x_outer_cm / 2.0 + left_margin_x_cm
            vertical_positions = [
                (first_x_cm + i * cell_size_cm) / 100.0 for i in range(0, num_cells_x + 1)
            ]
        if num_cells_y >= 1:
            remainder_y_cm = y_outer_cm - num_cells_y * cell_size_cm
            bottom_margin_y_cm = remainder_y_cm / 2.0
            first_y_cm = -y_outer_cm / 2.0 + bottom_margin_y_cm
            horizontal_positions = [
                (first_y_cm + i * cell_size_cm) / 100.0 for i in range(0, num_cells_y + 1)
            ]
    else:
        # от угла +X +Y: шагаем внутрь области
        if num_cells_x >= 1:
            start_x_cm = x_outer_cm / 2.0 - num_cells_x * cell_size_cm
            vertical_positions = [
                (start_x_cm + i * cell_size_cm) / 100.0 for i in range(0, num_cells_x + 1)
            ]
        if num_cells_y >= 1:
            start_y_cm = y_outer_cm / 2.0 - num_cells_y * cell_size_cm
            horizontal_positions = [
                (start_y_cm + i * cell_size_cm) / 100.0 for i in range(0, num_cells_y + 1)
            ]

    # убираем самые крайние значения, чтобы не дублировать периметр
    def drop_edges(values, v_min, v_max, eps=1e-7):
        return [v for v in values if (v - v_min) > eps and (v_max - v) > eps]

    v_pos = drop_edges(vertical_positions, -half_x, half_x)
    h_pos = drop_edges(horizontal_positions, -half_y, half_y)

    line_co = []
    y_min, y_max = -half_y, half_y
    for x in v_pos:
        line_co.append((x, y_min, z_pos))
        line_co.append((x, y_max, z_pos))

    x_min, x_max = -half_x, half_x
    for y in h_pos:
        line_co.append((x_min, y, z_pos))
        line_co.append((x_max, y, z_pos))

    return line_co


def lines():
    settings = bpy.context.scene.poly_source
    # значения приходят в сантиметрах, переводим в метры
    x = settings.unit_x / 100.0
    y = settings.unit_y / 100.0
    z = settings.offset_z / 100.0
    x_pad = (settings.unit_x - (settings.padding * 2.0)) / 100.0
    y_pad = (settings.unit_y - (settings.padding * 2.0)) / 100.0

    lines_co = []

    if settings.one2one:
        lines_co = [
            (x/2, x/2, z), (-x/2, x/2, z),
            (-x/2, x/2, z), (-x/2, -x/2, z),
            (-x/2, -x/2, z), (x/2, -x/2, z),
            (x/2, -x/2, z), (x/2, x/2, z),

            (x_pad/2, x_pad/2, z), (-x_pad/2, x_pad/2, z),
            (-x_pad/2, x_pad/2, z), (-x_pad/2, -x_pad/2, z),
            (-x_pad/2, -x_pad/2, z), (x_pad/2, -x_pad/2, z),
            (x_pad/2, -x_pad/2, z), (x_pad/2, x_pad/2, z),
        ]

    else:
        lines_co = [
            (x/2, y/2, z), (-x/2, y/2, z),
            (-x/2, y/2, z), (-x/2, -y/2, z),
            (-x/2, -y/2, z), (x/2, -y/2, z),
            (x/2, -y/2, z), (x/2, y/2, z),

            (x_pad/2, y_pad/2, z), (-x_pad/2, y_pad/2, z),
            (-x_pad/2, y_pad/2, z), (-x_pad/2, -y_pad/2, z),
            (-x_pad/2, -y_pad/2, z), (x_pad/2, -y_pad/2, z),
            (x_pad/2, -y_pad/2, z), (x_pad/2, y_pad/2, z),
        ]

    return lines_co


def box():
    settings = bpy.context.scene.poly_source
    # значения приходят в сантиметрах, переводим в метры
    x_pad = (settings.unit_x - (settings.padding * 2.0)) / 100.0
    y_pad = (settings.unit_y - (settings.padding * 2.0)) / 100.0
    z = settings.offset_z / 100.0
    h = settings.height / 100.0

    if settings.one2one:
        face_co = [
            (x_pad/2, x_pad/2, z),
            (x_pad/2, -x_pad/2, z),
            (-x_pad/2, -x_pad/2, z),
            (-x_pad/2, x_pad/2, z),
            (x_pad/2, x_pad/2, h),
            (x_pad/2, -x_pad/2, h),
            (-x_pad/2, -x_pad/2, h),
            (-x_pad/2, x_pad/2, h),
        ]
    else:
        face_co = [
            (x_pad/2, y_pad/2, z),
            (x_pad/2, -y_pad/2, z),
            (-x_pad/2, -y_pad/2, z),
            (-x_pad/2, y_pad/2, z),
            (x_pad/2, y_pad/2, h),
            (x_pad/2, -y_pad/2, h),
            (-x_pad/2, -y_pad/2, h),
            (-x_pad/2, y_pad/2, h),
        ]

    faces_indices = [
        (0, 1, 3), (1, 2, 3),
        (4, 5, 7), (5, 6, 7),
        (1, 2, 5), (2, 5, 6),
        (0, 1, 4), (1, 4, 5),
        (0, 3, 7), (0, 4, 7),
        (2, 3, 6), (3, 6, 7),
    ]

    return face_co, faces_indices


if bpy.app.version >= (4, 0, 0):
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
else:
    shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')


def draw_grid(self, context):
    props = get_addon_prefs()
    if not props:
        return
    settings = context.scene.poly_source

    shader.bind()

    # ширины из темы
    theme = context.preferences.themes['Default']
    edge_width = theme.view_3d.edge_width
    vertex_size = theme.view_3d.vertex_size

    state.blend_set('ALPHA')
    state.line_width_set(edge_width + 2)
    state.point_size_set(vertex_size)

    if not settings.grid_xray:
        state.depth_mask_set(False)
        state.depth_test_set('LESS_EQUAL')

    if settings.box:
        face_co, faces_indices = box()
        faces_batch = batch_for_shader(shader, 'TRIS', {"pos": face_co}, indices=faces_indices)
        shader.uniform_float("color", props.color_box)
        faces_batch.draw(shader)

    if settings.draw_sub_grid:
        grid_co = generate_grid()
        grid_batch = batch_for_shader(shader, 'LINES', {"pos": grid_co})
        c = props.color_grid
        shader.uniform_float("color", (c[0], c[1], c[2], c[3] / 2.0))
        grid_batch.draw(shader)

    lines_co = lines()
    edges_batch = batch_for_shader(shader, 'LINES', {"pos": lines_co})
    shader.uniform_float("color", props.color_grid)
    edges_batch.draw(shader)

    state.depth_mask_set(True)
    state.depth_test_set('NONE')
    state.face_culling_set('NONE')
    state.point_size_set(3.0)
    state.line_width_set(1.0)
    state.blend_set('NONE')


class PS_GT_grid(Gizmo):
    """Unit grid overlay gizmo"""
    bl_idname = 'PS_GT_grid'

    def draw(self, context):
        draw_grid(self, context)

    def setup(self):
        self.use_draw_modal = False


class PS_GGT_grid(GizmoGroup):
    """Unit grid overlay gizmo group"""
    bl_idname = 'PS_GGT_grid'
    bl_label = 'Grid'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'SHOW_MODAL_ALL', 'PERSISTENT'}

    @classmethod
    def poll(cls, context):
        return getattr(context.scene, 'poly_source', None) and context.scene.poly_source.draw_grid

    def setup(self, context):
        self.gizmos.new(PS_GT_grid.bl_idname)


classes = [
    PS_GT_grid,
    PS_GGT_grid,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
