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

# =========================
# 固定 IP 配置
# 根据你家路由器网段修改
# 如果你的路由器是 192.168.1.1，就用下面这一组
# =========================
STATIC_IP = "192.168.1.188"
SUBNET_MASK = "255.255.255.0"
GATEWAY = "192.168.1.1"
DNS = "192.168.1.1"

# =========================
# 舵机引脚配置
# 底部舵机：左右旋转
# 头部舵机：上下转动
# =========================
BASE_SERVO_PIN = 13
HEAD_SERVO_PIN = 25

# =========================
# 舵机保护区间
# 防止舵机转向过头
# =========================
BASE_MIN = 40
BASE_MAX = 140

HEAD_MIN = 0
HEAD_MAX = 100

# =========================
# 初始角度
# =========================
base_current = 90
head_current = 90

# =========================
# 初始化 PWM
# =========================
base_pwm = PWM(Pin(BASE_SERVO_PIN), freq=50)
head_pwm = PWM(Pin(HEAD_SERVO_PIN), freq=50)


def clamp(value, min_value, max_value):
    """
    限制数值范围
    """
    if value < min_value:
        return min_value
    if value > max_value:
        return max_value
    return value


def angle_to_duty(angle):
    """
    将角度转换为 ESP32 MicroPython PWM duty
    常见 180 度舵机可先使用 26 到 128
    如果角度不准，可以微调 min_duty 和 max_duty
    """
    min_duty = 26
    max_duty = 128
    duty = int(min_duty + (max_duty - min_duty) * angle / 180)
    return duty


def write_servo(pwm, angle):
    """
    写入舵机 PWM
    """
    duty = angle_to_duty(angle)
    pwm.duty(duty)


def set_base(angle):
    """
    设置底部舵机角度，带保护区间
    """
    global base_current

    angle = int(angle)
    angle = clamp(angle, BASE_MIN, BASE_MAX)

    base_current = angle
    write_servo(base_pwm, angle)

    print("底部舵机:", angle)
    return angle


def set_head(angle):
    """
    设置头部舵机角度，带保护区间
    """
    global head_current

    angle = int(angle)
    angle = clamp(angle, HEAD_MIN, HEAD_MAX)

    head_current = angle
    write_servo(head_pwm, angle)

    print("头部舵机:", angle)
    return angle


def smooth_move(target_base, target_head, step=3, delay_time=0.012):
    """
    平滑移动两个舵机，减少电流冲击
    step 越大动作越快
    delay_time 越大动作越慢
    """
    global base_current, head_current

    target_base = clamp(int(target_base), BASE_MIN, BASE_MAX)
    target_head = clamp(int(target_head), HEAD_MIN, HEAD_MAX)

    start_base = base_current
    start_head = head_current

    diff_base = target_base - start_base
    diff_head = target_head - start_head

    max_diff = max(abs(diff_base), abs(diff_head))

    if max_diff == 0:
        return

    steps = int(max_diff / step)
    if steps < 1:
        steps = 1

    for i in range(1, steps + 1):
        new_base = int(start_base + diff_base * i / steps)
        new_head = int(start_head + diff_head * i / steps)

        write_servo(base_pwm, new_base)
        write_servo(head_pwm, new_head)

        base_current = new_base
        head_current = new_head

        time.sleep(delay_time)

    base_current = target_base
    head_current = target_head

    write_servo(base_pwm, base_current)
    write_servo(head_pwm, head_current)

    print("底部舵机:", base_current)
    print("头部舵机:", head_current)


def center():
    """
    两个舵机回中
    """
    smooth_move(90, 90)
    return "已回到中间"


def look_left():
    """
    向左看
    如果实际方向反了，把 65 改成 115
    """
    smooth_move(65, 90)
    return "已向左看"


def look_right():
    """
    向右看
    如果实际方向反了，把 115 改成 65
    """
    smooth_move(115, 90)
    return "已向右看"


def look_up():
    """
    抬头
    如果实际方向反了，把 60 改成 100
    """
    smooth_move(base_current, 60)
    return "已抬头"


def look_down():
    """
    低头
    如果实际方向反了，把 100 改成 60
    """
    smooth_move(base_current, 100)
    return "已低头"


def nod():
    """
    点头动作
    """
    for _ in range(2):
        smooth_move(base_current, 65)
        time.sleep(0.15)
        smooth_move(base_current, 95)
        time.sleep(0.15)

    smooth_move(base_current, 90)
    return "点头完成"


