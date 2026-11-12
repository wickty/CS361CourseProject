"""Run: python -m unittest discover -s tests -v"""
import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from main import main
from recipe_store import load_recipes, add_recipe, delete_recipe, save_recipes


class MealPlannerTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.path = Path(self.folder.name) / 'recipes.json'

    def tearDown(self):
        self.folder.cleanup()

    def run_ui(self, answers):
        output = io.StringIO()
        with patch('builtins.input', side_effect=answers), contextlib.redirect_stdout(output):
            exit_code = main(self.path)
        self.assertEqual(exit_code, 0)
        return output.getvalue()

    def test_save_and_reload(self):
        recipe = {'name': 'Eggs', 'servings': 2, 'ingredients': [{'amount': 4.0, 'unit': 'each', 'name': 'eggs'}], 'steps': ['Mix', 'Cook']}
        save_recipes(self.path, add_recipe([], recipe))
        self.assertEqual(load_recipes(self.path), [recipe])

    def test_delete_does_not_change_original_list(self):
        entries = [{'name': 'A'}, {'name': 'B'}]
        self.assertEqual(delete_recipe(entries, 0), [{'name': 'B'}])
        self.assertEqual(len(entries), 2)

    def test_add_view_delete_persist(self):
        output = self.run_ui([
            '1', 'Eggs', '2', '4', 'each', 'eggs', 'n', 'Mix eggs', 'n', 'y',
            '2', '1', '', '3', '1', 'n', '3', '1', 'y', '0'
        ])
        self.assertIn('RECIPE SAVED: Eggs', output)
        self.assertIn('Ingredients:', output)
        self.assertIn('Deletion canceled. Recipe was kept.', output)
        self.assertIn('RECIPE DELETED: Eggs', output)
        self.assertEqual(load_recipes(self.path), [])

    def test_invalid_numbers_retry(self):
        output = self.run_ui([
            '1', 'Pasta', '-2', 'oops', '2', '0', '1',
            '1', 'cup', 'pasta', 'n', 'Boil', 'n', 'y', '0'
        ])
        self.assertGreaterEqual(output.count('Invalid input. Please enter a positive'), 3)
        self.assertEqual(load_recipes(self.path)[0]['servings'], 2)

    def test_cancel_without_saving(self):
        output = self.run_ui(['1', 'Toast', 'cancel', '0'])
        self.assertIn('Nothing was saved.', output)
        self.assertEqual(load_recipes(self.path), [])

    def test_empty_list_alternate_add(self):
        output = self.run_ui(['2', '1', 'Toast', '1', '1', 'slice', 'bread', 'n', 'Toast it', 'n', 'y', '0'])
        self.assertIn('another way to start adding', output)
        self.assertEqual(load_recipes(self.path)[0]['name'], 'Toast')

    def test_invalid_menu_does_not_crash(self):
        self.assertIn('Invalid option', self.run_ui(['xyz', '', '0']))

    def test_cancel_delete_keeps_recipe(self):
        save_recipes(self.path, [{'name': 'Toast'}])
        self.assertIn('Recipe was kept', self.run_ui(['3', '1', 'n', '0']))
        self.assertEqual(len(load_recipes(self.path)), 1)


if __name__ == '__main__':
    unittest.main()
