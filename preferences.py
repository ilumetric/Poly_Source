import bpy
from bpy.types import AddonPreferences, PropertyGroup
from bpy.props import EnumProperty, FloatVectorProperty, BoolProperty, FloatProperty, IntProperty
from .icons import preview_collections
import rna_keymap_ui
from .utils.utils import get_hotkey_entry_item
from . import check


# --- Scene Settings
class PS_settings(PropertyGroup):

    

    


    # --- Polycount
    def polycount_widget(self, context):
        wm = context.window_manager
        if self.PS_polycount:
            wm.gizmo_group_type_ensure('PS_GGT_polycount_group')
        else:
            wm.gizmo_group_type_unlink_delayed('PS_GGT_polycount_group')

    PS_polycount: BoolProperty(name="Poly Count", default=False, update=polycount_widget)
    tris_count: IntProperty(name="Tris Count", min=1, soft_max=5000, default=2500) # , subtype='FACTOR'
 

    # --- Envira Grid
    def grid_widget(self, context):
        wm = context.window_manager
        if self.PS_envira_grid:
            wm.gizmo_group_type_ensure('PS_GGT_draw_grid_group')
        else:
            wm.gizmo_group_type_unlink_delayed('PS_GGT_draw_grid_group')

    PS_envira_grid: BoolProperty(name="Props Grid", default=False, update=grid_widget)

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


    def update_check(self, context):
        check.UPDATE = True
    PS_check: BoolProperty(name="Mesh Check", default=False)
    use_mod_che: BoolProperty(name="Use Modifiers", description="Use the data from the modifiers", default=False, update=update_check)
    xray_for_check: BoolProperty(name="X-Ray", description="", default=False, update=update_check)
    non_manifold_check: BoolProperty(name="Non Manifold", description="Non Manifold Edges", default=True, update=update_check)
    v_alone: BoolProperty(name="Vertex Alone", description="Vertexes that are not connected to the geometry", default=True, update=update_check)
    v_bound: BoolProperty(name="Vertex Boundary", description="Vertexes that are located at the edge of the geometry", default=False, update=update_check)
    e_pole: BoolProperty(name="Vertex E-Pole", description="Vertexes that are connected to 5 edges", default=False, update=update_check)
    n_pole: BoolProperty(name="Vertex N-Pole", description="Vertexes that are connected to 3 edges", default=False, update=update_check)
    f_pole: BoolProperty(name="More 5 Pole", description="Vertexes that are connected to more than 5 edges", default=False, update=update_check)
    tris: BoolProperty(name="Tris", description="Polygons with three vertexes", default=False, update=update_check)
    ngone: BoolProperty(name="N-Gone", description="Polygons with more than 4 vertexes", default=True, update=update_check)
    custom_count: BoolProperty(name="Custom", description="Custom number of vertexes in the polygon", default=False, update=update_check)
    custom_count_verts: IntProperty(name="Number of Vertices in the Polygon", description=" ", min=3, default=5, update=update_check)
    

    panel_groops: EnumProperty(
                    name='Groops', 
                    description = '',
                    items = [
                        ('TRANSFORM', 'Transform', '', 'EMPTY_ARROWS', 0),
                        ('OPS', 'Operators', '', 'NODETREE', 1),
                        ('DISPLAY', 'Display', '', 'RESTRICT_VIEW_OFF', 2),
                        ],
                    default = 'TRANSFORM',
                    )



