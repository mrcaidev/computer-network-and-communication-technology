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

# 定位重要目录。
config_dir = os.path.join(rootdir, File.CONFIG_DIR)
log_dir = os.path.join(rootdir, File.LOG_DIR)
rsc_dir = os.path.join(rootdir, File.RSC_DIR)

# 时区设置。
timezone(timedelta(hours=8))


def log(src: str, message: str) -> bool:
    """记录日志。

    Args:
        src: 发起记录请求的来源。
        message: 要记录的信息。

    Returns:
        是否记录成功，成功为`True`，失败为`False`。
    """
    try:
        with open(
            os.path.join(log_dir, f"{src}.log"), mode="a", encoding="utf-8"
        ) as fa:
            fa.write(f"[{eval(File.FULL_TIME)}] {message}\n")
    except FileNotFoundError:
        return False
    else:
        return True


def get_device_map(device_id: str) -> dict:
    """获取设备端口配置。

    Args:
        device_id: 设备号。

    Returns:
        设备配置，包括：
        - "app": 该设备的应用层端口号。
        - "net": 该设备的网络层端口号。
        - "phy": 该设备的物理层端口号。
    """
    filepath = os.path.join(config_dir, File.DEVICE_MAP)
    # 打开配置文件。
    try:
        with open(filepath, "r", encoding="utf-8") as fr:
            # 读取该设备配置。
            try:
                config: dict = loads(fr.read())[device_id]
            except KeyError:
                print(f"[Config Error] Device {device_id} absence")
                exit(-1)
            else:
                return config
    except FileNotFoundError:
        print(f"[Config Error] {filepath} not found")
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
    filepath = os.path.join(config_dir, File.ROUTER_ENV)
    # 打开配置文件。
    try:
        with open(filepath, "r", encoding="utf-8") as fr:
            # 读取初始路由表。
            try:
                env: dict = loads(fr.read())[device_id]
            except KeyError:
                print(f"[Config Error] Device {device_id} absence")
                exit(-1)
            else:
                return env
    except FileNotFoundError:
        print(f"[Config Error] {filepath} not found")
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
