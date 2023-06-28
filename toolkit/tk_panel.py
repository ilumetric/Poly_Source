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
    bevelSub = pcoll["bevelSub"]
    fix_icon = pcoll["fix_icon"]
    auto_s_icon = pcoll["180"]


    #col = pie.column(align=False)
    box = pie.box()

    if context.mode == 'OBJECT':
        #row = col.row(align=True)
        box.label(text='Reset Transform')

        box.scale_x = 1.3


        # --- Bool Tool
        addons = context.preferences.addons.keys()[:]
        if 'object_boolean_tools' in addons:
            row = box.row(align=True)
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



        row = box.row(align=True) 
        row.operator('ps.reset_location_object', text='', icon_value=x_icon.icon_id).axis = 'X'
        row.operator('ps.reset_location_object', text='', icon_value=y_icon.icon_id).axis = 'Y'
        row.operator('ps.reset_location_object', text='', icon_value=z_icon.icon_id).axis = 'Z'
        sub = row.row()
        sub.operator('ps.reset_location_object', text='Location').axis = 'ALL'
        
        row = box.row(align=True)
        row.operator('ps.reset_rotation_object', text='', icon_value=x_icon.icon_id).axis = 'X'
        row.operator('ps.reset_rotation_object', text='', icon_value=y_icon.icon_id).axis = 'Y'
        row.operator('ps.reset_rotation_object', text='', icon_value=z_icon.icon_id).axis = 'Z'
        sub = row.row()
        sub.operator('ps.reset_rotation_object', text='Rotation').axis = 'ALL'
        
        row = box.row(align=True)
        row.operator('ps.reset_scale_object', text='', icon_value=x_icon.icon_id).axis = 'X'
        row.operator('ps.reset_scale_object', text='', icon_value=y_icon.icon_id).axis = 'Y'
        row.operator('ps.reset_scale_object', text='', icon_value=z_icon.icon_id).axis = 'Z'
        sub = row.row()
        sub.operator('ps.reset_scale_object', text='Scale').axis = 'ALL'
        
        row = box.row(align=True)           
        row.operator("ps.reset_location_object", text='Reset All', icon_value=reset_all.icon_id).axis = 'ALL_T'


    elif context.mode == 'EDIT_MESH':
        box.label(text='Reset Transform')
        box.scale_x = 1.3

        row = box.row(align=True)
        row.operator("ps.locvert", text='', icon_value=x_icon.icon_id).axis = 'X'
        row.operator("ps.locvert", text='', icon_value=y_icon.icon_id).axis = 'Y'
        row.operator("ps.locvert", text='', icon_value=z_icon.icon_id).axis = 'Z'
        sub = row.row()
        sub.operator("ps.locvert", text='Location').axis = 'ALL'


    pie.separator()

    box = pie.box()
    # --- Mirror
    row = box.row(align=True)
    row.scale_x = 20
    row.operator('ps.add_mirror_mod', text="", icon_value=x_icon.icon_id).axis = 'X'
    row.separator(factor=0.15)
    row.operator('ps.add_mirror_mod', text="", icon_value=y_icon.icon_id).axis = 'Y'
    row.separator(factor=0.15)
    row.operator('ps.add_mirror_mod', text="", icon_value=z_icon.icon_id).axis = 'Z'

    

    # --- Subdivision
    box.operator('ps.submod', text='Bevel For Crease', icon_value=bevelSub.icon_id)

    # --- Solidify
    box.operator('ps.solidify', text='Solidify', icon='MOD_SOLIDIFY')

    # --- Triangulate
    box.operator("ps.triangulate", text='', icon='MOD_TRIANGULATE')

    
    pie.separator()
    # --- SHADE
    box = pie.box()
    #row = box.row()
    """ if context.mode == 'OBJECT':
        row.operator('object.shade_smooth', text='Smooth', icon = 'ANTIALIASED')
        row.operator('object.shade_flat', text='Flat', icon = 'ALIASED')

    elif context.mode == 'EDIT_MESH':
        row.operator('mesh.faces_shade_smooth', text='Smooth', icon = 'ANTIALIASED')
        row.operator('mesh.faces_shade_flat', text='Flat', icon = 'ALIASED') """
        
    box.operator('ps.normalfix', text='Fix', icon_value=fix_icon.icon_id)

    row = box.row(align=True)
    row.operator('ps.autosmooth', text='', icon_value=auto_s_icon.icon_id)
    row.prop(context.object.data, 'auto_smooth_angle', text=' ', icon='META_BALL')
    row.prop(context.object.data, 'use_auto_smooth', text='', icon='MOD_SMOOTH')
    #sub = row.row()
    
    


