import click
import os

from parser import get_json, get_python
from typing import Callable
from util import mkdir


@click.group(chain=True)
@click.argument('source', type=click.Path(exists=True, file_okay=True, dir_okay=True))
@click.argument('dest', type=click.Path(dir_okay=True))
@click.option('--force', '-f', is_flag=True, help='Force overwrite of existing files.', default=False)
@click.option('--recursive', '-r', is_flag=True, help='Recursively generate files.', default=False)
@click.pass_context
def generate():
    pass


@generate.command('json')
@click.argument('source', type=click.Path(exists=True, file_okay=True, dir_okay=True))
@click.argument('dest', type=click.Path(dir_okay=True))
@click.option('--force', '-f', is_flag=True, help='Force overwrite of existing files.', default=False)
@click.option('--recursive', '-r', is_flag=True, help='Recursively generate files.', default=False)
def generate_json(source: str, dest: str, force: bool, recursive: bool):
    print('generate_json')
    _generate(
        source=source,
        dest=dest,
        force=force,
        recursive=recursive,
        method=get_json,
        ending='.json'
    )

@generate.command('python')
def generate_python(source: str, dest: str, force: bool, recursive: bool):
    print('generate_python')
    _generate(
        source=source,
        dest=dest,
        force=force,
        recursive=recursive,
        method=get_python,
        ending='.py',
    )

def _generate(source: str, dest: str, force: bool, recursive: bool, method: Callable[[str], str], ending: str):
    print('_generate')
    source = os.path.abspath(source)
    dest = os.path.abspath(dest)
    if os.path.isfile(source):
        _generate_file(
            source=source,
            dest=dest,
            force=force,
            method=method,
            ending=ending,
        )
    elif os.path.isdir(source):
        _generate_folder(
            source=source,
            dest=dest,
            force=force,
            recursive=recursive,
            method=method,
            ending=ending,
        )
    else:
        raise click.BadArgumentUsage('Source must be a file or directory.')

def _generate_file(source: str, dest: str, force: bool, method: Callable[[str], str], ending: str):
    print('_generate_file')
    if not source.endswith('.dm'):
        raise click.BadArgumentUsage('Source file must be a .dm file.')
    dest = os.path.splitext(dest)[0] + ending

    if force or not os.path.exists(dest):
        folder = os.path.dirname(dest)
        if not os.path.exists(folder):
            mkdir(folder)
        with open(dest, 'w') as file:
            file.write(method(source))
    elif os.path.exists(dest):
        raise click.BadArgumentUsage('Destination file already exists.')


def _generate_folder(source: str, dest: str, force: bool, recursive: bool, method: Callable[[str], str], ending: str):
    print('_generate_folder')
    source = os.path.abspath(source)
    if recursive:
        for source_root, dirs, files in os.walk(source):
            dest_root = source_root.replace(source, dest)
            mkdir(dest_root)
            for directory in dirs:
                mkdir(os.path.join(dest_root, directory))
            for file in files:
                _generate_file(
                    source=os.path.join(source_root, file),
                    dest=os.path.join(dest_root, file),
                    force=force,
                    method=method,
                    ending=ending,
                )
    else:
        for file in os.listdir(source):
            _generate_file(
                source=os.path.join(source, file),
                dest=os.path.join(dest, file),
                force=force,
                method=method,
                ending=ending,
            )


generate = click.CommandCollection(sources=[generate])
