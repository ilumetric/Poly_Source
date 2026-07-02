import bpy

# корневой пакет аддона (для совместимости с системой расширений Blender 5)
_addon_package = __package__.rsplit(".", 1)[0]


def get_addon_prefs():
    # безопасно возвращает preferences аддона или None
    try:
        return bpy.context.preferences.addons[_addon_package].preferences
    except Exception:
        return None


def get_active_3d_view():
    # возвращает активный 3D вьюпорт или None
    screen = getattr(bpy.context, 'screen', None)
    if screen is None:
        return None
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    return space
    return None
