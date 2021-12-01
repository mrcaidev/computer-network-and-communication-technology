import os
from datetime import datetime, timedelta, timezone
from json import loads

from utils.params import File

# 获取当前目录和上级目录。
cwd = os.getcwd()
cwd_parent = os.path.dirname(cwd)

# 如果配置目录在上级目录下，那么根目录是上级目录。
if os.path.exists(os.path.join(cwd_parent, File.CONFIG_DIR)):
    rootdir = cwd_parent

# 如果配置目录在当前目录下，那么当前目录为根目录。
elif os.path.exists(os.path.join(cwd, File.CONFIG_DIR)):
    rootdir = cwd

# 定位config目录与配置文件。
config_dir = os.path.join(rootdir, File.CONFIG_DIR)

batch_dir = os.path.join(config_dir, File.BATCH_DIR)
devicemap_dir = os.path.join(config_dir, File.DEVICEMAP_DIR)
ne_dir = os.path.join(config_dir, File.NE_DIR)

formal_batch = os.path.join(config_dir, f"{File.BATCH}.bat")
formal_devicemap = os.path.join(config_dir, f"{File.DEVICEMAP}.json")
formal_ne = os.path.join(config_dir, f"{File.NE}.txt")

# 定位rsc目录。
rsc_dir = os.path.join(rootdir, File.RSC_DIR)

# 时区设置。
timezone(timedelta(hours=8))


def cover_batch(stage: str) -> None:
    """将一键启动文件改为阶段对应配置。

    Args:
        stage: 指定阶段。
    """
    src = os.path.join(batch_dir, f"{stage}.bat")

    # 读取阶段配置。
    with open(src, "r", encoding="utf-8") as fr:
        config = fr.read()

    # 写入正式配置。
    with open(formal_batch, "w", encoding="utf-8") as fw:
        fw.write(config)


def cover_ne(stage: str) -> None:
    """将物理层配置文件改为阶段对应配置。

    Args:
        stage: 指定阶段。
    """
    src = os.path.join(ne_dir, f"{stage}.txt")

    # 读取阶段配置。
    with open(src, "r", encoding="utf-8") as fr:
        config = fr.read()

    # 写入正式配置。
    with open(formal_ne, "w", encoding="utf-8") as fw:
        fw.write(config)


def cover_devicemap(stage: str) -> None:
    """将设备拓扑文件改为阶段对应配置。

    Args:
        stage: 指定阶段。
    """
    src = os.path.join(devicemap_dir, f"{stage}.json")

    # 读取阶段配置。
    with open(src, "r", encoding="utf-8") as fr:
        config = fr.read()

    # 写入正式配置。
    with open(formal_devicemap, "w", encoding="utf-8") as fw:
        fw.write(config)


def run_batch() -> None:
    """运行一键启动文件。"""
    os.system(formal_batch)


def get_hosts() -> list[str]:
    """获取主机列表。

    Returns:
        拓扑内的主机设备号列表。
    """
    # 打开配置文件。
    try:
        with open(formal_devicemap, "r", encoding="utf-8") as fr:
            # 读取该设备配置。
            try:
                hosts = loads(fr.read())["host"]
            except KeyError:
                print(f"[Error] Hosts absence")
                exit(-1)
            else:
                return hosts
    except FileNotFoundError:
        print(f"[Error] {formal_devicemap} not found")
        exit(-1)


def get_switch_phynum(device_id: str) -> int:
    """获取交换机物理层数量。

    Args:
        device_id: 设备号。

    Returns:
        物理层数量。
    """
    # 打开配置文件。
    try:
        with open(formal_devicemap, "r", encoding="utf-8") as fr:
            # 读取该设备配置。
            try:
                num = loads(fr.read())["switch"][device_id]["phynum"]
            except KeyError:
                print(f"[Error] Device {device_id} absence")
                exit(-1)
            else:
                return num
    except FileNotFoundError:
        print(f"[Error] {formal_devicemap} not found")
        exit(-1)


def get_router_WAN(device_id: str) -> dict[str, dict]:
    """获取路由表广域网环境。

    Args:
        device_id: 路由器设备号。

    Returns:
        路由器广域网环境，键值对格式如下：
        - 键：相邻路由器的网络层端口号。
        - 值：到达该路由器的路径信息，包含下列两个键：
            - "exit": 要到达该路由器，消息应该从哪个本地物理层端口送出。
            - "cost": 到达该路由器的费用。
    """
    # 打开配置文件。
    try:
        with open(formal_devicemap, "r", encoding="utf-8") as fr:
            # 读取初始路由表。
            try:
                WAN_env: dict = loads(fr.read())["router"][device_id]["WAN"]
            except KeyError:
                print(f"[Error] Device {device_id} absence")
                exit(-1)
            else:
                return WAN_env
    except FileNotFoundError:
        print(f"[Error] {formal_devicemap} not found")
        exit(-1)


def get_router_LAN(device_id: str) -> dict[str, str]:
    """获取路由表局域网环境。

    Args:
        device_id: 路由器设备号。

    Returns:
        路由器局域网环境，键值对格式如下：
        - 键：所属主机的设备号。
        - 值：到达该主机的本地物理层端口号。
    """
    # 打开配置文件。
    try:
        with open(formal_devicemap, "r", encoding="utf-8") as fr:
            # 读取初始路由表。
            try:
                LAN_env: dict = loads(fr.read())["router"][device_id]["LAN"]
            except KeyError:
                print(f"[Error] Device {device_id} absence")
                exit(-1)
            else:
                return LAN_env
    except FileNotFoundError:
        print(f"[Error] {formal_devicemap} not found")
        exit(-1)


def save_rsc(data: bytes) -> tuple[str, bool]:
    """保存文件至资源目录。

    Args:
        data: 字节形式的文件内容。

    Returns:
        保存成功为`True`，保存失败为`False`。
    """
    filepath = os.path.join(rsc_dir, f"received-{eval(File.ABBR_TIME)}.png")
    try:
        with open(filepath, "wb") as fw:
            fw.write(data)
    except Exception:
        return "", False
    else:
        return filepath, True
