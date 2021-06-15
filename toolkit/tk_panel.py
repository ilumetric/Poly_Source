import bpy
from bpy.types import Operator, Panel, Menu
from ..icons import preview_collections



# bl_parent_id = "PT_PT_transform_panel"
# bl_category = 'Pivot Transform'


class PS_PT_uv_maps_panel(Panel):
    bl_label = "UV Channel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_idname = 'PS_PT_uv_maps_panel'


    def draw(self, context):
        layout = self.layout
        me = context.object.data
        row = layout.row()
        col = row.column()
        col.template_list("MESH_UL_uvmaps", "uvmaps", me, "uv_layers", me.uv_layers, "active_index", rows=2)
        col = row.column(align=True)
        col.operator("mesh.uv_texture_add", icon='ADD', text="")
        col.operator("mesh.uv_texture_remove", icon='REMOVE', text="") 



# --- General Panel
def fast_tool_kit(self, context, layout):
    pcoll = preview_collections["main"]
    x_icon = pcoll["x_icon"]
    y_icon = pcoll["y_icon"]
    z_icon = pcoll["z_icon"]
    reset_all = pcoll["reset_icon"]
    fix_icon = pcoll["fix_icon"]
    bevelSub = pcoll["bevelSub"]
    tool_icon = pcoll["tool"]
    auto_s_icon = pcoll["180"]
    bevelW_icon = pcoll["bevelW"]
    creaseW_icon = pcoll["creaseW"]


    box_all = layout.box()

    box_all.label(text='Tool Kit')

    
    # --- Transform
    box = box_all.box()
    col = box.column(align=True)
    
    if context.mode == 'OBJECT':
        row = col.row(align=True) 
        row.scale_x = 2
        row.operator("ps.reset_location_object", text='', icon_value=x_icon.icon_id).axis = 'X'
        row.operator("ps.reset_location_object", text='', icon_value=y_icon.icon_id).axis = 'Y'
        row.operator("ps.reset_location_object", text='', icon_value=z_icon.icon_id).axis = 'Z'
        row.operator("object.location_clear", text='Location').clear_delta=False
        
        row = col.row(align=True)
        row.scale_x = 2
        row.operator("ps.reset_rotation_object", text='', icon_value=x_icon.icon_id).axis = 'X'
        row.operator("ps.reset_rotation_object", text='', icon_value=y_icon.icon_id).axis = 'Y'
        row.operator("ps.reset_rotation_object", text='', icon_value=z_icon.icon_id).axis = 'Z'
        row.operator("object.rotation_clear", text='Rotation').clear_delta=False
        
        row = col.row(align=True)
        row.scale_x = 2
        row.operator("ps.reset_scale_object", text='', icon_value=x_icon.icon_id).axis = 'X'
        row.operator("ps.reset_scale_object", text='', icon_value=y_icon.icon_id).axis = 'Y'
        row.operator("ps.reset_scale_object", text='', icon_value=z_icon.icon_id).axis = 'Z'
        row.operator("object.scale_clear", text='Scale').clear_delta=False
        
        row = col.row(align=True)           
        row.operator("ps.reset_location_object", text='Reset All', icon_value=reset_all.icon_id).axis = 'ALL'

        
        


    elif context.mode == 'EDIT_MESH':
        row = col.row(align=True) 
        row.scale_x = 2
        row.operator("ps.locvert", text='', icon_value=x_icon.icon_id).axis = 'X'
        row.operator("ps.locvert", text='', icon_value=y_icon.icon_id).axis = 'Y'
        row.operator("ps.locvert", text='', icon_value=z_icon.icon_id).axis = 'Z'
        row.operator("ps.locvert", text='Location').axis = 'ALL'
    





    
    

    
    # --- Smooth
    if context.active_object.type == 'MESH':
        box = box_all.box()
        row = box.row(align=True)   
        row.operator("ps.autosmooth",text='', icon_value=auto_s_icon.icon_id)
        row.prop(context.object.data, 'auto_smooth_angle',text=' ', icon='META_BALL')
        row.prop(context.object.data, 'use_auto_smooth', text='', icon='MOD_SMOOTH')
        sub = row.row()
        #sub.scale_x = 1.0
        sub.operator("ps.normalfix", text='Fix', icon_value=fix_icon.icon_id)
   

    
    
    

    #Modifier
    
    box = box_all.box()
    row = box.row()        
    row.label(text="Modifiers", icon_value=tool_icon.icon_id)    
    

    



    # --- Triangulate
    if context.active_object.type == 'MESH':
        box.operator("ps.triangulate", text='', icon='MOD_TRIANGULATE')





    # --- Subdivision
    box.operator('ps.submod', text='Bevel For Crease', icon_value=bevelSub.icon_id)


    # --- Solidify
    box.operator('ps.solidify', text='Solidify', icon='MOD_SOLIDIFY')
    

    # --- Mirror
    row = box.row(align=True)     
    row.scale_x = 3
    row.operator('ps.add_mirror_mod', text="", icon_value=x_icon.icon_id).axis = 'X'    
    row.operator('ps.add_mirror_mod', text="", icon_value=y_icon.icon_id).axis = 'Y' 
    row.operator('ps.add_mirror_mod', text="", icon_value=z_icon.icon_id).axis = 'Z' 

    


    if context.mode == 'EDIT_MESH':
        box = box_all.box()
        row = box.row(align=True)
        row.label(text="Weight")
        row.scale_x = 2.0
        row.operator("ps.edge_data", text='Bevel', icon_value=bevelW_icon.icon_id).mode = 'BEVEL'
        row.operator("ps.edge_data", text='Crease', icon_value=creaseW_icon.icon_id).mode = 'CREASE'

        row = box.row(align=True)
        row.scale_x = 1.15
        row.operator('mesh.edges_select_sharp', icon='LINCURVE')
        row.operator('mesh.select_nth', icon='TEXTURE_DATA')



    box = box_all.box()
    row = box.row(align=True)
    row.operator("ps.clear_dots", icon='SHADERFX')
    row.operator("ps.remove_vertex_non_manifold", icon='SHADERFX')
    box.operator("ps.cylinder_optimizer", icon='MESH_CYLINDER').rounding = False
    box.operator("ps.cylinder_optimizer", text='Rounding Up', icon='MESH_CYLINDER').rounding = True





