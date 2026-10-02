import network
import socket
import time
import gc
import ujson
import machine
from machine import Pin, UART

# =========================================================
# WiFi配置
# =========================================================
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"

STATIC_IP = "192.168.1.188"
SUBNET_MASK = "255.255.255.0"
GATEWAY = "192.168.1.1"
DNS = "192.168.1.1"

# =========================================================
# JW300服务器
# =========================================================
REMOTE_SERVER = "YOUR_SERVER_IP"
REMOTE_PORT = 8666

# =========================================================
# 继电器（低电平触发）
# =========================================================
relay_low = Pin(26, Pin.OUT, value=1)
relay_mid = Pin(27, Pin.OUT, value=1)
relay_high = Pin(32, Pin.OUT, value=1)
relay_spare = Pin(33, Pin.OUT, value=1)

# =========================================================
# UART（JW300）
# =========================================================
uart = UART(2, baudrate=115200, tx=17, rx=16)

# =========================================================
# 状态变量
# =========================================================
fan_current_level = "off"
last_state_cache = None

LEVEL_NAME = {
    "off": "关闭",
    "low": "低档",
    "mid": "中档",
    "high": "高档"
}

# =========================================================
# WiFi连接
# =========================================================
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    wlan.ifconfig((STATIC_IP, SUBNET_MASK, GATEWAY, DNS))
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    while not wlan.isconnected():
        time.sleep(1)

    print("WiFi OK:", wlan.ifconfig())
    return wlan.ifconfig()[0]

# =========================================================
# 继电器控制
# =========================================================
def all_off():
    relay_low.value(1)
    relay_mid.value(1)
    relay_high.value(1)
    relay_spare.value(1)

def set_fan(level):
    global fan_current_level

    all_off()
    time.sleep_ms(100)

    if level == "low":
        relay_low.value(0)
    elif level == "mid":
        relay_mid.value(0)
    elif level == "high":
        relay_high.value(0)
    else:
        level = "off"

    fan_current_level = level

    # ⭐ 状态变化立即上报
    send_to_server(force=True)

    return "OK"

# =========================================================
# JW300上报（事件触发）
# =========================================================
def send_to_server(force=False):
    global last_state_cache

    try:
        data = {
            "device": "esp32_fan",
            "level": fan_current_level,
            "level_name": LEVEL_NAME[fan_current_level],
            "ts": time.ticks_ms()
        }

        state_str = ujson.dumps(data)

        # ⭐ 如果没变化，不发送
        if (not force) and (state_str == last_state_cache):
            return

        uart.write(state_str + "\n")
        last_state_cache = state_str

        print("发送JW300:", state_str)

    except Exception as e:
        print("发送失败:", e)

# =========================================================
# UART接收（远程控制）
# =========================================================
def check_uart():
    if uart.any():
        try:
            line = uart.readline()
            if line:
                msg = line.decode().strip()
                print("收到:", msg)

                cmd = ujson.loads(msg)

                if "level" in cmd:
                    set_fan(cmd["level"])

        except Exception as e:
            print("解析失败:", e)

# =========================================================
# Web页面
# =========================================================
HTML = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">

<title>ESP32 智能风扇控制系统</title>

<style>
body {
    margin:0;
    font-family: Arial, sans-serif;
    background: radial-gradient(circle at top, #0f2027, #203a43, #2c5364);
    color: #00f7ff;
    text-align: center;
}

/* 标题 */
h2 {
    margin-top: 40px;
    font-size: 28px;
    letter-spacing: 2px;
    text-shadow: 0 0 10px #00f7ff;
}

/* 容器 */
.container {
    margin-top: 60px;
}

/* 按钮 */
button {
    background: rgba(0, 247, 255, 0.1);
    border: 1px solid #00f7ff;
    color: #00f7ff;
    padding: 15px 30px;
    margin: 10px;
    font-size: 16px;
    border-radius: 8px;
    cursor: pointer;
    transition: 0.3s;
    box-shadow: 0 0 10px rgba(0, 247, 255, 0.3);
}

button:hover {
    background: #00f7ff;
    color: #000;
    box-shadow: 0 0 20px #00f7ff;
}

/* 状态显示 */
.status {
    margin-top: 30px;
    font-size: 18px;
    color: #ffffff;
}
</style>

</head>

<body>

<h2>⚡ ESP32 智能风扇控制系统</h2>

<div class="container">

    <button onclick="send('low')">低档</button>
    <button onclick="send('mid')">中档</button>
    <button onclick="send('high')">高档</button>
    <button onclick="send('off')">关闭</button>

    <div class="status" id="status">状态：等待操作</div>

</div>

<script>
function send(level){
    fetch('/fan?level=' + level)
    .then(res => res.text())
    .then(data => {
        document.getElementById("status").innerHTML =
        "状态：" + level;
    });
}
</script>

</body>
</html>
"""

# =========================================================
# Web Server
# =========================================================
def start_server(ip):
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(5)

    print("Web服务启动:", ip)

    while True:
        cl, addr = s.accept()
        req = cl.recv(1024).decode()

        path = req.split(" ")[1]

        if "/fan" in path:
            if "level=" in path:
                level = path.split("level=")[1]
                set_fan(level)
                cl.send("HTTP/1.1 200 OK\r\n\r\nOK")
            else:
                cl.send("HTTP/1.1 200 OK\r\n\r\nERR")

        elif "/status" in path:
            cl.send("HTTP/1.1 200 OK\r\n\r\n" + fan_current_level)

        else:
            cl.send("HTTP/1.1 200 OK\r\n\r\n" + HTML)

        cl.close()

        # ⭐ UART接收远程控制
        check_uart()

        gc.collect()
        
def response(client, data, ctype="text/html"):
    client.send("HTTP/1.1 200 OK\r\n")
    client.send("Content-Type: text/html; charset=utf-8\r\n")
    client.send("Connection: close\r\n\r\n")
    client.send(data)

# =========================================================
# 主程序
# =========================================================
print("系统启动")

all_off()
connect_wifi()

start_server(STATIC_IP)