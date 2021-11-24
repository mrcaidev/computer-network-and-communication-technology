import os
from datetime import datetime, timedelta, timezone
from json import loads

from utils.constant import File

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
    """
    记录日志。

    Args:
        src: 发起记录请求的来源。
        message: 要记录的信息。

    Returns:
        是否记录成功，成功为True，失败为False。
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
    """
    获取配置文件内的设备端口配置。

    Args:
        device_id: 设备号。

    Returns:
        包含该设备配置的字典，键在下列三个字段中取：
        - "app": 该设备的应用层端口号。
        - "net": 该设备的网络层端口号。
        - "phy": 该设备的物理层端口号。
    """
    # 打开配置文件。
    filepath = os.path.join(config_dir, File.DEVICE_MAP)
    try:
        with open(filepath, "r", encoding="utf-8") as fr:
            # 读取该设备配置。
            try:
                config: dict = loads(fr.read())[device_id]

            # 如果配置读取出错，就报错退出。
            except KeyError:
                print(f"[Error] Wrong device id: {device_id}.")
                exit(-1)

            # 如果配置读取成功，就返回配置。
            else:
                return config

    # 如果找不到配置文件，就报错退出。
    except FileNotFoundError:
        print(f"[Error] {filepath} not found.")
        exit(-1)


def get_router_env(device_id: str) -> dict[str, dict]:
    """
    获取配置文件内的初始路由表。

    Args:
        device_id: 设备号。

    Returns:
        包含该设备配置的字典，键在下列三个字段中取：
        - "app": 该设备的应用层端口号。
        - "net": 该设备的网络层端口号。
        - "phy": 该设备的物理层端口号。
    """
    # 打开配置文件。
    filepath = os.path.join(config_dir, File.ROUTER_ENV)
    try:
        with open(filepath, "r", encoding="utf-8") as fr:
            # 读取初始路由表。
            try:
                env: dict = loads(fr.read())[device_id]

            # 如果配置读取出错，就报错退出。
            except KeyError:
                print(f"[Error] Wrong device id: {device_id}.")
                exit(-1)

            # 如果配置读取成功，就返回配置。
            else:
                return env

    # 如果找不到配置文件，就报错退出。
    except FileNotFoundError:
        print(f"[Error] {filepath} not found.")
        exit(-1)


def search_rsc(filename: str) -> str:
    """
    在资源目录下寻找某文件。

    Args:
        filename: 目标文件名。

    Returns:
        如果存在，则返回该文件的绝对路径；如果不存在，则返回None。
    """
    filepath = os.path.join(rsc_dir, filename)
    return filepath if os.path.exists(filepath) else None


def save_file(data: bytes) -> tuple[str, bool]:
    """
    保存文件至资源目录。

    Args:
        data: 字节形式的文件内容。

    Returns:
        是否成功保存，成功为True，失败为False。
    """
    filepath = os.path.join(rsc_dir, f"received-{eval(File.ABBR_TIME)}.png")
    try:
        with open(filepath, "wb") as fw:
            fw.write(data)
    except Exception:
        return "", False
    else:
        return filepath, True
