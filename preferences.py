import bpy
from bpy.types import AddonPreferences, PropertyGroup
from bpy.props import EnumProperty, FloatVectorProperty, BoolProperty, FloatProperty, IntProperty
from .icons import preview_collections
import rna_keymap_ui
from .utils.utils import get_hotkey_entry_item
from . import check
from math import radians



class PS_settings(PropertyGroup):

    # rotation increment presets
    def set_increment_angles(self, context):
        if self.increment_angles == '5':
            context.scene.tool_settings.snap_angle_increment_3d = radians(5)
        elif self.increment_angles == '10':
            context.scene.tool_settings.snap_angle_increment_3d = radians(10)
        elif self.increment_angles == '15':
            context.scene.tool_settings.snap_angle_increment_3d = radians(15)
        elif self.increment_angles == '30':
            context.scene.tool_settings.snap_angle_increment_3d = radians(30)
        elif self.increment_angles == '45':
            context.scene.tool_settings.snap_angle_increment_3d = radians(45)
        elif self.increment_angles == '60':
            context.scene.tool_settings.snap_angle_increment_3d = radians(60)
        elif self.increment_angles == '90':
            context.scene.tool_settings.snap_angle_increment_3d = radians(90)

    increment_angles: EnumProperty(
        name='Increment Angles',
        description='Selection of angle for snapping',
        items=[
            ('5', '5°', ''),
            ('10', '10°', ''),
            ('15', '15°', ''),
            ('30', '30°', ''),
            ('45', '45°', ''),
            ('60', '60°', ''),
            ('90', '90°', ''),
        ],
        default='45',
        update=set_increment_angles,
    )




    def polycount_widget(self, context):
        wm = context.window_manager
        if self.PS_polycount:
            wm.gizmo_group_type_ensure('PS_GGT_polycount_group')
        else:
            wm.gizmo_group_type_unlink_delayed('PS_GGT_polycount_group')

    PS_polycount: BoolProperty(name="Poly Count", default=False, update=polycount_widget)
    tris_count: IntProperty(name="Tris Count", min=1, soft_max=5000, default=2500)


    # grid
    draw_grid: BoolProperty(name="Grid", default=False)
    box: BoolProperty(name="Box", default=False)
    grid_xray: BoolProperty(name="X-Ray", default=False)
    one2one: BoolProperty(name="1x1", default=True)
    unit_x: FloatProperty(name="X", description = " ", min=1, soft_max=1000.0, default=100.0)
    unit_y: FloatProperty(name="Y", description = " ", min=1, soft_max=1000.0, default=100.0)
    offset_z: FloatProperty(name="Z Offset", description = "cm", default=0.0)
    padding: FloatProperty(name="Padding", description = "cm", min=0.0, soft_min=5.0, soft_max=20, default=10)
    height: FloatProperty(name="Height", description = "cm", min=0.0, soft_min=10.0, soft_max=200.0, default=180.0)
    draw_sub_grid: BoolProperty(name="Sub Grid", default=True)
    grid_cell_size: FloatProperty(name="Cell Size", description="cm", min=1.0, soft_max=200.0, default=100.0)
    grid_align_center: BoolProperty(name="Align Center", default=True)


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
    elongated_tris: BoolProperty(name="Elongated Tris", description=" ", default=True, update=update_check) # TODO description

    elongated_aspect_ratio: FloatProperty(name="Elongated Aspect Ratio", description = "Display of elongated triangles", min=0.0, soft_max=100.0, default=45.0, subtype='FACTOR', update=update_check)
    custom_count: BoolProperty(name="Custom", description="Custom number of vertexes in the polygon", default=False, update=update_check)
    custom_count_verts: IntProperty(name="Number of Vertices in the Polygon", description=" ", min=3, default=5, update=update_check)


    panel_groops: EnumProperty(
                    name='Groops',
                    description = '',
                    items = [
                        ('TRANSFORM', 'Transform', '', 'EMPTY_ARROWS', 0),
                        ('DISPLAY', 'Display', '', 'RESTRICT_VIEW_OFF', 1),
                        ],
                    default = 'TRANSFORM',
                    )


    base_edge_size: FloatProperty(name="Base Edge Size", default=0.1, min=0.001, max=1.0)
    adaptive_curvature_threshold: FloatProperty(name="Adaptive Curvature Threshold", default=10.0, min=0.1, max=180.0)


