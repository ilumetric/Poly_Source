import bpy
from bpy.types import Panel
from ..icons import preview_collections
from ..utils.utils import get_active_3d_view, get_addon_prefs
from .. import check


# --- вспомогательные функции для PS_PT_tool_kit ---

def display_panel(self, context, layout):
    """панель настроек отображения"""
    space_data = get_active_3d_view()
    if space_data is not None:
        overlay = space_data.overlay
        if overlay.show_retopology:
            box = layout.box()
            box.prop(overlay, 'show_retopology', icon='GREASEPENCIL')
            box.prop(overlay, 'retopology_offset')
            theme = context.preferences.themes[0].view_3d
            box.prop(theme, 'face_retopology')
            box.prop(theme, 'edge_width')
            box.prop(theme, 'vertex_size')
        else:
            layout.prop(overlay, 'show_retopology', icon='GREASEPENCIL')


# --- классы панелей ---

class PS_PT_unit_grid(Panel):
    """Unit grid overlay settings"""
    bl_label = 'Unit Grid'
    bl_idname = 'PS_PT_unit_grid'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'PS'

    def draw_header(self, context):
        self.layout.prop(context.scene.poly_source, "draw_grid", text="")

    def draw(self, context):
        settings = context.scene.poly_source
        if settings.draw_grid:
            layout = self.layout

            row = layout.row()
            row.prop(settings, 'box', text="Draw Box", toggle=True)
            row.prop(settings, 'grid_xray', toggle=True)
            row.prop(settings, 'one2one', toggle=True)

            row = layout.row(align=True)
            row.prop(settings, 'unit_x')
            if not settings.one2one:
                row.prop(settings, 'unit_y')
            if settings.box:
                row.prop(settings, 'height')

            row = layout.row()
            row.prop(settings, 'padding')
            row.prop(settings, 'offset_z')

            if settings.draw_sub_grid:
                row = layout.row(align=True)
                row.prop(settings, 'draw_sub_grid', text="", icon='MESH_GRID')
                row.prop(settings, 'grid_cell_size')
                row.prop(settings, 'grid_align_center', text="", icon='SNAP_FACE_CENTER')
            else:
                layout.prop(settings, 'draw_sub_grid')


class PS_PT_check(Panel):
    """Mesh check overlay configuration"""
    bl_idname = 'PS_PT_check'
    bl_label = 'Check Objects'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'

    @staticmethod
    def _check_row(layout, settings, prefs, toggle_prop, color_prop):
        """рисует строку: кнопка-переключатель + полоска цвета справа"""
        row = layout.row(align=True)
        row.prop(settings, toggle_prop, toggle=True)
        sub = row.row(align=True)
        sub.scale_x = 0.3
        sub.enabled = getattr(settings, toggle_prop)
        sub.prop(prefs, color_prop, text="")

    def draw(self, context):
        settings = context.scene.poly_source
        prefs = get_addon_prefs()
        layout = self.layout

        row = layout.row()
        col = row.column()
        col.scale_y = 1.5
        self._check_row(col, settings, prefs, "v_alone", "v_alone_color")
        self._check_row(col, settings, prefs, "v_bound", "bound_col")
        self._check_row(col, settings, prefs, "n_pole", "n_pole_col")
        self._check_row(col, settings, prefs, "e_pole", "e_pole_col")
        self._check_row(col, settings, prefs, "f_pole", "f_pole_col")

        col = row.column()
        col.scale_y = 1.5
        self._check_row(col, settings, prefs, "tris", "tris_col")
        self._check_row(col, settings, prefs, "ngone", "ngone_col")
        self._check_row(col, settings, prefs, "non_manifold_check", "non_manifold_color")
        self._check_row(col, settings, prefs, "elongated_tris", "elongated_tris_col")
        self._check_row(col, settings, prefs, "custom_count", "custom_col")

        if settings.elongated_tris:
            layout.prop(settings, "elongated_aspect_ratio")
        if settings.custom_count:
            layout.prop(settings, "custom_count_verts")

        # статистика по найденным проблемам
        any_active = any([
            settings.v_alone, settings.v_bound, settings.e_pole,
            settings.n_pole, settings.f_pole, settings.tris,
            settings.ngone, settings.non_manifold_check, settings.custom_count,
        ])
        if any_active:
            box = layout.box()
            if settings.v_alone:
                box.label(text='Isolated Vertices: ' + str(check.v_alone_count))
            if settings.v_bound:
                box.label(text='Boundary: ' + str(check.v_bound_count))
            if settings.e_pole:
                box.label(text='E-Pole (5): ' + str(check.e_pole_count))
            if settings.n_pole:
                box.label(text='N-Pole (3): ' + str(check.n_pole_count))
            if settings.f_pole:
                box.label(text='>5 Pole: ' + str(check.f_pole_count))
            if settings.tris:
                box.label(text='Triangles: ' + str(len(check.tris_co) // 3))
            if settings.ngone:
                box.label(text='N-Gons: ' + str(len(check.ngone_idx)))
            if settings.non_manifold_check:
                box.label(text='Non-Manifold: ' + str(len(check.e_non_idx)))
            if settings.elongated_tris:
                box.label(text='Elongated Tris: ' + str(len(check.elongated_tris_co) // 6))
            if settings.custom_count:
                box.label(text='Custom: ' + str(len(check.custom_faces_idx)))

        layout.prop(settings, "xray_for_check")
        layout.prop(settings, "use_modifiers")


panels_classes = [
    PS_PT_check,
    PS_PT_unit_grid,
]
