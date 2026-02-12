# legacy bl_info для совместимости с Blender Development (VSCode/Cursor)
# основные метаданные хранятся в blender_manifest.toml
bl_info = {
    'name': 'Poly Source',
    'author': 'Max Derksen',
    'version': (5, 2, 0),
    'blender': (5, 0, 0),
    'location': 'VIEW 3D > Top Bar',
    'category': '3D View',
}

from . import (
    icons,
    preferences,
    camera_sync,
    ui,
    check,
    color_randomizer,
    polycount,
    envira_grid,
    wire_for_selected,
)

from .utils import (
    ops,
    fill_mesh,
    cylinder_optimizer,
)


def register():
    # базовые модули (иконки, операторы, настройки)
    icons.register()
    ops.register()
    preferences.register()

    # UI и визуализация
    camera_sync.register()
    ui.register()
    check.register()
    color_randomizer.register()
    polycount.register()
    envira_grid.register()
    wire_for_selected.register()

    # утилиты
    fill_mesh.register()
    cylinder_optimizer.register()


def unregister():
    # утилиты
    cylinder_optimizer.unregister()
    fill_mesh.unregister()

    # UI и визуализация
    wire_for_selected.unregister()
    envira_grid.unregister()
    polycount.unregister()
    color_randomizer.unregister()
    check.unregister()
    ui.unregister()
    camera_sync.unregister()

    # базовые модули (в обратном порядке)
    preferences.unregister()
    ops.unregister()
    icons.unregister()