class PS_preferences(AddonPreferences):
    bl_idname = 'Poly_Source'

    # функции апдейта
    def update_select_wireframe(self, context):
        if self.b_wire_for_selected == False:
            context.scene.show_wire_for_selected = False





    low_suffix: BoolProperty(name="_Low ", description="To use to count only the objects in the collections of the _LOW suffix", default=False)

    maxVerts: IntProperty(name="Maximum Vertices In Active Object", description="If the active object has too many vertexes, this may affect performance during rendering.", min=3, soft_max=200000, default=50000)
    maxObjs: IntProperty(name="Maximum number of selected objects", description="If the active object has too many objects, this may affect performance during rendering.", min=1, soft_max=500, default=50)

    color_grid: FloatVectorProperty(name="Grid Color", subtype='COLOR', default=(0.1, 0.1, 0.1, 0.9), size=4, min=0.0, max=1.0, description="Select a color for grid")
    color_box: FloatVectorProperty(name="Box Color", subtype='COLOR', default=(1.0, 0.03, 0.17, 0.1), size=4, min=0.0, max=1.0, description="Select a color for box")

    point_width: FloatProperty(name="Point Width", description="Edge Width", min=1.0, soft_max=30.0, default=15)
    line_width: FloatProperty(name="Edge Width", description="Edge Width", min=1.0, soft_max=30.0, default=5)

    v_alone_color: FloatVectorProperty(name="Vertex Color", subtype='COLOR', default=(0.0, 1.0, 0.0, 1.0), size=4, min=0.0, max=1.0, description="Vertexes that are not connected to the geometry")
    non_manifold_color: FloatVectorProperty(name="Non Manifold Color", subtype='COLOR', default=(1.0, 0.0, 0.0, 0.5), size=4, min=0.0, max=1.0, description="Non Manifold Edges")
    bound_col: FloatVectorProperty(name="Bound Color", subtype='COLOR', default=(0.5, 0.0, 1.0, 0.5), size=4, min=0.0, max=1.0, description="Vertexes that are located at the edge of the geometry")
    e_pole_col: FloatVectorProperty(name="E-Pole Color", subtype='COLOR', default=(1.0, 0.5, 0.0, 0.5), size=4, min=0.0, max=1.0, description="Vertexes that are connected to 5 edges")
    n_pole_col: FloatVectorProperty(name="N-Pole Color", subtype='COLOR', default=(1.0, 1.0, 0.0, 0.5), size=4, min=0.0, max=1.0, description="Vertexes that are connected to 3 edges")
    f_pole_col: FloatVectorProperty(name="More 5 Pole Color", subtype='COLOR', default=(1.0, 0.0, 1.0, 0.5), size=4, min=0.0, max=1.0, description="Vertexes that are connected to more than 5 edges")
    tris_col: FloatVectorProperty(name="Tris Color", subtype='COLOR', default=(0.0, 0.5, 1.0, 0.5), size=4, min=0.0, max=1.0, description="Polygons with three vertexes")
    ngone_col: FloatVectorProperty(name="NGone Color", subtype='COLOR', default=(1.0, 0.1, 0.0, 0.5), size=4, min=0.0, max=1.0, description="Polygons with more than 4 vertexes")
    elongated_tris_col: FloatVectorProperty(name="Elongated Tris Color", subtype='COLOR', default=(0.78, 0.0, 0.95, 0.9), size=4, min=0.0, max=1.0, description=" ")
    custom_col: FloatVectorProperty(name="Polygon Color For Custom Mode", subtype='COLOR', default=(0.95, 0.78, 0.0, 0.5), size=4, min=0.0, max=1.0, description=" ")


    # опции для включения и отключения функционала
    b_color_radomizer: BoolProperty(name="Color Randomizer", description="Function to randomize the color by adding a prefix to the object name. Works with 3D View > Shading Popover > Color > Random", default=True)
    b_bool_tool: BoolProperty(name="Bool Tool", description="Enable the display of basic Bool operators", default=True)
    b_add_objects: BoolProperty(name="Custom Objects in Add Menu", default=False)
    b_wire_for_selected: BoolProperty(name="Wireframe for Selected", description="3D View > Overlays Popover", default=False, update=update_select_wireframe)
    b_presets_increment_angles: BoolProperty(name="Presets Increment Angles", description="3D View > Snapping Popover", default=True)
    b_camera_sync: BoolProperty(name="Camera Sync", description="3D View Header", default=False)


    b_count_header: BoolProperty(name="Polycount: Header", default=True)
    b_count_view_header_l: BoolProperty(name="Polycount: Viewport Header Left", default=False)
    b_count_view_header_r: BoolProperty(name="Polycount: Viewport Header Right", default=False)
    b_count_tool_header: BoolProperty(name="Polycount: Tool Header (may conflict with other addons)", default=False)



    tabs: EnumProperty(name="Tabs", items = [("GENERAL", "General", ""), ("KEYMAPS", "Keymaps", "")], default="GENERAL")

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, 'tabs', expand=True)

        if self.tabs == 'GENERAL':
            self.draw_general(layout)

        elif self.tabs == 'KEYMAPS':
            self.draw_keymaps(context, layout)

    def draw_general(self, layout):
        pcoll = preview_collections['main']
        market_icon = pcoll['market_icon']
        gumroad_icon = pcoll['gumroad_icon']
        artstation_icon = pcoll['artstation_icon']

        box = layout.box()
        box.label(text='Tools')
        box.prop(self, 'b_color_radomizer')
        box.prop(self, 'b_bool_tool')
        box.prop(self, 'b_add_objects')
        box.prop(self, 'b_wire_for_selected')
        box.prop(self, 'b_presets_increment_angles')
        box.prop(self, 'b_camera_sync')
        box.separator()
        box.prop(self, 'b_count_header')
        box.prop(self, 'b_count_view_header_l')
        box.prop(self, 'b_count_view_header_r')
        box.prop(self, 'b_count_tool_header')



        col = layout.column()
        col.prop(self, "maxVerts")
        col.prop(self, "maxObjs")
        col.prop(self, "point_width")
        col.prop(self, "line_width")
        col.separator()





        box = layout.box()

        box.separator()
        box.label(text="Mesh Check")

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
        row.prop(self, "elongated_tris_col")
        row.prop(self, "custom_col")



        box.separator()
        box.label(text="Unit Grid:")
        row = box.row()
        row.prop(self, "color_grid")
        row.prop(self, "color_box")



        layout.label(text='Links')
        row = layout.row()
        row.operator('wm.url_open', text='Blender Market', icon_value=market_icon.icon_id).url = "https://blendermarket.com/creators/derksen"
        row.operator('wm.url_open', text='Gumroad', icon_value=gumroad_icon.icon_id).url = "https://derksen.gumroad.com"
        row.operator('wm.url_open', text='Artstation', icon_value=artstation_icon.icon_id).url = "https://www.artstation.com/derksen"


    def draw_keymaps(self, context, layout):
        col = layout.column()
        col.label(text='Keymap')

        wm = context.window_manager
        kc = wm.keyconfigs.user
        km = kc.keymaps['3D View']

        kmi = get_hotkey_entry_item(km, 'wm.call_panel', 'PS_PT_tool_kit', 'none')
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

    bpy.types.Scene.poly_source = bpy.props.PointerProperty(type=PS_settings)

    wm = bpy.context.window_manager
    addon_keyconfig = wm.keyconfigs.addon

    kc = addon_keyconfig
    if not kc:
        return

    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')

    kmi = km.keymap_items.new('wm.call_panel', type='SPACE', value='PRESS')
    kmi.properties.name = 'PS_PT_tool_kit'
    addon_keymaps.append((km, kmi))




def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.poly_source

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()