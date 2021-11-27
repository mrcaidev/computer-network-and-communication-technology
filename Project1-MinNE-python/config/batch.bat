@REM ------------------------------ cd to /config
cd %~dp0
@REM ------------------------------ Host 1
start python ../src/app.py 1
start python ../src/net.py 1
start ../bin/phy.exe 1 PHY 0
@REM ------------------------------ Host 2
start python ../src/app.py 2
start python ../src/net.py 2
start ../bin/phy.exe 2 PHY 0