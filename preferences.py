import bpy
import rna_keymap_ui
from bpy.types import AddonPreferences, PropertyGroup
from bpy.props import (
    EnumProperty,
    FloatVectorProperty,
    BoolProperty,
    FloatProperty,
    IntProperty,
    PointerProperty,
)
from .icons import preview_collections
from .utils.utils import get_hotkey_entry_item
from . import check


class PS_PG_settings(PropertyGroup):
    """Scene-level settings for Poly Source"""

    # --- polycount виджет
    def polycount_widget(self, context):
        wm = context.window_manager
        if self.show_polycount:
            wm.gizmo_group_type_ensure('PS_GGT_polycount_group')
        else:
            wm.gizmo_group_type_unlink_delayed('PS_GGT_polycount_group')

    show_polycount: BoolProperty(
        name="Poly Count",
        description="Display polygon counter overlay in the 3D viewport",
        default=False,
        update=polycount_widget,
    )
    tris_count: IntProperty(
        name="Tris Count",
        description="Target triangle budget for the scene polycount indicator",
        min=1, soft_max=5000, default=2500,
    )

    # --- grid настройки
    draw_grid: BoolProperty(name="Grid", description="Display unit grid overlay in the 3D viewport", default=False)
    box: BoolProperty(name="Box", description="Display bounding box volume above the grid", default=False)
    grid_xray: BoolProperty(name="X-Ray", description="Draw grid on top of all geometry", default=False)
    one2one: BoolProperty(name="1x1", description="Lock grid width and depth to equal dimensions", default=True)
    unit_x: FloatProperty(name="X", description="Grid width in centimeters", min=1, soft_max=1000.0, default=100.0)
    unit_y: FloatProperty(name="Y", description="Grid depth in centimeters", min=1, soft_max=1000.0, default=100.0)
    offset_z: FloatProperty(name="Z Offset", description="Vertical offset of the grid in centimeters", default=0.0)
    padding: FloatProperty(name="Padding", description="Inner padding from grid boundary in centimeters", min=0.0, soft_min=5.0, soft_max=20, default=10)
    height: FloatProperty(name="Height", description="Bounding box height in centimeters", min=0.0, soft_min=10.0, soft_max=200.0, default=180.0)
    draw_sub_grid: BoolProperty(name="Sub Grid", description="Display subdivision lines inside the main grid", default=True)
    grid_cell_size: FloatProperty(name="Cell Size", description="Size of each sub-grid cell in centimeters", min=1.0, soft_max=200.0, default=100.0)
    grid_align_center: BoolProperty(name="Align Center", description="Center sub-grid cells within the main grid boundary", default=True)

    # --- mesh check настройки
    def update_check(self, context):
        check.UPDATE = True

    show_check: BoolProperty(
        name="Mesh Check",
        description="Enable mesh analysis overlay for selected objects",
        default=False,
    )
    use_modifiers: BoolProperty(
        name="Use Modifiers",
        description="Analyze mesh with applied modifier stack instead of base mesh",
        default=False,
        update=update_check,
    )
    xray_for_check: BoolProperty(
        name="X-Ray",
        description="Draw check results on top of all geometry",
        default=False,
        update=update_check,
    )
    non_manifold_check: BoolProperty(
        name="Non Manifold",
        description="Highlight edges shared by more or fewer than two faces",
        default=True,
        update=update_check,
    )
    v_alone: BoolProperty(
        name="Isolated Vertices",
        description="Highlight isolated vertices with no connected edges",
        default=True,
        update=update_check,
    )
    v_bound: BoolProperty(
        name="Boundary",
        description="Highlight vertices on open mesh boundaries",
        default=False,
        update=update_check,
    )
    e_pole: BoolProperty(
        name="E-Pole (5)",
        description="Highlight vertices connected to exactly 5 edges (E-poles)",
        default=False,
        update=update_check,
    )
    n_pole: BoolProperty(
        name="N-Pole (3)",
        description="Highlight vertices connected to exactly 3 edges (N-poles)",
        default=False,
        update=update_check,
    )
    f_pole: BoolProperty(
        name=">5 Pole",
        description="Highlight vertices connected to more than 5 edges (extraordinary poles)",
        default=False,
        update=update_check,
    )
    tris: BoolProperty(
        name="Tris",
        description="Highlight triangular faces (3 vertices)",
        default=False,
        update=update_check,
    )
    ngone: BoolProperty(
        name="N-Gon",
        description="Highlight N-gon faces (more than 4 vertices)",
        default=True,
        update=update_check,
    )
    elongated_tris: BoolProperty(
        name="Elongated Tris",
        description="Highlight triangles with a high length-to-height aspect ratio",
        default=True,
        update=update_check,
    )
    elongated_aspect_ratio: FloatProperty(
        name="Elongated Aspect Ratio",
        description="Minimum aspect ratio threshold to flag a triangle as elongated",
        min=0.0, soft_max=100.0, default=45.0, subtype='FACTOR',
        update=update_check,
    )
    custom_count: BoolProperty(
        name="Custom",
        description="Highlight faces with a specific vertex count",
        default=False,
        update=update_check,
    )
    custom_count_verts: IntProperty(
        name="Number of Vertices in the Polygon",
        description="Target vertex count per face for custom highlight",
        min=3, default=5,
        update=update_check,
    )

    # --- группы панели
    panel_groups: EnumProperty(
        name='Groups',
        description='Switch between Tool Kit panel sections',
        items=[
            ('TRANSFORM', 'Transform', 'Reset and transfer object transforms', 'EMPTY_ARROWS', 0),
            ('DISPLAY', 'Display', 'Viewport display and retopology settings', 'RESTRICT_VIEW_OFF', 1),
        ],
        default='TRANSFORM',
    )


