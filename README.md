# CS361 Meal Planner – Milestone #1

A small text-based recipe manager written in Python. Users can **add, view, and delete recipes**. Data is saved locally in `recipes.json` between runs. This is a standalone Main Program.

## Run

1. Install Python 3.9 or newer.
2. Open a terminal in the folder containing `main.py`.
3. Run:
   ```sh
   python main.py
   ```
   On Windows, `py main.py` may work if `python` is not recognized.
4. Use the numbered menu. Type `cancel` at any Add Recipe prompt to return without saving. Choose `0` on numbered lists to go back.

## Features

- **Add Recipe:** Name, positive whole-number servings, at least one ingredient (positive amount, unit, name), and at least one step. Invalid numbers are rejected and re-requested. Users confirm before saving.
- **View Recipes:** Shows a numbered list, followed by the selected recipe's ingredients and numbered steps. An empty list offers an alternate route to Add Recipe.
- **Delete Recipe:** Shows a numbered list and a permanent-deletion warning. Users must type `y` to delete; `n` keeps the recipe.
- **Help:** Explains the order of steps, navigation, storage, and costs.

## Quality attributes

- **Reliability:** Saved recipes survive restart; invalid numeric input is re-prompted without crashing. `recipe_store.py` writes to a temporary file before replacing the data file.
- **Usability:** Numbered menus, clear `Ingredients`/`Steps` headings, Help, and return/cancel prompts.
- **Modifiability:** Storage operations are in `recipe_store.py` without any `input()`/`print()`, separate from the UI in `main.py`.

## Run automated tests

```sh
python -m unittest discover -s tests -v
```

Tests use temporary files, so your actual `recipes.json` is not touched.

## Files

- `main.py`: command-line interface and input validation.
- `recipe_store.py`: recipe storage and list operations.
- `tests/test_meal_planner.py`: automated tests.
- `.gitignore`: prevents local recipe data from being committed.

## Privacy

Recipes stay in a local `recipes.json` file and are not sent over the internet. No accounts, passwords, or API keys are required.
