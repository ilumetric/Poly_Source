import bpy
from bpy.types import Menu
from ..icons import preview_collections
from ..utils.utils import get_addon_prefs


class PS_MT_modifiers(Menu):
    """Modifier presets submenu"""
    bl_label = 'Modifiers'
    bl_idname = 'PS_MT_modifiers'

    def draw(self, context):
        pcoll = preview_collections["main"]
        layout = self.layout
        layout.operator('object.ps_tris_weighted_normal', text='Tris & Weighted Normal', icon_value=pcoll["fix_icon"].icon_id)
        layout.operator('object.ps_triangulate', text='Triangulate', icon='MOD_TRIANGULATE')
        layout.operator('object.ps_add_subsurf_and_bevel', text='Crease Bevel', icon_value=pcoll["bevelSub"].icon_id)
        layout.operator('object.ps_solidify', text='Solidify', icon='MOD_SOLIDIFY')


class PS_MT_test(Menu):
    """Utility operators submenu"""
    bl_label = 'TEST'
    bl_idname = 'PS_MT_test'

    def draw(self, context):
        layout = self.layout
        if context.mode == 'EDIT_MESH':
            layout.operator("mesh.ps_clear_dots", icon='SHADERFX')
            layout.operator("mesh.ps_remove_vertex_non_manifold", icon='SHADERFX')
            layout.operator("mesh.ps_cylinder_optimizer", icon='MESH_CYLINDER').rounding = False
            layout.operator("mesh.ps_cylinder_optimizer", text='Rounding Up', icon='MESH_CYLINDER').rounding = True
            layout.operator("mesh.ps_del_long_faces")
            layout.operator("outliner.orphans_purge", text="Purge")
            layout.operator('mesh.ps_fill_from_points')
        if context.mode == 'OBJECT':
            layout.operator('object.ps_transfer_transform')
            layout.operator('object.ps_clear_materials')
            layout.operator('object.ps_clear_data')
            layout.operator('object.ps_unreal_material')
            layout.operator('object.ps_distribute_objects')


class PS_MT_main(Menu):
    """Main Poly Source context menu"""
    bl_label = 'Poly Source'
    bl_idname = 'PS_MT_main'
    bl_options = {'SEARCH_ON_KEY_PRESS'}

    def draw(self, context):
        pcoll = preview_collections["main"]
        seam_icon = pcoll["seam"]
        sharp_icon = pcoll["sharp"]
        bevelW_icon = pcoll["bevelW"]
        creaseW_icon = pcoll["creaseW"]

        layout = self.layout
        layout.menu('PS_MT_modifiers')
        layout.menu('PS_MT_test')

        if context.mode == 'EDIT_MESH':
            layout.separator()

            op = layout.operator('mesh.ps_set_edge_data', text='Seam / Sharp', icon_value=seam_icon.icon_id)
            op.do_seam = True
            op.do_sharp = True
            op.do_bevel = False
            op.do_crease = False

            op = layout.operator('mesh.ps_set_edge_data', text='Seam', icon_value=seam_icon.icon_id)
            op.do_seam = True
            op.do_sharp = False
            op.do_bevel = False
            op.do_crease = False

            op = layout.operator('mesh.ps_set_edge_data', text='Sharp', icon_value=sharp_icon.icon_id)
            op.do_sharp = True
            op.do_seam = False
            op.do_bevel = False
            op.do_crease = False

            op = layout.operator('mesh.ps_set_edge_data', text='Bevel', icon_value=bevelW_icon.icon_id)
            op.do_bevel = True
            op.do_seam = False
            op.do_sharp = False
            op.do_crease = False

            op = layout.operator('mesh.ps_set_edge_data', text='Crease', icon_value=creaseW_icon.icon_id)
            op.do_crease = True
            op.do_seam = False
            op.do_sharp = False
            op.do_bevel = False

            layout.separator()
            layout.operator('mesh.edges_select_sharp', icon='LINCURVE')
            layout.operator('mesh.select_nth', icon='TEXTURE_DATA')
            layout.operator('mesh.loop_multi_select', text='Edge Loop', icon='MATSPHERE').ring = False
            layout.operator('mesh.loop_multi_select', text='Edge Ring', icon='SNAP_EDGE').ring = True
            layout.operator('mesh.region_to_loop', text='Boundary Loop', icon='MESH_GRID')


def rmb_menu(self, context):
    if context.mode in ['OBJECT', 'EDIT_MESH']:
        self.layout.menu('PS_MT_main')


def preset_increment_angle(self, context):
    props = get_addon_prefs()
    if not props or not props.b_presets_increment_angles:
        return

    from math import degrees

    ts = context.scene.tool_settings

    # определяем целевое свойство в зависимости от редактора
    space = context.space_data
    if space and space.type == 'IMAGE_EDITOR':
        attr = 'snap_angle_increment_2d'
    else:
        attr = 'snap_angle_increment_3d'

    current_angle = round(degrees(getattr(ts, attr)))

    row = self.layout.row(align=True)
    for angle in [5, 10, 15, 30, 45, 60, 90]:
        op = row.operator(
            'scene.ps_set_increment_angle',
            text=f'{angle}\u00b0',
            depress=(current_angle == angle),
        )
        op.angle = angle
        op.target = attr


def outliner_header_button(self, context):
    self.layout.operator('object.ps_random_name', text='', icon='QUESTION')


menus_classes = [
    PS_MT_modifiers,
    PS_MT_test,
    PS_MT_main,
]
