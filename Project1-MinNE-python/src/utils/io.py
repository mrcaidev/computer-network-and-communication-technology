import os
from datetime import datetime, timedelta, timezone
from json import loads

# 各重要目录名。
CONFIG_DIR = "config"
RSC_DIR = "resource"
LOG_DIR = "log"

# 获取当前目录和上级目录。
cwd = os.getcwd()
cwd_parent = os.path.dirname(cwd)

# 如果 config 目录在上级目录下，那么根目录是上级目录。
if os.path.exists(os.path.join(cwd_parent, CONFIG_DIR)):
    rootdir = cwd_parent

# 如果 config 目录在当前目录下，那么当前目录为根目录。
elif os.path.exists(os.path.join(cwd, CONFIG_DIR)):
    rootdir = cwd

# 定位 config 目录与配置文件。
config_dir = os.path.join(rootdir, CONFIG_DIR)
batch_dir = os.path.join(config_dir, "batch-backup")
devicemap_dir = os.path.join(config_dir, "devicemap-backup")
ne_dir = os.path.join(config_dir, "ne-backup")

batch_file = os.path.join(config_dir, "batch.bat")
devicemap_file = os.path.join(config_dir, "devicemap.json")
ne_file = os.path.join(config_dir, "ne.txt")

# 定位 rsc 目录。
rsc_dir = os.path.join(rootdir, RSC_DIR)
if not os.path.exists(rsc_dir):
    os.mkdir(rsc_dir)

# 定位 log 目录。
log_dir = os.path.join(rootdir, LOG_DIR)
if not os.path.exists(log_dir):
    os.mkdir(log_dir)

# 时区设置。
timezone(timedelta(hours=8))


def write_log(device_id: str, message: str) -> None:
    """记录日志。

    Args:
        device_id: 发起记录请求的设备号。
        message: 要记录的日志消息。
    """
    log_path = os.path.join(log_dir, f"{device_id}.log")
    with open(log_path, "a", encoding="utf-8") as fa:
        fa.write(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] {message}\n")


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
    with open(batch_file, "w", encoding="utf-8") as fw:
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
    with open(ne_file, "w", encoding="utf-8") as fw:
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
    with open(devicemap_file, "w", encoding="utf-8") as fw:
        fw.write(config)


def run_batch() -> None:
    """运行一键启动文件。"""
    os.system(batch_file)


def get_host_config() -> list[str]:
    """获取主机配置。

    Returns:
        拓扑内的主机设备号列表。
    """
    # 打开配置文件。
    try:
        with open(devicemap_file, "r", encoding="utf-8") as fr:
            # 读取该设备配置。
            try:
                hosts = loads(fr.read())["host"]
            except KeyError:
                print(f"[Error] Hosts absence")
                exit(-1)
            else:
                return hosts
    except FileNotFoundError:
        print(f"[Error] {devicemap_file} not found")
        exit(-1)


def get_switch_config(device_id: str) -> int:
    """获取交换机配置。

    Args:
        device_id: 设备号。

    Returns:
        物理层数量。
    """
    # 打开配置文件。
    try:
        with open(devicemap_file, "r", encoding="utf-8") as fr:
            # 读取该设备配置。
            try:
                num = loads(fr.read())["switch"][device_id]["phynum"]
            except KeyError:
                print(f"[Error] Device {device_id} absence")
                exit(-1)
            else:
                return num
    except FileNotFoundError:
        print(f"[Error] {devicemap_file} not found")
        exit(-1)


def get_router_WAN(device_id: str) -> dict[str, dict]:
    """获取路由表广域网环境。

    Args:
        device_id: 路由器设备号。

    Returns:
        路由器广域网环境。
        - 键: 相邻路由器的网络层端口号。
        - 值: 到达该路由器的路径信息，包含下列两个键:
            - "exit": 要到达该路由器，消息应该从哪个本地物理层端口送出。
            - "cost": 到达该路由器的费用。
    """
    # 打开配置文件。
    try:
        with open(devicemap_file, "r", encoding="utf-8") as fr:
            # 读取初始路由表。
            try:
                WAN_env: dict = loads(fr.read())["router"][device_id]["WAN"]
            except KeyError:
                print(f"[Error] Device {device_id} absence")
                exit(-1)
            else:
                return WAN_env
    except FileNotFoundError:
        print(f"[Error] {devicemap_file} not found")
        exit(-1)


def get_router_LAN(device_id: str) -> dict[str, str]:
    """获取路由表局域网环境。

    Args:
        device_id: 路由器设备号。

    Returns:
        路由器局域网环境。
        - 键: 所属主机的设备号。
        - 值: 到达该主机的本地物理层端口号。
    """
    # 打开配置文件。
    try:
        with open(devicemap_file, "r", encoding="utf-8") as fr:
            # 读取初始路由表。
            try:
                LAN_env: dict = loads(fr.read())["router"][device_id]["LAN"]
            except KeyError:
                print(f"[Error] Device {device_id} absence")
                exit(-1)
            else:
                return LAN_env
    except FileNotFoundError:
        print(f"[Error] {devicemap_file} not found")
        exit(-1)


def save_rsc(data: bytes) -> tuple[str, bool]:
    """保存文件至资源目录。

    Args:
        data: 字节形式的文件内容。

    Returns:
        保存成功为`True`，保存失败为`False`。
    """
    filepath = os.path.join(
        rsc_dir, f"received-{datetime.now().strftime('%H%M%S')}.png")
    try:
        with open(filepath, "wb") as fw:
            fw.write(data)
    except Exception:
        return "", False
    else:
        return filepath, True
