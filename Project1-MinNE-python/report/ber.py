import matplotlib.pyplot as plt
import numpy as np

plt.style.use(["fast"])

ber = np.linspace(0, 1, 11)
send_2 = np.array(
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
recv_2 = np.array(
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
send_3 = np.array(
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
recv_3 = np.array(
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
send_4 = np.array(
    [
        [1882.0, 1310.2, 1638.0],
        [1910.2, 1710.3, 1776.4],
        [1624.6, 1365.4, 1434.5],
        [1304.3, 1665.4, 1446.7],
        [1033.8, 1037.5, 1538.6],
        [957.3, 784.2, 1034.5],
        [1051.5, 831.4, 767.7],
        [852.5, 981.3, 1388.6],
        [999.2, 767.0, 1022.6],
        [367.5, 534.1, 777.3],
        [596.7, 119.1, 479.5],
    ]
)
recv_4 = np.array(
    [
        [2176.5, 1310.2, 1573.4],
        [2139.7, 1820.7, 1776.4],
        [1842.0, 1584.2, 1653.1],
        [1522.4, 2014.4, 1847.6],
        [1068.9, 1236.2, 1684.1],
        [1177.3, 1026.2, 1123.5],
        [1177.8, 994.8, 897.6],
        [979.5, 1185.3, 1412.6],
        [1078.3, 840.2, 1089.0],
        [575.7, 658.6, 894.6],
        [601.3, 218.3, 593.7],
    ]
)

send_2_average = np.array([np.mean(lst) for lst in send_2])
recv_2_average = np.array([np.mean(lst) for lst in recv_2])
send_3_average = np.array([np.mean(lst) for lst in send_3])
recv_3_average = np.array([np.mean(lst) for lst in recv_3])
send_4_average = np.array([np.mean(lst) for lst in send_4])
recv_4_average = np.array([np.mean(lst) for lst in recv_4])

fig, axes = plt.subplots(1, 3)

plt.subplot(1, 3, 1)
plt.title("Stage 2")
plt.xlim(0, 1)
plt.ylim(0, 5000)
plt.plot(ber, send_2_average, label="Send")
plt.plot(ber, recv_2_average, label="Receive")
plt.legend()

plt.subplot(1, 3, 2)
plt.title("Stage 3")
plt.xlim(0, 1)
plt.ylim(0, 5000)
plt.plot(ber, send_3_average, label="Send")
plt.plot(ber, recv_3_average, label="Receive")
plt.legend()

plt.subplot(1, 3, 3)
plt.title("Stage 4")
plt.xlim(0, 1)
plt.ylim(0, 5000)
plt.plot(ber, send_4_average, label="Send")
plt.plot(ber, recv_4_average, label="Receive")
plt.legend()

fig.add_subplot(111, frameon=False)
plt.tick_params(labelcolor="none", top=False, bottom=False, left=False, right=False)
plt.suptitle("BER's Impact on Sending/Receiving Speed")
plt.xlabel("Bit Error Rate (%)")
plt.ylabel("Speed (bps)")
plt.show()
