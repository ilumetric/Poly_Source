"""Сборка zip-расширения официальным сборщиком Blender.

Универсальный скрипт (часть переносимого пакета ilumetric): не привязан к
конкретному аддону — всё берёт из blender_manifest.toml (имя, версия,
[build]-исключения). Корень аддона ищется вверх по дереву от расположения
скрипта до первого blender_manifest.toml, поэтому скрипт работает из
ilumetric/ на любой глубине и из корня аддона.

Путь к Blender (по приоритету):
  1. переменная окружения BLENDER_EXE;
  2. константа BLENDER_EXE_DEFAULT ниже;
  3. `blender` в PATH.
"""
import os
import re
import shutil
import sys
import datetime
import subprocess

# ============================================================================
#  ПУТЬ К BLENDER по умолчанию — замени после обновления/переустановки
#  (Blender Launcher держит exe в папке с версией+хэшем) либо задай
#  переменную окружения BLENDER_EXE, чтобы не трогать скрипт.
# ============================================================================
BLENDER_EXE_DEFAULT = r"E:\Software\Blender Launcher\stable\blender-5.1.2-stable.ec6e62d40fa9\blender.exe"
# ============================================================================

# Консоль Windows бывает в cp1252 — переключаем вывод на UTF-8, чтобы кириллица
# в сообщениях не роняла скрипт.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass


def _find_addon_root(start_dir):
    """Первая папка вверх от start_dir (включительно) с blender_manifest.toml."""
    d = start_dir
    while True:
        if os.path.isfile(os.path.join(d, "blender_manifest.toml")):
            return d
        parent = os.path.dirname(d)
        if parent == d:  # дошли до корня диска
            sys.exit(
                "Не найден blender_manifest.toml ни в одной папке вверх от:\n"
                f"  {start_dir}\n"
                "Скрипт должен лежать внутри дерева аддона-расширения."
            )
        d = parent


def _find_blender():
    """Путь к Blender: env BLENDER_EXE → константа → PATH."""
    env = os.environ.get("BLENDER_EXE")
    if env:
        if os.path.isfile(env):
            return env
        sys.exit(f"BLENDER_EXE указывает на несуществующий файл:\n  {env}")
    if os.path.isfile(BLENDER_EXE_DEFAULT):
        return BLENDER_EXE_DEFAULT
    found = shutil.which("blender")
    if found:
        return found
    sys.exit(
        "Blender не найден. Задай переменную окружения BLENDER_EXE,\n"
        "обнови BLENDER_EXE_DEFAULT в начале build_zip.py\n"
        "или добавь blender в PATH."
    )


BLENDER_EXE = _find_blender()

# --- Пути относительно расположения скрипта (не зависит от cwd) ---
script_dir = os.path.dirname(os.path.realpath(__file__))
addon_root = _find_addon_root(script_dir)
manifest_path = os.path.join(addon_root, "blender_manifest.toml")

# --- blender_manifest.toml — единственный источник правды ---
# Правки делаем через regex, чтобы сохранить комментарии и переводы строк.

def _read_manifest():
    with open(manifest_path, "r", encoding="utf-8", newline="") as f:
        return f.read()

def _write_manifest(content):
    with open(manifest_path, "w", encoding="utf-8", newline="") as f:
        f.write(content)

def get_manifest_field(key):
    content = _read_manifest()
    match = re.search(r'(?m)^%s\s*=\s*"([^"]*)"' % re.escape(key), content)
    if not match:
        raise ValueError(f"Не найдено поле '{key}' в blender_manifest.toml.")
    return match.group(1)

def set_manifest_version(new_version):
    """Записать поле `version` в манифест (не трогая schema_version / blender_version_min)."""
    content = _read_manifest()
    match = re.search(r'(?m)^(version\s*=\s*")([^"]*)(")', content)
    if not match:
        raise ValueError("Не найдено поле 'version' в blender_manifest.toml.")
    content = content[:match.start(2)] + new_version + content[match.end(2):]
    _write_manifest(content)

def bump_patch(version):
    parts = version.split(".")
    try:
        parts[-1] = str(int(parts[-1]) + 1)
    except ValueError:
        raise ValueError(f"Не удалось увеличить версию: {version!r}")
    return ".".join(parts)

def run_blender_extension(args):
    """Вызвать `blender --factory-startup --command extension <args>`.
    --factory-startup отключает пользовательские аддоны/настройки, чтобы их
    ошибки в фоновом режиме не засоряли вывод сборки."""
    cmd = [BLENDER_EXE, "--factory-startup", "--command", "extension"] + args
    return subprocess.run(cmd).returncode

# 1) Поднять patch-версию в манифесте (с возможностью отката при ошибке)
old_version = get_manifest_field("version")
version = bump_patch(old_version)
set_manifest_version(version)
print(f"Версия: {old_version} -> {version}")

def fail(message):
    """Откатить версию в манифесте и выйти с ошибкой."""
    set_manifest_version(old_version)
    sys.exit(f"{message}\nВерсия в манифесте возвращена на {old_version}.")

# 2) Имя архива (как раньше: Имя_версия_дата.zip) в родительской папке
addon_name = get_manifest_field("name").replace(" ", "_")
version_str = version.replace(".", "")                     # "5.2.11" -> "5211"
build_date = datetime.datetime.now().strftime("%d%m%y")    # ДДММГГ
zip_name = f"{addon_name}_{version_str}_{build_date}.zip"
parent_dir = os.path.dirname(addon_root)
zip_path = os.path.join(parent_dir, zip_name)

# 3) Сборка официальным сборщиком Blender (гарантированный формат расширения +
#    проверка манифеста). Исключения берутся из секции [build] манифеста.
print("\n=== extension build ===")
if run_blender_extension(["build", "--source-dir", addon_root, "--output-filepath", zip_path]) != 0:
    fail("Сборка не удалась.")

# 4) Валидация готового архива
print("\n=== extension validate ===")
if run_blender_extension(["validate", zip_path]) != 0:
    fail("Валидация не прошла.")

print(f"\nГотово. Архив расширения: {zip_path}")
