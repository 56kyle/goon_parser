
import pytest

from goon_parser.parser import remove_functions, remove_inline_comments, remove_multiline_comments

with open('data/chemistry/Chemistry-Recipes.dm', 'r') as f:
    recipes = f.readlines()

with open('data/chemistry/Chemistry-Reactions.dm', 'r') as f:
    reactions = f.readlines()

def test_remove_functions():
    assert not remove_functions(reactions)
    assert remove_functions(recipes)

def test_remove_comments():
    lines = remove_inline_comments(reactions)
    lines = remove_multiline_comments(lines)
    for line in lines:
        assert line



