# Counting Names
A GUI-based program to search a PDF for all nouns (words that start with a capitalized letter) and the pages they occur on.  
The result will be saved to a given file.  

### Install
```bash
pip install .
count_names_ui
```
Consider using a venv!
### Development
use `pip install -e .` to install the package in edit mode.

### Building an executable for windows
It's highly recommended to use a venv for that!
```bash
python3 -m pip install -r requirements_exe.txt
pyinstaller .\src\count_names\__init__.py --onefile --name word-counter.exe
```
The executable `word-counter.exe` will be located in `.\dist\`.  
You can copy it freely everywhere. It will still work!  
