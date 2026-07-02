import bpy
import blf
import bmesh
from bpy.types import Gizmo, GizmoGroup
from .utils.utils import get_addon_prefs


_FONT_ID = 0
_LABEL_COLOR = (0.58, 0.72, 0.0)
_VALUE_COLOR = (0.9, 0.9, 0.9)


def _draw_text(x, y, text, color):
    blf.position(_FONT_ID, x, y, 0)
    blf.size(_FONT_ID, 14)
    blf.color(_FONT_ID, color[0], color[1], color[2], 1.0)
    blf.enable(_FONT_ID, blf.SHADOW)
    blf.shadow(_FONT_ID, 3, 0.0, 0.0, 0.0, 1.0)
    blf.draw(_FONT_ID, text)


def polycount(self, context):
    """отрисовка счётчика полигонов в вьюпорте"""
    if context.active_object is None:
        return

    props = get_addon_prefs()
    if not props:
        return
    settings = context.scene.poly_source

    _draw_text(10, 45, "Polycount: " + str(settings.tris_count) + "/", _LABEL_COLOR)

    # подсчёт треугольников сцены
    if not props.low_suffix:
        viewlayer = context.view_layer
        try:
            stats = context.scene.statistics(viewlayer)
            # ищем секцию с треугольниками по ключу "Tris" (или берём последний элемент)
            tris = 0
            for part in stats.split(" | "):
                stripped = part.strip()
                if stripped.startswith("Tris"):
                    tris_str = stripped.split(":")[-1].strip().replace(',', '').replace(' ', '')
                    tris = int(tris_str)
                    break
            else:
                # если "Tris" не найден, берём число из последнего элемента
                last = stats.split(" | ")[-1]
                if ":" in last:
                    tris_str = last.split(":")[-1].strip().replace(',', '').replace(' ', '')
                    tris = int(tris_str)
        except (ValueError, IndexError, AttributeError):
            tris = 0
    else:
        tris = 0
        for collection in bpy.data.collections:
            name = collection.name
            if name.endswith("_low") or name.endswith("_Low") or name.endswith("_LOW"):
                for obj in collection.objects:
                    if obj.type == 'MESH':
                        if obj.mode == 'EDIT':
                            bm = bmesh.from_edit_mesh(obj.data)
                            tris += sum(len(f.verts) - 2 for f in bm.faces)
                        else:
                            tris += sum(len(f.vertices) - 2 for f in obj.data.polygons)

    # цвет на основе коэффициента
    coef = settings.tris_count / tris if tris > 0 else 1
    if coef < 1:
        col = (1.0, 0.1, 0.0)
    elif 1.2 > coef > 1:
        col = (1.0, 0.5, 0.0)
    else:
        col = _VALUE_COLOR

    value_x = 110 + len(str(settings.tris_count)) * 6

    # количество треугольников сцены
    _draw_text(value_x, 45, str(tris), col)

    # подсчёт треугольников активного объекта
    active_tris = 0
    for obj in context.objects_in_mode_unique_data:
        if obj.type == 'MESH':
            if obj.mode == 'EDIT':
                bm = bmesh.from_edit_mesh(obj.data)
                active_tris += sum(len(f.verts) - 2 for f in bm.faces)
            else:
                active_tris += sum(len(f.vertices) - 2 for f in obj.data.polygons)

    _draw_text(10, 30, "Active Object: ", _LABEL_COLOR)
    _draw_text(value_x, 30, str(active_tris), _VALUE_COLOR)


class PS_GT_polycount(Gizmo):
    """Polycount overlay gizmo"""
    bl_idname = 'PS_GT_polycount'

    def draw(self, context):
        polycount(self, context)


class PS_GGT_polycount_group(GizmoGroup):
    """Polycount overlay gizmo group"""
    bl_idname = 'PS_GGT_polycount_group'
    bl_label = 'Poly Count'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'SHOW_MODAL_ALL'}

    @classmethod
    def poll(cls, context):
        if context.active_object is not None:
            settings = context.scene.poly_source
            return settings.show_polycount
        return False

    def setup(self, context):
        mesh = self.gizmos.new('PS_GT_polycount')
        mesh.use_draw_modal = True
        self.mesh = mesh

    def draw_prepare(self, context):
        settings = context.scene.poly_source
        self.mesh.hide = not settings.show_polycount


classes = [
    PS_GT_polycount,
    PS_GGT_polycount_group,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
