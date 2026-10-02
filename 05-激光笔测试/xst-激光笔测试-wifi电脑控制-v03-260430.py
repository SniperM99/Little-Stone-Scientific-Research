from machine import Pin
import network
import socket
import time

# =========================
# WiFi 配置
# =========================
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"

# =========================
# 继电器配置
# =========================
RELAY_PIN = 26

# 你的原代码是：
# relay.value(1) = 激光器开启
# relay.value(0) = 激光器关闭
# 所以这里使用高电平触发
ACTIVE_HIGH = True

relay = Pin(RELAY_PIN, Pin.OUT)


def laser_on():
    if ACTIVE_HIGH:
        relay.value(1)
    else:
        relay.value(0)
    print("激光器开启")


def laser_off():
    if ACTIVE_HIGH:
        relay.value(0)
    else:
        relay.value(1)
    print("激光器关闭")


def is_laser_on():
    if ACTIVE_HIGH:
        return relay.value() == 1
    else:
        return relay.value() == 0


# 默认关闭激光器
laser_off()


# =========================
# 连接 WiFi
# =========================
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    # 如果之前连接过，先断开一下
    if wlan.isconnected():
        wlan.disconnect()
        time.sleep(1)

    print("正在连接 WiFi...")
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    for i in range(30):
        if wlan.isconnected():
            break
        print("等待连接...", i + 1)
        time.sleep(1)

    if not wlan.isconnected():
        print("WiFi 连接失败，请检查 WiFi 名称和密码")
        return None

    ip = wlan.ifconfig()[0]
    print("WiFi 连接成功")
    print("ESP32 IP 地址:", ip)
    print("请在电脑浏览器打开: http://{}".format(ip))

    return ip


