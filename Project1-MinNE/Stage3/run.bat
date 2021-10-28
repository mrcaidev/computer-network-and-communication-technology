cd %~dp0bin
@REM --------------------------------------------------
start "Host 1 Phy" "./phy" 1 PHY 0
start "Host 2 Phy" "./phy" 2 PHY 0
start "Switch 1 Phy to host 1" "./phy" 3 PHY 0
start "Switch 1 Phy to host 2" "./phy" 3 PHY 1
@REM --------------------------------------------------
start "Host 1 Net" "./net" 11300 11200 11100
start "Host 2 Net" "./net" 12300 12200 12100
start "Switch 1 Net" "./switch" 13200 13100 13101
@REM --------------------------------------------------
start "Host 1 App" "./app" 11300 11200
start "Host 2 App" "./app" 12300 12200