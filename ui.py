import bpy
import bmesh
from bpy.types import Panel, Menu
from .icons import preview_collections
from .utils.utils import get_active_3d_view

from . import check



def get_polygons_count_ui(context, layout):
    props = context.preferences.addons['Poly_Source'].preferences
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

            if _total_vertices > props.maxVerts or _total_objects > props.maxObjs:
                break

        if _total_vertices < props.maxVerts and _total_objects < props.maxObjs:
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
    pcoll = preview_collections['main']
    bool_diff_icon = pcoll['bool_diff']
    bool_union_icon = pcoll['bool_union']
    bool_intersect_icon = pcoll['bool_intersect']
    bool_slice_icon = pcoll['bool_slice']
    row = layout.row(align=True)
    row.operator('object.ps_bool_difference', text='', icon_value=bool_diff_icon.icon_id)
    row.operator('object.ps_bool_union', text='', icon_value=bool_union_icon.icon_id)
    row.operator('object.ps_bool_intersect', text='', icon_value=bool_intersect_icon.icon_id)
    row.operator('object.ps_bool_slice', text='', icon_value=bool_slice_icon.icon_id)


def header_panel(self, context):
    props = context.preferences.addons['Poly_Source'].preferences
    settings = context.scene.poly_source
    pcoll = preview_collections['main']
    check_icon = pcoll['check_icon']


    if context.region.alignment == 'TOP':
        if context.object:
            if context.object.type == 'MESH':
                if props.b_count_header:
                    layout = self.layout
                    row = layout.row(align=True)
                    row.popover(panel='PS_PT_tool_kit', text='')
                    get_polygons_count_ui(context, row)
                    row.separator(factor=0.2)
                    row.prop(settings, 'PS_check', text='', icon_value=check_icon.icon_id)
                    if settings.PS_check:
                        row.popover(panel='PS_PT_check', text='')
                    #check_panel(self, context, row)
                    if props.b_bool_tool:
                        bool_ui(context, layout)


def viewHeader_L_panel(self, context):
    props = context.preferences.addons['Poly_Source'].preferences
    settings = context.scene.poly_source
    pcoll = preview_collections['main']
    check_icon = pcoll['check_icon']

    if context.object:
        if context.object.type == 'MESH':
            if props.b_count_view_header_l:
                layout = self.layout
                row = layout.row(align=True)
                row.popover(panel='PS_PT_tool_kit', text='')
                get_polygons_count_ui(context, row)
                row.separator(factor=0.2)
                row.prop(settings, 'PS_check', text='', icon_value=check_icon.icon_id)
                if settings.PS_check:
                    row.popover(panel='PS_PT_check', text='')
                #check_panel(self, context, row)
                if props.b_bool_tool:
                    bool_ui(context, layout)


def viewHeader_R_panel(self, context):
    props = context.preferences.addons['Poly_Source'].preferences
    settings = context.scene.poly_source
    pcoll = preview_collections['main']
    check_icon = pcoll['check_icon']

    if context.object:
        if context.object.type == 'MESH':
            if props.b_count_view_header_r:
                layout = self.layout
                row = layout.row(align=True)
                row.popover(panel='PS_PT_tool_kit', text='')
                get_polygons_count_ui(context, row)
                row.separator(factor=0.2)
                row.prop(settings, 'PS_check', text='', icon_value=check_icon.icon_id)
                if settings.PS_check:
                    row.popover(panel='PS_PT_check', text='')
                #check_panel(self, context, row)
                if props.b_bool_tool:
                    bool_ui(context, layout)


# def tool_panel(self, context):
#     props = context.preferences.addons['Poly_Source'].preferences
#     settings = context.scene.poly_source
#     pcoll = preview_collections['main']
#     check_icon = pcoll['check_icon']

#     if context.object:
#         if context.object.type == 'MESH':
#             if props.b_count_tool_header:
#                 layout = self.layout
#                 row = layout.row(align=True)
#                 row.popover(panel='PS_PT_tool_kit', text='')
#                 get_polygons_count_ui(context, row)
#                 row.separator(factor=0.2)
#                 row.prop(settings, 'PS_check', text='' , icon_value=check_icon.icon_id)
#                 if settings.PS_check:
#                     row.popover(panel='PS_PT_check', text='')
#                 #check_panel(self, context, row)
#                 if props.b_bool_tool:
#                     bool_ui(context, layout)


