import json
import os
import re

from typing import List, Dict

from goon_parser.logger import log


# General parser utility functions
# ================================================================

def is_attribute(line: str) -> bool:
    if '(' in line:
        result = ' = ' in line.split('(')[0]
    else:
        result = ' = ' in line and ')' not in line
    return result

def is_function(line: str) -> bool:
    result = '(' in line and not is_attribute(line)
    return result

def is_definition(line: str) -> bool:
    result = line.startswith('#define')
    return result

def is_undefinition(line: str) -> bool:
    return line.startswith('#undef')

def is_empty(line: str) -> bool:
    return re.match(r'^\s*$', line) is not None

def is_directory(line: str) -> bool:
    other_options = [
        is_function,
        is_attribute,
        is_definition,
        is_undefinition,
        is_empty,
    ]
    for option in other_options:
        if option(line):
            return False
    return True

def get_tabs(line: str) -> int:
    return line.count('\t')


# Main parser functions
# ================================================================

def remove_functions(lines: List[str]) -> List[str]:
    in_function = False
    tabs = 0
    new_lines = []
    for line in lines:
        if (is_attribute(line) or is_directory(line)) and get_tabs(line) <= tabs and in_function:
            log.debug('function end - ', line)
            in_function = False
        if is_function(line) and not in_function:
            log.debug('function start - ', line)
            in_function = True
            tabs = get_tabs(line)
        if not in_function:
            new_lines.append(line)
    return new_lines

def remove_inline_comments(lines: List[str]) -> List[str]:
    log.debug('remove_inline_comments')
    return [re.sub(r' ?//.*', '', line) for line in lines]

def remove_multiline_comments(lines: List[str]) -> List[str]:
    log.debug('remove_multiline_comments')
    text = 'REMOVE_ME'.join(lines)
    amt = text.count('/*')
    while amt > 0:
        text, amt = re.subn(r'/\*[^*]+\*/', '', text)
    return text.split('REMOVE_ME')

def combine_split_lines(lines: List[str]) -> List[str]:
    log.debug('combine_split_lines')
    new_lines = []
    for line in lines:
        try:
            if new_lines[-1].endswith('\\\n'):
                new_lines[-1] = new_lines[-1].rstrip('\\\n') + line.lstrip()
            else:
                new_lines.append(line)
        except IndexError:
            new_lines.append(line)
    return new_lines

def combine_multiline_strings(lines: List[str]) -> List[str]:
    log.debug('combine_multiline_strings')
    new_lines = []
    in_multi = False
    for i, line in enumerate(lines):
        if is_attribute(line) and '{"' in line:
            in_multi = True
            new_lines.append(line.replace('{"', '"').rstrip('\n'))
        elif '"}' in line and in_multi:
            in_multi = False
            new_lines[-1] += (line.replace('"}', '"').lstrip('\t').lstrip('\n'))
        elif in_multi:
            new_lines[-1] += (line.strip('\t').strip('\n'))
        else:
            new_lines.append(line)
    return new_lines

def replace_single_quotes(lines: List[str]) -> List[str]:
    log.debug('replace_single_quotes')
    new_lines = []
    for line in lines:
        if '\'' in line and '"' not in line:
            new_lines.append(line.replace('\'', '"'))
        else:
            new_lines.append(line)
    return new_lines

def remove_empty_lines(lines: List[str]) -> List[str]:
    log.debug('remove_empty_lines')
    return [line for line in lines if not is_empty(line)]

def remove_definitions(lines: List[str]) -> List[str]:
    log.debug('remove_definitions')
    new_lines = []
    for line in lines:
        if not is_definition(line):
            new_lines.append(line)
    return new_lines

def get_key(line: str) -> str:
    if is_attribute(line):
        return line.split(' = ')[0].replace('\t', '').replace('\n', '')
    elif is_directory(line):
        log.debug(f'directory - {line}')
        return line.replace('\t', '').replace('\n', '')
    else:
        raise ValueError(f'Invalid line: {line}')

