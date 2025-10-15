import bpy
from bpy.app.handlers import persistent
from .utils.utils import get_addon_prefs

# допустимые типы объектов для показа wire
ALLOWED_TYPES = {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT'}

# кэш выбранных объектов по сцене (scene pointer -> set(object names))
_prev_selected_by_scene = {}

# флаг регистрации таймера
_timer_running = False


# def _get_addon_prefs():
#     """возвращает настройки аддона или None"""
#     try:
#         return bpy.context.preferences.addons['Poly_Source'].preferences
#     except Exception:
#         return None


def _is_global_feature_enabled():
    """проверяет, включен ли функционал в настройках аддона"""
    prefs = get_addon_prefs()
    return bool(prefs and getattr(prefs, 'b_wire_for_selected', False))


def _is_scene_feature_enabled(scene):
    """проверяет, включен ли функционал на уровне сцены"""
    try:
        return bool(getattr(scene, 'show_wire_for_selected', False))
    except Exception:
        return False


def update_objects_wireframe(scene, enable_wire):
    """обновляет состояние wireframe для всех объектов сцены"""
    for obj in scene.objects:
        if obj.type in ALLOWED_TYPES:
            if enable_wire:
                # включаем только для выбранных
                try:
                    obj.show_wire = obj.select_get()
                except Exception:
                    obj.show_wire = False
            else:
                obj.show_wire = False


def _get_selected_names_for_scene(scene):
    """возвращает множество имён выбранных объектов для указанной сцены (объединение по всем окнам этой сцены)"""
    result = set()
    wm = getattr(bpy.context, 'window_manager', None)
    if wm is None:
        return result
    try:
        for window in wm.windows:
            if window.scene != scene:
                continue
            try:
                for obj in window.view_layer.objects.selected:
                    result.add(obj.name)
            except Exception:
                # на случай недоступного view_layer
                pass
    except Exception:
        pass
    return result


def _update_selection_wires_for_scene(scene, current_selected_names):
    """включает wire для новых выбранных и выключает для снятых, без полного обхода сцены"""
    scene_id = scene.as_pointer()
    prev_names = _prev_selected_by_scene.get(scene_id, set())

    to_enable = current_selected_names - prev_names
    to_disable = prev_names - current_selected_names

    # применяем только к тем, кто реально существует и допустимого типа
    for name in to_enable:
        obj = scene.objects.get(name)
        if obj and obj.type in ALLOWED_TYPES:
            obj.show_wire = True

    for name in to_disable:
        obj = scene.objects.get(name)
        if obj and obj.type in ALLOWED_TYPES:
            obj.show_wire = False

    # сохраняем актуальное состояние
    valid_now = set()
    for name in current_selected_names:
        obj = scene.objects.get(name)
        if obj and obj.type in ALLOWED_TYPES:
            valid_now.add(name)
    _prev_selected_by_scene[scene_id] = valid_now


def _clear_cached_scene_state(scene):
    """очищает кэш выбора по сцене и выключает wire только у тех, кто был отмечен ранее"""
    scene_id = scene.as_pointer()
    prev_names = _prev_selected_by_scene.get(scene_id)
    if prev_names:
        for name in list(prev_names):
            obj = scene.objects.get(name)
            if obj and obj.type in ALLOWED_TYPES:
                obj.show_wire = False
        _prev_selected_by_scene[scene_id] = set()


def on_wire_setting_changed(self, context):
    """обработчик изменения настройки wireframe на сцене"""
    scene = context.scene
    if getattr(scene, 'show_wire_for_selected', False):
        # включили — синхронизируем сразу целиком для корректного старта
        update_objects_wireframe(scene, True)
        # и обновляем кэш выбора
        _prev_selected_by_scene[scene.as_pointer()] = _get_selected_names_for_scene(scene)
    else:
        # выключили — погасим и очистим кэш
        update_objects_wireframe(scene, False)
        _clear_cached_scene_state(scene)


def overlay(self, context):
    """добавляет настройку в панель оверлея"""
    props = get_addon_prefs()
    if props and getattr(props, 'b_wire_for_selected', False):
        self.layout.prop(context.scene, "show_wire_for_selected", text="Display Wireframe for Selected")


def _wire_timer():
    """таймер для стабильного отслеживания изменения выбора объектов"""
    try:
        # если глобально выключено — выключим всё, что было включено ранее, и поддержим таймер живым
        if not _is_global_feature_enabled():
            try:
                for scene in _iterate_window_scenes():
                    _clear_cached_scene_state(scene)
            except Exception:
                pass
            return 0.5

        wm = getattr(bpy.context, 'window_manager', None)
        if wm is None:
            return 0.5

        # собираем уникальные сцены из открытых окон
        seen_scene_ids = set()
        for window in wm.windows:
            scene = window.scene
            if scene is None:
                continue
            scene_id = scene.as_pointer()
            if scene_id in seen_scene_ids:
                continue
            seen_scene_ids.add(scene_id)

            # если сценовый флаг выключен — очищаем только ранее отмеченных и пропускаем
            if not _is_scene_feature_enabled(scene):
                _clear_cached_scene_state(scene)
                continue

            # актуальные выбранные имена (объединение по окнам этой сцены)
            current_selected_names = _get_selected_names_for_scene(scene)
            _update_selection_wires_for_scene(scene, current_selected_names)

        # частота опроса
        return 0.2
    except Exception:
        # если что-то пошло не так — не роняем таймер
        return 0.5


@persistent
def _on_load_post(dummy):
    """после загрузки файла синхронизируем состояние для всех сцен, показанных в окнах"""
    try:
        wm = getattr(bpy.context, 'window_manager', None)
        if wm is None:
            return
        for window in wm.windows:
            scene = window.scene
            if scene is None:
                continue
            # сбрасываем кэш на случай другой сцены/файла
            _clear_cached_scene_state(scene)
            if _is_global_feature_enabled() and _is_scene_feature_enabled(scene):
                update_objects_wireframe(scene, True)
                _prev_selected_by_scene[scene.as_pointer()] = _get_selected_names_for_scene(scene)
    except Exception:
        pass


def _ensure_timer_running():
    """запускает таймер, если он ещё не запущен"""
    global _timer_running
    if not _timer_running:
        try:
            bpy.app.timers.register(_wire_timer, first_interval=0.2)
            _timer_running = True
        except Exception:
            _timer_running = False


def _stop_timer():
    """останавливает таймер, если он запущен"""
    global _timer_running
    if _timer_running:
        try:
            bpy.app.timers.unregister(_wire_timer)
        except Exception:
            pass
        _timer_running = False


def _iterate_window_scenes():
    """даёт уникальные сцены, открытые в окнах"""
    wm = getattr(bpy.context, 'window_manager', None)
    if wm is None:
        return []
    result = []
    seen = set()
    try:
        for window in wm.windows:
            scene = window.scene
            if scene is None:
                continue
            sid = scene.as_pointer()
            if sid in seen:
                continue
            seen.add(sid)
            result.append(scene)
    except Exception:
        pass
    return result


def register():
    """регистрирует функционал"""
    # регистрируем свойство сцены с обработчиком изменения
    if not hasattr(bpy.types.Scene, 'show_wire_for_selected'):
        bpy.types.Scene.show_wire_for_selected = bpy.props.BoolProperty(
            name="Wireframe for Selected",
            description=(
                "Display wireframe only for selected objects.\n"
                "Warning: When enabled, manually toggling an object's wireframe display will not work."
            ),
            default=False,
            update=on_wire_setting_changed,
        )

    # UI — избегаем дублирования
    try:
        bpy.types.VIEW3D_PT_overlay.remove(overlay)
    except Exception:
        pass
    bpy.types.VIEW3D_PT_overlay.append(overlay)

    # обработчики
    if _on_load_post not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_on_load_post)

    # таймер
    _ensure_timer_running()


def unregister():
    """отменяет регистрацию функционала"""
    # таймер
    _stop_timer()

    # обработчики
    try:
        if _on_load_post in bpy.app.handlers.load_post:
            bpy.app.handlers.load_post.remove(_on_load_post)
    except Exception:
        pass

    # вырубим wire во всех открытых сценах
    try:
        for scene in _iterate_window_scenes():
            update_objects_wireframe(scene, False)
            _clear_cached_scene_state(scene)
    except Exception:
        pass

    # свойство сцены
    try:
        if hasattr(bpy.types.Scene, "show_wire_for_selected"):
            del bpy.types.Scene.show_wire_for_selected
    except Exception:
        pass

    # UI
    try:
        bpy.types.VIEW3D_PT_overlay.remove(overlay)
    except Exception:
        pass
