import bpy
from bpy.types import Panel, Menu, Operator
from ..icons import preview_collections
from bpy.props import EnumProperty



# --- TRANSFORM ---
def transform_panel(self, context, pie):
    pcoll = preview_collections["main"]
    x_icon = pcoll["x_icon"]
    y_icon = pcoll["y_icon"]
    z_icon = pcoll["z_icon"]
    reset_all = pcoll["reset_icon"]

    col = pie.column(align=False)
    
    if context.mode == 'OBJECT':
        #row = col.row(align=True)
        col.label(text='Reset Transform')

        col.scale_x = 1.3


        # --- Bool Tool
        addons = context.preferences.addons.keys()[:]
        if 'object_boolean_tools' in addons:
            row = col.row(align=True)
            row.label(icon='AUTO')
            row.operator('object.booltool_auto_difference', text='', icon='SELECT_SUBTRACT')
            row.operator('object.booltool_auto_union', text='', icon="SELECT_EXTEND")
            row.operator('object.booltool_auto_intersect', text='', icon="SELECT_INTERSECT")
            row.operator('object.booltool_auto_slice', text='', icon="SELECT_DIFFERENCE")
            
            sub = row.row(align=True)
            sub.label(icon='BRUSH_DATA')
            sub.operator('btool.boolean_diff', text='', icon='SELECT_SUBTRACT')
            sub.operator('btool.boolean_union', text='', icon="SELECT_EXTEND")
            sub.operator('btool.boolean_inters', text='', icon="SELECT_INTERSECT")
            sub.operator('btool.boolean_slice', text='', icon="SELECT_DIFFERENCE")



        row = col.row(align=True) 
        row.operator('ps.reset_location_object', text='', icon_value=x_icon.icon_id).axis = 'X'
        row.operator('ps.reset_location_object', text='', icon_value=y_icon.icon_id).axis = 'Y'
        row.operator('ps.reset_location_object', text='', icon_value=z_icon.icon_id).axis = 'Z'
        sub = row.row()
        sub.operator('ps.reset_location_object', text='Location').axis = 'ALL'
        
        row = col.row(align=True)
        row.operator('ps.reset_rotation_object', text='', icon_value=x_icon.icon_id).axis = 'X'
        row.operator('ps.reset_rotation_object', text='', icon_value=y_icon.icon_id).axis = 'Y'
        row.operator('ps.reset_rotation_object', text='', icon_value=z_icon.icon_id).axis = 'Z'
        sub = row.row()
        sub.operator('ps.reset_rotation_object', text='Rotation').axis = 'ALL'
        
        row = col.row(align=True)
        row.operator('ps.reset_scale_object', text='', icon_value=x_icon.icon_id).axis = 'X'
        row.operator('ps.reset_scale_object', text='', icon_value=y_icon.icon_id).axis = 'Y'
        row.operator('ps.reset_scale_object', text='', icon_value=z_icon.icon_id).axis = 'Z'
        sub = row.row()
        sub.operator('ps.reset_scale_object', text='Scale').axis = 'ALL'
        
        row = col.row(align=True)           
        row.operator("ps.reset_location_object", text='Reset All', icon_value=reset_all.icon_id).axis = 'ALL_T'


    elif context.mode == 'EDIT_MESH':
        col.label(text='Reset Transform')
        col.scale_x = 1.3

        row = col.row(align=True)
        row.operator("ps.locvert", text='', icon_value=x_icon.icon_id).axis = 'X'
        row.operator("ps.locvert", text='', icon_value=y_icon.icon_id).axis = 'Y'
        row.operator("ps.locvert", text='', icon_value=z_icon.icon_id).axis = 'Z'
        sub = row.row()
        sub.operator("ps.locvert", text='Location').axis = 'ALL'


# --- MODIFIERS Panel
def modifier_panel(self, context, layout):
    pcoll = preview_collections["main"]
    x_icon = pcoll["x_icon"]
    y_icon = pcoll["y_icon"]
    z_icon = pcoll["z_icon"]
    bevelSub = pcoll["bevelSub"]

    #layout.alignment = 'LEFT'

    # --- Triangulate
    layout.operator("ps.triangulate", text='', icon='MOD_TRIANGULATE')

    # --- Subdivision
    layout.operator('ps.submod', text='Bevel For Crease', icon_value=bevelSub.icon_id)

    # --- Solidify
    layout.operator('ps.solidify', text='Solidify', icon='MOD_SOLIDIFY')
    
    # --- Mirror
    row = layout.row(align=True)     
    #row.scale_x = 2
    row.operator('ps.add_mirror_mod', text=" ", icon_value=x_icon.icon_id).axis = 'X'    
    row.operator('ps.add_mirror_mod', text=" ", icon_value=y_icon.icon_id).axis = 'Y' 
    row.operator('ps.add_mirror_mod', text=" ", icon_value=z_icon.icon_id).axis = 'Z'