# --- Object Property Panel
def object_display(self, context, layout):
    box = layout.box()

    box.label(text='Viewport Display')

    box.use_property_split = True

    obj = context.object
    obj_type = obj.type
    is_geometry = (obj_type in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'VOLUME', 'HAIR', 'POINTCLOUD'})
    is_wire = (obj_type in {'CAMERA', 'EMPTY'})
    is_empty_image = (obj_type == 'EMPTY' and obj.empty_display_type == 'IMAGE')
    is_dupli = (obj.instance_type != 'NONE')
    is_gpencil = (obj_type == 'GPENCIL')

    col = box.column(heading="Show")
    col.prop(obj, "show_name", text="Name")
    col.prop(obj, "show_axis", text="Axis")

    # Makes no sense for cameras, armatures, etc.!
    # but these settings do apply to dupli instances
    if is_geometry or is_dupli:
        col.prop(obj, "show_wire", text="Wireframe")
    if obj_type == 'MESH' or is_dupli:
        col.prop(obj, "show_all_edges", text="All Edges")
    if is_geometry:
        col.prop(obj, "show_texture_space", text="Texture Space")
        col.prop(obj.display, "show_shadows", text="Shadow")
    col.prop(obj, "show_in_front", text="In Front")
    # if obj_type == 'MESH' or is_empty_image:
    #    col.prop(obj, "show_transparent", text="Transparency")
    sub = box.column()
    if is_wire:
        # wire objects only use the max. display type for duplis
        sub.active = is_dupli
    sub.prop(obj, "display_type", text="Display As")

    if is_geometry or is_dupli or is_empty_image or is_gpencil:
        # Only useful with object having faces/materials...
        col.prop(obj, "color")

    col = box.column(align=False, heading="Bounds")
    col.use_property_decorate = False
    row = col.row(align=True)
    sub = row.row(align=True)
    sub.prop(obj, "show_bounds", text="")
    sub = sub.row(align=True)
    sub.active = obj.show_bounds or (obj.display_type == 'BOUNDS')
    sub.prop(obj, "display_bounds_type", text="")
    row.prop_decorator(obj, "display_bounds_type")


    # --- Show Wire
    """ if context.mode == 'OBJECT':
    col = box.column() 
    #row.scale_x = 2 """
    col = box.column()
    col.prop(context.space_data.overlay, 'show_wireframes', text='All Wireframe')
    #col.prop(context.object, 'show_wire', text='Obj', icon='URL')


# --- UV Maps Panel
def uv_maps(self, context, layout):
    layout = layout.box()

    layout.label(text='UV Maps')

    me = context.object.data #mesh

    row = layout.row()
    col = row.column()

    col.template_list("MESH_UL_uvmaps", "uvmaps", me, "uv_layers", me.uv_layers, "active_index", rows=2)

    col = row.column(align=True)
    col.operator("mesh.uv_texture_add", icon='ADD', text="")
    col.operator("mesh.uv_texture_remove", icon='REMOVE', text="")


# --- Unit Panel
def unit(self, context, layout):
    layout = layout.box()

    unit = context.scene.unit_settings

    layout.use_property_split = True
    layout.use_property_decorate = False

    layout.prop(unit, "system")

    col = layout.column()
    col.enabled = unit.system != 'NONE'
    col.prop(unit, "scale_length")
    col.prop(unit, "use_separate")

    col = layout.column()
    col.prop(unit, "system_rotation", text="Rotation")
    subcol = col.column()
    subcol.enabled = unit.system != 'NONE'
    subcol.prop(unit, "length_unit", text="Length")
    subcol.prop(unit, "mass_unit", text="Mass")
    subcol.prop(unit, "time_unit", text="Time")
    subcol.prop(unit, "temperature_unit", text="Temperature")








class PS_OT_tk_panel(Operator):
    bl_idname = "ps.tk_panel"
    bl_label = "Tool Kit"
    bl_options = {'REGISTER', 'INTERNAL'}
    

    @classmethod
    def poll(self, context):
        if context.active_object != None:
            return context.mode in {'EDIT_MESH', 'OBJECT'}

    
    def execute(self, context):
        return {'FINISHED'} 
    
    def invoke(self, context, event):
        if context.mode == 'OBJECT':
            return context.window_manager.invoke_popup(self, width = 600)#invoke_props_dialog

        elif context.mode == 'EDIT_MESH':
            return context.window_manager.invoke_popup(self, width = 600)


    def draw(self, context):
        layout = self.layout
        flow = layout.grid_flow(row_major=False, columns=3, even_columns=True, even_rows=False, align=False)
        #row = layout.row()

        #flow = layout.column_flow(columns=4, align=False)
        
     
        fast_tool_kit(self, context, flow)
        
        object_display(self, context, flow)

        uv_maps(self, context, flow)

        #unit(self, context, flow)
 
   
     
        






        
        
        
            
            
          

classes = [
    PS_PT_uv_maps_panel,
    PS_OT_tk_panel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)