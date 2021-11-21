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
send_speed_2 = np.array(
    [
        [2642.8, 2874.0, 2925.1],
        [2600.5, 2273.9, 2560.4],
        [1799.9, 1741.9, 1761.4],
        [2521.0, 1904.5, 1437.0],
        [1436.8, 1605.0, 1099.0],
        [1310.3, 1800.0, 1883.1],
        [702.9, 802.8, 1621.7],
        [1289.7, 1017.6, 1671.4],
        [2481.5, 608.9, 768.9],
        [806.8, 1169.9, 1462.6],
        [562.8, 946.6, 1099.1],
    ]
)
recv_speed_2 = np.array(
    [
        [2925.3, 3343.4, 3412.6],
        [2874.7, 2480.4, 2874.2],
        [1949.6, 1860.8, 1927.4],
        [2874.2, 2047.0, 1545.2],
        [1530.7, 1741.5, 3485.8],
        [1388.0, 1973.6, 2073.8],
        [1269.8, 1621.2, 1742.4],
        [1353.5, 1070.8, 1799.7],
        [2823.1, 980.7, 795.1],
        [1653.9, 1231.5, 1574.9],
        [576.7, 980.7, 1153.5],
    ]
)

send_speed_1_average = np.array([np.mean(lst) for lst in send_speed_1])
recv_speed_1_average = np.array([np.mean(lst) for lst in recv_speed_1])
send_speed_2_average = np.array([np.mean(lst) for lst in send_speed_2])
recv_speed_2_average = np.array([np.mean(lst) for lst in recv_speed_2])

fig, axes = plt.subplots(1, 2)

plt.subplot(1, 2, 1)
plt.title("No Switch")
plt.xlim(0, 1)
plt.ylim(0, 5000)
plt.plot(ber, send_speed_1_average, label="Send")
plt.plot(ber, recv_speed_1_average, label="Receive")
plt.legend()

plt.subplot(1, 2, 2)
plt.title("With Switch")
plt.xlim(0, 1)
plt.ylim(0, 5000)
plt.plot(ber, send_speed_2_average, label="Send")
plt.plot(ber, recv_speed_2_average, label="Receive")
plt.legend()

fig.add_subplot(111, frameon=False)
plt.tick_params(labelcolor="none", top=False, bottom=False, left=False, right=False)
plt.suptitle("BER's Impact on Sending/Receiving Speed")
plt.xlabel("Bit Error Rate (%)")
plt.ylabel("Speed (bps)")
plt.show()
