import bpy
from bpy.types import Panel, Menu
from ..icons import preview_collections
from ..ui import draw_panel


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
        #draw_panel(self, context, row.row(align=True), scale_x=1.0, scale_y=1.0)

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


# --- SHADE Panel
class PS_PT_shade(Panel):
    bl_idname = 'PS_PT_shade'
    bl_label = 'Shade'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'

    @classmethod
    def poll(cls, context):
        return context.object.type == 'MESH'

    def draw(self, context):
        pcoll = preview_collections["main"]
        fix_icon = pcoll["fix_icon"]
        auto_s_icon = pcoll["180"]

        layout = self.layout

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


# --- MODIFIERS Panel
class PS_PT_modifiers(Panel):
    bl_idname = 'PS_PT_modifiers'
    bl_label = 'Modifiers'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'

    @classmethod
    def poll(cls, context):
        return context.object.type == 'MESH'

    def draw(self, context):
        pcoll = preview_collections["main"]
        x_icon = pcoll["x_icon"]
        y_icon = pcoll["y_icon"]
        z_icon = pcoll["z_icon"]
        bevelSub = pcoll["bevelSub"]

        layout = self.layout

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


# --- OPERATORS Panel
class PS_PT_operators(Panel):
    bl_idname = 'PS_PT_operators'
    bl_label = 'Operators'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'

    @classmethod
    def poll(cls, context):
        return context.object.type == 'MESH'

    def draw(self, context):
        layout = self.layout

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


# ---- PIE ----
class PS_MT_tk_menu(Menu):
    bl_idname = 'PS_MT_tk_menu'
    bl_label = 'Tool Kit'

    def draw(self, context):
        pcoll = preview_collections["main"]
        ngon_icon = pcoll["ngon_icon"]
        quad_icon = pcoll["quad_icon"]
        tris_icon = pcoll["tris_icon"] 
        bevelW_icon = pcoll["bevelW"]
        creaseW_icon = pcoll["creaseW"]

        sca_y = 1.3
        layout = self.layout
        pie = layout.menu_pie()

        pie.operator("view3d.copybuffer", text = '1', icon = 'BLENDER')                              # 1
        pie.operator("view3d.copybuffer", text = '2', icon = 'BLENDER')                              # 2
        pie.operator("view3d.copybuffer", text = '3', icon = 'BLENDER')                              # 3
        pie.operator("view3d.copybuffer", text = '4', icon = 'BLENDER')                              # 4

        if context.mode == 'EDIT_MESH':
            pie.operator('ps.edge_data', text='Seam', icon_value=creaseW_icon.icon_id).mode = 'SEAM'     # 5
            pie.operator('ps.edge_data', text='Sharp', icon_value=bevelW_icon.icon_id).mode = 'SHARP'    # 6
            pie.operator('ps.edge_data', text='Bevel', icon_value=bevelW_icon.icon_id).mode = 'BEVEL'    # 7
            pie.operator('ps.edge_data', text='Crease', icon_value=creaseW_icon.icon_id).mode = 'CREASE' # 8

        elif context.mode == 'OBJECT':
            pie.operator("view3d.copybuffer", text = '5', icon = 'BLENDER')
            pie.operator("view3d.copybuffer", text = '6', icon = 'BLENDER')                            
            pie.operator("view3d.copybuffer", text = '7', icon = 'BLENDER')                            
            pie.operator("view3d.copybuffer", text = '8', icon = 'BLENDER')

        else:
            pie.operator("view3d.copybuffer", text = '5', icon = 'BLENDER')
            pie.operator("view3d.copybuffer", text = '6', icon = 'BLENDER')                            
            pie.operator("view3d.copybuffer", text = '7', icon = 'BLENDER')                            
            pie.operator("view3d.copybuffer", text = '8', icon = 'BLENDER')




        # --- Bottom Menu
        pie.separator()
        pie.separator()
        other = pie.column()
        gap = other.column()
        gap.separator()
        gap.scale_y = 7
        other_menu = other.box().column()
        other_menu.scale_y=sca_y
        other_menu.scale_x = 1.2
        """ if context.mode == 'OBJECT':
            other_menu.operator('object.shade_smooth', icon = 'ANTIALIASED')
            other_menu.operator('object.shade_flat', icon = 'ALIASED')  """
        
        other_menu.popover('PS_PT_modifiers', text='Modifiers', icon='MODIFIER')
        other_menu.popover('PS_PT_shade', text='Shade', icon='SHADING_RENDERED')
        other_menu.popover('PS_PT_operators')
        other_menu.popover('OBJECT_PT_display')
        other_menu.popover('PS_PT_settings_draw_mesh', icon_value=ngon_icon.icon_id)
        other_menu.popover('SCENE_PT_unit')


        # --- Top Menu
        other = pie.column()
        other_menu = other.box().column()
        other_menu.scale_y=sca_y
        transform_panel(self, context, other_menu)
        gap = other.column()
        gap.separator()
        gap.scale_y = 7



classes = [
    PS_PT_shade,
    PS_PT_modifiers,
    PS_PT_operators,
    PS_MT_tk_menu,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)