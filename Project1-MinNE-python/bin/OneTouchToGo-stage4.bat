@REM ------------------------------ cd to /bin
cd %~dp0
@REM ------------------------------ Router 1
start python ../src/router.py 1
@REM start ./phy.exe 1 PHY 0
@REM start ./phy.exe 1 PHY 1
@REM start ./phy.exe 1 PHY 2
@REM @REM ------------------------------ Router 2
@REM start python ../src/router.py 2
@REM start ./phy.exe 2 PHY 0
@REM start ./phy.exe 2 PHY 1
@REM start ./phy.exe 2 PHY 2
@REM @REM ------------------------------ Router 3
@REM start python ../src/router.py 3
@REM start ./phy.exe 3 PHY 0
@REM start ./phy.exe 3 PHY 1
@REM start ./phy.exe 3 PHY 2
@REM @REM ------------------------------ Host 4
@REM start python ../src/app.py 4
@REM start python ../src/net.py 4
@REM start ./phy.exe 4 PHY 0
@REM @REM ------------------------------ Switch 5
@REM start python ../src/switch.py 5
@REM start ./phy.exe 5 PHY 0
@REM start ./phy.exe 5 PHY 1
@REM @REM ------------------------------ Host 7
@REM start python ../src/app.py 7
@REM start python ../src/net.py 7
@REM start ./phy.exe 7 PHY 0