cd %~dp0bin
@REM --------------------------------------------------
start "Host 1 Phy" "./phy" 1 PHY 0
start "Host 2 Phy" "./phy" 2 PHY 0
start "Host 3 Phy" "./phy" 4 PHY 0
start "Host 4 Phy" "./phy" 5 PHY 0
start "Switcher 1 Phy to router" "./phy" 3 PHY 0
start "Switcher 1 Phy to host 1" "./phy" 3 PHY 1
start "Switcher 1 Phy to host 2" "./phy" 3 PHY 2
start "Switcher 2 Phy to router" "./phy" 6 PHY 0
start "Switcher 2 Phy to host 3" "./phy" 6 PHY 1
start "Switcher 2 Phy to host 4" "./phy" 6 PHY 2
start "Router Phy to switcher 1" "./phy" 7 PHY 0
start "Router Phy to switcher 2" "./phy" 7 PHY 1
@REM --------------------------------------------------
start "Host 1 Net" "./net" 11300 11200 11100
start "Host 2 Net" "./net" 12300 12200 12100
start "Host 3 Net" "./net" 14300 14200 14100
start "Host 4 Net" "./net" 15300 15200 15100
start "Switcher 1 Net" "./switcher" 13200 13102 13100 13101
start "Switcher 2 Net" "./switcher" 16200 16102 16100 16101
start "Router Net" "./router" 17200 17100 17101
@REM --------------------------------------------------
start "Host 1 App" "./app" 11300 11200
start "Host 2 App" "./app" 12300 12200
start "Host 3 App" "./app" 14300 14200
start "Host 4 App" "./app" 15300 15200