# Wichtige Befehle

## make venv

- python -m venv venv

## freeze requirements.txt

- pip freeze > requirments.txt

## install requirements.txt

- pip install -r requirements.txt



# Build pyinstaller unter MAC




# Build pyinstaller unter Windows

pyinstaller --onefile --windowed --icon=icons/LukeWare_icon.ico app.py -n "D&S ParGenerator"

pyinstaller ".\D&S ParGenerator.spec"
