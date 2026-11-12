"""CS361 Milestone #1: small command-line recipe manager."""

from pathlib import Path
from recipe_store import (
    RecipeStorageError, add_recipe, delete_recipe, load_recipes, save_recipes
)

DATA_FILE = Path(__file__).resolve().parent / 'recipes.json'
CANCEL = 'cancel'


def ask(prompt, allow_empty=False):
    """Read text; 'cancel' backs out of the current task."""
    while True:
        value = input(prompt).strip()
        if value.lower() == CANCEL:
            return None
        if value or allow_empty:
            return value
        print('Please enter something, or type cancel to go back.')


def positive_number(prompt, whole=False):
    while True:
        text = ask(prompt)
        if text is None:
            return None
        try:
            number = int(text) if whole else float(text)
            if number <= 0 or (not whole and number != number):
                raise ValueError
            return number
        except ValueError:
            kind = 'whole number' if whole else 'number'
            print(f'Invalid input. Please enter a positive {kind}.')


def yes_no(prompt):
    while True:
        answer = ask(prompt)
        if answer is None:
            return None
        if answer.lower() in ('y', 'n'):
            return answer.lower() == 'y'
        print('Please type y for yes or n for no (or cancel to go back).')


def choose_recipe(recipes, heading):
    if not recipes:
        return None
    while True:
        print(f'\n{heading}')
        for number, recipe in enumerate(recipes, 1):
            print(f'{number}. {recipe["name"]}')
        print('0. Main menu')
        answer = input('Choose a recipe number: ').strip()
        if answer in ('0', 'cancel'):
            return None
        if answer.isdigit() and 1 <= int(answer) <= len(recipes):
            return int(answer) - 1
        print('Invalid selection. Choose one of the numbers shown.')


def gather_entries(kind, name, build):
    """Collect at least one ingredient or step, with cancellation."""
    entries = []
    while True:
        entry = build(len(entries) + 1)
        if entry is None:
            return None
        entries.append(entry)
        more = yes_no(f'Add another {kind}? (y/n): ')
        if more is None:
            return None
        if not more:
            return entries


def new_ingredient(number):
    amount = positive_number(f'Ingredient {number} amount: ')
    if amount is None:
        return None
    unit = ask('Unit (for example, cups or each): ')
    if unit is None:
        return None
    ingredient_name = ask('Ingredient name: ')
    if ingredient_name is None:
        return None
    return {'amount': amount, 'unit': unit, 'name': ingredient_name}


def new_step(number):
    return ask(f'Step {number}: ')


def add_recipe_screen(recipes, path):
    print('\nADD RECIPE')
    print('Steps: name, servings, ingredients, directions, then save.')
    print("Type 'cancel' at any prompt to leave without saving.")
    name = ask('Recipe name: ')
    if name is None:
        print('Add recipe canceled. Nothing was saved.')
        return recipes
    servings = positive_number('Servings: ', whole=True)
    if servings is None:
        print('Add recipe canceled. Nothing was saved.')
        return recipes
    ingredients = gather_entries('ingredient', name, new_ingredient)
    if ingredients is None:
        print('Add recipe canceled. Nothing was saved.')
        return recipes
    steps = gather_entries('step', name, new_step)
    if steps is None:
        print('Add recipe canceled. Nothing was saved.')
        return recipes
    confirm = yes_no(f'Save {name}? (y/n): ')
    if not confirm:
        print('Add recipe canceled. Nothing was saved.')
        return recipes
    updated = add_recipe(recipes, {
        'name': name, 'servings': servings,
        'ingredients': ingredients, 'steps': steps
    })
    save_recipes(path, updated)
    print(f'RECIPE SAVED: {name} was saved successfully.')
    return updated


def show_details(recipe):
    print(f'\n{recipe["name"].upper()}')
    print(f'Servings: {recipe["servings"]}')
    print('Ingredients:')
    for ingredient in recipe['ingredients']:
        print(f' - {ingredient["amount"]:g} {ingredient["unit"]} {ingredient["name"]}')
    print('Steps:')
    for index, step in enumerate(recipe['steps'], 1):
        print(f' {index}. {step}')
    input('Press Enter to return to the main menu...')


def view_recipes_screen(recipes, path):
    if not recipes:
        print('\nSAVED RECIPES')
        print('You have no saved recipes yet. Add a recipe first to see it here.')
        print('1. Add recipe here (another way to start adding)')
        print('0. Main menu')
        while True:
            answer = input('Choose an option: ').strip()
            if answer == '1':
                return add_recipe_screen(recipes, path)
            if answer in ('0', 'cancel'):
                return recipes
            print('Please choose 1 or 0.')
    chosen = choose_recipe(recipes, 'SAVED RECIPES')
    if chosen is not None:
        show_details(recipes[chosen])
    return recipes


def delete_recipe_screen(recipes, path):
    if not recipes:
        print('\nNo recipes to delete. Add a recipe first.')
        return recipes
    chosen = choose_recipe(recipes, 'DELETE RECIPE')
    if chosen is None:
        print('Deletion canceled. No recipes were changed.')
        return recipes
    name = recipes[chosen]['name']
    print(f'\nDELETE {name.upper()}?')
    print('This permanently removes the saved recipe.')
    print('This cannot be undone after confirmation.')
    print('Type n (or cancel) to keep it.')
    confirm = yes_no('Confirm (y/n): ')
    if not confirm:
        print('Deletion canceled. Recipe was kept.')
        return recipes
    updated = delete_recipe(recipes, chosen)
    save_recipes(path, updated)
    print(f'RECIPE DELETED: {name} was deleted.')
    return updated


def show_help():
    print('\nHELP')
    print('1. Add: enter a name, servings, ingredients, and directions; then save.')
    print('2. View: choose a number to read a recipe.')
    print('3. Delete: choose a number and confirm before removing it.')
    print("Type 'cancel' to stop entering a recipe without saving it.")
    print('Choose 0 in numbered lists to return to the main menu.')
    print('Your recipes are saved locally on this computer in recipes.json.')
    print('The program is free; entering a recipe takes some time.')
    print('Deleted recipes cannot be recovered after you confirm deletion.')
    input('Press Enter to return to the main menu...')


def main(path=DATA_FILE):
    try:
        recipes = load_recipes(path)
    except RecipeStorageError as exc:
        print(f'ERROR: {exc}')
        print('Your existing data was not changed. Correct the file and restart.')
        return 1
    while True:
        print('\nMEAL PLANNER')
        print('Store your recipes in one place.')
        print('Free to use. Recipes are saved on this computer.')
        print('1. Add recipe')
        print('2. View recipes')
        print('3. Delete recipe')
        print('4. Help')
        print('0. Exit')
        choice = input('Choose an option: ').strip()
        try:
            if choice == '1':
                recipes = add_recipe_screen(recipes, path)
            elif choice == '2':
                recipes = view_recipes_screen(recipes, path)
            elif choice == '3':
                recipes = delete_recipe_screen(recipes, path)
            elif choice == '4':
                show_help()
            elif choice == '0':
                print('Goodbye!')
                return 0
            else:
                print('Invalid option. Choose 0, 1, 2, 3, or 4.')
        except RecipeStorageError as exc:
            print(f'ERROR: {exc}')
            print('Change was not saved. Your existing data was not overwritten.')
        except (EOFError, KeyboardInterrupt):
            print('\nGoodbye!')
            return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (EOFError, KeyboardInterrupt):
        print('\nGoodbye!')
