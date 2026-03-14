from pathlib import Path

root = Path(".")  # или Path(".") если запускаешь из корня проекта

IGNORE = {
    ".venv", "__pycache__", "dist", "build", ".git", ".idea", ".vscode",
    "node_modules", "*.egg-info", ".pytest_cache", "*.pyc", "*.pyo",
    "*.log", "*.json", "*.db"
}

def should_ignore(p: Path) -> bool:
    name = p.name.lower()
    for pattern in IGNORE:
        if pattern.startswith("*"):
            if name.endswith(pattern[1:]):
                return True
        elif name == pattern:
            return True
    return False

def print_tree_md(path: Path, prefix="", level=0, max_level=3):
    if level > max_level:
        return

    try:
        items = [p for p in path.iterdir() if not should_ignore(p)]
    except PermissionError:
        return

    items.sort(key=lambda p: (p.is_file(), p.name.lower()))

    for i, item in enumerate(items):
        is_last = i == len(items) - 1
        item_prefix = "└── " if is_last else "├── "
        print(f"{prefix}{item_prefix}{item.name}")

        if item.is_dir():
            new_prefix = prefix + ("    " if is_last else "│   ")
            print_tree_md(item, new_prefix, level + 1, max_level)


if __name__ == "__main__":
    print("```text")
    print_tree_md(root)
    print("```")