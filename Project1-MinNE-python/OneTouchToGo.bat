cd %~dp0
@REM --------------------------------------------------
start python app.py 11300 11200
start python net.py 11300 11200 11100
start python app.py 12300 12200
start python net.py 12300 12200 12100
start phy 1 PHY 0
start phy 2 PHY 0