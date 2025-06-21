import sys

from cx_Freeze import setup

gui_name: str = 'GUITEConverter'
console_name: str = 'CConverter'

build_exe_options = {
    'excludes': ['tkinter', ],
    'zip_include_packages': ['encodings', 'collections', 'importlib', 'wx'],
    'include_files': ['Data', 'README.md'],
    'build_exe': 'build_app',
}

if sys.platform.startswith('win'):
    gui_name = 'GUITEConverter.exe'
    console_name = 'CConverter.exe'
    build_exe_options['include_msvcr'] = True

setup(
    name='TEConverter',
    version='0.1',
    description='TEConverter',
    options={'build_exe': build_exe_options},
    executables=[{'script': 'gui_converter.py', 'base': 'gui', 'target_name': gui_name},
                 {'script': 'console_converter.py', 'base': 'console', 'target_name': console_name},
                 ],
)