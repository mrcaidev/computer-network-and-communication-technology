import re

import matplotlib.pyplot as plt
import numpy as np
from numpy.core.fromnumeric import mean

plt.style.use(["fast"])

ber = np.linspace(0, 1, 11)

send_speed_uni = [
    1299.8999999999999,
    1025.2666666666667,
    645.2666666666668,
    653.5666666666666,
    893.1333333333333,
    777.5,
    381.0,
    476.63333333333327,
    372.5333333333333,
    418.9666666666667,
    310.06666666666666,
]
recv_speed_uni = [
    1510.2333333333336,
    1163.2333333333333,
    1141.9666666666667,
    1062.2,
    1084.3666666666668,
    869.4666666666667,
    414.93333333333334,
    603.8333333333333,
    428.06666666666666,
    502.2333333333333,
    354.1333333333334,
]

with open("log/1.log", "r", encoding="utf-8") as fr:
    send_speed_bro = np.array(
        [float(speed) for speed in re.findall(r": (.*?)bps", fr.read())]
    )
    send_speed_bro = [
        mean(send_speed_bro[i : i + 3]) for i in range(0, len(send_speed_bro), 3)
    ]
    print(send_speed_bro)

with open("log/2.log", "r", encoding="utf-8") as fr:
    recv_speed_bro = np.array(
        [float(speed) for speed in re.findall(r": (.*?)bps", fr.read())]
    )
    recv_speed_bro = [
        mean(recv_speed_bro[i : i + 3]) for i in range(0, len(recv_speed_bro), 3)
    ]
    print(recv_speed_bro)

fig, axes = plt.subplots(1, 2, sharex=True)

plt.subplot(1, 2, 1)
plt.title("Unicast")
plt.xlim(0, 1)
plt.ylim(0, 3000)
plt.plot(ber, send_speed_uni, label="Send")
plt.plot(ber, recv_speed_uni, label="Receive")
plt.legend()
plt.grid()

plt.subplot(1, 2, 2)
plt.title("Broadcast")
plt.xlim(0, 1)
plt.ylim(0, 3000)
plt.plot(ber, send_speed_bro, label="Send")
plt.plot(ber, recv_speed_bro, label="Receive")
plt.legend()
plt.grid()

fig.add_subplot(111, frameon=False)
plt.tick_params(labelcolor="none", top=False, bottom=False, left=False, right=False)
plt.suptitle("BER's Impact on Throughput")
plt.xlabel("Bit Error Rate (%)")
plt.ylabel("Speed (bps)")
plt.show()