def shake_head():
    """
    左右摇头动作
    """
    for _ in range(2):
        smooth_move(65, head_current)
        time.sleep(0.15)
        smooth_move(115, head_current)
        time.sleep(0.15)

    smooth_move(90, head_current)
    return "摇头完成"


def dance():
    """
    简单跳舞动作
    """
    actions = [
        (70, 90),
        (110, 90),
        (90, 70),
        (90, 100),
        (70, 75),
        (110, 95),
        (80, 85),
        (100, 95),
        (90, 90),
    ]

    for base_angle, head_angle in actions:
        smooth_move(base_angle, head_angle)
        time.sleep(0.12)

    center()
    return "跳舞完成"


def connect_wifi():
    """
    连接 WiFi，并设置 ESP32 固定 IP
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    print("设置固定 IP:", STATIC_IP)
    wlan.ifconfig((STATIC_IP, SUBNET_MASK, GATEWAY, DNS))

    if not wlan.isconnected():
        print("正在连接 WiFi:", WIFI_SSID)
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)

        timeout = 30
        while not wlan.isconnected() and timeout > 0:
            print("等待 WiFi 连接...")
            time.sleep(1)
            timeout -= 1

    if wlan.isconnected():
        ip = wlan.ifconfig()[0]
        print("WiFi 已连接")
        print("IP 地址:", ip)
        print("网关:", wlan.ifconfig()[2])
        return ip

    print("WiFi 连接失败")
    return None


def parse_query(path, key):
    """
    从请求路径中解析参数
    例如：
    /base?angle=90&_t=123456
    """
    if "?" not in path:
        return None

    query = path.split("?", 1)[1]
    params = query.split("&")

    for item in params:
        if "=" in item:
            k, v = item.split("=", 1)
            if k == key:
                return v

    return None


def make_html():
    """
    控制页面
    """
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>ESP32 舵机控制台</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
        body {
            margin: 0;
            padding: 16px;
            background: #f2f4f7;
            font-family: Arial, "Microsoft YaHei", sans-serif;
            color: #222;
        }

        .card {
            max-width: 520px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 18px;
            padding: 20px;
            box-shadow: 0 4px 18px rgba(0, 0, 0, 0.12);
        }

        h1 {
            text-align: center;
            font-size: 24px;
            margin: 8px 0 16px 0;
        }

        .status {
            background: #f7f9fc;
            border-radius: 12px;
            padding: 12px;
            margin-bottom: 16px;
            font-size: 16px;
            line-height: 1.8;
        }

        .msg {
            background: #eef6ff;
            border-radius: 12px;
            padding: 12px;
            margin: 12px 0 16px 0;
            font-size: 16px;
            color: #1677ff;
            text-align: center;
        }

        .section-title {
            font-weight: bold;
            margin-top: 18px;
            margin-bottom: 8px;
            text-align: left;
        }

        .btn {
            width: 100%;
            border: 0;
            border-radius: 12px;
            background: #1677ff;
            color: white;
            font-size: 18px;
            padding: 14px;
            margin: 6px 0;
        }

        .btn:active {
            background: #0958d9;
        }

        .btn.secondary {
            background: #13c2c2;
        }

        .btn.warning {
            background: #fa8c16;
        }

        .row {
            display: flex;
            gap: 10px;
        }

        .row .btn {
            flex: 1;
        }

        input[type=range] {
            width: 100%;
            margin-top: 10px;
        }

        .value-box {
            text-align: center;
            font-size: 16px;
            margin: 8px 0 12px 0;
        }

        .safe {
            font-size: 14px;
            color: #666;
            margin-top: 4px;
        }

        .footer {
            text-align: center;
            font-size: 13px;
            color: #888;
            margin-top: 18px;
        }
    </style>
</head>

<body>
    <div class="card">
        <h1>ESP32 舵机控制台</h1>

        <div class="status">
            当前底部舵机角度：<b>""" + str(base_current) + """</b> 度<br>
            当前头部舵机角度：<b>""" + str(head_current) + """</b> 度<br>
            底部保护区间：""" + str(BASE_MIN) + """ 到 """ + str(BASE_MAX) + """ 度<br>
            头部保护区间：""" + str(HEAD_MIN) + """ 到 """ + str(HEAD_MAX) + """ 度
        </div>

        <button type="button" class="btn" onclick="sendCmd('/center')">回到中间</button>

        <div class="row">
            <button type="button" class="btn" onclick="sendCmd('/left')">左看</button>
            <button type="button" class="btn" onclick="sendCmd('/right')">右看</button>
        </div>

        <div class="row">
            <button type="button" class="btn secondary" onclick="sendCmd('/up')">抬头</button>
            <button type="button" class="btn secondary" onclick="sendCmd('/down')">低头</button>
        </div>

        <div class="row">
            <button type="button" class="btn warning" onclick="sendCmd('/nod')">点头</button>
            <button type="button" class="btn warning" onclick="sendCmd('/shake')">摇头</button>
        </div>

        <button type="button" class="btn" onclick="sendCmd('/dance')">跳舞</button>

        <div id="msgBox" class="msg">
            等待操作
        </div>

        <div class="section-title">底部舵机控制</div>
        <div class="safe">保护区间：""" + str(BASE_MIN) + """ 到 """ + str(BASE_MAX) + """ 度</div>
        <input id="baseSlider"
               type="range"
               min=\"""" + str(BASE_MIN) + """\"
               max=\"""" + str(BASE_MAX) + """\"
               value=\"""" + str(base_current) + """\"
               oninput="baseText.innerText=this.value"
               onchange="setBase(this.value)">
        <div class="value-box">底部角度：<span id="baseText">""" + str(base_current) + """</span> 度</div>

        <div class="section-title">头部舵机控制</div>
        <div class="safe">保护区间：""" + str(HEAD_MIN) + """ 到 """ + str(HEAD_MAX) + """ 度</div>
        <input id="headSlider"
               type="range"
               min=\"""" + str(HEAD_MIN) + """\"
               max=\"""" + str(HEAD_MAX) + """\"
               value=\"""" + str(head_current) + """\"
               oninput="headText.innerText=this.value"
               onchange="setHead(this.value)">
        <div class="value-box">头部角度：<span id="headText">""" + str(head_current) + """</span> 度</div>

        <div class="footer">
            手机和 ESP32 需要连接同一个 WiFi<br>
            当前控制地址：""" + STATIC_IP + """
        </div>
    </div>

    <script>
        var sending = false;

        function updateStatus(text) {
            var box = document.getElementById("msgBox");
            if (box) {
                box.innerText = text;
            }
        }

        function addTimestamp(url) {
            var sep = url.indexOf("?") >= 0 ? "&" : "?";
            return url + sep + "_t=" + new Date().getTime();
        }

        function sendCmd(url) {
            if (sending) {
                updateStatus("上一条指令还在执行，请稍等");
                return;
            }

            sending = true;
            updateStatus("正在发送指令...");

            var realUrl = addTimestamp(url);

            fetch(realUrl, {
                method: "GET",
                cache: "no-store"
            })
            .then(function(response) {
                return response.text();
            })
            .then(function(data) {
                console.log(data);
                updateStatus(data);
                sending = false;
            })
            .catch(function(error) {
                updateStatus("请求失败：" + error);
                sending = false;
            });
        }

        function setBase(value) {
            baseText.innerText = value;

            if (sending) {
                updateStatus("上一条指令还在执行，请稍等");
                return;
            }

            sending = true;
            updateStatus("正在设置底部舵机...");

            var url = addTimestamp("/base?angle=" + value);

            fetch(url, {
                method: "GET",
                cache: "no-store"
            })
            .then(function(response) {
                return response.text();
            })
            .then(function(data) {
                console.log(data);
                updateStatus(data);
                sending = false;
            })
            .catch(function(error) {
                updateStatus("请求失败：" + error);
                sending = false;
            });
        }

        function setHead(value) {
            headText.innerText = value;

            if (sending) {
                updateStatus("上一条指令还在执行，请稍等");
                return;
            }

            sending = true;
            updateStatus("正在设置头部舵机...");

            var url = addTimestamp("/head?angle=" + value);

            fetch(url, {
                method: "GET",
                cache: "no-store"
            })
            .then(function(response) {
                return response.text();
            })
            .then(function(data) {
                console.log(data);
                updateStatus(data);
                sending = false;
            })
            .catch(function(error) {
                updateStatus("请求失败：" + error);
                sending = false;
            });
        }
    </script>
</body>
</html>
"""
    return html