# --- Addon preferences
class PS_preferences(AddonPreferences):
    bl_idname = __package__
    

    header: BoolProperty(name="Header", default=True)
    viewHeader_L: BoolProperty(name="Viewport Header Left", default=False)
    viewHeader_R: BoolProperty(name="Viewport Header Right", default=False)
    toolHeader: BoolProperty(name="Tool Header", default=False)
    add_objects: BoolProperty(name="Custom Objects in Add Menu", default=True)

    

    #Polycount
    low_suffix: BoolProperty(name="_Low ", description="To use to count only the objects in the collections of the _LOW suffix", default=False)
    
    maxVerts: IntProperty(name="Maximum Vertices In Active Object", description="If the active object has too many vertexes, this may affect performance during rendering.", min=3, soft_max=200000, default=50000)
    
    maxObjs: IntProperty(name="Maximum number of selected objects", description="If the active object has too many objects, this may affect performance during rendering.", min=1, soft_max=500, default=50)


    


    # --- Props Grid
    lines_props_grid: FloatVectorProperty(name="Lines Props Grid Color", subtype='COLOR', default=(0.1, 0.1, 0.1, 0.9), size=4, min=0.0, max=1.0, description="Select a color for lines props grid") # TODO description 
    box_props_grid: FloatVectorProperty(name="Box Color", subtype='COLOR', default=(1.0, 0.03, 0.17, 0.05), size=4, min=0.0, max=1.0, description="Select a color for Box")
    unit_grid: FloatVectorProperty(name="Unit Grid Color", subtype='COLOR', default=(0.0, 0.48, 1.0, 0.1), size=4, min=0.0, max=1.0, description="Select a color for unit grid")

    # --- Draw Mesh
    #verts_size: IntProperty(name="Vertex", description="Verts Size", min=1, soft_max=12, default=5, subtype='FACTOR')
    #edge_width: FloatProperty(name="Edge", description="Edge Width", min=1.0, soft_max=5.0, default=2, subtype='FACTOR')
    
   
    VE_color: FloatVectorProperty(name="Vertex & Edge Color", subtype='COLOR', default=(0.0, 0.0, 0.0, 1.0), size=4, min=0.0, max=1.0, description="Select a color for vertices & edges")
    F_color: FloatVectorProperty(name="Face Color", subtype='COLOR', default=(0.0, 0.33, 1.0), size=3, min=0.0, max=1.0, description="Select a color for faces")
    select_color: FloatVectorProperty(name="Select Color", subtype='COLOR', default=(1.0, 1.0, 1.0), size=3, min=0.0, max=1.0, description="Select a color for elements")
    v_alone_color: FloatVectorProperty(name="Vertex Color", subtype='COLOR', default=(0.0, 1.0, 0.0, 1.0), size=4, min=0.0, max=1.0, description="Vertexes that are not connected to the geometry")
    non_manifold_color: FloatVectorProperty(name="Non Manifold Color", subtype='COLOR', default=(1.0, 0.0, 0.0, 0.5), size=4, min=0.0, max=1.0, description="Non Manifold Edges")
    bound_col: FloatVectorProperty(name="Bound Color", subtype='COLOR', default=(0.5, 0.0, 1.0, 0.5), size=4, min=0.0, max=1.0, description="Vertexes that are located at the edge of the geometry")
    e_pole_col: FloatVectorProperty(name="E-Pole Color", subtype='COLOR', default=(1.0, 0.5, 0.0, 0.5), size=4, min=0.0, max=1.0, description="Vertexes that are connected to 5 edges")
    n_pole_col: FloatVectorProperty(name="N-Pole Color", subtype='COLOR', default=(1.0, 1.0, 0.0, 0.5), size=4, min=0.0, max=1.0, description="Vertexes that are connected to 3 edges")
    f_pole_col: FloatVectorProperty(name="More 5 Pole Color", subtype='COLOR', default=(1.0, 0.0, 1.0, 0.5), size=4, min=0.0, max=1.0, description="Vertexes that are connected to more than 5 edges")
    tris_col: FloatVectorProperty(name="Tris Color", subtype='COLOR', default=(0.0, 0.5, 1.0, 0.5), size=4, min=0.0, max=1.0, description="Polygons with three vertexes")
    ngone_col: FloatVectorProperty(name="NGone Color", subtype='COLOR', default=(1.0, 0.1, 0.0, 0.5), size=4, min=0.0, max=1.0, description="Polygons with more than 4 vertexes")
    custom_col: FloatVectorProperty(name="Polygon Color For Custom Mode", subtype='COLOR', default=(0.95, 0.78, 0.0, 0.5), size=4, min=0.0, max=1.0, description=" ")

    tabs: EnumProperty(name="Tabs", items = [("GENERAL", "General", ""), ("KEYMAPS", "Keymaps", "")], default="GENERAL")
    

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
        col.prop(self, "maxVerts")
        col.prop(self, "maxObjs")
        col.separator()
        
        col.prop(self, "header")
        col.prop(self, "viewHeader_L")
        col.prop(self, "viewHeader_R")
        col.prop(self, "toolHeader")
        col.prop(self, "add_objects")


        box = layout.box()


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
        row.separator(factor=0.3)
        row.operator("wm.url_open", text="Gumroad", icon_value=gumroad_icon.icon_id).url = "https://derksen.gumroad.com"
        row.separator(factor=0.3)
        row.operator("wm.url_open", text="Artstation", icon_value=artstation_icon.icon_id).url = "https://www.artstation.com/derksen"


    def draw_keymaps(self, context, layout):
        col = layout.column()
        col.label(text="Keymap")
        
        """ keymap = context.window_manager.keyconfigs.user.keymaps['3D View']
        keymap_items = keymap.keymap_items
        km = keymap.active()
        layout.template_event_from_keymap_item(keymap_items["ps.tool_kit_panel"]) """


        wm = context.window_manager
        kc = wm.keyconfigs.user
        km = kc.keymaps['3D View']





        kmi = get_hotkey_entry_item(km, 'wm.call_panel', 'PS_PT_tool_kit', 'none')
        if kmi:
            col.context_pointer_set('keymap', km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
        else:
            col.label(text='No hotkey entry found')

        kmi = get_hotkey_entry_item(km, 'ps.ngons_select', 'none', 'none')
        if kmi:
            col.context_pointer_set('keymap', km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
        else:
            col.label(text='No hotkey entry found')

        kmi = get_hotkey_entry_item(km, 'ps.quads_select', 'none', 'none')
        if kmi:
            col.context_pointer_set('keymap', km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
        else:
            col.label(text='No hotkey entry found')

        kmi = get_hotkey_entry_item(km, 'ps.tris_select', 'none', 'none')
        if kmi:
            col.context_pointer_set('keymap', km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
        else:
            col.label(text='No hotkey entry found')

        kmi = get_hotkey_entry_item(km, 'ps.clear_dots', 'none', 'none')
        if kmi:
            col.context_pointer_set('keymap', km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
        else:
            col.label(text='No hotkey entry found')

        kmi = get_hotkey_entry_item(km, 'ps.remove_vertex_non_manifold', 'none', 'none')
        if kmi:
            col.context_pointer_set('keymap', km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
        else:
            col.label(text='No hotkey entry found')


        col.label(text="*some hotkeys may not work because of the use of other addons")


addon_keymaps = []  


classes = [
    PS_settings,
    PS_preferences,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


    bpy.types.Scene.PS_scene_set = bpy.props.PointerProperty(type=PS_settings)


    
    wm = bpy.context.window_manager
    addon_keyconfig = wm.keyconfigs.addon

    kc = addon_keyconfig
    if not kc:
        return

    

    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')


    kmi = km.keymap_items.new('wm.call_panel', type='SPACE', value='PRESS')
    kmi.properties.name = 'PS_PT_tool_kit'
    addon_keymaps.append((km, kmi))

    # Pie
    kmi = km.keymap_items.new('ps.ngons_select', type = 'ONE', value = 'PRESS', ctrl=False, alt=True, shift=False, oskey=False)
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new('ps.quads_select', type = 'TWO', value = 'PRESS', ctrl=False, alt=True, shift=False, oskey=False)
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new('ps.tris_select', type = 'THREE', value = 'PRESS', ctrl=False, alt=True, shift=False, oskey=False)
    addon_keymaps.append((km, kmi))
    
    kmi = km.keymap_items.new('ps.clear_dots', type = 'C', value = 'PRESS', ctrl=True, alt=True, shift=False, oskey=False)
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new('ps.remove_vertex_non_manifold', type = 'N', value = 'PRESS', ctrl=True, alt=True, shift=False, oskey=False)
    addon_keymaps.append((km, kmi))
    del addon_keyconfig

    

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.PS_scene_set

    
    

    # --- Remove Keymap
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()