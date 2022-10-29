import bpy, bmesh
from bpy.types import Operator, Panel, Menu
from .icons import preview_collections
from .preferences import get_preferences
from . import check



class PS_PT_settings_draw_mesh(Panel):
    bl_idname = 'PS_PT_settings_draw_mesh'
    bl_label = 'Draw Mesh Settings'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'


    @classmethod
    def poll(self, context):
        if context.object:
            return context.object.type == 'MESH'


    def draw(self, context):
        pcoll = preview_collections[ 'main' ]
        calculate_icon = pcoll[ 'calculate_icon' ]
        check_icon = pcoll[ 'check_icon' ]
        box_icon = pcoll[ 'box_icon' ]
        grid_icon = pcoll[ 'grid_icon' ]
        draw_icon = pcoll[ 'draw_icon' ]


        props = get_preferences()
        settings = context.scene.PS_scene_set

        layout = self.layout
     

        # --- Retopology
        #layout.prop(props, "draw_", toggle=True) # TODO TEST 



        if settings.PS_retopology == False: 
            layout.prop(settings, 'PS_retopology', icon_value = draw_icon.icon_id )

        else:
            box = layout.box()
            box.prop(settings, 'PS_retopology', icon_value = draw_icon.icon_id )

            row = box.row(align=True)
            row.prop( settings, 'draw_verts', icon = 'VERTEXSEL' )
            row.prop( settings, 'draw_edges', icon = 'EDGESEL' )
            row.prop( settings, 'draw_faces', icon = 'FACESEL' )


            row = box.row(align=True)
            row.scale_x = 1.0
            row.label(text="Width")
            row.scale_x = 3.0
            row.prop(props, "verts_size")
            row.prop(props, "edge_width")

            box.prop(props, "z_bias", text="Z-Bias:")
            box.prop(props, "z_offset", text="Z-Offset:")
            box.prop(props, "opacity", text="Opacity:")

            row = box.row()
            row.scale_x = 1.0
            row.prop(props, "xray_ret")
            row.scale_x = 1.1
            row.prop(props, "use_mod_ret")

            box.prop(props, 'maxVerts_retop')




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
        if settings.PS_polycount == False:
            layout.prop(settings, "PS_polycount", icon_value=calculate_icon.icon_id)
        
        else:
            box = layout.box()
            box.prop(settings, "PS_polycount", icon_value=calculate_icon.icon_id)
            
            row = box.row(align=True)
            row.prop(settings, "tris_count")
            row.scale_x = 0.4
            row.prop(props, "low_suffix", toggle=True)




        # --- Envira Grid
        if settings.PS_envira_grid == False:
            layout.prop(settings, "PS_envira_grid", icon_value=grid_icon.icon_id)
        
        else:
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
        box.prop(props, 'maxVerts')
        box.prop(props, 'maxObjs')
        if context.mode == 'EDIT_MESH':
            box.prop(context.space_data.overlay, 'show_occlude_wire')

            
def get_maxObjs_status(maxObjs):
    
    sel_ob = bpy.context.selected_objects
    
    objs_count = 0
    maxObjs_status = True
        
    for obj in sel_ob:
        if obj.type == 'MESH':
            objs_count += 1
            if objs_count > maxObjs:
                maxObjs_status = False
                break
    return maxObjs_status

def get_maxVerts_status(maxVerts):
    
    sel_ob = bpy.context.selected_objects
    
    vertex_count = 0
    maxVerts_status = True
        
    for obj in sel_ob:
        if obj.type == 'MESH':
            vertex_count += len(obj.data.vertices)
            if vertex_count > maxVerts:
                maxVerts_status = False
                break
    return maxVerts_status

def polygon_counter():
    
    sel_ob = bpy.context.selected_objects

    ngon = 0    
    quad = 0
    tris = 0
    
    if bpy.context.mode != 'EDIT_MESH':
        for obj in sel_ob:
            if obj.type == 'MESH':    
                for loop in obj.data.polygons:
                    count = loop.loop_total
                    if count == 3:
                        tris += 1
                    elif count == 4:
                        quad += 1
                    else:
                        ngon += 1
    else:
        for obj in sel_ob:
            if obj.type == 'MESH':
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
    return str(ngon), str(quad), str(tris)        