# =========================
# 网页内容
# =========================
def web_page():
    laser_is_on = is_laser_on()

    if laser_is_on:
        state_text = "激光器正在开启"
        state_emoji = "🔴"
        state_color = "#ff4d6d"
        state_bg = "#fff0f3"
        robot_eye = "● ●"
    else:
        state_text = "激光器已经关闭"
        state_emoji = "🟢"
        state_color = "#2fb344"
        state_bg = "#effaf1"
        robot_eye = "◕ ◕"

    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>小石头激光控制台</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            min-height: 100vh;
            font-family: Arial, "Microsoft YaHei", sans-serif;
            background: linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }}

        .page {{
            width: 100%;
            max-width: 430px;
        }}

        .card {{
            background: #ffffff;
            border-radius: 28px;
            padding: 28px 24px;
            text-align: center;
            box-shadow: 0 18px 40px rgba(0, 0, 0, 0.18);
            border: 5px solid rgba(255, 255, 255, 0.7);
        }}

        .title {{
            font-size: 28px;
            font-weight: 900;
            color: #2454a6;
            margin-bottom: 6px;
        }}

        .subtitle {{
            font-size: 15px;
            color: #6b7280;
            margin-bottom: 22px;
        }}

        .robot {{
            width: 130px;
            height: 105px;
            background: linear-gradient(180deg, #ffe066, #ffc300);
            border-radius: 30px;
            margin: 0 auto 20px auto;
            position: relative;
            box-shadow: inset 0 -8px 0 rgba(0,0,0,0.08);
        }}

        .robot:before {{
            content: "";
            position: absolute;
            top: -18px;
            left: 58px;
            width: 14px;
            height: 22px;
            background: #2454a6;
            border-radius: 10px;
        }}

        .robot:after {{
            content: "";
            position: absolute;
            top: -28px;
            left: 50px;
            width: 30px;
            height: 30px;
            background: #ff4d6d;
            border-radius: 50%;
            border: 5px solid #ffffff;
        }}

        .eyes {{
            font-size: 32px;
            color: #2454a6;
            padding-top: 25px;
            letter-spacing: 14px;
            padding-left: 13px;
        }}

        .mouth {{
            width: 52px;
            height: 18px;
            border-bottom: 5px solid #2454a6;
            border-radius: 0 0 40px 40px;
            margin: 8px auto 0 auto;
        }}

        .state-box {{
            background: {state_bg};
            border: 3px dashed {state_color};
            border-radius: 22px;
            padding: 18px;
            margin: 18px 0 24px 0;
        }}

        .state-label {{
            font-size: 15px;
            color: #6b7280;
            margin-bottom: 8px;
        }}

        .state-text {{
            font-size: 24px;
            font-weight: 900;
            color: {state_color};
        }}

        .btn {{
            display: block;
            width: 100%;
            padding: 18px 16px;
            margin: 14px 0;
            border-radius: 20px;
            text-decoration: none;
            font-size: 22px;
            font-weight: 900;
            color: white;
            box-shadow: 0 8px 0 rgba(0,0,0,0.16);
            transition: transform 0.08s ease;
        }}

        .btn:active {{
            transform: translateY(5px);
            box-shadow: 0 3px 0 rgba(0,0,0,0.16);
        }}

        .btn-on {{
            background: linear-gradient(180deg, #ff6b6b, #f03e3e);
        }}

        .btn-off {{
            background: linear-gradient(180deg, #51cf66, #2f9e44);
        }}

        .btn-pulse {{
            background: linear-gradient(180deg, #4dabf7, #1971c2);
        }}

        .safe {{
            background: #fff7d6;
            border-radius: 18px;
            padding: 14px;
            margin-top: 20px;
            color: #7a5c00;
            font-size: 14px;
            line-height: 1.7;
            border: 2px solid #ffd43b;
        }}

        .footer {{
            margin-top: 16px;
            font-size: 13px;
            color: #94a3b8;
        }}
    </style>
</head>

<body>
    <div class="page">
        <div class="card">
            <div class="title">小石头激光控制台</div>
            <div class="subtitle">ESP32 局域网控制页面</div>

            <div class="robot">
                <div class="eyes">{robot_eye}</div>
                <div class="mouth"></div>
            </div>

            <div class="state-box">
                <div class="state-label">当前状态</div>
                <div class="state-text">{state_emoji} {state_text}</div>
            </div>

            <a class="btn btn-on" href="/on">🔴 打开激光器</a>
            <a class="btn btn-off" href="/off">🟢 关闭激光器</a>
            <a class="btn btn-pulse" href="/pulse">⏱ 点亮 5 秒</a>

            <div class="safe">
                ⚠️ 安全提醒：激光不能照眼睛，也不要照镜子、玻璃、金属等反光物。<br>
                小朋友操作时，旁边必须有大人看护。
            </div>

            <div class="footer">
                Powered by ESP32
            </div>
        </div>
    </div>
</body>
</html>
""".format(
        state_bg=state_bg,
        state_color=state_color,
        state_text=state_text,
        state_emoji=state_emoji,
        robot_eye=robot_eye
    )

    return html


# =========================
# 启动 Web 服务
# =========================
ip = connect_wifi()

if ip is None:
    laser_off()
else:
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    s = socket.socket()

    try:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except:
        pass

    s.bind(addr)
    s.listen(5)

    print("Web 服务已启动，监听端口 80")
    print("浏览器访问: http://{}".format(ip))

    while True:
        try:
            conn, addr = s.accept()
            print("客户端连接:", addr)

            request = conn.recv(1024)
            request = request.decode("utf-8")
            print(request)

            # 解析访问路径
            if "GET /on" in request:
                laser_on()

            elif "GET /off" in request:
                laser_off()

            elif "GET /pulse" in request:
                laser_on()
                time.sleep(5)
                laser_off()

            response = web_page()

            conn.send("HTTP/1.1 200 OK\r\n")
            conn.send("Content-Type: text/html; charset=utf-8\r\n")
            conn.send("Connection: close\r\n")
            conn.send("\r\n")
            conn.sendall(response)
            conn.close()

        except Exception as e:
            print("发生错误:", e)
            try:
                conn.close()
            except:
                pass
            laser_off()