cd %~dp0
@REM --------------------------------------------------
start python ../src/app.py 11300 11200
start python ../src/net.py 11300 11200 11100
start python ../src/app.py 12300 12200
start python ../src/net.py 12300 12200 12100
start python ../src/switch.py 13200 13100 13101
start ./phy.exe 1 PHY 0
start ./phy.exe 2 PHY 0
start ./phy.exe 3 PHY 0
start ./phy.exe 3 PHY 1