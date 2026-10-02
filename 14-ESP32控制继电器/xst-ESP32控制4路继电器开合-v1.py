import network
import socket
import time
import gc
from machine import Pin

# =========================================================
# WiFi 配置
# =========================================================
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"

# =========================================================
# 固定 IP 配置
# 手机浏览器访问：http://192.168.1.188
# =========================================================
STATIC_IP = "192.168.1.188"
SUBNET_MASK = "255.255.255.0"
GATEWAY = "192.168.1.1"
DNS = "192.168.1.1"

# =========================================================
# 四路继电器引脚配置
# 建议避开 ESP32 启动敏感引脚
# =========================================================
RELAY_LOW_PIN = 26       # IN1：低档
RELAY_MID_PIN = 27       # IN2：中档
RELAY_HIGH_PIN = 32      # IN3：高档
RELAY_SPARE_PIN = 33     # IN4：预留，不参与档位控制

# =========================================================
# 继电器触发方式
# 常见四路继电器模块为低电平触发：
#   0 = 吸合
#   1 = 释放
#
# 如果你的继电器是高电平触发，请改成：
# RELAY_ON_LEVEL = 1
# RELAY_OFF_LEVEL = 0
# =========================================================
RELAY_ON_LEVEL = 0
RELAY_OFF_LEVEL = 1

# 档位切换保护时间：
# 先完全断开全部档位，再等待一小段时间，随后接通目标档位
SWITCH_DELAY_MS = 100

# =========================================================
# 状态变量
# =========================================================
fan_current_level = "off"

LEVEL_NAME = {
    "off": "关闭",
    "low": "低档",
    "mid": "中档",
    "high": "高档"
}

# =========================================================
# 初始化继电器
# =========================================================
relay_low = Pin(RELAY_LOW_PIN, Pin.OUT)
relay_mid = Pin(RELAY_MID_PIN, Pin.OUT)
relay_high = Pin(RELAY_HIGH_PIN, Pin.OUT)
relay_spare = Pin(RELAY_SPARE_PIN, Pin.OUT)


