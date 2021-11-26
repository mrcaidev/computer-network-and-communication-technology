@REM ------------------------------ cd to /config
cd %~dp0
@REM ------------------------------ Router 1
start python ../src/router.py 1
start ../bin/phy.exe 1 PHY 0
start ../bin/phy.exe 1 PHY 1
start ../bin/phy.exe 1 PHY 2
@REM ------------------------------ Router 2
start python ../src/router.py 2
start ../bin/phy.exe 2 PHY 0
start ../bin/phy.exe 2 PHY 1
start ../bin/phy.exe 2 PHY 2
@REM ------------------------------ Router 3
start python ../src/router.py 3
start ../bin/phy.exe 3 PHY 0
start ../bin/phy.exe 3 PHY 1
start ../bin/phy.exe 3 PHY 2
@REM ------------------------------ Host 4
start python ../src/app.py 4
start python ../src/net.py 4
start ../bin/phy.exe 4 PHY 0
@REM ------------------------------ Switch 5
start python ../src/switch.py 5
start ../bin/phy.exe 5 PHY 0
start ../bin/phy.exe 5 PHY 1
@REM ------------------------------ Host 7
start python ../src/app.py 7
start python ../src/net.py 7
start ../bin/phy.exe 7 PHY 0