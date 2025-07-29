import bpy
from bpy.app.handlers import persistent

# Глобальная переменная для отслеживания предыдущего состояния свойства
prev_show_wire_for_selected = None

def is_wire_enabled():
    """Проверяет, включен ли функционал wireframe в настройках и сцене"""
    try:
        # Проверяем настройки аддона
        if not bpy.context.preferences.addons[__package__].preferences.b_wire_for_selected:
            return False
        # Проверяем настройки сцены
        if not bpy.context.scene.show_wire_for_selected:
            return False
        return True
    except (AttributeError, KeyError):
        return False

def is_valid_context():
    """Проверяет, находится ли контекст в правильном состоянии для работы с wireframe"""
    try:
        # Проверяем режим
        if bpy.context.mode != 'OBJECT':
            return False
            
        # Проверяем тип пространства
        if not bpy.context.space_data or bpy.context.space_data.type != 'VIEW_3D':
            return False
            
        # Проверяем наличие необходимых атрибутов
        if not hasattr(bpy.context.space_data, 'overlay') or not hasattr(bpy.context.space_data.overlay, 'show_wireframes'):
            return False
            
        # Проверяем глобальное отображение wireframes
        if bpy.context.space_data.overlay.show_wireframes:
            return False
            
        return True
    except (AttributeError, KeyError):
        return False

def update_objects_wireframe(scene, enable_wire):
    """Обновляет состояние wireframe для всех объектов"""
    for obj in scene.objects:
        if obj.type in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT'}:
            if enable_wire:
                obj.show_wire = obj.select_get()
            else:
                obj.show_wire = False

@persistent
def update_wire_display(scene):
    global prev_show_wire_for_selected
    
    # Проверяем, включен ли функционал
    if not is_wire_enabled():
        # Если функционал выключен, но был включен ранее - выключаем wireframe
        if prev_show_wire_for_selected:
            update_objects_wireframe(scene, False)
            prev_show_wire_for_selected = False
        return

    # Проверяем контекст
    if not is_valid_context():
        return

    # Обновляем состояние wireframe
    update_objects_wireframe(scene, True)
    prev_show_wire_for_selected = True

def on_wire_setting_changed(self, context):
    """Обработчик изменения настройки wireframe"""
    scene = context.scene
    if scene.show_wire_for_selected:
        # Если включили, сразу обновляем состояние
        update_objects_wireframe(scene, True)
    else:
        # Если выключили, выключаем wireframe
        update_objects_wireframe(scene, False)

def overlay(self, context):
    """Добавляет настройку в панель оверлея"""
    props = context.preferences.addons[__package__].preferences
    if props.b_wire_for_selected:
        self.layout.prop(context.scene, "show_wire_for_selected", text="Display Wireframe for Selected")

def register():
    """Регистрирует функционал"""
    global prev_show_wire_for_selected
    prev_show_wire_for_selected = False

    # Регистрируем свойство сцены с обработчиком изменения
    bpy.types.Scene.show_wire_for_selected = bpy.props.BoolProperty(
        name="Wireframe for Selected",
        description=(
            "Display wireframe only for selected objects.\n"
            "Warning: When enabled, manually toggling an object's wireframe display will not work."
        ),
        default=False,
        update=on_wire_setting_changed
    )
    
    # Добавляем хендлер и UI
    bpy.app.handlers.depsgraph_update_post.append(update_wire_display)
    bpy.types.VIEW3D_PT_overlay.append(overlay)

def unregister():
    """Отменяет регистрацию функционала"""
    # Удаляем хендлер
    if update_wire_display in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(update_wire_display)
    
    # Выключаем wireframe у всех объектов
    if bpy.context.scene:
        update_objects_wireframe(bpy.context.scene, False)
    
    # Удаляем свойство сцены
    if hasattr(bpy.types.Scene, "show_wire_for_selected"):
        del bpy.types.Scene.show_wire_for_selected
    
    # Удаляем UI
    if hasattr(bpy.types.VIEW3D_PT_overlay, "draw"):
        bpy.types.VIEW3D_PT_overlay.remove(overlay)
