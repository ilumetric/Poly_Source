import bpy
from bpy.types import AddonPreferences, PropertyGroup
from bpy.props import EnumProperty, FloatVectorProperty, BoolProperty, FloatProperty, IntProperty, CollectionProperty



import os
import sys
import importlib  

import bpy.utils.previews 



# --- Scene Settings
class PS_settings(PropertyGroup):
    
    def run_draw(self, context):
        if self.retopo_mode:
            bpy.ops.ps.draw_mesh('INVOKE_DEFAULT')
        
        if context.area:
            context.area.tag_redraw()
    

    def run_draw_props_grid(self, context):
        if self.draw_envira_grid:
            bpy.ops.ps.draw_props_grid('INVOKE_DEFAULT')

        if context.area:
            context.area.tag_redraw()

    



    mesh_check: BoolProperty(name="Mesh Check", default=False)

    retopo_mode: BoolProperty(name="Retopology Mode", default=False, update=run_draw)

    polycount:  BoolProperty(name="Poly Count", default=False)
    tris_count: IntProperty(name="Tris Count", min=1, soft_max=5000, default=2500) # , subtype='FACTOR'
 



    # --- Envira Grid
    draw_envira_grid: BoolProperty(name="Props Grid", default=False, update=run_draw_props_grid)
    one_unit: EnumProperty(name="One Unit", items = [("CM", "cm", ""), ("M", "m", "")], default="M",  description="One Unit")


    
    one2one: BoolProperty(name="1x1", default=True)
    unit_x: FloatProperty(name="X", description = " ", min=1.0, soft_max=5.0, default=1.0, subtype='FACTOR')
    unit_y: FloatProperty(name="Y", description = " ", min=1.0, soft_max=5.0, default=1.0, subtype='FACTOR')
    float_z: FloatProperty(name="Z Position", description = " ", default=0.0)

    padding: FloatProperty(name="Padding(cm)", description = " ", min=0.0, soft_max=20, default=10, subtype='FACTOR')

    draw_unit_grid: BoolProperty(name="Grid", default=False)
    one_unit_length: FloatProperty(name="One Unit Lenght(m)", description = " ", default=1.0, min=0.01)


    box: BoolProperty(name="Box", default=False)
    box_height: FloatProperty(name="Box Height", description = " ", min=0.0, soft_max=2.0, default=1.0, subtype='FACTOR')



