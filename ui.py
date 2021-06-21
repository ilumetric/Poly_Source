import bpy
import bmesh
import os
from bpy.types import Operator, Panel, Menu

from .icons import preview_collections



def activate():
    if bpy.context.active_object != None:
        #if bpy.context.active_object.select_get():
        return bpy.context.object.type == 'MESH'


class PS_PT_settings_draw_mesh(Panel):
    bl_idname = 'PS_PT_settings_draw_mesh'
    bl_label = 'Draw Mesh Settings'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'

    @classmethod
    def poll(self, context):
        return activate()

    def draw(self, context):
        pcoll = preview_collections["main"]
        calculate_icon = pcoll["calculate_icon"]
        check_icon = pcoll["check_icon"]
        box_icon = pcoll["box_icon"]
        grid_icon = pcoll["grid_icon"]
        draw_icon = pcoll["draw_icon"]


        props = context.preferences.addons[__package__.split(".")[0]].preferences
        settings = context.scene.ps_set_

        layout = self.layout
     

        # --- Retopology
        #layout.prop(props, "draw_", toggle=True) # TODO TEST 



        if settings.retopo_mode == False: 
            layout.prop(settings, "retopo_mode", icon_value=draw_icon.icon_id)

        else:
            box = layout.box()
            box.prop(settings, "retopo_mode", icon_value=draw_icon.icon_id)

            row_W = box.row(align=True)
            row_W.scale_x = 1.0
            row_W.label(text="Width")
            row_W.scale_x = 3.0
            row_W.prop(props, "verts_size")
            row_W.prop(props, "edge_width")

            box.prop(props, "z_bias", text="Z-Bias:")
            box.prop(props, "opacity", text="Opacity:")

            row_P = box.row()
            row_P.scale_x = 1.0
            row_P.prop(props, "xray_ret")
            row_P.scale_x = 1.1
            row_P.prop(props, "use_mod_ret")



        # --- Mesh Check
        if settings.PS_check == False: 
            layout.prop(settings, "PS_check", icon_value=check_icon.icon_id)
                
        else:
            box = layout.box()
            box.prop(settings, "PS_check", icon_value=check_icon.icon_id)
    
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
            row_P.prop(props, "xray_che")
            row_P.scale_x = 1.1
            row_P.prop(props, "use_mod_che")
     



        # --- Polycount
        if settings.polycount == False:
            layout.prop(settings, "polycount", icon_value=calculate_icon.icon_id)
        
        else:
            box = layout.box()
            box.prop(settings, "polycount", icon_value=calculate_icon.icon_id)
        
            row = box.row(align=True)
            row.prop(settings, "tris_count")
            row.scale_x = 0.4
            row.prop(props, "low_suffix", toggle=True)




        # --- Envira Grid
        if settings.draw_envira_grid == False:
            layout.prop(settings, "draw_envira_grid", icon_value=grid_icon.icon_id)
        
        else:
            box = layout.box()
            row = box.row()
            row.prop(settings, "draw_envira_grid", icon_value=grid_icon.icon_id)
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

            """ layout.prop(settings, 'array')
            if settings.array:
                layout.prop(settings, 'array_count') """

            if settings.box:
                box.prop(settings, 'box_height')

            box.prop(settings, 'draw_unit_grid')
            if settings.draw_unit_grid:
                box.prop(settings, 'one_unit_length')



        # --- Operators
        box = layout.box()
        box.prop(props, "max_points")
        
        if context.mode == 'EDIT_MESH':
            box.prop(context.space_data.overlay, "show_occlude_wire")
        
        



def draw_panel(self, context, row):
    props = context.preferences.addons[__package__.split(".")[0]].preferences
    pcoll = preview_collections["main"]

    obj = context.active_object
    
    if context.region.alignment != 'RIGHT':
        if activate():
            
            
            tris = 0
            quad = 0
            ngon = 0
            
            if len(obj.data.vertices) < props.max_points:
                if context.mode != 'EDIT_MESH': 
                    for loop in obj.data.polygons:
                        count = loop.loop_total
                        if count == 3:
                            tris += 1
                        elif count == 4:
                            quad += 1
                        else:
                            ngon += 1 


                else: 
                    bm = bmesh.from_edit_mesh(obj.data)
                    for face in bm.faces:
                        verts = 0
                        for i in face.verts:
                            verts += 1

                        if verts == 3:
                            tris += 1
                        elif verts == 4:
                            quad += 1
                        else:
                            ngon += 1 
            


            

                #bmesh.update_edit_mesh(obj.data) 

                polyNGon = str(ngon)
                polyQuad = str(quad)
                polyTris = str(tris)
                

                
                #layout = self.layout
                #layout.separator()
                #row = layout.row(align=True) 
                #row.alignment='LEFT'
                ngon_icon = pcoll["ngon_icon"] 
                quad_icon = pcoll["quad_icon"]
                tris_icon = pcoll["tris_icon"] 
                
                row.operator("ps.ngons", text=polyNGon, icon_value=ngon_icon.icon_id)    
                row.operator("ps.quads", text=polyQuad, icon_value=quad_icon.icon_id)
                row.operator("ps.tris", text=polyTris, icon_value=tris_icon.icon_id)

            else:
                box = row.box()
                point_max = str(props.max_points)
                box.label(text="Points > " + point_max, icon='ERROR')





