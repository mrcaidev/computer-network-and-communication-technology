import matplotlib.pyplot as plt
import numpy as np

plt.style.use(["fast"])

ber = np.linspace(0, 1, 11)
send_speed_1 = np.array(
    [1581.9, 1389.2, 1257.6, 1010.7, 952.8, 825.5, 772.1, 572.0, 445.1, 281.2, 173.3]
)
recv_speed_1 = np.array(
    [1748.2, 1510.2, 1350.0, 1068.2, 985.1, 866.0, 806.0, 590.2, 472.0, 313.2, 206.1]
)
send_speed_2 = np.array(
    [802.3, 799.4, 660.9, 496.6, 392.7, 380.4, 360.6, 345.9, 283.3, 190.4, 120.6]
)
recv_speed_2 = np.array(
    [842.4, 840.2, 687.0, 512.8, 402.2, 389.4, 372.8, 353.6, 301.2, 210.5, 134.4]
)

fig, axes = plt.subplots(1, 2)

plt.subplot(1, 2, 1)
plt.title("No Switch")
plt.xlim(0, 1)
plt.ylim(0, 2000)
plt.plot(ber, send_speed_1, label="Send")
plt.plot(ber, recv_speed_1, label="Receive")
plt.legend()

plt.subplot(1, 2, 2)
plt.title("With Switch")
plt.xlim(0, 1)
plt.ylim(0, 2000)
plt.plot(ber, send_speed_2, label="Send")
plt.plot(ber, recv_speed_2, label="Receive")
plt.legend()

fig.add_subplot(111, frameon=False)
plt.tick_params(labelcolor="none", top=False, bottom=False, left=False, right=False)
plt.suptitle("BER's Impact on Sending/Receiving Speed")
plt.xlabel("Bit Error Rate (%)")
plt.ylabel("Speed (bps)")
plt.show()