def tool_panel(self, context):
    layout = self.layout

    self.draw_tool_settings(context)

    layout.separator_spacer()
    if context.object:
        props = context.preferences.addons['Poly_Source'].preferences
        settings = context.scene.poly_source
        pcoll = preview_collections['main']
        check_icon = pcoll['check_icon']
        if context.object.type == 'MESH':
            if props.b_count_tool_header:
                layout = self.layout
                row = layout.row(align=True)
                row.popover(panel='PS_PT_tool_kit', text='')
                get_polygons_count_ui(context, row)
                row.separator(factor=0.2)
                row.prop(settings, 'PS_check', text='' , icon_value=check_icon.icon_id)
                if settings.PS_check:
                    row.popover(panel='PS_PT_check', text='')
                if props.b_bool_tool:
                    bool_ui(context, layout)
    layout.separator_spacer()

    self.draw_mode_settings(context)

# --- ADD OBJECT
# Layout
def custom_objects(self, context):
    props = context.preferences.addons['Poly_Source'].preferences

    if props.b_add_objects:
        pcoll = preview_collections["main"]
        cylinder_icon = pcoll["cylinder"]
        tube_icon = pcoll["tube"]
        cube_icon = pcoll["cube"]

        layout = self.layout
        layout.separator()
        layout.label(text='Poly Source')
        layout.operator("object.ps_create_cube", text="Cube", icon_value=cube_icon.icon_id)
        layout.operator("object.ps_create_cylinder", text="Cylinder", icon_value=cylinder_icon.icon_id)
        layout.operator("object.ps_create_tube", text="Tube", icon_value=tube_icon.icon_id)
    else:
        pass



# --- TRANSFORM ---
def transform_panel(self, context, pie):
    pcoll = preview_collections["main"]
    x_icon = pcoll["x_icon"]
    y_icon = pcoll["y_icon"]
    z_icon = pcoll["z_icon"]
    reset_all = pcoll["reset_icon"]

    box = pie
    if context.mode == 'OBJECT':
        box.label(text='Reset Transform')
        box.scale_x = 1.3

        row = box.row()
        row.operator('object.ps_reset_location_object', text='', icon_value=x_icon.icon_id).axis = 'X'
        row.operator('object.ps_reset_location_object', text='', icon_value=y_icon.icon_id).axis = 'Y'
        row.operator('object.ps_reset_location_object', text='', icon_value=z_icon.icon_id).axis = 'Z'
        row.operator('object.ps_reset_location_object', text='Location').axis = 'ALL'

        row = box.row()
        row.operator('object.ps_reset_rotation_object', text='', icon_value=x_icon.icon_id).axis = 'X'
        row.operator('object.ps_reset_rotation_object', text='', icon_value=y_icon.icon_id).axis = 'Y'
        row.operator('object.ps_reset_rotation_object', text='', icon_value=z_icon.icon_id).axis = 'Z'
        row.operator('object.ps_reset_rotation_object', text='Rotation').axis = 'ALL'

        row = box.row()
        row.operator('object.ps_reset_scale_object', text='', icon_value=x_icon.icon_id).axis = 'X'
        row.operator('object.ps_reset_scale_object', text='', icon_value=y_icon.icon_id).axis = 'Y'
        row.operator('object.ps_reset_scale_object', text='', icon_value=z_icon.icon_id).axis = 'Z'
        row.operator('object.ps_reset_scale_object', text='Scale').axis = 'ALL'

        box.operator("object.ps_reset_location_object", text='Reset All', icon_value=reset_all.icon_id).axis = 'ALL_T'

    elif context.mode == 'EDIT_MESH':
        box.label(text='Reset Transform')
        box.scale_x = 1.3

        row = box.row()
        row.operator("mesh.ps_locvert", text='', icon_value=x_icon.icon_id).axis = 'X'
        row.operator("mesh.ps_locvert", text='', icon_value=y_icon.icon_id).axis = 'Y'
        row.operator("mesh.ps_locvert", text='', icon_value=z_icon.icon_id).axis = 'Z'
        row.operator("mesh.ps_locvert", text='Location').axis = 'ALL'


