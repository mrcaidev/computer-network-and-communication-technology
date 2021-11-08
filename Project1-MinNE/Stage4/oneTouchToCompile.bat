cd %~dp0
g++ src/app.cpp -o bin/app -lws2_32
g++ src/net.cpp -o bin/net -lws2_32
g++ src/switcher.cpp -o bin/switcher -lws2_32
g++ src/router.cpp -o bin/router -lws2_32