# --- Set Data
def set_data_panel(self, context, layout):
    pcoll = preview_collections["main"] 
    bevelW_icon = pcoll["bevelW"]
    creaseW_icon = pcoll["creaseW"]

    layout.operator('ps.edge_data', text='Seam', icon_value=creaseW_icon.icon_id).mode = 'SEAM'
    layout.operator('ps.edge_data', text='Sharp', icon_value=bevelW_icon.icon_id).mode = 'SHARP'
    layout.operator('ps.edge_data', text='Bevel', icon_value=bevelW_icon.icon_id).mode = 'BEVEL'
    layout.operator('ps.edge_data', text='Crease', icon_value=creaseW_icon.icon_id).mode = 'CREASE'


# --- SHADE Panel
def shade_panel(self, context, layout):
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


# --- OPERATORS Panel
def operators_panel(self, context, layout):
    if context.mode == 'EDIT_MESH':
        layout.operator('mesh.edges_select_sharp', icon = 'LINCURVE')
        layout.operator('mesh.select_nth', icon = 'TEXTURE_DATA')

    layout.operator("ps.clear_dots", icon='SHADERFX')
    layout.operator("ps.remove_vertex_non_manifold", icon='SHADERFX')
    layout.operator("ps.cylinder_optimizer", icon='MESH_CYLINDER').rounding = False
    layout.operator("ps.cylinder_optimizer", text='Rounding Up', icon='MESH_CYLINDER').rounding = True
    #box.operator("ps.fill_mesh", icon='MOD_LATTICE') # TODO 
    layout.operator("ps.del_long_faces")

    layout.separator()
    layout.operator('ps.transfer_transform') # TODO перенести в другое место
    
    #layout.operator('ps.add_material')
    #layout.operator('ps.delaunay_triangulation')








class PS_OT_tool_kit_panel(Operator):
    bl_idname = 'ps.tool_kit_panel'
    bl_label = 'Tool Kit'
    #bl_description = ' '
    #bl_options = {'REGISTER'}
    

    groops: EnumProperty(
                        name='Groops', 
                        description = '',
                        items = [
                            ('TRANSFORM', 'Transform', '', 'EMPTY_ARROWS', 0), 
                            ('MODIFIER', 'Blender', '', 'MODIFIER', 1),
                            ('SHADE', 'Shade', '', 'SHADING_RENDERED', 2),
                            ('OP', 'operators', '', 'NODETREE', 3),
                            ('DATA', 'Set Data', '', 'OUTLINER_DATA_MESH', 4),
                            ],
                        default = 'TRANSFORM',
                        )


    def execute(self, context):
        return {'FINISHED'}


    def invoke(self, context, event):
        """ print('region', context.region.width, context.region.x)
        print('area', context.area.width, context.area.x)
        x = event.mouse_region_x + 20
        y = event.mouse_region_y - 20
        context.window.cursor_warp(x, y) """
        #return wm.invoke_props_popup(self, event)
        #return wm.invoke_props_dialog(self, width=100) # --- с конпкой ОК
        #return wm.invoke_confirm(self, event) # --- как при сохранении настроек
        #return context.window_manager.invoke_search_popup(self)
        wm = context.window_manager
        return  wm.invoke_popup(self, width=300) # wm.invoke_props_popup(self, event) #


    def draw(self, context):
        pcoll = preview_collections['main']
        ngon_icon = pcoll['ngon_icon']
        bevelW_icon = pcoll['bevelW']

        layout = self.layout

        row = layout.row(align=False)

        right = row.column(align=False)
        right.scale_x = 1.5
        right.scale_y = 1.5
        right.prop(self, 'groops', expand=True, icon_only=True)



        left = row.box()
        #layout.emboss = 'PULLDOWN_MENU'

        if self.groops == 'TRANSFORM':
            transform_panel(self, context, left)

        elif self.groops == 'MODIFIER':
            modifier_panel(self, context, left)

        elif self.groops == 'SHADE':
            shade_panel(self, context, left)

        elif self.groops == 'OP':
            operators_panel(self, context, left)
        
        elif self.groops == 'DATA':
            set_data_panel(self, context, left)
   

        """left.popover('PS_PT_settings_draw_mesh', icon_value=ngon_icon.icon_id)       # 6
        left.popover('OBJECT_PT_display', icon='RESTRICT_VIEW_ON')                   # 7
        left.popover('SCENE_PT_unit', icon='SNAP_INCREMENT')                         # 8 """



classes = [
    PS_OT_tool_kit_panel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)