def display_panel(self, context, layout):
    pcoll = preview_collections['main']
    draw_icon = pcoll['draw_icon']

    space_data = get_active_3d_view()

    if space_data is not None:
        overlay = space_data.overlay

        if overlay.show_retopology:
            box = layout.box()
            box.prop(overlay, 'show_retopology', icon_value=draw_icon.icon_id)
            box.prop(overlay, 'retopology_offset')

            theme = context.preferences.themes[0].view_3d
            box.prop(theme, 'face_retopology')
            box.prop(theme, 'edge_width')
            box.prop(theme, 'vertex_size')
        else:
            layout.prop(overlay, 'show_retopology', icon_value=draw_icon.icon_id)

    # unit grid UI перенесён в отдельную панель PS_PT_UnitGrid


class PS_PT_UnitGrid(Panel):
    bl_label = 'Unit Grid'
    bl_idname = 'PS_PT_UnitGrid'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'PS'

    def draw_header(self, context):
        self.layout.prop(context.scene.poly_source, "draw_grid", text="")

    def draw(self, context):
        settings = context.scene.poly_source
        if settings.draw_grid:
            layout = self.layout
            pcoll = preview_collections['main']
            box_icon = pcoll['box_icon']
            row = layout.row()
            row.prop(settings, 'box', text="Draw Box", toggle=True, icon_value=box_icon.icon_id)
            row.prop(settings, 'grid_xray', toggle=True)
            row.prop(settings, 'one2one', toggle=True)

            row = layout.row(align=True)
            row.prop(settings, 'unit_x')
            if settings.one2one is False:
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


class PS_PT_tool_kit(Panel):
    bl_idname = 'PS_PT_tool_kit'
    bl_label = 'Tool Kit'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_ui_units_x = 13


    def draw(self, context):
        settings = context.scene.poly_source
        layout = self.layout
        row = layout.row(align=False)
        right = row.column(align=False)
        right.scale_x = 1.5
        right.scale_y = 1.5
        right.prop(settings, 'panel_groops', expand=True, icon_only=True)
        col = row.column()

        if settings.panel_groops == 'TRANSFORM':
            transform_panel(self, context, col)

        elif settings.panel_groops == 'DISPLAY':
            display_panel(self, context, col)


