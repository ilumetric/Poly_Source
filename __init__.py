# метаданные аддона хранятся в blender_manifest.toml
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
    edge_decal,
)

from .utils import (
    ops,
    fill_mesh,
    cylinder_optimizer,
)

# порядок важен: иконки и операторы нужны UI, preferences — всем остальным
_modules = (
    icons,
    ops,
    preferences,
    camera_sync,
    ui,
    check,
    color_randomizer,
    polycount,
    envira_grid,
    wire_for_selected,
    edge_decal,
    fill_mesh,
    cylinder_optimizer,
)


def register():
    for module in _modules:
        module.register()


def unregister():
    for module in reversed(_modules):
        module.unregister()
