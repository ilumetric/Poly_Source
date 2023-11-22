import bpy
import bmesh
from bpy.types import Operator, Panel, Menu
from .icons import preview_collections
from .utils.utils import get_active_3d_view
from bpy.props import EnumProperty
from . import check

    
        
        
        


def get_polygons_count_ui(context, layout):
    props = context.preferences.addons[__package__].preferences
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
            
            layout.operator('ps.ngons_select', text=str(_ngon), icon_value=ngon_icon.icon_id)    
            layout.operator('ps.quads_select', text=str(_quad), icon_value=quad_icon.icon_id)
            layout.operator('ps.tris_select', text=str(_tris), icon_value=tris_icon.icon_id)

        else:
            layout.operator('ps.ngons_select', text='', icon_value=ngon_icon.icon_id)    
            layout.operator('ps.quads_select', text='', icon_value= quad_icon.icon_id)
            layout.operator('ps.tris_select', text='', icon_value=tris_icon.icon_id)

            box = layout.box()   
            box.label(text='Vertex/Obj Excess', icon='ERROR')



""" def check_panel(self, context, layout):
    sel_obj = context.selected_objects
    scale_check = [True for s in sel_obj if s.scale[0] != 1 or s.scale[1] != 1 or s.scale[2] != 1]
    if True in scale_check:
        row = layout.row(align=True)
        row.alert = True
        row.label(text='', icon='ERROR') """


def header_panel(self, context):
    props = context.preferences.addons[__package__].preferences
    settings = context.scene.PS_scene_set
    pcoll = preview_collections['main']
    check_icon = pcoll['check_icon']

    
    if context.region.alignment == 'TOP':
        if context.object:
            if context.object.type == 'MESH':
                if props.header:
                    layout = self.layout
                    row = layout.row(align=True)
                    row.popover(panel='PS_PT_tool_kit', text='')
                    get_polygons_count_ui(context, row)
                    row.separator(factor=0.2)
                    row.prop(settings, 'PS_check', text='', icon_value=check_icon.icon_id)
                    if settings.PS_check:
                        row.popover(panel='PS_PT_check', text='')
                    #check_panel(self, context, row)


def viewHeader_L_panel(self, context):
    props = context.preferences.addons[__package__].preferences
    settings = context.scene.PS_scene_set
    pcoll = preview_collections['main']
    check_icon = pcoll['check_icon']

    if context.object:
        if context.object.type == 'MESH':
            if props.viewHeader_L:
                layout = self.layout
                row = layout.row(align=True)
                row.popover(panel='PS_PT_tool_kit', text='')
                get_polygons_count_ui(context, row)
                row.separator(factor=0.2)
                row.prop(settings, 'PS_check', text='', icon_value=check_icon.icon_id)
                if settings.PS_check:
                    row.popover(panel='PS_PT_check', text='')
                #check_panel(self, context, row)

def viewHeader_R_panel(self, context):
    props = context.preferences.addons[__package__].preferences
    settings = context.scene.PS_scene_set
    pcoll = preview_collections['main']
    check_icon = pcoll['check_icon']

    if context.object:
        if context.object.type == 'MESH':
            if props.viewHeader_R:
                layout = self.layout
                row = layout.row(align=True)
                row.popover(panel='PS_PT_tool_kit', text='')
                get_polygons_count_ui(context, row)
                row.separator(factor=0.2)
                row.prop(settings, 'PS_check', text='', icon_value=check_icon.icon_id)
                if settings.PS_check:
                    row.popover(panel='PS_PT_check', text='')
                #check_panel(self, context, row)

def tool_panel(self, context):
    props = context.preferences.addons[__package__].preferences
    settings = context.scene.PS_scene_set
    pcoll = preview_collections['main']
    check_icon = pcoll['check_icon']

    if context.object:
        if context.object.type == 'MESH':
            if props.toolHeader:
                layout = self.layout
                row = layout.row(align=True)
                row.popover(panel='PS_PT_tool_kit', text='')
                get_polygons_count_ui(context, row)
                row.separator(factor=0.2)
                row.prop(settings, 'PS_check', text='' , icon_value=check_icon.icon_id)
                if settings.PS_check:
                    row.popover(panel='PS_PT_check', text='')
                #check_panel(self, context, row)
        















# --- ADD OBJECT
# Layout
def custom_objects(self, context):
    props = context.preferences.addons[__package__].preferences

    if props.add_objects:
        pcoll = preview_collections["main"]
        cylinder_icon = pcoll["cylinder"]
        tube_icon = pcoll["tube"]
        cube_icon = pcoll["cube"]

        layout = self.layout
        layout.separator()
        layout.label(text='Poly Source')
        layout.operator("ps.create_cube", text="Cube", icon_value=cube_icon.icon_id)
        layout.operator("ps.create_cylinder", text="Cylinder", icon_value=cylinder_icon.icon_id)
        layout.operator("ps.create_tube", text="Tube", icon_value=tube_icon.icon_id)

    else:
        pass



















