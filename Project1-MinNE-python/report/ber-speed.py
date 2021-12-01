import re

import matplotlib.pyplot as plt
import numpy as np
from numpy.core.fromnumeric import mean

plt.style.use(["fast"])

ber = np.linspace(0, 1, 11)

with open("log/1.log", "r", encoding="utf-8") as fr:
    send_speed = np.array(
        [float(speed) for speed in re.findall(r": (.*?)bps", fr.read())]
    )
    send_speed = [mean(send_speed[i : i + 3]) for i in range(0, len(send_speed), 3)]

with open("log/2.log", "r", encoding="utf-8") as fr:
    recv_speed = np.array(
        [float(speed) for speed in re.findall(r": (.*?)bps", fr.read())]
    )
    recv_speed = [mean(recv_speed[i : i + 3]) for i in range(0, len(recv_speed), 3)]

plt.title("BER's Impact on Throughput")
plt.xlabel("Bit Error Rate (%)")
plt.ylabel("Speed (bps)")
plt.xlim(0, 1)
plt.ylim(0, 5000)
plt.plot(ber, send_speed, label="Send")
plt.plot(ber, recv_speed, label="Receive")

plt.grid()
plt.legend()
plt.show()
