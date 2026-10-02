from mcp.server.fastmcp import FastMCP
import logging
import requests

logger = logging.getLogger("xiaozhi_servo_robot_mcp")

mcp = FastMCP("XiaoShiServoRobot")

SERVO_SERVER_BASE_URL = "http://192.168.1.188"

VALID_ACTIONS = {
    "dance": "跳舞",
    "nod": "点头",
    "shake": "摇头",
    "left": "看左边",
    "right": "看右边",
    "up": "抬头",
    "down": "低头",
    "center": "回到中间",
}


def request_servo(path: str, params: dict | None = None) -> dict:
    """
    调用舵机 ESP32 的 HTTP 接口。
    返回内容控制在较短范围内，适合小智 MCP 工具返回。
    """
    url = SERVO_SERVER_BASE_URL + path

    try:
        logger.info("Request servo url=%s params=%s", url, params)

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        text = response.text
        if len(text) > 300:
            text = text[:300]

        logger.info(
            "Servo response status=%s text=%s",
            response.status_code,
            text
        )

        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "message": text
        }

    except Exception as e:
        logger.exception("Servo request failed")
        return {
            "success": False,
            "message": "舵机控制失败：" + str(e)
        }


@mcp.tool()
def control_xiaoshi_robot_action(action_name: str) -> dict:
    """
    控制小石头舵机机器人执行一个动作。

    当用户想让机器人做动作时使用这个工具。
    action_name 参数必须使用下面这些英文动作名称之一：
    dance 表示跳舞；
    nod 表示点头；
    shake 表示摇头；
    left 表示看左边；
    right 表示看右边；
    up 表示抬头；
    down 表示低头；
    center 表示回到中间。

    用户说“跳个舞”“表演一下”“机器人跳舞”时，action_name 使用 dance。
    用户说“点点头”“点头”时，action_name 使用 nod。
    用户说“摇摇头”“摇头”时，action_name 使用 shake。
    用户说“看左边”“向左看”时，action_name 使用 left。
    用户说“看右边”“向右看”时，action_name 使用 right。
    用户说“抬头”“看上面”时，action_name 使用 up。
    用户说“低头”“看下面”时，action_name 使用 down。
    用户说“回中”“回到中间”“恢复原位”时，action_name 使用 center。
    """
    action_name = str(action_name).strip().lower()

    if action_name not in VALID_ACTIONS:
        return {
            "success": False,
            "message": "未知动作。可用动作有：dance, nod, shake, left, right, up, down, center"
        }

    result = request_servo(
        "/action",
        params={
            "name": action_name
        }
    )

    if result.get("success"):
        result["action_name"] = action_name
        result["action_label"] = VALID_ACTIONS[action_name]

    return result


@mcp.tool()
def set_xiaoshi_robot_head_angle(head_angle: int) -> dict:
    """
    设置小石头舵机机器人的头部舵机角度。

    当用户要求头部转到某个角度时使用这个工具。
    head_angle 表示头部舵机角度，安全范围是 0 到 100。
    如果用户说“头部转到80度”“把头抬到60度”“头低到100度”，就使用这个工具。
    """
    try:
        head_angle = int(head_angle)
    except Exception:
        return {
            "success": False,
            "message": "head_angle 必须是数字"
        }

    if head_angle < 0:
        head_angle = 0

    if head_angle > 100:
        head_angle = 100

    result = request_servo(
        "/head",
        params={
            "angle": head_angle
        }
    )

    if result.get("success"):
        result["head_angle"] = head_angle

    return result


@mcp.tool()
def set_xiaoshi_robot_base_angle(base_angle: int) -> dict:
    """
    设置小石头舵机机器人的底部舵机角度。

    当用户要求底座、身体、左右方向转到某个角度时使用这个工具。
    base_angle 表示底部舵机角度，安全范围是 40 到 140。
    如果用户说“底部转到120度”“身体转到80度”“向左转到60度”，就使用这个工具。
    """
    try:
        base_angle = int(base_angle)
    except Exception:
        return {
            "success": False,
            "message": "base_angle 必须是数字"
        }

    if base_angle < 40:
        base_angle = 40

    if base_angle > 140:
        base_angle = 140

    result = request_servo(
        "/base",
        params={
            "angle": base_angle
        }
    )

    if result.get("success"):
        result["base_angle"] = base_angle

    return result


@mcp.tool()
def test_xiaoshi_robot_connection() -> dict:
    """
    测试小石头舵机机器人是否在线。

    当用户说“测试机器人连接”“看看机器人能不能控制”“检查舵机连接”时使用这个工具。
    这个工具会让机器人回到中间位置，用于确认 MCP 到舵机 ESP32 的链路是否正常。
    """
    return request_servo(
        "/action",
        params={
            "name": "center"
        }
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")