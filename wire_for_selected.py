import bpy
from bpy.app.handlers import persistent
from .utils.utils import get_addon_prefs

# допустимые типы объектов для показа wire
ALLOWED_TYPES = {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT'}

# кэш выбранных объектов по сцене (scene pointer -> set(object names))
_prev_selected_by_scene = {}


def _global_enabled():
    """включен ли функционал в настройках аддона"""
    prefs = get_addon_prefs()
    return bool(prefs is not None and prefs.b_wire_for_selected)


def _feature_enabled(scene):
    """включен ли функционал глобально и на уровне сцены"""
    return _global_enabled() and bool(getattr(scene, 'show_wire_for_selected', False))


def _windows():
    wms = bpy.data.window_managers
    return wms[0].windows if wms else ()


def _selected_names(scene):
    """имена выбранных объектов сцены (объединение по всем окнам этой сцены)"""
    result = set()
    for window in _windows():
        if window.scene is scene:
            result.update(obj.name for obj in window.view_layer.objects.selected)
    return result


def _sync_scene(scene, enable):
    """полная синхронизация wireframe для всех объектов сцены"""
    if enable:
        selected = _selected_names(scene)
        for obj in scene.objects:
            if obj.type in ALLOWED_TYPES:
                obj.show_wire = obj.name in selected
        _prev_selected_by_scene[scene.as_pointer()] = selected
    else:
        for obj in scene.objects:
            if obj.type in ALLOWED_TYPES:
                obj.show_wire = False
        _prev_selected_by_scene.pop(scene.as_pointer(), None)


def _clear_cached_scene_state(scene):
    """выключает wire только у тех объектов, что были отмечены ранее"""
    prev_names = _prev_selected_by_scene.pop(scene.as_pointer(), None)
    if not prev_names:
        return
    for name in prev_names:
        obj = scene.objects.get(name)
        if obj is not None and obj.type in ALLOWED_TYPES:
            obj.show_wire = False


def on_wire_setting_changed(self, context):
    """обработчик изменения настройки wireframe на сцене"""
    scene = context.scene
    _sync_scene(scene, _feature_enabled(scene))


def overlay(self, context):
    """добавляет настройку в панель оверлея"""
    if _global_enabled():
        self.layout.prop(context.scene, "show_wire_for_selected", text="Display Wireframe for Selected")


@persistent
def _on_depsgraph_update(scene, depsgraph):
    """событийное отслеживание изменения выбора объектов"""
    if not _feature_enabled(scene):
        # функционал выключили в настройках — гасим ранее отмеченные объекты
        if _prev_selected_by_scene.get(scene.as_pointer()):
            _clear_cached_scene_state(scene)
        return

    current = _selected_names(scene)
    prev = _prev_selected_by_scene.get(scene.as_pointer(), set())
    if current == prev:
        # запись show_wire сама по себе триггерит depsgraph update —
        # ранний выход разрывает цикл
        return

    for name in current - prev:
        obj = scene.objects.get(name)
        if obj is not None and obj.type in ALLOWED_TYPES:
            obj.show_wire = True

    for name in prev - current:
        obj = scene.objects.get(name)
        if obj is not None and obj.type in ALLOWED_TYPES:
            obj.show_wire = False

    _prev_selected_by_scene[scene.as_pointer()] = current


@persistent
def _on_load_post(dummy):
    """после загрузки файла синхронизируем состояние для сцен, показанных в окнах"""
    _prev_selected_by_scene.clear()
    for window in _windows():
        scene = window.scene
        if scene is not None and _feature_enabled(scene):
            _sync_scene(scene, True)


def register():
    bpy.types.Scene.show_wire_for_selected = bpy.props.BoolProperty(
        name="Wireframe for Selected",
        description=(
            "Display wireframe only for selected objects.\n"
            "Warning: When enabled, manually toggling an object's wireframe display will not work."
        ),
        default=False,
        update=on_wire_setting_changed,
    )

    bpy.types.VIEW3D_PT_overlay.append(overlay)

    if _on_load_post not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_on_load_post)
    if _on_depsgraph_update not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(_on_depsgraph_update)


def unregister():
    if _on_depsgraph_update in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(_on_depsgraph_update)
    if _on_load_post in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_on_load_post)

    # гасим wire во всех открытых сценах
    seen = set()
    for window in _windows():
        scene = window.scene
        if scene is not None and scene.as_pointer() not in seen:
            seen.add(scene.as_pointer())
            _sync_scene(scene, False)
    _prev_selected_by_scene.clear()

    bpy.types.VIEW3D_PT_overlay.remove(overlay)

    del bpy.types.Scene.show_wire_for_selected