# --- TRANSFORM ---
def transform_panel(self, context, pie):
    pcoll = preview_collections["main"]
    x_icon = pcoll["x_icon"]
    y_icon = pcoll["y_icon"]
    z_icon = pcoll["z_icon"]
    reset_all = pcoll["reset_icon"]
    bevelSub = pcoll["bevelSub"]
    fix_icon = pcoll["fix_icon"]
    auto_s_icon = pcoll["180"]
    bevelW_icon = pcoll["bevelW"]
    creaseW_icon = pcoll["creaseW"]
    seam_icon = pcoll["seam"]
    sharp_icon = pcoll["sharp"]

    box = pie.box()

    if context.mode == 'OBJECT':
        box.label(text='Reset Transform')
        box.scale_x = 1.3

        # --- Bool Tool
        if 'object_boolean_tools' in context.preferences.addons.keys():
            row = box.row(align=True)
            row.label(icon='AUTO')
            row.operator('object.booltool_auto_difference', text='', icon='SELECT_SUBTRACT')
            row.operator('object.booltool_auto_union', text='', icon="SELECT_EXTEND")
            row.operator('object.booltool_auto_intersect', text='', icon="SELECT_INTERSECT")
            row.operator('object.booltool_auto_slice', text='', icon="SELECT_DIFFERENCE")
            row.label(icon='BRUSH_DATA')
            row.operator('btool.boolean_diff', text='', icon='SELECT_SUBTRACT')
            row.operator('btool.boolean_union', text='', icon="SELECT_EXTEND")
            row.operator('btool.boolean_inters', text='', icon="SELECT_INTERSECT")
            row.operator('btool.boolean_slice', text='', icon="SELECT_DIFFERENCE")



        row = box.row(align=True) 
        row.operator('ps.reset_location_object', text='', icon_value=x_icon.icon_id).axis = 'X'
        row.operator('ps.reset_location_object', text='', icon_value=y_icon.icon_id).axis = 'Y'
        row.operator('ps.reset_location_object', text='', icon_value=z_icon.icon_id).axis = 'Z'
        row.separator(factor=0.2)
        row.operator('ps.reset_location_object', text='Location').axis = 'ALL'
        
        row = box.row(align=True)
        row.operator('ps.reset_rotation_object', text='', icon_value=x_icon.icon_id).axis = 'X'
        row.operator('ps.reset_rotation_object', text='', icon_value=y_icon.icon_id).axis = 'Y'
        row.operator('ps.reset_rotation_object', text='', icon_value=z_icon.icon_id).axis = 'Z'
        row.separator(factor=0.2)
        row.operator('ps.reset_rotation_object', text='Rotation').axis = 'ALL'
        
        row = box.row(align=True)
        row.operator('ps.reset_scale_object', text='', icon_value=x_icon.icon_id).axis = 'X'
        row.operator('ps.reset_scale_object', text='', icon_value=y_icon.icon_id).axis = 'Y'
        row.operator('ps.reset_scale_object', text='', icon_value=z_icon.icon_id).axis = 'Z'
        row.separator(factor=0.2)
        row.operator('ps.reset_scale_object', text='Scale').axis = 'ALL'
                 
        box.operator("ps.reset_location_object", text='Reset All', icon_value=reset_all.icon_id).axis = 'ALL_T'


    elif context.mode == 'EDIT_MESH':
        box.label(text='Reset Transform')
        box.scale_x = 1.3

        row = box.row(align=True)
        row.operator("ps.locvert", text='', icon_value=x_icon.icon_id).axis = 'X'
        row.operator("ps.locvert", text='', icon_value=y_icon.icon_id).axis = 'Y'
        row.operator("ps.locvert", text='', icon_value=z_icon.icon_id).axis = 'Z'
        row.separator(factor=0.2)
        row.operator("ps.locvert", text='Location').axis = 'ALL'

    box = pie.box()
    box.label(text='Modifiers')
    row = box.row(align=True)
    row.operator('ps.submod', text='Crease Bevel', icon_value=bevelSub.icon_id)
    row.separator(factor=0.2)
    row.operator('ps.solidify', text='Solidify', icon='MOD_SOLIDIFY')
    box.operator("ps.triangulate", text='Triangulate', icon='MOD_TRIANGULATE')

    box = pie.box()
    box.label(text='Normals')
    row = box.row(align=True)
    row.operator('ps.normalfix', text='Fix', icon_value=fix_icon.icon_id)
    row.separator(factor=0.2)
    row.operator('ps.autosmooth', text='', icon_value=auto_s_icon.icon_id)
    row.prop(context.object.data, 'auto_smooth_angle', text=' ', icon='META_BALL')
    row.prop(context.object.data, 'use_auto_smooth', text='', icon='MOD_SMOOTH')

    

    box = pie.box()
    box.label(text='Edge Data')
    row = box.row(align=True)
    row.operator('ps.edge_data', text='Seam', icon_value=seam_icon.icon_id).mode = 'SEAM'
    row.separator(factor=0.2)
    row.operator('ps.edge_data', text='Sharp', icon_value=sharp_icon.icon_id).mode = 'SHARP'
    row = box.row(align=True)
    row.operator('ps.edge_data', text='Bevel', icon_value=bevelW_icon.icon_id).mode = 'BEVEL'
    row.separator(factor=0.2)
    row.operator('ps.edge_data', text='Crease', icon_value=creaseW_icon.icon_id).mode = 'CREASE'


