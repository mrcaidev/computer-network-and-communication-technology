@REM ------------------------------ cd to /bin
cd %~dp0
@REM ------------------------------ Host 1
start python ../src/app.py 1
start python ../src/net.py 1
start ./phy.exe 1 PHY 0
@REM ------------------------------ Host 2
start python ../src/app.py 2
start python ../src/net.py 2
start ./phy.exe 2 PHY 0
@REM ------------------------------ Switch 3
start python ../src/switch.py 3
start ./phy.exe 3 PHY 0
start ./phy.exe 3 PHY 1