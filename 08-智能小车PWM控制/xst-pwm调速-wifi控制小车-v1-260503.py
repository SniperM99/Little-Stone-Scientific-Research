import network
import socket
import time
import gc
from machine import Pin, PWM

# =========================
# WiFi 配置
# =========================
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"

# 不想固定 IP 就保持空字符串
# 想固定 IP 可以写成 "192.168.1.188" 之类
STATIC_IP = "192.168.1.189"
SUBNET_MASK = "255.255.255.0"
GATEWAY = "192.168.1.1"
DNS = "192.168.1.1"

# =========================
# 可选：关闭舵机云台信号
# 如果舵机信号线还接在 GPIO13 和 GPIO25，可以保留
# =========================
SERVO_BASE_PIN = 13
SERVO_HEAD_PIN = 25

servo_base = Pin(SERVO_BASE_PIN, Pin.OUT)
servo_head = Pin(SERVO_HEAD_PIN, Pin.OUT)
servo_base.value(0)
servo_head.value(0)

time.sleep(0.5)

# =========================
# L298N 小车控制引脚
# =========================
IN1 = Pin(16, Pin.OUT)
IN2 = Pin(17, Pin.OUT)
IN3 = Pin(18, Pin.OUT)
IN4 = Pin(19, Pin.OUT)

ENA = PWM(Pin(21), freq=1000)
ENB = PWM(Pin(23), freq=1000)


def clamp(value, min_value, max_value):
    if value < min_value:
        return min_value
    if value > max_value:
        return max_value
    return value


def speed_to_duty(speed):
    """
    speed: 0~100
    ESP32 MicroPython PWM duty: 0~1023
    """
    speed = clamp(speed, 0, 100)
    return int(speed * 1023 / 100)


def set_speed(speed):
    duty = speed_to_duty(speed)
    ENA.duty(duty)
    ENB.duty(duty)
    print("速度:", speed, "%", "PWM:", duty)


def stop():
    IN1.value(0)
    IN2.value(0)
    IN3.value(0)
    IN4.value(0)
    set_speed(0)
    print("停止")


def forward(speed=60):
    IN1.value(1)
    IN2.value(0)
    IN3.value(1)
    IN4.value(0)
    set_speed(speed)
    print("前进")


def backward(speed=60):
    IN1.value(0)
    IN2.value(1)
    IN3.value(0)
    IN4.value(1)
    set_speed(speed)
    print("后退")


def left(speed=60):
    IN1.value(0)
    IN2.value(1)
    IN3.value(1)
    IN4.value(0)
    set_speed(speed)
    print("左转")


def right(speed=60):
    IN1.value(1)
    IN2.value(0)
    IN3.value(0)
    IN4.value(1)
    set_speed(speed)
    print("右转")


def gentle_left(speed=60):
    """
    慢左转：左轮停，右轮前进
    """
    IN1.value(0)
    IN2.value(0)
    IN3.value(1)
    IN4.value(0)
    set_speed(speed)
    print("慢左转")


def gentle_right(speed=60):
    """
    慢右转：左轮前进，右轮停
    """
    IN1.value(1)
    IN2.value(0)
    IN3.value(0)
    IN4.value(0)
    set_speed(speed)
    print("慢右转")


# 上电先停止，防止小车突然跑
stop()


