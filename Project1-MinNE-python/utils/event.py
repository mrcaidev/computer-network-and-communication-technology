from utils.param import Constant as const


def get_mode_from_user() -> str:
    """
    从用户键盘输入获取当前工作模式。

    Returns:
        网元当前的工作模式，包括下列四种：
        - `utils.param.Constant.RECV`: 接收模式。
        - `utils.param.Constant.UNICAST`: 单播模式。
        - `utils.param.Constant.BROADCAST`: 广播模式。
        - `utils.param.Constant.QUIT`: 退出程序。
    """
    print("-----------------------------")
    print("|        Select mode        |")
    print("| 1::Receive     2::Unicast |")
    print("| 3::Broadcast   4::Quit    |")
    print("-----------------------------")
    while True:
        mode = input(">>> ")
        if mode in const.MODES:
            return mode


def get_port_from_user() -> str:
    """
    从用户键盘输入获取端口号。

    Returns:
        在[1, 65535]区间内的端口号。
    """
    while True:
        port = input(">>> ")
        try:
            port_num = int(port)
        except Exception:
            print("[Error] Port should be an integer.")
            continue
        else:
            if 1 <= port_num <= 65535:
                return port
            else:
                print("[Error] Port should fall between 1 and 65535.")


def get_message_from_user() -> str:
    """
    从用户键盘输入获取要发送的消息。

    Returns:
        消息字符串。
    """
    print("Input a piece of message:")
    while True:
        message = input(">>> ")
        if message != "":
            return message
