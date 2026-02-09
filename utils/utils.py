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
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    return space
    return None


def get_hotkey_entry_item(km, kmi_name, kmi_value, properties):
    # поиск элемента хоткея по имени и свойствам
    for i, km_item in enumerate(km.keymap_items):
        if km.keymap_items.keys()[i] == kmi_name:
            if properties == 'name':
                if km.keymap_items[i].properties.name == kmi_value:
                    return km_item
            elif properties == 'tab':
                if km.keymap_items[i].properties.tab == kmi_value:
                    return km_item
            elif properties == 'none':
                return km_item
    return None