def polygons_panel(self, context, layout):
    props = get_preferences()
    pcoll = preview_collections[ 'main' ]

    
    if context.region.alignment != 'RIGHT' and context.object:
        if get_maxObjs_status(props.maxObjs) and get_maxP_status(props.maxVerts):
            polygons = polygon_counter()

            polyNGon = polygons[0]
            polyQuad = polygons[1]
            polyTris = polygons[2]

            ngon_icon = pcoll[ 'ngon_icon' ] 
            quad_icon = pcoll[ 'quad_icon' ]
            tris_icon = pcoll[ 'tris_icon' ] 

            layout.operator( 'ps.ngons', text = polyNGon, icon_value = ngon_icon.icon_id )    
            layout.operator( 'ps.quads', text = polyQuad, icon_value = quad_icon.icon_id )
            layout.operator( 'ps.tris', text = polyTris, icon_value = tris_icon.icon_id )

        else:
            box = layout.box()   
            box.label( text = 'High Vertex or Objs value', icon = 'ERROR' )



def check_panel(self, context, layout):
    
    CHECK = False
    
    if context.mode == 'OBJECT' and context.object:

        objs = context.selected_objects
        for obj in objs:
            verts = obj.data.vertices
            edges = obj.data.edges
            faces = obj.data.polygons


    if CHECK:
        layout.operator( 'ps.ngons', text = '', icon = 'ERROR' )


def header_panel(self, context):
    props = get_preferences()
    if context.object:
        if context.object.type == 'MESH':
            if props.header:
                layout = self.layout
                row = layout.row( align = True ) 
                polygons_panel( self, context, row )
                #row.popover(panel='PS_PT_settings_draw_mesh', text="")


def viewHeader_L_panel(self, context):
    props = get_preferences()
    if context.object:
        if context.object.type == 'MESH':
            if props.viewHeader_L:
                layout = self.layout
                row = layout.row( align = True )
                #check_panel( self, context, row ) # TODO
                polygons_panel( self, context, row )
                row.popover( panel = 'PS_PT_settings_draw_mesh', text = '' )


def viewHeader_R_panel(self, context):
    props = get_preferences()
    if context.object:
        if context.object.type == 'MESH':
            if props.viewHeader_R:
                layout = self.layout
                row = layout.row( align = True )
                #check_panel( self, context, row ) # TODO
                polygons_panel( self, context, row )
                row.popover( panel = 'PS_PT_settings_draw_mesh', text='' )


def tool_panel(self, context):
    props = get_preferences()
    if context.object:
        if context.object.type == 'MESH':
            layout = self.layout
            row = layout.row( align = True )
            if props.toolHeader:
                #check_panel( self, context, row )  # TODO
                polygons_panel( self, context, row )
                row.popover( panel = 'PS_PT_settings_draw_mesh', text = '' )

        






# --- OPERATORS

class PS_OT_ps_ngons(Operator):
    bl_idname = 'ps.ngons'
    bl_label = 'NGons'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'Number Of NGons. Click To Select'
             
    @classmethod
    def poll(cls, context):
        if context.active_object:
            return context.active_object.type == 'MESH'

    def execute(self, context):
        bpy.ops.object.mode_set( mode = 'EDIT' )
        bpy.ops.mesh.select_all( action = 'DESELECT' )
        #context.tool_settings.mesh_select_mode = ( False, False, True )
        bpy.ops.mesh.select_face_by_sides( number = 4, type = 'GREATER' )
        return {'FINISHED'}



class PS_OT_ps_quads(Operator):
    bl_idname = 'ps.quads'
    bl_label = 'Quads'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'Number Of Quads. Click To Select'

    @classmethod
    def poll(cls, context):
        if context.active_object:
            return context.active_object.type == 'MESH'

    def execute(self, context):
        bpy.ops.object.mode_set( mode = 'EDIT' )
        bpy.ops.mesh.select_all( action = 'DESELECT' )
        #context.tool_settings.mesh_select_mode=(False, False, True)
        bpy.ops.mesh.select_face_by_sides( number = 4, type = 'EQUAL' )
        return {'FINISHED'}



class PS_OT_ps_tris(Operator):
    bl_idname = 'ps.tris'
    bl_label = 'Tris'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'Number Of Tris. Click To Select'

    @classmethod
    def poll(cls, context):
        if context.active_object:
            return context.active_object.type == 'MESH'
            
    def execute(self, context):
        bpy.ops.object.mode_set( mode = 'EDIT' )
        bpy.ops.mesh.select_all( action = 'DESELECT' )
        #context.tool_settings.mesh_select_mode=(False, False, True)
        bpy.ops.mesh.select_face_by_sides( number = 3, type = 'EQUAL' )
        return {'FINISHED'}










# --- ADD OBJECT
# Layout
def custom_objects(self, context):
    props = get_preferences()

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













classes = [
    PS_PT_settings_draw_mesh,
    PS_OT_ps_ngons,
    PS_OT_ps_quads,
    PS_OT_ps_tris,
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
