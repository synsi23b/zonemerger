# zonemerger

1. copy the environment file `cp env .env`
2. edit the file `nano .env`
3. install requirements `pip3 install -r requirements.txt` (maybe use a venv, but im running ina container so whatever)
4. running will take forever, so run in a byobu or screen session
5. launch `python3 main.py`

logs can be found in the log folder, errors and crashes are not caught. Problems with ffmpeg halt the exectution
