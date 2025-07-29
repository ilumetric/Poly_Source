import zipfile
import os
import re
import datetime
import glob

# --- Новый код: функция для инкремента версии ---
def increment_version_in_init():
    init_path = "__init__.py"
    with open(init_path, "r", encoding="utf-8") as f:
        content = f.read()
    # Найти строку с версией
    version_match = re.search(r"('version':\s*\()(.*?)(\))", content, re.DOTALL)
    if not version_match:
        raise ValueError("Не найдена версия в bl_info.")
    version_tuple = version_match.group(2)
    # Разбить на элементы, убрать пробелы
    parts = [x.strip() for x in version_tuple.split(",")]
    # Инкрементировать последнюю цифру
    try:
        last = int(parts[-1]) + 1
        parts[-1] = str(last)
    except Exception as e:
        raise ValueError(f"Ошибка при увеличении версии: {e}")
    new_version = ", ".join(parts)
    new_content = (content[:version_match.start(2)] + new_version + content[version_match.end(2):])
    with open(init_path, "w", encoding="utf-8") as f:
        f.write(new_content)

# --- Вызов функции до получения версии ---
increment_version_in_init()

def get_version_parts():
    with open("__init__.py", "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r"['\"]version['\"]\s*:\s*\((.*?)\)", content)
    if match:
        parts = [x.strip().strip("'\"") for x in match.group(1).split(",")]
        return tuple(parts)
    raise ValueError("Не найдена версия в bl_info.")

def get_addon_name():
    with open("__init__.py", "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r"'name':\s*'([^']+)'", content)
    if match:
        return match.group(1).replace(' ', '_')
    raise ValueError("Не найдено имя аддона в bl_info.")

version_parts = get_version_parts()
# Заменяем греческую букву стадии на латинскую для имени архива
stage_letter_map = {'α': 'a', 'β': 'b', 'γ': 'g', 'δ': 'd'}
if len(version_parts) >= 5:
    stage_letter = stage_letter_map.get(version_parts[3], version_parts[3])
    version_str = f"{version_parts[0]}{version_parts[1]}{version_parts[2]}{stage_letter}{version_parts[4]}"
elif len(version_parts) == 4:
    stage_letter = stage_letter_map.get(version_parts[3], version_parts[3])
    version_str = f"{version_parts[0]}{version_parts[1]}{version_parts[2]}{stage_letter}"
else:
    version_str = f"{version_parts[0]}{version_parts[1]}{version_parts[2]}"

addon_name = get_addon_name()

# Формат даты: ДДММГГ
build_date = datetime.datetime.now().strftime("%d%m%y")

zip_name = f"{addon_name}_{version_str}_{build_date}.zip"

exclude = [
    ".git", ".vscode", "__pycache__",
    ".mypy_cache", zip_name, "build_zip.py",
    ".gitattributes", ".gitignore", ".pylintrc",
    "pyproject.toml",
    ]

project_dir = os.path.basename(os.getcwd())
parent_dir = os.path.dirname(os.getcwd())
zip_path = os.path.join(parent_dir, zip_name)

def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in exclude]
        for file in files:
            if file not in exclude:
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, path)
                ziph.write(full_path, os.path.join(project_dir, relative_path))

with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    zipdir(".", zipf)

print(f"Создан архив: {zip_path}")