def fix_tabs(lines: List[str]) -> List[str]:
    log.debug('fix_tabs')
    new_lines = []
    for line in lines:
        if is_attribute(line):
            try:
                sections = line.split(' = ')
                before_equals = sections[0]
                after_equals = ' = '.join(sections[1:])
            except ValueError as e:
                print(line)
                raise e
            before_equals = before_equals.replace('    ', '\t').replace(' ', '')
            new_lines.append(f'{before_equals} = {after_equals}')
        elif is_directory(line):
            new_lines.append(line.replace('    ', '\t').replace(' ', ''))
        else:
            new_lines.append(line)
    return new_lines

def condense_directories(lines: List[str]) -> List[str]:
    log.debug('condense_directories')
    new_lines = lines
    current_directory = ''
    current_tabs = 0

    while ('\t' * current_tabs) in '\n'.join(new_lines):
        for i, line in enumerate(new_lines):
            if line.count('\t') == current_tabs:
                if is_directory(line):
                    current_directory = get_key(line)
            elif line.count('\t') == current_tabs + 1:
                if is_attribute(line) or is_directory(line):
                    line_key = get_key(line)
                    key_path = os.path.split(line_key)
                    while '/' in key_path[0] or '\\' in key_path[0]:
                        key_path = [*os.path.split(key_path[0]), *key_path[1:]]
                        if key_path[0] == '/' or key_path[0] == '\\':
                            key_path = [*key_path[1:]]
                            break
                    new_lines[i] = line.replace(line_key, os.path.join(current_directory, *key_path), 1)
                else:
                    raise ValueError(f'Invalid line: {line}')
        current_tabs += 1
    return new_lines

def remove_directories(lines: List[str]) -> List[str]:
    log.debug('remove_directories')
    new_lines = []
    for line in lines:
        if not is_directory(line):
            new_lines.append(line)
    return new_lines

def remove_tabs(lines: List[str]) -> List[str]:
    log.debug('remove_tabs')
    return [line.replace('\t', '') for line in lines]

def fix_lists(lines: List[str]) -> List[str]:
    log.debug('fix_lists')
    new_lines = []
    for line in lines:
        new_lines.append(re.subn(r'list\((.*)\)', fix_list_contents, line)[0])
        if 'werewolf' in line:
            log.debug(f'line: {line}')
            log.debug(f'new_lines[-1]: {new_lines[-1]}')
    return new_lines

def fix_list_contents(match: re.Match) -> str:
    contents = match.group(1)
    contents = contents.strip(' ')
    if not contents.endswith(','):
        contents = contents + ','
    new_contents = re.sub(r'("(?: ?= ?\S+?)?,)"', r'\1 "', contents)  # Fixes missing spaces after commas
    kv_pairs = re.findall(r'"[^"]+"(?: ?= ?\S+)?,', new_contents)
    for pair in kv_pairs:
        if not pair.endswith(',') and ',' in pair:
            raise ValueError(f'Invalid list: {contents}')
    needs_dict = False
    for kv in kv_pairs:
        if re.match(r'".*" ?= ?.*', kv):
            needs_dict = True
    if needs_dict:
        new_pairs = {}
        for kv in kv_pairs:
            kv_match = re.match(r'(".*")(?: ?= ?([^,]*))?', kv)
            key = kv_match.group(1).strip('"')
            value = kv_match.group(2)
            if value:
                value = value.strip('"')
                try:
                    value = int(value)
                except ValueError:
                    pass
            new_pairs[key] = value
        return str(new_pairs)
    else:
        results = str([kv.strip(',').strip('"') for kv in kv_pairs])
        return results

def remove_undef(lines: List[str]) -> List[str]:
    log.debug('remove_undef')
    new_lines = []
    for line in lines:
        if not is_undefinition(line):
            new_lines.append(line)
    return new_lines