class PS_PT_check(Panel):
    bl_idname = 'PS_PT_check'
    bl_label = 'Check Objects'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    #bl_ui_units_x = 13


    def draw(self, context):
        settings = context.scene.poly_source
        layout = self.layout

        row = layout.row()
        col = row.column()
        col.scale_y = 1.5
        col.prop(settings, "v_alone",  toggle=True)
        col.prop(settings, "v_bound", toggle=True)
        col.prop(settings, "e_pole", toggle=True)
        col.prop(settings, "n_pole", toggle=True)
        col.prop(settings, "f_pole", toggle=True)
        #col.prop(settings, "analyze_edges_curvature", toggle=True)

        col = row.column()
        col.scale_y = 1.5
        col.prop(settings, "tris", toggle=True)
        col.prop(settings, "ngone", toggle=True)
        col.prop(settings, "non_manifold_check", toggle=True)
        col.prop(settings, "elongated_tris", toggle=True)
        col.prop(settings, "custom_count", toggle=True)


        if settings.elongated_tris:
            layout.prop(settings, "elongated_aspect_ratio")

        if settings.custom_count:
            layout.prop(settings, "custom_count_verts")

        """ if settings.analyze_edges_curvature:
            layout.prop(settings, "base_edge_size")
            layout.prop(settings, "adaptive_curvature_threshold") """


        if True in [settings.v_alone, settings.v_bound, settings.e_pole, settings.n_pole, settings.f_pole, settings.tris, settings.ngone, settings.non_manifold_check, settings.custom_count]:
            box = layout.box()
            if settings.v_alone:
                box.label(text='Vertex Alone: ' + str(len(check.v_alone_co)))

            if settings.v_bound:
                box.label(text='Vertex Boundary: ' + str(len(check.v_bound_co)))

            if settings.e_pole:
                box.label(text='Vertex E-Pole: ' + str(len(check.e_pole_co)))

            if settings.n_pole:
                box.label(text='Vertex N-Pole: ' + str(len(check.n_pole_co)))

            if settings.f_pole:
                box.label(text='More 5 Pole: ' + str(len(check.f_pole_co)))

            if settings.tris:
                box.label(text='Triangles: ' + str(len(check.tris_co)//3))

            if settings.ngone:
                box.label(text='N-Gone: ' + str(len(check.ngone_idx)))

            if settings.non_manifold_check:
                box.label(text='Non Manifold: ' + str(len(check.e_non_idx)))

            if settings.elongated_tris:
                box.label(text='Elongated Tris: ' + str(len(check.elongated_tris_co)//3))

            if settings.custom_count:
                box.label(text='Custom: ' + str(len(check.custom_faces_idx)))


        layout.prop(settings, "xray_for_check")
        layout.prop(settings, "use_mod_che")


class PS_MT_modifiers(Menu):
    bl_label = 'Modifiers'
    bl_idname = 'PS_MT_modifiers'

    def draw(self, context):
        pcoll = preview_collections["main"]
        bevelSub = pcoll["bevelSub"]
        fix_icon = pcoll["fix_icon"]

        layout = self.layout
        layout.operator('object.ps_tris_weighted_normal', text='Tris & Weighted Normal', icon_value=fix_icon.icon_id)
        layout.operator('object.ps_triangulate', text='Triangulate', icon='MOD_TRIANGULATE')
        layout.operator('object.ps_add_subsurf_and_bevel', text='Crease Bevel', icon_value=bevelSub.icon_id)
        layout.operator('object.ps_solidify', text='Solidify', icon='MOD_SOLIDIFY')


class PS_MT_test(Menu):
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
    props = context.preferences.addons['Poly_Source'].preferences
    if props.b_presets_increment_angles:
        self.layout.prop(context.scene.poly_source, 'increment_angles', expand=True)


def outliner_header_button(self, context):
    layout = self.layout
    layout.operator('object.ps_random_name', text='', icon='QUESTION')


classes = [
    PS_PT_tool_kit,
    PS_PT_check,
    PS_PT_UnitGrid,
    PS_MT_modifiers,
    PS_MT_test,
    PS_MT_main,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


    bpy.types.VIEW3D_HT_tool_header.draw = tool_panel


    bpy.types.TOPBAR_HT_upper_bar.append(header_panel)
    bpy.types.VIEW3D_MT_editor_menus.append(viewHeader_L_panel)
    bpy.types.VIEW3D_HT_header.append(viewHeader_R_panel)
    #bpy.types.VIEW3D_HT_tool_header.append(tool_panel)
    bpy.types.VIEW3D_MT_mesh_add.append(custom_objects)


    bpy.types.VIEW3D_MT_editor_menus.append(rmb_menu)
    bpy.types.VIEW3D_MT_object_context_menu.prepend(rmb_menu)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.prepend(rmb_menu)

    # Add button to outliner header
    bpy.types.OUTLINER_HT_header.append(outliner_header_button)

    bpy.types.VIEW3D_PT_snapping.append(preset_increment_angle)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bpy.types.TOPBAR_HT_upper_bar.remove(header_panel)
    bpy.types.VIEW3D_MT_editor_menus.remove(viewHeader_L_panel)
    bpy.types.VIEW3D_HT_header.remove(viewHeader_R_panel)
    #bpy.types.VIEW3D_HT_tool_header.remove(tool_panel)
    bpy.types.VIEW3D_MT_mesh_add.remove(custom_objects)


    bpy.types.VIEW3D_MT_editor_menus.remove(rmb_menu)
    bpy.types.VIEW3D_MT_object_context_menu.remove(rmb_menu)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.remove(rmb_menu)

    # Remove button from outliner header
    bpy.types.OUTLINER_HT_header.remove(outliner_header_button)

    bpy.types.VIEW3D_PT_snapping.remove(preset_increment_angle)