class PS_preferences(AddonPreferences):
    """Addon preferences for Poly Source"""
    bl_idname = __package__

    def update_select_wireframe(self, context):
        if not self.b_wire_for_selected:
            context.scene.show_wire_for_selected = False

    # =============================================
    # --- кнопки в хедере вьюпорта ---
    # =============================================
    b_color_randomizer: BoolProperty(
        name="Color Randomizer",
        description="Show color randomizer buttons in 3D Viewport header",
        default=True,
    )
    b_bool_tool: BoolProperty(
        name="Bool Tool",
        description="Show boolean operation buttons in 3D Viewport header",
        default=True,
    )
    b_camera_sync: BoolProperty(
        name="Camera Sync",
        description="Show camera lock and view controls in 3D Viewport header",
        default=False,
    )

    # =============================================
    # --- polycount: расположение и лимиты ---
    # =============================================
    b_count_header: BoolProperty(
        name="Polycount: Header",
        description="Display polygon counter in the top bar header",
        default=True,
    )
    b_count_view_header_l: BoolProperty(
        name="Polycount: Viewport Header Left",
        description="Display polygon counter in the left section of the viewport header",
        default=False,
    )
    b_count_view_header_r: BoolProperty(
        name="Polycount: Viewport Header Right",
        description="Display polygon counter in the right section of the viewport header",
        default=False,
    )
    b_count_tool_header: BoolProperty(
        name="Polycount: Tool Header",
        description="Display polygon counter in the tool header (may conflict with other addons)",
        default=False,
    )
    low_suffix: BoolProperty(
        name="_Low",
        description="Count polygons only in collections with _LOW suffix",
        default=False,
    )
    max_verts: IntProperty(
        name="Maximum Vertices In Active Object",
        description="Skip header polycount when selected objects exceed this vertex count",
        min=3, soft_max=200000, default=50000,
    )
    max_objs: IntProperty(
        name="Maximum Number of Selected Objects",
        description="Skip header polycount when the number of selected objects exceeds this limit",
        min=1, soft_max=500, default=50,
    )

    # =============================================
    # --- панели и инструменты ---
    # =============================================
    b_transform_plus: BoolProperty(
        name="Transform+",
        description="Show enhanced Transform panel in the sidebar with quick reset and copy buttons",
        default=False,
    )
    b_wire_for_selected: BoolProperty(
        name="Wireframe for Selected",
        description="Automatically display wireframe overlay on selected objects",
        default=False,
        update=update_select_wireframe,
    )
    b_presets_increment_angles: BoolProperty(
        name="Presets Increment Angles",
        description="Show angle presets in the snapping popover",
        default=True,
    )

    # =============================================
    # --- mesh check: размеры и цвета ---
    # =============================================
    point_width: FloatProperty(
        name="Point Size",
        description="Size of highlighted vertex points in the mesh check overlay",
        min=1.0, soft_max=30.0, default=15,
    )
    line_width: FloatProperty(
        name="Edge Width",
        description="Width of highlighted edge lines in the mesh check overlay",
        min=1.0, soft_max=30.0, default=5,
    )

    # --- вершины (points) ---
    v_alone_color: FloatVectorProperty(
        name="Isolated Vertex", subtype='COLOR',
        default=(1.0, 0.0, 0.0, 0.9), size=4, min=0.0, max=1.0,
        description="Highlight color for isolated vertices with no connected edges",
    )
    bound_col: FloatVectorProperty(
        name="Boundary", subtype='COLOR',
        default=(0.0, 0.8, 0.9, 0.9), size=4, min=0.0, max=1.0,
        description="Highlight color for vertices on open mesh boundaries",
    )
    n_pole_col: FloatVectorProperty(
        name="N-Pole (3 Edges)", subtype='COLOR',
        default=(1.0, 0.9, 0.0, 0.9), size=4, min=0.0, max=1.0,
        description="Highlight color for N-pole vertices connected to exactly 3 edges",
    )
    e_pole_col: FloatVectorProperty(
        name="E-Pole (5 Edges)", subtype='COLOR',
        default=(1.0, 0.5, 0.0, 0.9), size=4, min=0.0, max=1.0,
        description="Highlight color for E-pole vertices connected to exactly 5 edges",
    )
    f_pole_col: FloatVectorProperty(
        name=">5 Pole", subtype='COLOR',
        default=(1.0, 0.1, 0.55, 0.9), size=4, min=0.0, max=1.0,
        description="Highlight color for extraordinary pole vertices with more than 5 edges",
    )

    # --- рёбра (lines) ---
    non_manifold_color: FloatVectorProperty(
        name="Non-Manifold", subtype='COLOR',
        default=(1.0, 0.0, 0.0, 0.7), size=4, min=0.0, max=1.0,
        description="Highlight color for non-manifold edges",
    )
    elongated_tris_col: FloatVectorProperty(
        name="Elongated Tris", subtype='COLOR',
        default=(0.55, 0.1, 1.0, 0.7), size=4, min=0.0, max=1.0,
        description="Highlight color for edges of elongated triangles",
    )

    # --- грани (faces) ---
    tris_col: FloatVectorProperty(
        name="Triangles", subtype='COLOR',
        default=(0.2, 0.55, 1.0, 0.5), size=4, min=0.0, max=1.0,
        description="Highlight color for triangular faces",
    )
    ngone_col: FloatVectorProperty(
        name="N-Gons", subtype='COLOR',
        default=(0.85, 0.2, 0.25, 0.5), size=4, min=0.0, max=1.0,
        description="Highlight color for N-gon faces with more than 4 vertices",
    )
    custom_col: FloatVectorProperty(
        name="Custom", subtype='COLOR',
        default=(0.95, 0.65, 0.05, 0.5), size=4, min=0.0, max=1.0,
        description="Highlight color for faces matching the custom vertex count",
    )

    # =============================================
    # --- unit grid: цвета ---
    # =============================================
    color_grid: FloatVectorProperty(
        name="Grid Color", subtype='COLOR',
        default=(0.1, 0.1, 0.1, 0.9), size=4, min=0.0, max=1.0,
        description="Color of the unit grid lines",
    )
    color_box: FloatVectorProperty(
        name="Box Color", subtype='COLOR',
        default=(1.0, 0.03, 0.17, 0.1), size=4, min=0.0, max=1.0,
        description="Fill color of the bounding box volume",
    )

    # --- вкладки настроек
    tabs: EnumProperty(
        name="Tabs",
        description="Switch between preference tabs",
        items=[
            ("GENERAL", "General", "General addon settings"),
            ("KEYMAPS", "Keymaps", "Keyboard shortcut configuration"),
        ],
        default="GENERAL",
    )

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, 'tabs', expand=True)

        if self.tabs == 'GENERAL':
            self._draw_general(layout)
        elif self.tabs == 'KEYMAPS':
            self._draw_keymaps(context, layout)

    def _draw_general(self, layout):
        layout.use_property_split = True

        pcoll = preview_collections['main']

        # --- кнопки в хедере вьюпорта ---
        box = layout.box()

        row = box.row()
        row.label(text='Viewport Header', icon='WINDOW')
        col = box.column(align=True)
        col.prop(self, 'b_color_randomizer')
        col.prop(self, 'b_bool_tool')
        col.prop(self, 'b_camera_sync')

        # --- счётчик полигонов ---
        box = layout.box()
        row = box.row()
        row.label(text='Polycount', icon='MESH_ICOSPHERE')
        col = box.column(align=True)
        col.prop(self, 'b_count_header')
        col.prop(self, 'b_count_view_header_l')
        col.prop(self, 'b_count_view_header_r')
        col.prop(self, 'b_count_tool_header')
        box.separator(factor=0.5)
        box.label(text='Performance Limits:')
        col = box.column(align=True)
        col.prop(self, 'low_suffix')
        col.prop(self, "max_verts")
        col.prop(self, "max_objs")

        # --- панели и инструменты ---
        box = layout.box()
        row = box.row()
        row.label(text='Panels & Tools', icon='TOOL_SETTINGS')
        col = box.column(align=True)
        col.prop(self, 'b_transform_plus')
        col.prop(self, 'b_wire_for_selected')
        col.prop(self, 'b_presets_increment_angles')

        # --- mesh check: цвета и размеры ---
        box = layout.box()
        row = box.row()
        row.label(text='Mesh Check', icon='SHADING_WIRE')
        col = box.column(align=True)
        col.prop(self, "point_width")
        col.prop(self, "line_width")

        box.separator(factor=0.5)
        box.label(text='Vertex Colors:')
        col = box.column(align=True)
        col.prop(self, "v_alone_color")
        col.prop(self, "bound_col")
        col.prop(self, "n_pole_col")
        col.prop(self, "e_pole_col")
        col.prop(self, "f_pole_col")

        box.separator(factor=0.5)
        box.label(text='Edge Colors:')
        col = box.column(align=True)
        col.prop(self, "non_manifold_color")
        col.prop(self, "elongated_tris_col")

        box.separator(factor=0.5)
        box.label(text='Face Colors:')
        col = box.column(align=True)
        col.prop(self, "tris_col")
        col.prop(self, "ngone_col")
        col.prop(self, "custom_col")

        # --- unit grid: цвета ---
        box = layout.box()
        box.label(text='Unit Grid', icon='MESH_GRID')
        col = box.column(align=True)
        col.prop(self, "color_grid")
        col.prop(self, "color_box")

        # --- ссылки ---
        box = layout.box()
        row = box.row()
        row.label(text='Links', icon='URL')
        row = box.row()
        row.operator('wm.url_open', text='Blender Market', icon_value=pcoll['market_icon'].icon_id).url = "https://blendermarket.com/creators/derksen"
        row.operator('wm.url_open', text='Gumroad', icon_value=pcoll['gumroad_icon'].icon_id).url = "https://derksen.gumroad.com"
        row.operator('wm.url_open', text='Artstation', icon_value=pcoll['artstation_icon'].icon_id).url = "https://www.artstation.com/derksen"

    def _draw_keymaps(self, context, layout):
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
    PS_PG_settings,
    PS_preferences,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.poly_source = PointerProperty(type=PS_PG_settings)

    wm = bpy.context.window_manager
    addon_keyconfig = wm.keyconfigs.addon
    if not addon_keyconfig:
        return

    km = addon_keyconfig.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new('wm.call_panel', type='SPACE', value='PRESS')
    kmi.properties.name = 'PS_PT_tool_kit'
    addon_keymaps.append((km, kmi))


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.poly_source

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
