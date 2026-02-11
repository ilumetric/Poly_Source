import bpy
import bmesh
from ..icons import preview_collections
from ..utils.utils import get_addon_prefs


def get_polygons_count_ui(context, layout):
    """отрисовка счётчика полигонов в хедере"""
    props = get_addon_prefs()
    if not props:
        return
    pcoll = preview_collections['main']
    ngon_icon = pcoll['ngon_icon']
    quad_icon = pcoll['quad_icon']
    tris_icon = pcoll['tris_icon']
    layout.separator(factor=0.2)

    if context.region.alignment != 'RIGHT' and context.object:
        objs = context.selected_objects
        _tris, _quad, _ngon = 0, 0, 0
        _total_vertices, _total_objects = 0, 0

        for obj in objs:
            if obj.type != 'MESH':
                continue
            _total_vertices += len(obj.data.vertices)
            _total_objects += 1
            if _total_vertices > props.max_verts or _total_objects > props.max_objs:
                break

        if _total_vertices < props.max_verts and _total_objects < props.max_objs:
            if context.mode == 'EDIT_MESH':
                for obj in objs:
                    bm = bmesh.from_edit_mesh(obj.data)
                    _tris += sum(1 for face in bm.faces if len(face.verts) == 3)
                    _quad += sum(1 for face in bm.faces if len(face.verts) == 4)
                    _ngon += sum(1 for face in bm.faces if len(face.verts) > 4)
            else:
                for obj in objs:
                    if obj.type == 'MESH':
                        for polygon in obj.data.polygons:
                            count = polygon.loop_total
                            if count == 3:
                                _tris += 1
                            elif count == 4:
                                _quad += 1
                            else:
                                _ngon += 1

            layout.operator('mesh.ps_select_polygons', text=str(_ngon), icon_value=ngon_icon.icon_id).polygon_type = 'NGONS'
            layout.operator('mesh.ps_select_polygons', text=str(_quad), icon_value=quad_icon.icon_id).polygon_type = 'QUADS'
            layout.operator('mesh.ps_select_polygons', text=str(_tris), icon_value=tris_icon.icon_id).polygon_type = 'TRIS'
        else:
            layout.operator('mesh.ps_select_polygons', text='', icon_value=ngon_icon.icon_id).polygon_type = 'NGONS'
            layout.operator('mesh.ps_select_polygons', text='', icon_value=quad_icon.icon_id).polygon_type = 'QUADS'
            layout.operator('mesh.ps_select_polygons', text='', icon_value=tris_icon.icon_id).polygon_type = 'TRIS'
            box = layout.box()
            box.label(text='Vertex/Obj Excess', icon='ERROR')


def bool_ui(context, layout):
    """отрисовка кнопок булевых операций"""
    pcoll = preview_collections['main']
    row = layout.row(align=True)
    row.operator('object.ps_bool_difference', text='', icon_value=pcoll['bool_diff'].icon_id)
    row.operator('object.ps_bool_union', text='', icon_value=pcoll['bool_union'].icon_id)
    row.operator('object.ps_bool_intersect', text='', icon_value=pcoll['bool_intersect'].icon_id)
    row.operator('object.ps_bool_slice', text='', icon_value=pcoll['bool_slice'].icon_id)


def _draw_header_content(self, context, check_prop):
    """общая логика для хедер-панелей"""
    props = get_addon_prefs()
    if not props:
        return
    if not getattr(props, check_prop, False):
        return
    if not context.object or context.object.type != 'MESH':
        return

    settings = context.scene.poly_source
    pcoll = preview_collections['main']
    check_icon = pcoll['check_icon']

    layout = self.layout
    row = layout.row(align=True)
    row.popover(panel='PS_PT_transform_plus', text='', icon='EMPTY_ARROWS')
    #row.popover(panel='PS_PT_tool_kit', text='')
    get_polygons_count_ui(context, row)
    row.separator(factor=0.2)
    row.prop(settings, 'show_check', text='', icon_value=check_icon.icon_id)
    if settings.show_check:
        row.popover(panel='PS_PT_check', text='')
    if props.b_bool_tool:
        bool_ui(context, layout)


def header_panel(self, context):
    """панель в верхнем хедере"""
    if context.region.alignment == 'TOP':
        _draw_header_content(self, context, 'b_count_header')


def view_header_left_panel(self, context):
    """панель в левом хедере вьюпорта"""
    _draw_header_content(self, context, 'b_count_view_header_l')


def view_header_right_panel(self, context):
    """панель в правом хедере вьюпорта"""
    _draw_header_content(self, context, 'b_count_view_header_r')


def tool_panel(self, context):
    """панель в тулхедере"""
    layout = self.layout
    self.draw_tool_settings(context)
    layout.separator_spacer()

    if context.object:
        props = get_addon_prefs()
        if not props:
            layout.separator_spacer()
            self.draw_mode_settings(context)
            return
        settings = context.scene.poly_source
        pcoll = preview_collections['main']
        check_icon = pcoll['check_icon']

        if context.object.type == 'MESH' and props.b_count_tool_header:
            row = layout.row(align=True)
            row.popover(panel='PS_PT_transform_plus', text='', icon='EMPTY_ARROWS')
            get_polygons_count_ui(context, row)
            row.separator(factor=0.2)
            row.prop(settings, 'show_check', text='', icon_value=check_icon.icon_id)
            if settings.show_check:
                row.popover(panel='PS_PT_check', text='')
            if props.b_bool_tool:
                bool_ui(context, layout)
            #row.popover(panel='PS_PT_tool_kit', text='')

    layout.separator_spacer()
    self.draw_mode_settings(context)