def display_panel(self, context, layout):
    pcoll = preview_collections[ 'main' ]
    calculate_icon = pcoll[ 'calculate_icon' ]
    check_icon = pcoll[ 'check_icon' ]
    box_icon = pcoll[ 'box_icon' ]
    grid_icon = pcoll[ 'grid_icon' ]
    draw_icon = pcoll[ 'draw_icon' ]


    props = context.preferences.addons[__package__].preferences
    settings = context.scene.PS_scene_set

    
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

    



    # --- Mesh Check
    """ if settings.PS_check: 
        box = layout.box()
        box.prop(settings, 'PS_check', icon_value=check_icon.icon_id)

        row = box.row()
        col = row.column()
        col.scale_y = 1.5
        col.prop(props, "v_alone", toggle=True)
        col.prop(props, "v_bound", toggle=True)
        col.prop(props, "e_pole", toggle=True)
        col.prop(props, "n_pole", toggle=True)
        col.prop(props, "f_pole", toggle=True)

        col = row.column()
        col.scale_y = 1.5
        col.prop(props, "tris", toggle=True)
        col.prop(props, "ngone", toggle=True)
        col.prop(props, "non_manifold_check", toggle=True)
        

        rowC = box.row(align=True)
        rowC.prop(props, "custom_count")
        sub_rowC = rowC.row()
        sub_rowC.scale_x = 1.5
        sub_rowC.active = props.custom_count
        sub_rowC.prop(props, "custom_count_verts")

        row_P = box.row()
        row_P.scale_x = 1.0
        row_P.prop(props, "xray_for_check")
        row_P.scale_x = 1.1
        row_P.prop(props, "use_mod_che")
            
    else:
        layout.prop(settings, 'PS_check', icon_value=check_icon.icon_id) """
        
        

        



    """ # --- Polycount
    if settings.PS_polycount:
        box = layout.box()
        box.prop(settings, "PS_polycount", icon_value=calculate_icon.icon_id)
        
        row = box.row(align=True)
        row.prop(settings, "tris_count")
        row.scale_x = 0.4
        row.prop(props, "low_suffix", toggle=True)
    else:
        layout.prop(settings, "PS_polycount", icon_value=calculate_icon.icon_id) """
    
        




    # --- Envira Grid
    if settings.PS_envira_grid:
        box = layout.box()
        row = box.row()
        row.prop(settings, 'PS_envira_grid', icon_value=grid_icon.icon_id)
        row.prop(settings, 'box', icon_value=box_icon.icon_id)
    
        row = box.row()
        row.prop(settings, 'one_unit', expand=True)
        row.prop(settings, 'one2one', toggle=True)
        
        row_all = box.row()
        if settings.one2one:
            row_all.prop(settings, 'unit_x')

        else:
            row = row_all.row(align=True)
            row.prop(settings, 'unit_x')
            row.prop(settings, 'unit_y')

        box.prop(settings, 'float_z')
        box.prop(settings, 'padding')

        if settings.box:
            box.prop(settings, 'box_height')

        box.prop(settings, 'draw_unit_grid')
        if settings.draw_unit_grid:
            box.prop(settings, 'one_unit_length')
    
    else:
        layout.prop(settings, 'PS_envira_grid', icon_value=grid_icon.icon_id)

        



    # --- Operators
    box = layout.box()
    box.prop(props, 'maxVerts')
    box.prop(props, 'maxObjs')


