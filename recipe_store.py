"""Local JSON storage for the meal planner (no terminal input/output)."""

import json
import os
from pathlib import Path


class RecipeStorageError(Exception):
    """Raised when recipe data cannot safely be read or written."""


def load_recipes(path):
    path = Path(path)
    if not path.exists():
        return []
    try:
        with path.open('r', encoding='utf-8') as file:
            recipes = json.load(file)
        if not isinstance(recipes, list) or not all(isinstance(r, dict) for r in recipes):
            raise ValueError('Recipe data must be a list of recipe objects.')
        return recipes
    except (OSError, ValueError, TypeError) as exc:
        raise RecipeStorageError(f'Could not read saved recipes: {exc}') from exc


def save_recipes(path, recipes):
    path = Path(path)
    temporary = path.with_name(path.name + '.tmp')
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with temporary.open('w', encoding='utf-8') as file:
            json.dump(recipes, file, indent=2, ensure_ascii=False)
        os.replace(temporary, path)
    except (OSError, TypeError, ValueError) as exc:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
        raise RecipeStorageError(f'Could not save recipes: {exc}') from exc


def add_recipe(recipes, recipe):
    return [*recipes, recipe]


def delete_recipe(recipes, index):
    """Return a new list without the 0-based selected recipe."""
    if not (0 <= index < len(recipes)):
        raise IndexError('Recipe number is out of range')
    return recipes[:index] + recipes[index + 1:]