# --- Addon preferences
class PS_preferences(AddonPreferences):
    bl_idname = __package__
    
    

    






    draw_: BoolProperty(name="TEST", default=False) # TODO 

    #Polycount
    low_suffix: BoolProperty(name="_Low ", description="To use to count only the objects in the collections of the _LOW suffix", default=False)
    
    max_points: IntProperty(name="Maximum Vertices In Active Object", description="If the active object has too many vertexes, this may affect performance during rendering.", min=1, soft_max=200000, default=50000)


    header: BoolProperty(name="Header", default=False)
    viewHeader_L: BoolProperty(name="Viewport Header Left", default=True)
    viewHeader_R: BoolProperty(name="Viewport Header Right", default=False)
    toolHeader: BoolProperty(name="Tool Header", default=False)


    line_smooth: BoolProperty(name="Line Smooth(If You Need Accelerate)", default=True)


    tabs: EnumProperty(name="Tabs", items = [("GENERAL", "General", ""), ("KEYMAPS", "Keymaps", "")], default="GENERAL")


    # --- Props Grid
    lines_props_grid: FloatVectorProperty(name="Lines Props Grid Color", subtype='COLOR', default=(0.1, 0.1, 0.1, 0.9), size=4, min=0.0, max=1.0, description="Select a color for lines props grid") # TODO description 
    box_props_grid: FloatVectorProperty(name="Box Color", subtype='COLOR', default=(0.1, 0.3, 1.0, 0.05), size=4, min=0.0, max=1.0, description="Select a color for Box")
    unit_grid: FloatVectorProperty(name="Unit Grid Color", subtype='COLOR', default=(0.0, 0.48, 1.0, 0.1), size=4, min=0.0, max=1.0, description="Select a color for unit grid")

    # --- Draw Mesh
    verts_size: IntProperty(name="Vertex", description="Verts Size", min=1, soft_max=5, default=1, subtype='FACTOR')
    edge_width: FloatProperty(name="Edge", description="Edge Width", min=1.0, soft_max=5.0, default=2, subtype='FACTOR')
    z_bias: FloatProperty(name="Z-Bias", description="Z-Bias", min=0.000001, soft_max=1.0, default=0.5, subtype='FACTOR')
    opacity: FloatProperty(name="Opacity", description="Face Opacity", min=0.0, max=1.0, default=0.75, subtype='PERCENTAGE')
    



    
    VE_color: FloatVectorProperty(name="Vertex & Edge Color", subtype='COLOR', default=(0.0, 0.0, 0.0, 1.0), size=4, min=0.0, max=1.0, description="Select a color for vertices & edges")
    F_color: FloatVectorProperty(name="Face Color", subtype='COLOR', default=(0.0, 0.33, 1.0), min=0.0, max=1.0, description="Select a color for faces")
    select_color: FloatVectorProperty(name="Select Color", subtype='COLOR', default=(1.0, 1.0, 1.0, 0.9), size=4, min=0.0, max=1.0, description="Select a color for elements")


    v_alone_color: FloatVectorProperty(name="Vertex Color", subtype='COLOR', default=(0.0, 1.0, 0.0, 1.0), size=4, min=0.0, max=1.0, description="Vertexes that are not connected to the geometry")
    non_manifold_color: FloatVectorProperty(name="Non Manifold Color", subtype='COLOR', default=(1.0, 0.0, 0.0, 0.5), size=4, min=0.0, max=1.0, description="Non Manifold Edges")
    bound_col: FloatVectorProperty(name="Bound Color", subtype='COLOR', default=(0.5, 0.0, 1.0, 0.5), size=4, min=0.0, max=1.0, description="Vertexes that are located at the edge of the geometry")
    e_pole_col: FloatVectorProperty(name="E-Pole Color", subtype='COLOR', default=(1.0, 0.5, 0.0, 0.5), size=4, min=0.0, max=1.0, description="Vertexes that are connected to 5 edges")
    n_pole_col: FloatVectorProperty(name="N-Pole Color", subtype='COLOR', default=(1.0, 1.0, 0.0, 0.5), size=4, min=0.0, max=1.0, description="Vertexes that are connected to 3 edges")
    f_pole_col: FloatVectorProperty(name="More 5 Pole Color", subtype='COLOR', default=(1.0, 0.0, 1.0, 0.5), size=4, min=0.0, max=1.0, description="Vertexes that are connected to more than 5 edges")
    tris_col: FloatVectorProperty(name="Tris Color", subtype='COLOR', default=(0.0, 0.5, 1.0, 0.5), size=4, min=0.0, max=1.0, description="Polygons with three vertexes")
    ngone_col: FloatVectorProperty(name="NGone Color", subtype='COLOR', default=(1.0, 0.1, 0.0, 0.5), size=4, min=0.0, max=1.0, description="Polygons with more than 4 vertexes")
    


    use_mod_ret: BoolProperty(name="Use Modifiers", description="Use the data from the modifiers", default=False)
    use_mod_che: BoolProperty(name="Use Modifiers", description="Use the data from the modifiers", default=False)

    xray_ret: BoolProperty(name="X-Ray", description="", default=False)
    xray_che: BoolProperty(name="X-Ray", description="", default=False)


    non_manifold_check: BoolProperty(name="Non Manifold", description="Non Manifold Edges", default=True)
    v_alone: BoolProperty(name="Vertex Alone", description="Vertexes that are not connected to the geometry", default=True)
    v_bound: BoolProperty(name="Vertex Boundary", description="Vertexes that are located at the edge of the geometry", default=False)
    e_pole: BoolProperty(name="Vertex E-Pole", description="Vertexes that are connected to 5 edges", default=False)
    n_pole: BoolProperty(name="Vertex N-Pole", description="Vertexes that are connected to 3 edges", default=False)
    f_pole: BoolProperty(name="More 5 Pole", description="Vertexes that are connected to more than 5 edges", default=False)
    tris: BoolProperty(name="Tris", description="Polygons with three vertexes", default=False)
    ngone: BoolProperty(name="N-Gone", description="Polygons with more than 4 vertexes", default=True)
    


    custom_count: BoolProperty(name="Custom", description="Custom number of vertexes in the polygon", default=False)
    custom_count_verts: IntProperty(name="Number of vertexes in the polygon", description=" ", min=3, default=5)
    custom_col: FloatVectorProperty(name="Polygon Color For Custom Mode", subtype='COLOR', default=(0.95, 0.78, 0.0, 0.5), size=4, min=0.0, max=1.0, description=" ")



    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "tabs", expand=True)
        box = layout.box()

        if self.tabs == "GENERAL":
            self.draw_general(box)

        elif self.tabs == "KEYMAPS":
            self.draw_keymaps(context, box)


    def draw_general(self, layout):
        pcoll = preview_collections["main"]
        market_icon = pcoll["market_icon"]
        gumroad_icon = pcoll["gumroad_icon"]
        artstation_icon = pcoll["artstation_icon"]
        discord_icon = pcoll["discord_icon"]


        col = layout.column()
        col.prop(self, "max_points")
        col.separator()
        
        col.prop(self, "header", text="Header(Not Suport Advance Draw Mesh)")
        col.prop(self, "viewHeader_L")
        col.prop(self, "viewHeader_R")
        col.prop(self, "toolHeader")
        

        box = layout.box()
        box.prop(self, "line_smooth")


        
        
        box.separator()
        box.label(text="Retopology Mode:")
        
        row = box.row()
        row.prop(self, "VE_color")
        row = box.row()
        row.prop(self, "F_color")
        row = box.row()
        row.prop(self, "select_color")

        
        box.separator()
        box.label(text="Mesh Check:")

        row = box.row()
        row.prop(self, "v_alone_color")
        row.prop(self, "non_manifold_color")

        row = box.row()
        row.prop(self, "bound_col")
        row.prop(self, "e_pole_col")

        row = box.row()
        row.prop(self, "n_pole_col")
        row.prop(self, "f_pole_col")

        row = box.row()
        row.prop(self, "tris_col")
        row.prop(self, "ngone_col")

        row = box.row()
        row.prop(self, "custom_col")


        box.separator()
        box.label(text="Props Grid:")
        row = box.row()
        row.prop(self, "lines_props_grid")
        row.prop(self, "box_props_grid")
        row = box.row()
        row.prop(self, "unit_grid")


        col = layout.column()
        col.label(text="Links")
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("wm.url_open", text="Blender Market", icon_value=market_icon.icon_id).url = "https://blendermarket.com/creators/derksen"
        row.operator("wm.url_open", text="Gumroad", icon_value=gumroad_icon.icon_id).url = "https://gumroad.com/derksenyan"
        row.operator("wm.url_open", text="Artstation", icon_value=artstation_icon.icon_id).url = "https://www.artstation.com/derksen"
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("wm.url_open", text="Discord Channel", icon_value=discord_icon.icon_id).url = "https://discord.gg/YAJE9JGDXc"


    def draw_keymaps(self, context, layout):
        col = layout.column()
        col.label(text="Keymap")
        
        keymap = context.window_manager.keyconfigs.user.keymaps['3D View']
        keymap_items = keymap.keymap_items

        col.prop(keymap_items["ps.ngons"], 'type', text='NGons', full_event=True)
        col.prop(keymap_items["ps.quads"], 'type', text='Quads', full_event=True)
        col.prop(keymap_items["ps.tris"], 'type', text='Tris', full_event=True)
        col.prop(keymap_items["ps.clear_dots"], 'type', text='Clear Dots', full_event=True)
        col.prop(keymap_items["ps.remove_vertex_non_manifold"], 'type', text='Clear Dots', full_event=True)

        col.label(text="*some hotkeys may not work because of the use of other addons")







