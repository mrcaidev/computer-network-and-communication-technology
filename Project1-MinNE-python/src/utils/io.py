import os
from datetime import datetime, timedelta, timezone
from json import loads

from utils.params import File

# 获取当前目录和上级目录。
cwd = os.getcwd()
parent_dir = os.path.dirname(cwd)

# 如果配置目录在上级目录下，那么根目录是上级目录。
if os.path.exists(os.path.join(parent_dir, File.CONFIG_DIR)):
    rootdir = parent_dir

# 如果配置目录在当前目录下，那么当前目录为根目录。
elif os.path.exists(os.path.join(cwd, File.CONFIG_DIR)):
    rootdir = cwd

# 定位config目录与文件。
config_dir = os.path.join(rootdir, File.CONFIG_DIR)

batch_dir = os.path.join(config_dir, File.BATCH_DIR)
devicemap_dir = os.path.join(config_dir, File.DEVICEMAP_DIR)
ne_dir = os.path.join(config_dir, File.NE_DIR)

formal_batch = os.path.join(config_dir, f"{File.BATCH}.bat")
formal_devicemap = os.path.join(config_dir, f"{File.DEVICEMAP}.json")
formal_ne = os.path.join(config_dir, f"{File.NE}.txt")
formal_routerenv = os.path.join(config_dir, f"{File.ROUTERENV}.json")

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


def cover_devicemap(stage: str) -> None:
    """将端口映射文件改为阶段对应配置。

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


def run_batch() -> None:
    """运行一键启动文件。"""
    os.system(formal_batch)


def get_devicemap(device_id: str) -> dict:
    """获取设备端口配置。

    Args:
        device_id: 设备号。

    Returns:
        设备配置，包括：
        - "app": 该设备的应用层端口号。
        - "net": 该设备的网络层端口号。
        - "phy": 该设备的物理层端口号。
    """
    # 打开配置文件。
    try:
        with open(formal_devicemap, "r", encoding="utf-8") as fr:
            # 读取该设备配置。
            try:
                config: dict = loads(fr.read())[device_id]
            except KeyError:
                print(f"[Error] Device {device_id} absence")
                exit(-1)
            else:
                return config
    except FileNotFoundError:
        print(f"[Error] {formal_devicemap} not found")
        exit(-1)


def get_router_env(device_id: str) -> dict[str, dict]:
    """获取路由表周围环境。

    Args:
        device_id: 路由器设备号。

    Returns:
        路由器周围环境，键值对格式如下：
        - 键：相邻路由器的网络层端口号。
        - 值：到达该路由器的路径信息，包含下列两个键：
            - "exit": 要到达该路由器，消息应该从哪个本地物理层端口送出。
            - "cost": 到达该路由器的费用。
    """
    # 打开配置文件。
    try:
        with open(formal_routerenv, "r", encoding="utf-8") as fr:
            # 读取初始路由表。
            try:
                env: dict = loads(fr.read())[device_id]
            except KeyError:
                print(f"[Error] Device {device_id} absence")
                exit(-1)
            else:
                return env
    except FileNotFoundError:
        print(f"[Error] {formal_routerenv} not found")
        exit(-1)


def search_rsc(filename: str) -> str:
    """在资源目录下寻找某文件。

    Args:
        filename: 目标文件名。

    Returns:
        如果存在，则返回该文件的绝对路径；如果不存在，则返回None。
    """
    filepath = os.path.join(rsc_dir, filename)
    return filepath if os.path.exists(filepath) else ""


def save_rsc(data: bytes) -> tuple[str, bool]:
    """保存文件至资源目录。

    Args:
        data: 字节形式的文件内容。

    Returns:
        是否成功保存，成功为`True`，失败为`False`。
    """
    filepath = os.path.join(rsc_dir, f"received-{eval(File.ABBR_TIME)}.png")
    try:
        with open(filepath, "wb") as fw:
            fw.write(data)
    except Exception:
        return "", False
    else:
        return filepath, True
