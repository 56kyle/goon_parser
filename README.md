
# Goon Parser

## Installation
#### Using Pip
    pip install goon_parser

#### Using Poetry
    poetry add goon_parser


## Usage
##### CLI
    - Poetry
    poetry run generate json './path/to/file.dm' './path/to/output.json'
    poetry run generate json -r './path/to/folder' './path/to/output/folder'
    
    - Flags
    -r / --recursive = Will iterate through all files in the given folder and all sub folders
    -f / --force = Will overwrite any files that are written if they exist already
    

##### Parser
    from goon_parser.parser import get_dict, get_json

    chemistry_recipes_dict = get_dict('./Chemistry_Recipes.dm')
    chemistry_recipes_json = get_json('./Chemistry_Recipes.dm')

