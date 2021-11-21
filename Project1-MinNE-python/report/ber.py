import matplotlib.pyplot as plt
import numpy as np

plt.style.use(["fast"])

ber = np.linspace(0, 1, 11)
send_speed_1 = np.array(
    [
        [4094.1, 4201.7, 4310.3],
        [4200.1, 4307.3, 4680.9],
        [2925.0, 2340.1, 3897.5],
        [2388.5, 3274.9, 3896.1],
        [2339.3, 1973.6, 1475.4],
        [2155.7, 2214.3, 2242.9],
        [1800.0, 2824.1, 1468.0],
        [1574.8, 1574.8, 1574.8],
        [1153.0, 1654.8, 2155.2],
        [652.6, 925.6, 1310.4],
        [806.8, 810.8, 2306.9],
    ]
)
recv_speed_1 = np.array(
    [
        [4679.5, 4680.8, 4815.5],
        [4817.2, 4813.3, 5286.6],
        [3150.0, 2482.7, 4427.7],
        [2560.3, 3637.7, 4304.2],
        [2481.4, 2100.1, 1530.5],
        [2341.0, 2374.7, 2372.9],
        [1882.9, 3033.8, 1522.4],
        [2243.2, 2482.0, 1637.8],
        [1186.5, 1724.3, 2274.5],
        [1092.3, 947.0, 1353.8],
        [823.0, 835.6, 2481.9],
    ]
)
# send_speed_2 = np.array(
#     [802.3, 799.4, 660.9, 496.6, 392.7, 380.4, 360.6, 345.9, 283.3, 190.4, 120.6]
# )
# recv_speed_2 = np.array(
#     [842.4, 840.2, 687.0, 512.8, 402.2, 389.4, 372.8, 353.6, 301.2, 210.5, 134.4]
# )

send_speed_1_average = np.array([np.mean(lst) for lst in send_speed_1])
recv_speed_1_average = np.array([np.mean(lst) for lst in recv_speed_1])
plt.title("BER's Impact on Sending/Receiving Speed")
plt.xlim(0, 1)
plt.ylim(0, 5000)
plt.plot(ber, send_speed_1_average, label="Send")
plt.plot(ber, recv_speed_1_average, label="Receive")
plt.legend()
plt.grid(True)

# fig, axes = plt.subplots(1, 2)

# plt.subplot(1, 2, 1)
# plt.title("No Switch")
# plt.xlim(0, 1)
# plt.ylim(0, 2000)
# plt.plot(ber, send_speed_1, label="Send")
# plt.plot(ber, recv_speed_1, label="Receive")
# plt.legend()

# plt.subplot(1, 2, 2)
# plt.title("With Switch")
# plt.xlim(0, 1)
# plt.ylim(0, 2000)
# plt.plot(ber, send_speed_2, label="Send")
# plt.plot(ber, recv_speed_2, label="Receive")
# plt.legend()

# fig.add_subplot(111, frameon=False)
# plt.tick_params(labelcolor="none", top=False, bottom=False, left=False, right=False)
# plt.suptitle("BER's Impact on Sending/Receiving Speed")
plt.xlabel("Bit Error Rate (%)")
plt.ylabel("Speed (bps)")
plt.show()