def header_panel(self, context):
    props = context.preferences.addons[__package__].preferences

    if activate():
        if props.header == True:
            layout = self.layout
            row = layout.row(align=True) 
            draw_panel(self, context, row)
            #row.popover(panel='PS_PT_settings_draw_mesh', text="")

def viewHeader_L_panel(self, context):
    props = context.preferences.addons[__package__].preferences
    if activate():
        if props.viewHeader_L == True:
            layout = self.layout
            row = layout.row(align=True) 
            draw_panel(self, context, row)
            row.popover(panel='PS_PT_settings_draw_mesh', text="")


def viewHeader_R_panel(self, context):
    props = context.preferences.addons[__package__].preferences
    if activate():
        if props.viewHeader_R == True:
            layout = self.layout
            row = layout.row(align=True) 
            draw_panel(self, context, row)
            row.popover(panel='PS_PT_settings_draw_mesh', text="")





def tool_panel(self, context):
    props = context.preferences.addons[__package__].preferences
    if activate():
        layout = self.layout
        row = layout.row(align=True) 
        """ # Gizmo PRO
        if hasattr(bpy.types, bpy.ops.gizmopro.reset_location_object.idname()):
            draw_panel(self, context, row)
            row.popover(panel='PS_PT_settings_draw_mesh', text="") """

        if props.toolHeader == True:
            draw_panel(self, context, row)
            row.popover(panel='PS_PT_settings_draw_mesh', text="")

        






#OPERATOR
class PS_OT_ps_ngons(Operator):
    bl_idname = "ps.ngons"
    bl_label = "NGons"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Number Of NGons. Click To Select"
             
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH'

    def execute(self, context):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        context.tool_settings.mesh_select_mode=(False, False, True)
        bpy.ops.mesh.select_face_by_sides(number=4, type='GREATER')
        return {'FINISHED'}


class PS_OT_ps_quads(Operator):
    bl_idname = "ps.quads"
    bl_label = "Quads"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Number Of Quads. Click To Select"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH'

    def execute(self, context):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        context.tool_settings.mesh_select_mode=(False, False, True)
        bpy.ops.mesh.select_face_by_sides(number=4, type='EQUAL')
        return {'FINISHED'}


class PS_OT_ps_tris(Operator):
    bl_idname = "ps.tris"
    bl_label = "Tris"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Number Of Tris. Click To Select"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH'

    def execute(self, context):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        context.tool_settings.mesh_select_mode=(False, False, True)
        bpy.ops.mesh.select_face_by_sides(number=3, type='EQUAL')
        return {'FINISHED'}










# --- ADD OBJECT
# Layout
def layout_add_object(self, context):
    pcoll = preview_collections["main"]
    cylinder_icon = pcoll["cylinder"]
    tube_icon = pcoll["tube"]
    empty_PS_icon = pcoll["empty_mesh"]
    cube_icon = pcoll["cube"]

    layout = self.layout
    
    
    layout.operator("ps.create_empty_mesh", text="Empty Mesh", icon_value=empty_PS_icon.icon_id)
    layout.operator("ps.create_cube", text="Cube", icon_value=cube_icon.icon_id)
    layout.operator("ps.create_cylinder", text="Cylinder", icon_value=cylinder_icon.icon_id)
    layout.operator("ps.create_tube", text="Tube", icon_value=tube_icon.icon_id)



# Menu
class PS_MT_add_object(Menu):
    bl_idname = "PS_MT_add_object"
    bl_label = "Tool Kit"

    def draw(self, context):
        layout_add_object(self, context)



# Button In Add Menu
def add_object(self, context):
    pcoll = preview_collections["main"]
    addOb_icon = pcoll["addOb"]

    layout = self.layout
    layout.scale_x = 1.2
    if layout.direction != 'HORIZONTAL':
        layout.menu(menu='PS_MT_add_object', text="Tool Kit", icon_value=addOb_icon.icon_id)
        layout.separator()
    else:
        layout.menu(menu='PS_MT_add_object', text="", icon_value=addOb_icon.icon_id)
    layout.scale_x = 1.0
    #layout.separator()










classes = [
    PS_PT_settings_draw_mesh,
    PS_OT_ps_ngons,
    PS_OT_ps_quads,
    PS_OT_ps_tris,
    PS_MT_add_object,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_HT_upper_bar.append(header_panel)
    bpy.types.VIEW3D_MT_editor_menus.append(viewHeader_L_panel)
    bpy.types.VIEW3D_HT_header.append(viewHeader_R_panel)
    bpy.types.VIEW3D_HT_tool_header.append(tool_panel)
    bpy.types.VIEW3D_MT_editor_menus.prepend(add_object)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.TOPBAR_HT_upper_bar.remove(header_panel)
    bpy.types.VIEW3D_MT_editor_menus.remove(viewHeader_L_panel)
    bpy.types.VIEW3D_HT_header.remove(viewHeader_R_panel)
    bpy.types.VIEW3D_HT_tool_header.remove(tool_panel)
    bpy.types.VIEW3D_MT_editor_menus.prepend(add_object)