cd %~dp0
g++ src/app.cpp -o bin/app -lws2_32
g++ src/net.cpp -o bin/net -lws2_32
g++ src/switch.cpp -o bin/switch -lws2_32