""" # --- MODIFIERS Panel
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
    row.operator('ps.add_mirror_mod', text=" ", icon_value=z_icon.icon_id).axis = 'Z' """



def set_data_panel(self, context, layout): # --- Set Data
    pcoll = preview_collections["main"] 
    bevelW_icon = pcoll["bevelW"]
    creaseW_icon = pcoll["creaseW"]

    layout.operator('ps.edge_data', text='Seam', icon_value=creaseW_icon.icon_id).mode = 'SEAM'
    layout.operator('ps.edge_data', text='Sharp', icon_value=bevelW_icon.icon_id).mode = 'SHARP'
    layout.operator('ps.edge_data', text='Bevel', icon_value=bevelW_icon.icon_id).mode = 'BEVEL'
    layout.operator('ps.edge_data', text='Crease', icon_value=creaseW_icon.icon_id).mode = 'CREASE'



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
                            #('MODIFIER', 'Blender', '', 'MODIFIER', 1),
                            #('SHADE', 'Shade', '', 'SHADING_RENDERED', 1),
                            ('OP', 'operators', '', 'NODETREE', 1),
                            ('DATA', 'Set Data', '', 'OUTLINER_DATA_MESH', 2),
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
        layout = self.layout
        row = layout.row(align=False)
        right = row.column(align=False)
        right.scale_x = 1.5
        right.scale_y = 1.5
        right.prop(self, 'groops', expand=True, icon_only=True)
        col = row.column()

        if self.groops == 'TRANSFORM':
            transform_panel(self, context, col)

            """ elif self.groops == 'MODIFIER':
                modifier_panel(self, context, col) """

            """     elif self.groops == 'SHADE':
                shade_panel(self, context, col) """

        elif self.groops == 'OP':
            operators_panel(self, context, col)
        
        elif self.groops == 'DATA':
            set_data_panel(self, context, col)
   

        """left.popover('PS_PT_settings_draw_mesh', icon_value=ngon_icon.icon_id)       # 6
        left.popover('OBJECT_PT_display', icon='RESTRICT_VIEW_ON')                   # 7
        left.popover('SCENE_PT_unit', icon='SNAP_INCREMENT')                         # 8 """



# --- Panels For Gizmo PRO
class PS_PT_tool_kit_transform_panel(Panel):
    bl_idname = 'PS_PT_tool_kit_transform_panel'
    bl_label = 'Tool Kit: Transform'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_ui_units_x = 12


    def draw(self, context):
        layout = self.layout
        transform_panel(self, context, layout)



class PS_PT_tool_kit_operators_panel(Panel):
    bl_idname = 'PS_PT_tool_kit_operators_panel'
    bl_label = 'Tool Kit: Operators'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_ui_units_x = 12


    def draw(self, context):
        layout = self.layout
        operators_panel(self, context, layout)



class PS_PT_tool_kit_data_panel(Panel):
    bl_idname = 'PS_PT_tool_kit_data_panel'
    bl_label = 'Tool Kit: Data'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_ui_units_x = 12


    def draw(self, context):
        layout = self.layout
        set_data_panel(self, context, layout)



classes = [
    PS_OT_tool_kit_panel,
    PS_PT_tool_kit_transform_panel,
    PS_PT_tool_kit_operators_panel,
    PS_PT_tool_kit_data_panel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)