# =========================================================
# 页面 HTML
# =========================================================
HTML_PAGE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>石头智能风扇控制器</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            min-height: 100vh;
            padding: 18px;
            font-family: Arial, "Microsoft YaHei", sans-serif;
            background: linear-gradient(145deg, #dbeafe, #ecfeff, #f0fdf4);
            color: #0f172a;
        }

        .card {
            width: 100%;
            max-width: 460px;
            margin: 18px auto;
            background: rgba(255, 255, 255, 0.96);
            border-radius: 28px;
            padding: 20px 18px 24px 18px;
            box-shadow: 0 14px 40px rgba(15, 23, 42, 0.16);
        }

        .icon {
            width: 76px;
            height: 76px;
            margin: 4px auto 10px auto;
            border-radius: 50%;
            background: linear-gradient(135deg, #38bdf8, #2563eb);
            color: white;
            font-size: 42px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 10px 20px rgba(37, 99, 235, 0.28);
        }

        h1 {
            margin: 4px 0 5px 0;
            text-align: center;
            font-size: 25px;
        }

        .subtitle {
            text-align: center;
            color: #64748b;
            font-size: 14px;
            margin-bottom: 16px;
        }

        .status-card {
            border-radius: 18px;
            background: #eff6ff;
            border: 1px solid #bfdbfe;
            padding: 14px 10px;
            text-align: center;
            margin: 14px 0 18px 0;
        }

        .status-title {
            color: #64748b;
            font-size: 13px;
            margin-bottom: 5px;
        }

        .status-text {
            color: #1d4ed8;
            font-size: 25px;
            font-weight: bold;
        }

        .section-title {
            color: #334155;
            font-size: 15px;
            font-weight: bold;
            margin: 8px 0 10px 0;
        }

        .gear-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 9px;
        }

        button {
            border: none;
            width: 100%;
            border-radius: 17px;
            color: white;
            font-size: 17px;
            font-weight: bold;
            padding: 18px 5px;
            cursor: pointer;
            transition: transform 0.08s, opacity 0.15s;
        }

        button:active {
            transform: translateY(3px);
        }

        button:disabled {
            opacity: 0.6;
        }

        .low {
            background: linear-gradient(135deg, #38bdf8, #0284c7);
            box-shadow: 0 5px 0 #075985;
        }

        .mid {
            background: linear-gradient(135deg, #34d399, #059669);
            box-shadow: 0 5px 0 #065f46;
        }

        .high {
            background: linear-gradient(135deg, #fb923c, #ea580c);
            box-shadow: 0 5px 0 #9a3412;
        }

        .off {
            margin-top: 16px;
            background: linear-gradient(135deg, #f87171, #dc2626);
            box-shadow: 0 5px 0 #991b1b;
            padding: 16px 5px;
        }

        .message {
            margin-top: 19px;
            border-radius: 13px;
            padding: 11px 9px;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            color: #475569;
            text-align: center;
            min-height: 42px;
            font-size: 14px;
        }

        .safe {
            margin-top: 18px;
            border-radius: 14px;
            padding: 11px;
            background: #fff7ed;
            border: 1px solid #fed7aa;
            color: #9a3412;
            font-size: 13px;
            line-height: 1.6;
        }

        .footer {
            margin-top: 18px;
            color: #64748b;
            text-align: center;
            font-size: 12px;
            line-height: 1.7;
        }
    </style>
</head>

<body>
    <div class="card">
        <div class="icon">✣</div>
        <h1>智能风扇控制器</h1>
        <div class="subtitle">ESP32 + 四路继电器 · 手机局域网控制</div>

        <div class="status-card">
            <div class="status-title">当前运行状态</div>
            <div id="statusText" class="status-text">正在读取...</div>
        </div>

        <div class="section-title">选择风速档位</div>

        <div class="gear-grid">
            <button id="btnLow" class="low" onclick="setFan('low')">低档</button>
            <button id="btnMid" class="mid" onclick="setFan('mid')">中档</button>
            <button id="btnHigh" class="high" onclick="setFan('high')">高档</button>
        </div>

        <button id="btnOff" class="off" onclick="setFan('off')">关闭风扇</button>

        <div id="message" class="message">请选择档位</div>

        <div class="safe">
            系统互斥保护：切换任意档位时，会先关闭其他全部档位，再开启目标档位，防止低、中、高档同时接通。
        </div>

        <div class="footer">
            手机与 ESP32 需要连接同一个 WiFi<br>
            控制地址：http://192.168.1.188
        </div>
    </div>

    <script>
        var busy = false;

        function setMessage(text) {
            document.getElementById("message").innerText = text;
        }

        function setStatus(text) {
            document.getElementById("statusText").innerText = text;
        }

        function lockButtons(lockState) {
            document.getElementById("btnLow").disabled = lockState;
            document.getElementById("btnMid").disabled = lockState;
            document.getElementById("btnHigh").disabled = lockState;
            document.getElementById("btnOff").disabled = lockState;
        }

        function requestUrl(url) {
            var split = url.indexOf("?") >= 0 ? "&" : "?";
            return url + split + "_t=" + new Date().getTime();
        }

        function setFan(level) {
            if (busy) {
                setMessage("上一条指令正在执行");
                return;
            }

            busy = true;
            lockButtons(true);
            setMessage("正在切换档位...");

            fetch(requestUrl("/fan?level=" + level), {
                method: "GET",
                cache: "no-store"
            })
            .then(function(response) {
                return response.json();
            })
            .then(function(data) {
                setStatus(data.level_name);
                setMessage(data.message);
                busy = false;
                lockButtons(false);
            })
            .catch(function(error) {
                setMessage("请求失败，请检查 ESP32 连接");
                busy = false;
                lockButtons(false);
            });
        }

        function refreshStatus() {
            fetch(requestUrl("/status"), {
                method: "GET",
                cache: "no-store"
            })
            .then(function(response) {
                return response.json();
            })
            .then(function(data) {
                setStatus(data.level_name);
                setMessage("控制器连接正常");
            })
            .catch(function(error) {
                setStatus("连接失败");
                setMessage("请检查手机 WiFi 和控制器电源");
            });
        }

        window.addEventListener("load", refreshStatus);
    </script>
</body>
</html>
"""


# =========================================================
# 继电器控制函数
# =========================================================
def relay_on(relay):
    relay.value(RELAY_ON_LEVEL)


def relay_off(relay):
    relay.value(RELAY_OFF_LEVEL)


def all_relays_off():
    """
    关闭全部档位继电器。
    这是三档互斥控制的核心保护动作。
    """
    relay_off(relay_low)
    relay_off(relay_mid)
    relay_off(relay_high)
    relay_off(relay_spare)


def set_fan_level(level):
    """
    风扇档位互斥切换：
    1. 先关闭所有继电器；
    2. 等待继电器触点完全释放；
    3. 仅接通目标档位。
    """
    global fan_current_level

    if level not in ("off", "low", "mid", "high"):
        level = "off"

    # 任何切换都先全部断开，确保不会出现两个档位同时导通
    all_relays_off()
    time.sleep_ms(SWITCH_DELAY_MS)

    if level == "low":
        relay_on(relay_low)
        message = "已切换到低档，其他档位已关闭"

    elif level == "mid":
        relay_on(relay_mid)
        message = "已切换到中档，其他档位已关闭"

    elif level == "high":
        relay_on(relay_high)
        message = "已切换到高档，其他档位已关闭"

    else:
        level = "off"
        message = "风扇已关闭，全部档位已断开"

    fan_current_level = level

    print("风扇状态:", LEVEL_NAME[fan_current_level])
    return message


def fan_status_json(message="状态读取成功"):
    return (
        '{"level":"' + fan_current_level +
        '","level_name":"' + LEVEL_NAME[fan_current_level] +
        '","message":"' + message + '"}'
    )


# =========================================================
# WiFi 连接
# =========================================================
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)

    try:
        wlan.active(False)
        time.sleep(1)
    except Exception as e:
        print("关闭 WiFi 提示:", e)

    wlan.active(True)
    time.sleep(1)

    try:
        wlan.disconnect()
        time.sleep(0.5)
    except Exception as e:
        print("断开旧连接提示:", e)

    if STATIC_IP:
        try:
            wlan.ifconfig((STATIC_IP, SUBNET_MASK, GATEWAY, DNS))
            print("设置固定 IP:", STATIC_IP)
        except Exception as e:
            print("固定 IP 设置失败:", e)

    print("正在连接 WiFi:", WIFI_SSID)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    timeout = 30

    while not wlan.isconnected() and timeout > 0:
        print("等待 WiFi 连接...", timeout)
        time.sleep(1)
        timeout -= 1

    if wlan.isconnected():
        ip = wlan.ifconfig()[0]
        print("WiFi 已连接")
        print("IP 地址:", ip)
        print("手机浏览器访问：http://" + ip)
        return ip

    print("WiFi 连接失败")
    return None


# =========================================================
# HTTP 参数解析
# =========================================================
def parse_query(path, key):
    if "?" not in path:
        return None

    query = path.split("?", 1)[1]

    for item in query.split("&"):
        if "=" in item:
            k, v = item.split("=", 1)
            if k == key:
                return v

    return None


# =========================================================
# HTTP 响应函数
# =========================================================
def send_response(client, content, content_type="text/html", cache=False):
    body = content.encode("utf-8")

    header = "HTTP/1.1 200 OK\r\n"
    header += "Content-Type: " + content_type + "; charset=utf-8\r\n"
    header += "Content-Length: " + str(len(body)) + "\r\n"

    if cache:
        header += "Cache-Control: public, max-age=120\r\n"
    else:
        header += "Cache-Control: no-store, no-cache, must-revalidate, max-age=0\r\n"
        header += "Pragma: no-cache\r\n"
        header += "Expires: 0\r\n"

    header += "Connection: close\r\n\r\n"

    client.send(header.encode("utf-8"))

    chunk_size = 2048
    for i in range(0, len(body), chunk_size):
        client.send(body[i:i + chunk_size])


# =========================================================
# Web 服务
# =========================================================
def start_web_server(ip):
    address = socket.getaddrinfo("0.0.0.0", 80)[0][-1]

    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(address)
    server.listen(2)
    server.settimeout(3)

    print("风扇控制网页已启动")
    print("访问地址：http://" + ip)

    while True:
        client = None

        try:
            client, client_address = server.accept()
            client.settimeout(2)

            request = client.recv(1024)

            if not request:
                client.close()
                continue

            request_text = request.decode("utf-8")
            first_line = request_text.split("\r\n")[0]
            print("请求:", first_line)

            parts = first_line.split(" ")

            if len(parts) < 2:
                send_response(client, "Bad Request", "text/plain")
                client.close()
                continue

            path = parts[1]

            if path.startswith("/favicon.ico"):
                client.send(b"HTTP/1.1 204 No Content\r\nConnection: close\r\n\r\n")

            elif path.startswith("/fan"):
                level = parse_query(path, "level")

                if level is None:
                    message = "缺少 level 参数"
                else:
                    message = set_fan_level(level)

                send_response(
                    client,
                    fan_status_json(message),
                    "application/json"
                )

            elif path.startswith("/status"):
                send_response(
                    client,
                    fan_status_json(),
                    "application/json"
                )

            elif path.startswith("/off"):
                message = set_fan_level("off")
                send_response(
                    client,
                    fan_status_json(message),
                    "application/json"
                )

            else:
                send_response(client, HTML_PAGE, "text/html", cache=True)

            client.close()
            gc.collect()

        except OSError:
            if client:
                try:
                    client.close()
                except:
                    pass

            gc.collect()

        except Exception as e:
            print("Web 服务异常:", e)

            # 出现异常时，安全关闭所有档位
            try:
                set_fan_level("off")
            except:
                pass

            if client:
                try:
                    client.close()
                except:
                    pass

            gc.collect()


# =========================================================
# 主程序
# =========================================================
print("等待电源稳定")
time.sleep(2)

print("初始化继电器：全部关闭")
all_relays_off()
fan_current_level = "off"

ip = connect_wifi()

if ip:
    start_web_server(ip)
else:
    print("WiFi 未连接，无法启动手机网页控制")
    all_relays_off()