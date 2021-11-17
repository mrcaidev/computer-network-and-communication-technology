cd %~dp0
@REM --------------------------------------------------
start python app.py 11300 11200
start python net.py 11300 11200 12200
start python app.py 12300 12200
start python net.py 12300 12200 11200