def shade_panel(self, context, layout): # --- SHADE Panel
    pcoll = preview_collections["main"]
    fix_icon = pcoll["fix_icon"]
    auto_s_icon = pcoll["180"]


    row = layout.row()
    if context.mode == 'OBJECT':
        row.operator('object.shade_smooth', text='Smooth', icon = 'ANTIALIASED')
        row.operator('object.shade_flat', text='Flat', icon = 'ALIASED')

    elif context.mode == 'EDIT_MESH':
        row.operator('mesh.faces_shade_smooth', text='Smooth', icon = 'ANTIALIASED')
        row.operator('mesh.faces_shade_flat', text='Flat', icon = 'ALIASED')
        

    row = layout.row(align=True)
    row.operator('ps.autosmooth', text='', icon_value=auto_s_icon.icon_id)
    row.prop(context.object.data, 'auto_smooth_angle', text=' ', icon='META_BALL')
    row.prop(context.object.data, 'use_auto_smooth', text='', icon='MOD_SMOOTH')
    #sub = row.row()
    
    layout.operator('ps.normalfix', text='Fix', icon_value=fix_icon.icon_id)


def operators_panel(self, context, layout): # --- OPERATORS Panel
    if context.mode == 'EDIT_MESH':
        layout.operator('mesh.edges_select_sharp', icon = 'LINCURVE')
        layout.operator('mesh.select_nth', icon = 'TEXTURE_DATA')

    layout.operator("ps.clear_dots", icon='SHADERFX')
    layout.operator("ps.remove_vertex_non_manifold", icon='SHADERFX')
    layout.operator("ps.cylinder_optimizer", icon='MESH_CYLINDER').rounding = False
    layout.operator("ps.cylinder_optimizer", text='Rounding Up', icon='MESH_CYLINDER').rounding = True
    
    layout.operator("ps.del_long_faces")
    layout.operator('ps.clear_materials')
    layout.operator('ps.clear_data')
    layout.operator("outliner.orphans_purge", text="Purge")
    layout.separator()
    layout.operator('ps.transfer_transform') # TODO перенести в другое место
    
    #layout.operator('ps.add_material')
    layout.operator('ps.fill_from_points')





class PS_PT_tool_kit(Panel):
    bl_idname = 'PS_PT_tool_kit'
    bl_label = 'Tool Kit'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_ui_units_x = 13

    
    def draw(self, context):
        settings = context.scene.PS_scene_set
        layout = self.layout
        row = layout.row(align=False)
        right = row.column(align=False)
        right.scale_x = 1.5
        right.scale_y = 1.5
        right.prop(settings, 'panel_groops', expand=True, icon_only=True)
        col = row.column()

        if settings.panel_groops == 'TRANSFORM':
            transform_panel(self, context, col)

        elif settings.panel_groops == 'OPS':
            operators_panel(self, context, col)

        elif settings.panel_groops == 'DISPLAY':
            display_panel(self, context, col)






class PS_PT_check(Panel):
    bl_idname = 'PS_PT_check'
    bl_label = 'Check Objects'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    #bl_ui_units_x = 13

    
    def draw(self, context):
        settings = context.scene.PS_scene_set
        layout = self.layout
        
        row = layout.row()
        col = row.column()
        col.scale_y = 1.5
        col.prop(settings, "v_alone",  toggle=True)
        col.prop(settings, "v_bound", toggle=True)
        col.prop(settings, "e_pole", toggle=True)
        col.prop(settings, "n_pole", toggle=True)
        col.prop(settings, "f_pole", toggle=True)

        col = row.column()
        col.scale_y = 1.5
        col.prop(settings, "tris", toggle=True)
        col.prop(settings, "ngone", toggle=True)
        col.prop(settings, "non_manifold_check", toggle=True)
        col.prop(settings, "custom_count", toggle=True)


        if settings.custom_count:
            layout.prop(settings, "custom_count_verts")


        

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
            
            if settings.custom_count:
                box.label(text='Custom: ' + str(len(check.custom_faces_idx)))


        layout.prop(settings, "xray_for_check")
        layout.prop(settings, "use_mod_che")














classes = [
    PS_PT_tool_kit,
    PS_PT_check,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_HT_upper_bar.append(header_panel)
    bpy.types.VIEW3D_MT_editor_menus.append(viewHeader_L_panel)
    bpy.types.VIEW3D_HT_header.append(viewHeader_R_panel)
    bpy.types.VIEW3D_HT_tool_header.append(tool_panel)
    bpy.types.VIEW3D_MT_mesh_add.append(custom_objects)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.TOPBAR_HT_upper_bar.remove(header_panel)
    bpy.types.VIEW3D_MT_editor_menus.remove(viewHeader_L_panel)
    bpy.types.VIEW3D_HT_header.remove(viewHeader_R_panel)
    bpy.types.VIEW3D_HT_tool_header.remove(tool_panel)
    bpy.types.VIEW3D_MT_mesh_add.append(custom_objects)