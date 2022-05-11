
# Goon Parser

## Installation
#### Using Pip
    pip install goon_parser

#### Using Poetry
    poetry add goon_parser


## Usage
##### Parser
    from goon_parser.parser import get_dict, get_json

    chemistry_recipes_dict = get_dict('./Chemistry_Recipes.dm')
    chemistry_recipes_json = get_json('./Chemistry_Recipes.dm')