# =========================
# WiFi 连接
# =========================
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if STATIC_IP:
        wlan.ifconfig((STATIC_IP, SUBNET_MASK, GATEWAY, DNS))

    if not wlan.isconnected():
        print("正在连接 WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)

        for i in range(30):
            if wlan.isconnected():
                break
            print("等待 WiFi 连接:", i + 1)
            time.sleep(1)

    if wlan.isconnected():
        ip = wlan.ifconfig()[0]
        print("WiFi 已连接")
        print("小车控制地址: http://{}/".format(ip))
        return ip
    else:
        print("WiFi 连接失败")
        return None


# =========================
# 网页界面
# =========================
def web_page():
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>石头的小车遥控器</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            margin: 0;
            padding: 0;
            background: linear-gradient(160deg, #0f172a, #1d4ed8);
            font-family: Arial, "Microsoft YaHei", sans-serif;
            color: white;
            text-align: center;
        }
        .box {
            max-width: 520px;
            margin: 0 auto;
            padding: 22px;
        }
        h1 {
            font-size: 30px;
            margin-top: 16px;
            margin-bottom: 8px;
        }
        .subtitle {
            opacity: 0.85;
            margin-bottom: 20px;
        }
        .panel {
            background: rgba(255,255,255,0.13);
            border: 1px solid rgba(255,255,255,0.25);
            border-radius: 26px;
            padding: 22px;
            box-shadow: 0 16px 40px rgba(0,0,0,0.28);
        }
        .speed-text {
            font-size: 22px;
            margin-bottom: 10px;
        }
        input[type=range] {
            width: 92%;
            height: 34px;
        }
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 14px;
            margin-top: 24px;
        }
        button {
            border: none;
            border-radius: 20px;
            padding: 18px 6px;
            font-size: 22px;
            font-weight: bold;
            color: white;
            background: linear-gradient(180deg, #38bdf8, #2563eb);
            box-shadow: 0 8px 0 #1e40af;
            cursor: pointer;
            user-select: none;
        }
        button:active {
            transform: translateY(5px);
            box-shadow: 0 3px 0 #1e40af;
        }
        .stop {
            background: linear-gradient(180deg, #fb7185, #e11d48);
            box-shadow: 0 8px 0 #9f1239;
        }
        .small {
            font-size: 17px;
            padding: 15px 6px;
        }
        .empty {
            visibility: hidden;
        }
        .status {
            margin-top: 18px;
            font-size: 18px;
            min-height: 26px;
            color: #dbeafe;
        }
        .tip {
            margin-top: 14px;
            font-size: 14px;
            opacity: 0.75;
            line-height: 1.7;
        }
    </style>
</head>
<body>
    <div class="box">
        <h1>石头的小车遥控器</h1>
        <div class="subtitle">ESP32 + L298N 电机驱动</div>

        <div class="panel">
            <div class="speed-text">速度：<span id="speedValue">60</span>%</div>
            <input id="speed" type="range" min="0" max="100" value="60"
                   oninput="speedValue.innerText=this.value">

            <div class="grid">
                <button class="empty">空</button>
                <button onclick="go('forward')">前进</button>
                <button class="empty">空</button>

                <button onclick="go('left')">左转</button>
                <button class="stop" onclick="go('stop')">停止</button>
                <button onclick="go('right')">右转</button>

                <button class="empty">空</button>
                <button onclick="go('backward')">后退</button>
                <button class="empty">空</button>

                <button class="small" onclick="go('gentle_left')">慢左转</button>
                <button class="small stop" onclick="go('stop')">刹车</button>
                <button class="small" onclick="go('gentle_right')">慢右转</button>
            </div>

            <div class="status" id="status">等待指令</div>

            <div class="tip">
                第一次测试请把小车架起来，让轮子悬空。<br>
                方向确认正确后，再放到地上跑。
            </div>
        </div>
    </div>

    <script>
        function go(action) {
            let speed = document.getElementById("speed").value;
            let status = document.getElementById("status");

            fetch("/cmd?action=" + action + "&speed=" + speed)
                .then(response => response.text())
                .then(text => {
                    status.innerText = text;
                    console.log(text);
                })
                .catch(err => {
                    status.innerText = "连接失败";
                    console.log(err);
                });
        }
    </script>
</body>
</html>
"""
    return html


# =========================
# URL 参数解析
# =========================
def get_query_value(path, key, default_value):
    if "?" not in path:
        return default_value

    query = path.split("?", 1)[1]
    parts = query.split("&")

    for item in parts:
        if "=" in item:
            k, v = item.split("=", 1)
            if k == key:
                return v

    return default_value


def handle_command(path):
    action = get_query_value(path, "action", "stop")
    speed_text = get_query_value(path, "speed", "60")

    try:
        speed = int(speed_text)
    except:
        speed = 60

    speed = clamp(speed, 0, 100)

    # L298N 低速可能推不动，非停止动作低于 25 自动提高到 25
    if action != "stop" and speed < 25:
        speed = 25

    if action == "forward":
        forward(speed)
    elif action == "backward":
        backward(speed)
    elif action == "left":
        left(speed)
    elif action == "right":
        right(speed)
    elif action == "gentle_left":
        gentle_left(speed)
    elif action == "gentle_right":
        gentle_right(speed)
    else:
        stop()
        action = "stop"
        speed = 0

    return "动作: {}, 速度: {}%".format(action, speed)


# =========================
# 启动 Web 服务器
# =========================
def start_server():
    ip = connect_wifi()
    if not ip:
        stop()
        return

    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(5)

    print("网页服务器已启动")
    print("浏览器打开: http://{}/".format(ip))

    while True:
        conn = None
        try:
            conn, addr = s.accept()
            request = conn.recv(1024).decode("utf-8")

            if not request:
                conn.close()
                continue

            first_line = request.split("\r\n")[0]
            path = first_line.split(" ")[1]
            print("请求:", path)

            if path.startswith("/cmd"):
                result = handle_command(path)
                response = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: text/plain; charset=utf-8\r\n"
                    "Connection: close\r\n"
                    "\r\n" + result
                )
            else:
                response = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: text/html; charset=utf-8\r\n"
                    "Connection: close\r\n"
                    "\r\n" + web_page()
                )

            conn.send(response.encode("utf-8"))
            conn.close()
            gc.collect()

        except Exception as e:
            print("服务器错误:", e)
            stop()
            try:
                if conn:
                    conn.close()
            except:
                pass


start_server()