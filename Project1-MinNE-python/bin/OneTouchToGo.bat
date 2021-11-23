cd %~dp0
@REM --------------------------------------------------
start python ../src/app.py 1
@REM start python ../src/net.py 11300 11200 11100
@REM start ./phy.exe 1 PHY 0
@REM @REM --------------------------------------------------
@REM start python ../src/app.py 12300 12200
@REM start python ../src/net.py 12300 12200 12100
@REM start ./phy.exe 2 PHY 0
@REM @REM --------------------------------------------------
@REM start python ../src/switch.py 13200 13100 13101
@REM start ./phy.exe 3 PHY 0
@REM start ./phy.exe 3 PHY 1
@REM @REM --------------------------------------------------