addon_keymaps = []  
preview_collections = {}

classes = [
    PS_settings,
    PS_preferences,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


    bpy.types.Scene.ps_set_ = bpy.props.PointerProperty(type=PS_settings)


    
    wm = bpy.context.window_manager
    addon_keyconfig = wm.keyconfigs.addon

    kc = addon_keyconfig
    if not kc:
        return

    

    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    # Pie
    kmi = km.keymap_items.new("ps.ngons", type = "ONE",value="PRESS", ctrl=False, alt=True, shift=False, oskey=False)
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new("ps.quads", type = "TWO",value="PRESS", ctrl=False, alt=True, shift=False, oskey=False)
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new("ps.tris", type = "THREE",value="PRESS", ctrl=False, alt=True, shift=False, oskey=False)
    addon_keymaps.append((km, kmi))
    
    kmi = km.keymap_items.new("ps.clear_dots", type = "C",value="PRESS", ctrl=True, alt=True, shift=False, oskey=False)
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new("ps.remove_vertex_non_manifold", type = "N",value="PRESS", ctrl=True, alt=True, shift=False, oskey=False)
    addon_keymaps.append((km, kmi))
    del addon_keyconfig

    

    pcoll = bpy.utils.previews.new()
    my_icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    pcoll.load("market_icon", os.path.join(my_icons_dir, "market.png"), 'IMAGE')
    pcoll.load("gumroad_icon", os.path.join(my_icons_dir, "gumroad.png"), 'IMAGE')
    pcoll.load("artstation_icon", os.path.join(my_icons_dir, "artstation.png"), 'IMAGE')
    pcoll.load("discord_icon", os.path.join(my_icons_dir, "discord.png"), 'IMAGE')
    preview_collections["main"] = pcoll


    #bpy.app.handlers.load_post.append(run_draw)





def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.ps_set_

    
    

    #remove keymap entry
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    #bpy.app.handlers.load_post.remove(run_draw)