def send_response(client, content, content_type="text/html"):
    """
    返回 HTTP 响应，禁止浏览器缓存
    """
    response = "HTTP/1.1 200 OK\r\n"
    response += "Content-Type: " + content_type + "; charset=utf-8\r\n"
    response += "Cache-Control: no-store, no-cache, must-revalidate, max-age=0\r\n"
    response += "Pragma: no-cache\r\n"
    response += "Expires: 0\r\n"
    response += "Connection: close\r\n"
    response += "\r\n"
    response += content

    client.send(response.encode("utf-8"))


def start_web_server(ip):
    """
    启动 Web 服务
    """
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]

    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)

    # ESP32 资源有限，监听队列不要太大
    s.listen(1)
    s.settimeout(3)

    print("Web 服务已启动")
    print("请用浏览器访问: http://" + ip)

    while True:
        client = None

        try:
            client, addr = s.accept()
            client.settimeout(2)

            request = client.recv(1024)

            if not request:
                client.close()
                continue

            try:
                request_text = request.decode("utf-8")
            except:
                client.close()
                continue

            first_line = request_text.split("\r\n")[0]
            print("请求:", first_line)

            parts = first_line.split(" ")
            if len(parts) < 2:
                send_response(client, "Bad Request", "text/plain")
                client.close()
                continue

            path = parts[1]

            # 浏览器会自动请求 favicon.ico，直接返回空
            if path.startswith("/favicon.ico"):
                send_response(client, "", "text/plain")
                client.close()
                continue

            if path.startswith("/base"):
                value = parse_query(path, "angle")
                if value is not None:
                    angle = set_base(int(value))
                    send_response(client, "底部舵机已设置为 " + str(angle) + " 度", "text/plain")
                else:
                    send_response(client, "缺少 angle 参数", "text/plain")

            elif path.startswith("/head"):
                value = parse_query(path, "angle")
                if value is not None:
                    angle = set_head(int(value))
                    send_response(client, "头部舵机已设置为 " + str(angle) + " 度", "text/plain")
                else:
                    send_response(client, "缺少 angle 参数", "text/plain")

            elif path.startswith("/center"):
                msg = center()
                send_response(client, msg, "text/plain")

            elif path.startswith("/left"):
                msg = look_left()
                send_response(client, msg, "text/plain")

            elif path.startswith("/right"):
                msg = look_right()
                send_response(client, msg, "text/plain")

            elif path.startswith("/up"):
                msg = look_up()
                send_response(client, msg, "text/plain")

            elif path.startswith("/down"):
                msg = look_down()
                send_response(client, msg, "text/plain")

            elif path.startswith("/nod"):
                msg = nod()
                send_response(client, msg, "text/plain")

            elif path.startswith("/shake"):
                msg = shake_head()
                send_response(client, msg, "text/plain")

            elif path.startswith("/dance"):
                msg = dance()
                send_response(client, msg, "text/plain")
            
            elif path.startswith("/action"):
                name = parse_query(path, "name")

                if name is None:
                    send_response(client, "缺少 name 参数", "text/plain")

                elif name == "dance":
                    msg = dance()
                    send_response(client, msg, "text/plain")

                elif name == "nod":
                    msg = nod()
                    send_response(client, msg, "text/plain")

                elif name == "shake":
                    msg = shake_head()
                    send_response(client, msg, "text/plain")

                elif name == "center":
                    msg = center()
                    send_response(client, msg, "text/plain")

                elif name == "left":
                    msg = look_left()
                    send_response(client, msg, "text/plain")

                elif name == "right":
                    msg = look_right()
                    send_response(client, msg, "text/plain")

                elif name == "up":
                    msg = look_up()
                    send_response(client, msg, "text/plain")

                elif name == "down":
                    msg = look_down()
                    send_response(client, msg, "text/plain")
                else:
                    send_response(client, "未知动作: " + name, "text/plain")
            else:
                send_response(client, make_html(), "text/html")

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

            if client:
                try:
                    client.close()
                except:
                    pass

            gc.collect()


# =========================
# 主程序
# =========================
print("等待电源稳定")
time.sleep(2)

print("舵机回到初始位置")
center()

ip = connect_wifi()

if ip:
    start_web_server(ip)
else:
    print("WiFi 未连接，无法启动网页控制")