def fix_constants(lines: List[str]) -> List[str]:
    log.debug('fix_constants')
    new_lines = []
    for line in lines:
        match = re.match(r'.* = (.*)', line)
        value = match.group(1)
        if '"' not in value and '{' not in value and '[' not in value:
            try:
                value = int(value)
                new_lines.append(line)
            except ValueError:
                value = f'"{value}"'
                new_lines.append(line.replace(match.group(1), value))
        else:
            new_lines.append(line)
    return new_lines

def fix_new_lists(lines: List[str]) -> List[str]:
    log.debug('fix_new_lists')
    return [line.replace('new/[]', '[]') for line in lines]

def get_value(line: str) -> str:
    value = ' = '.join(line.split(' = ')[1:])
    return value.replace('\t', '').replace('\n', '').strip('"').strip('\'')

def make_dict(lines: List[str]) -> Dict[str, any]:
    log.debug('make_dict')
    base_dict = {}
    for i, line in enumerate(lines):
        key = get_key(line)
        value = get_value(line)
        if '"' in key:
            key = key.replace('"', '')
        key_segments = [key]
        while '/' in key_segments[0] or '\\' in key_segments[0]:
            if key_segments[0] == '/' or key_segments[0] == '\\':
                key_segments = [*key_segments[1:]]
                break
            key_segments = [*os.path.split(key_segments[0]), *key_segments[1:]]
        if value.startswith('{') or value.startswith('['):
            try:
                value = eval(value)
            except SyntaxError:
                log.warning(f'\tvalue - {value}')
                log.warning(f'\tline - {line}')
        elif value == 'null':
            value = None
        merge_dict = {key_segments[-1]: value}
        for segment in reversed(key_segments[:-1]):
            merge_dict = {segment: merge_dict}
        base_dict = merge(base_dict, merge_dict)
    for k, v in base_dict.items():
        if '"' in k:
            print(f'\t{k} = {v}')
    return base_dict

def merge(a, b, path=None, update=True):
    """Merges b into a"""
    path = [] if path is None else path
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass # same leaf value
            #elif isinstance(a[key], list) and isinstance(b[key], list):
                #for idx, val in enumerate(b[key]):
                    #a[key][idx] = merge(a[key][idx], b[key][idx], path + [str(key), str(idx)], update=update)
            elif update:
                a[key] = b[key]
            else:
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            try:
                a[key] = b[key]
            except Exception as e:
                print('a[key] = b[key]')
                print(f'a = {a}')
                print(f'b = {b}')
                print(f'key = {key}')
                raise e
    return a

def parse(lines: List[str]) -> List[str]:
    log.debug('parse')
    changes = [
        remove_inline_comments,
        remove_multiline_comments,
        combine_split_lines,
        combine_multiline_strings,
        remove_functions,
        replace_single_quotes,
        remove_empty_lines,
        remove_definitions,
        fix_tabs,
        condense_directories,
        remove_directories,
        remove_tabs,
        fix_lists,
        remove_undef,
        fix_constants,
        fix_new_lists,
    ]
    for change in changes:
        lines = change(lines)
    return lines


def get_dict(file_path: str) -> Dict[str, any]:
    with open(file_path, 'r', encoding='utf8') as f:
        lines = f.readlines()
        lines = parse(lines)
        return make_dict(lines)

def get_json(file_path: str, indent: int = 4) -> str:
    log.debug(f'get_json - {file_path}')
    """Returns a ss13 dm file as a json string"""
    try:
        return json.dumps(get_dict(file_path), indent=indent)
    except json.decoder.JSONDecodeError:
        return ''

def get_python(file_path: str) -> str:
    log.debug('get_python')
    """Returns a ss13 dm file as a python string"""
    return str(get_dict(file_path))


if __name__ == '__main__':
    with open('../data/current/chemistry/tools/food_and_drink.dm', 'r') as file:
        lines = file.readlines()
        lines = parse(lines)
        as_dict = make_dict(lines)
        json.dump(as_dict, open('test.json', 'w'), indent=4)







