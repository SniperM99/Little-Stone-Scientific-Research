import network
import socket
import time
import gc
from machine import Pin, PWM

# =========================================================
# WiFi 配置
# =========================================================
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"

# =========================================================
# 固定 IP 配置
# =========================================================
STATIC_IP = "192.168.1.188"
SUBNET_MASK = "255.255.255.0"
GATEWAY = "192.168.1.1"
DNS = "192.168.1.1"

# =========================================================
# 舵机云台引脚
# 底部舵机：左右旋转
# 头部舵机：上下转动
# =========================================================
BASE_SERVO_PIN = 13
HEAD_SERVO_PIN = 25

# =========================================================
# 激光器 / 继电器引脚
# =========================================================
RELAY_PIN = 26

# 大部分继电器模块：1 开启，0 关闭
# 如果你的继电器是低电平触发，改成：
# LASER_ON_LEVEL = 0
# LASER_OFF_LEVEL = 1
LASER_ON_LEVEL = 1
LASER_OFF_LEVEL = 0

# =========================================================
# L298N 小车控制引脚
# IN1 -> GPIO16
# IN2 -> GPIO17
# IN3 -> GPIO18
# IN4 -> GPIO19
# ENA -> GPIO21
# ENB -> GPIO23
# =========================================================
IN1_PIN = 16
IN2_PIN = 17
IN3_PIN = 18
IN4_PIN = 19
ENA_PIN = 21
ENB_PIN = 23

CAR_PWM_FREQ = 1000

# =========================================================
# 舵机保护区间
# =========================================================
BASE_MIN = 40
BASE_MAX = 140

HEAD_MIN = 0
HEAD_MAX = 100

# =========================================================
# 初始状态
# =========================================================
base_current = 90
head_current = 90
laser_current = False

car_current_action = "stop"
car_current_speed = 0
car_left_speed = 0
car_right_speed = 0

# =========================================================
# 初始化舵机 PWM
# =========================================================
base_pwm = PWM(Pin(BASE_SERVO_PIN), freq=50)
head_pwm = PWM(Pin(HEAD_SERVO_PIN), freq=50)

# =========================================================
# 初始化激光继电器
# =========================================================
relay = Pin(RELAY_PIN, Pin.OUT)
relay.value(LASER_OFF_LEVEL)

# =========================================================
# 初始化 L298N
# =========================================================
IN1 = Pin(IN1_PIN, Pin.OUT)
IN2 = Pin(IN2_PIN, Pin.OUT)
IN3 = Pin(IN3_PIN, Pin.OUT)
IN4 = Pin(IN4_PIN, Pin.OUT)

ENA = PWM(Pin(ENA_PIN), freq=CAR_PWM_FREQ)
ENB = PWM(Pin(ENB_PIN), freq=CAR_PWM_FREQ)


# =========================================================
# 通用工具函数
# =========================================================
def clamp(value, min_value, max_value):
    if value < min_value:
        return min_value
    if value > max_value:
        return max_value
    return value


# =========================================================
# 舵机控制
# =========================================================
def angle_to_duty(angle):
    """
    将角度转换为 ESP32 MicroPython PWM duty
    """
    min_duty = 26
    max_duty = 128
    duty = int(min_duty + (max_duty - min_duty) * angle / 180)
    return duty


def write_servo(pwm, angle):
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
    smooth_move(90, 90)
    return "云台已回到中间"


def look_left():
    smooth_move(65, 90)
    return "云台已向左看"


def look_right():
    smooth_move(115, 90)
    return "云台已向右看"


def look_up():
    smooth_move(base_current, 60)
    return "云台已抬头"


def look_down():
    smooth_move(base_current, 100)
    return "云台已低头"


def nod():
    for _ in range(2):
        smooth_move(base_current, 65)
        time.sleep(0.15)
        smooth_move(base_current, 95)
        time.sleep(0.15)

    smooth_move(base_current, 90)
    return "点头完成"


def shake_head():
    for _ in range(2):
        smooth_move(65, head_current)
        time.sleep(0.15)
        smooth_move(115, head_current)
        time.sleep(0.15)

    smooth_move(90, head_current)
    return "摇头完成"


# =========================================================
# 激光控制
# =========================================================
def laser_on():
    global laser_current

    relay.value(LASER_ON_LEVEL)
    laser_current = True

    print("激光器开启")
    return "激光器已开启"


def laser_off():
    global laser_current

    relay.value(LASER_OFF_LEVEL)
    laser_current = False

    print("激光器关闭")
    return "激光器已关闭"


def laser_status_text():
    if laser_current:
        return "开启"
    return "关闭"


# =========================================================
# 小车控制
# =========================================================
def speed_to_duty(speed):
    """
    speed: 0~100
    ESP32 MicroPython PWM duty: 0~1023
    """
    speed = clamp(int(speed), 0, 100)
    return int(speed * 1023 / 100)


def set_car_speed(speed):
    """
    同时设置左右两路速度，保留给传统动作使用
    """
    duty = speed_to_duty(speed)

    ENA.duty(duty)
    ENB.duty(duty)

    print("小车速度:", speed, "%", "PWM:", duty)


def set_left_motor(speed):
    """
    左轮单独控制
    speed: -100 ~ 100
    正数前进，负数后退，0停止
    """
    speed = clamp(int(speed), -100, 100)

    if speed > 0:
        IN1.value(1)
        IN2.value(0)
        ENA.duty(speed_to_duty(speed))
    elif speed < 0:
        IN1.value(0)
        IN2.value(1)
        ENA.duty(speed_to_duty(-speed))
    else:
        IN1.value(0)
        IN2.value(0)
        ENA.duty(0)


def set_right_motor(speed):
    """
    右轮单独控制
    speed: -100 ~ 100
    正数前进，负数后退，0停止
    """
    speed = clamp(int(speed), -100, 100)

    if speed > 0:
        IN3.value(1)
        IN4.value(0)
        ENB.duty(speed_to_duty(speed))
    elif speed < 0:
        IN3.value(0)
        IN4.value(1)
        ENB.duty(speed_to_duty(-speed))
    else:
        IN3.value(0)
        IN4.value(0)
        ENB.duty(0)


def car_drive(left_speed, right_speed):
    """
    摇杆差速控制
    left_speed: 左轮速度 -100 ~ 100
    right_speed: 右轮速度 -100 ~ 100
    """
    global car_current_action, car_current_speed, car_left_speed, car_right_speed

    try:
        left_speed = int(left_speed)
    except:
        left_speed = 0

    try:
        right_speed = int(right_speed)
    except:
        right_speed = 0

    left_speed = clamp(left_speed, -100, 100)
    right_speed = clamp(right_speed, -100, 100)

    # 死区处理：太小的速度直接停止，避免电机嗡嗡响但不动
    if abs(left_speed) < 8:
        left_speed = 0
    if abs(right_speed) < 8:
        right_speed = 0

    set_left_motor(left_speed)
    set_right_motor(right_speed)

    car_left_speed = left_speed
    car_right_speed = right_speed

    if left_speed == 0 and right_speed == 0:
        car_current_action = "stop"
        car_current_speed = 0
        print("摇杆停止")
        return "摇杆停止"

    car_current_action = "joystick"
    car_current_speed = max(abs(left_speed), abs(right_speed))

    print("摇杆控制 左轮:", left_speed, "右轮:", right_speed)
    return "摇杆控制：左轮 {}%，右轮 {}%".format(left_speed, right_speed)


def car_stop():
    global car_current_action, car_current_speed, car_left_speed, car_right_speed

    IN1.value(0)
    IN2.value(0)
    IN3.value(0)
    IN4.value(0)

    ENA.duty(0)
    ENB.duty(0)

    car_current_action = "stop"
    car_current_speed = 0
    car_left_speed = 0
    car_right_speed = 0

    print("小车停止")
    return "小车已停止"


def car_forward(speed=60):
    global car_current_action, car_current_speed

    speed = clamp(int(speed), 0, 100)

    IN1.value(1)
    IN2.value(0)
    IN3.value(1)
    IN4.value(0)

    set_car_speed(speed)

    car_current_action = "forward"
    car_current_speed = speed

    print("小车前进")
    return "小车前进，速度 {}%".format(speed)


def car_backward(speed=60):
    global car_current_action, car_current_speed

    speed = clamp(int(speed), 0, 100)

    IN1.value(0)
    IN2.value(1)
    IN3.value(0)
    IN4.value(1)

    set_car_speed(speed)

    car_current_action = "backward"
    car_current_speed = speed

    print("小车后退")
    return "小车后退，速度 {}%".format(speed)


def car_left(speed=60):
    global car_current_action, car_current_speed

    speed = clamp(int(speed), 0, 100)

    IN1.value(0)
    IN2.value(1)
    IN3.value(1)
    IN4.value(0)

    set_car_speed(speed)

    car_current_action = "left"
    car_current_speed = speed

    print("小车左转")
    return "小车左转，速度 {}%".format(speed)


def car_right(speed=60):
    global car_current_action, car_current_speed

    speed = clamp(int(speed), 0, 100)

    IN1.value(1)
    IN2.value(0)
    IN3.value(0)
    IN4.value(1)

    set_car_speed(speed)

    car_current_action = "right"
    car_current_speed = speed

    print("小车右转")
    return "小车右转，速度 {}%".format(speed)


def car_gentle_left(speed=60):
    global car_current_action, car_current_speed

    speed = clamp(int(speed), 0, 100)

    IN1.value(0)
    IN2.value(0)
    IN3.value(1)
    IN4.value(0)

    set_car_speed(speed)

    car_current_action = "gentle_left"
    car_current_speed = speed

    print("小车慢左转")
    return "小车慢左转，速度 {}%".format(speed)


def car_gentle_right(speed=60):
    global car_current_action, car_current_speed

    speed = clamp(int(speed), 0, 100)

    IN1.value(1)
    IN2.value(0)
    IN3.value(0)
    IN4.value(0)

    set_car_speed(speed)

    car_current_action = "gentle_right"
    car_current_speed = speed

    print("小车慢右转")
    return "小车慢右转，速度 {}%".format(speed)


def car_action(action, speed=60):
    """
    小车传统动作统一入口
    主要给跳舞动作和兼容接口使用
    """
    try:
        speed = int(speed)
    except:
        speed = 60

    speed = clamp(speed, 0, 100)

    if action != "stop" and speed < 25:
        speed = 25

    if action == "forward":
        return car_forward(speed)
    elif action == "backward":
        return car_backward(speed)
    elif action == "left":
        return car_left(speed)
    elif action == "right":
        return car_right(speed)
    elif action == "gentle_left":
        return car_gentle_left(speed)
    elif action == "gentle_right":
        return car_gentle_right(speed)
    else:
        return car_stop()


# =========================================================
# 多功能跳舞：安全版
# =========================================================
def car_pulse(action, speed=30, run_time=0.18, stop_time=0.08):
    """
    小车短促动作：
    让小车动一下，然后马上停，降低电机瞬间电流和持续电流压力。
    """
    car_action(action, speed)
    time.sleep(run_time)
    car_stop()
    time.sleep(stop_time)


def dance():
    """
    安全版多功能跳舞，持续约 15 秒

    跳舞期间：
    1. 激光打开
    2. 小车短促移动
    3. 云台上下左右摆动
    4. 结束后小车停止、云台回中、激光关闭
    """
    print("开始安全版多功能跳舞")

    dance_seconds = 15
    start_time = time.time()

    try:
        laser_on()
        time.sleep(0.3)

        actions = [
            # base, head, car_action, car_speed, car_time
            (80, 85, "forward", 30, 0.16),
            (100, 85, "backward", 30, 0.16),
            (85, 95, "gentle_left", 32, 0.16),
            (95, 95, "gentle_right", 32, 0.16),
            (90, 90, "stop", 0, 0.10),

            (75, 75, "forward", 32, 0.18),
            (105, 75, "backward", 32, 0.18),
            (80, 100, "gentle_left", 34, 0.18),
            (100, 100, "gentle_right", 34, 0.18),
            (90, 90, "stop", 0, 0.10),

            (70, 90, "gentle_left", 35, 0.18),
            (110, 90, "gentle_right", 35, 0.18),
            (90, 70, "forward", 34, 0.16),
            (90, 100, "backward", 34, 0.16),
            (90, 90, "stop", 0, 0.10),

            (78, 80, "forward", 36, 0.16),
            (102, 80, "gentle_right", 36, 0.16),
            (78, 98, "backward", 34, 0.16),
            (102, 98, "gentle_left", 36, 0.16),
            (90, 90, "stop", 0, 0.10),
        ]

        index = 0

        while time.time() - start_time < dance_seconds:
            base_angle, head_angle, move_name, move_speed, move_time = actions[index]

            if move_name != "stop":
                car_pulse(move_name, move_speed, move_time, 0.08)
            else:
                car_stop()
                time.sleep(0.12)

            smooth_move(base_angle, head_angle, step=4, delay_time=0.014)
            time.sleep(0.08)

            index += 1
            if index >= len(actions):
                index = 0

        return "安全版多功能跳舞完成：小车已停止，云台已回中，激光已关闭"

    finally:
        car_stop()
        time.sleep(0.1)
        center()
        time.sleep(0.1)
        laser_off()
        print("安全版多功能跳舞结束")


def emergency_stop():
    """
    紧急停止：小车停止、激光关闭、云台回中
    """
    car_stop()
    laser_off()
    center()
    return "已紧急停止：小车停止，激光关闭，云台回中"


# =========================================================
# WiFi 连接：稳定版
# =========================================================
def connect_wifi():
    """
    稳定版 WiFi 连接函数
    解决 Thonny 软重启后 Wifi Internal Error 问题
    """
    wlan = network.WLAN(network.STA_IF)

    try:
        wlan.active(False)
        time.sleep(1)
    except Exception as e:
        print("关闭 WiFi 时提示:", e)

    wlan.active(True)
    time.sleep(1)

    try:
        wlan.disconnect()
        time.sleep(0.5)
    except Exception as e:
        print("断开旧 WiFi 时提示:", e)

    if STATIC_IP:
        try:
            print("设置固定 IP:", STATIC_IP)
            wlan.ifconfig((STATIC_IP, SUBNET_MASK, GATEWAY, DNS))
            time.sleep(0.5)
        except Exception as e:
            print("设置固定 IP 失败:", e)

    print("正在连接 WiFi:", WIFI_SSID)

    try:
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    except OSError as e:
        print("第一次连接 WiFi 失败:", e)
        print("重新初始化 WiFi 后再试一次")

        try:
            wlan.active(False)
            time.sleep(2)
            wlan.active(True)
            time.sleep(1)

            if STATIC_IP:
                wlan.ifconfig((STATIC_IP, SUBNET_MASK, GATEWAY, DNS))

            wlan.connect(WIFI_SSID, WIFI_PASSWORD)

        except Exception as e2:
            print("第二次连接 WiFi 仍然失败:", e2)
            return None

    timeout = 30

    while not wlan.isconnected() and timeout > 0:
        print("等待 WiFi 连接...", timeout)
        time.sleep(1)
        timeout -= 1

    if wlan.isconnected():
        ip = wlan.ifconfig()[0]
        print("WiFi 已连接")
        print("IP 地址:", ip)
        print("网关:", wlan.ifconfig()[2])
        print("请用浏览器访问: http://" + ip)
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
    params = query.split("&")

    for item in params:
        if "=" in item:
            k, v = item.split("=", 1)
            if k == key:
                return v

    return None


# =========================================================
# 网页
# =========================================================
def make_html():
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>石头多功能机器人控制台</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
        body {
            margin: 0;
            padding: 14px;
            background: linear-gradient(135deg, #dbeafe, #f5d0fe);
            font-family: Arial, "Microsoft YaHei", sans-serif;
            color: #111827;
        }

        .card {
            max-width: 560px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 24px;
            padding: 18px;
            box-shadow: 0 10px 32px rgba(15, 23, 42, 0.20);
        }

        h1 {
            text-align: center;
            font-size: 25px;
            margin: 8px 0 6px 0;
        }

        .subtitle {
            text-align: center;
            color: #64748b;
            font-size: 14px;
            margin-bottom: 14px;
        }

        .status {
            background: #f8fafc;
            border-radius: 16px;
            padding: 12px;
            margin-bottom: 14px;
            font-size: 15px;
            line-height: 1.8;
            border: 1px solid #e2e8f0;
        }

        .msg {
            background: #eff6ff;
            border-radius: 14px;
            padding: 12px;
            margin: 12px 0 16px 0;
            font-size: 16px;
            color: #1d4ed8;
            text-align: center;
            border: 1px solid #bfdbfe;
        }

        .section-title {
            font-weight: bold;
            margin-top: 18px;
            margin-bottom: 8px;
            font-size: 17px;
            text-align: left;
        }

        .row {
            display: flex;
            gap: 10px;
        }

        .btn {
            width: 100%;
            border: 0;
            border-radius: 14px;
            background: #2563eb;
            color: white;
            font-size: 17px;
            font-weight: bold;
            padding: 14px 8px;
            margin: 6px 0;
            box-shadow: 0 5px 0 #1e40af;
        }

        .btn:active {
            transform: translateY(4px);
            box-shadow: 0 1px 0 #1e40af;
        }

        .btn.secondary {
            background: #0891b2;
            box-shadow: 0 5px 0 #155e75;
        }

        .btn.warning {
            background: #f97316;
            box-shadow: 0 5px 0 #c2410c;
        }

        .btn.danger {
            background: #ef4444;
            box-shadow: 0 5px 0 #991b1b;
        }

        .btn.green {
            background: #22c55e;
            box-shadow: 0 5px 0 #15803d;
        }

        .btn.purple {
            background: #8b5cf6;
            box-shadow: 0 5px 0 #6d28d9;
        }

        .btn.stop {
            background: #dc2626;
            box-shadow: 0 5px 0 #7f1d1d;
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
            line-height: 1.6;
        }

        .laser-safe {
            font-size: 14px;
            color: #b42318;
            line-height: 1.6;
            background: #fff1f0;
            border: 1px solid #fecaca;
            padding: 10px;
            border-radius: 12px;
            margin-top: 8px;
        }

        .joystick-area {
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 14px 0 8px 0;
        }

        .joystick-base {
            width: 190px;
            height: 190px;
            border-radius: 50%;
            background: radial-gradient(circle at 35% 35%, #dbeafe, #93c5fd);
            border: 4px solid #2563eb;
            position: relative;
            box-shadow: inset 0 8px 18px rgba(30, 64, 175, 0.25),
                        0 10px 24px rgba(15, 23, 42, 0.25);
            touch-action: none;
            user-select: none;
            margin: 8px auto;
        }

        .joystick-knob {
            width: 76px;
            height: 76px;
            border-radius: 50%;
            background: radial-gradient(circle at 35% 35%, #ffffff, #60a5fa);
            border: 3px solid #1d4ed8;
            position: absolute;
            left: 57px;
            top: 57px;
            box-shadow: 0 8px 16px rgba(15, 23, 42, 0.35);
            transition: left 0.05s linear, top 0.05s linear;
        }

        .footer {
            text-align: center;
            font-size: 13px;
            color: #64748b;
            margin-top: 18px;
            line-height: 1.7;
        }
    </style>
</head>

<body>
    <div class="card">
        <h1>石头多功能机器人控制台</h1>
        <div class="subtitle">ESP32 + L298N 小车 + 云台 + 激光</div>

        <div class="status">
            小车状态：<b>""" + str(car_current_action) + """</b>，速度：<b>""" + str(car_current_speed) + """%</b><br>
            左轮速度：<b>""" + str(car_left_speed) + """%</b>，右轮速度：<b>""" + str(car_right_speed) + """%</b><br>
            底部舵机角度：<b>""" + str(base_current) + """</b> 度<br>
            头部舵机角度：<b>""" + str(head_current) + """</b> 度<br>
            激光器状态：<b>""" + laser_status_text() + """</b>
        </div>

        <div id="msgBox" class="msg">等待操作</div>

        <div class="section-title">一键动作</div>
        <button type="button" class="btn purple" onclick="sendCmd('/dance')">多功能跳舞：小车 + 云台 + 激光</button>
        <button type="button" class="btn stop" onclick="sendCmd('/stop')">紧急停止全部</button>

        <div class="section-title">小车速度上限</div>
        <input id="carSpeed"
               type="range"
               min="0"
               max="100"
               value="60"
               oninput="carSpeedText.innerText=this.value">
        <div class="value-box">速度上限：<span id="carSpeedText">60</span>%</div>

        <div class="section-title">小车摇杆控制</div>
        <div class="safe">
            拖动圆形摇杆控制小车，松手自动停止。<br>
            上：前进；下：后退；左/右：原地旋转；斜向：边走边转。
        </div>

        <div class="joystick-area">
            <div id="joystickBase" class="joystick-base">
                <div id="joystickKnob" class="joystick-knob"></div>
            </div>
        </div>

        <div class="value-box">
            摇杆状态：<span id="joyText">停止</span>
        </div>

        <div class="section-title">激光器控制</div>
        <div class="row">
            <button type="button" class="btn danger" onclick="sendCmd('/laser/on')">开启激光</button>
            <button type="button" class="btn green" onclick="sendCmd('/laser/off')">关闭激光</button>
        </div>

        <div class="laser-safe">
            安全提醒：不要照射人眼、动物眼睛、镜子、玻璃和金属反光面。
        </div>

        <div class="section-title">云台快捷动作</div>
        <button type="button" class="btn" onclick="sendCmd('/center')">云台回中</button>

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

        <div class="section-title">底部舵机控制</div>
        <div class="safe">保护区间：""" + str(BASE_MIN) + """ 到 """ + str(BASE_MAX) + """ 度</div>
        <input id="baseSlider"
               type="range"
               min=\"""" + str(BASE_MIN) + """\"
               max=\"""" + str(BASE_MAX) + """\"
               value=\"""" + str(base_current) + """\"
               oninput="document.getElementById('baseText').innerText=this.value"
               onchange="setBase(this.value)">
        <div class="value-box">底部角度：<span id="baseText">""" + str(base_current) + """</span> 度</div>

        <div class="section-title">头部舵机控制</div>
        <div class="safe">保护区间：""" + str(HEAD_MIN) + """ 到 """ + str(HEAD_MAX) + """ 度</div>
        <input id="headSlider"
               type="range"
               min=\"""" + str(HEAD_MIN) + """\"
               max=\"""" + str(HEAD_MAX) + """\"
               value=\"""" + str(head_current) + """\"
               oninput="document.getElementById('headText').innerText=this.value"
               onchange="setHead(this.value)">
        <div class="value-box">头部角度：<span id="headText">""" + str(head_current) + """</span> 度</div>

        <div class="footer">
            手机和 ESP32 需要连接同一个 WiFi<br>
            当前控制地址：http://""" + STATIC_IP + """
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
                console.log(error);
            });
        }

        function setBase(value) {
            document.getElementById("baseText").innerText = value;
            sendCmd("/base?angle=" + value);
        }

        function setHead(value) {
            document.getElementById("headText").innerText = value;
            sendCmd("/head?angle=" + value);
        }

        var joyBase = null;
        var joyKnob = null;
        var joyText = null;
        var joyActive = false;
        var joyLastSend = 0;
        var joySendInterval = 120;

        function clampJs(value, minValue, maxValue) {
            if (value < minValue) return minValue;
            if (value > maxValue) return maxValue;
            return value;
        }

        function sendDrive(left, right, force) {
            var now = Date.now();

            if (!force && now - joyLastSend < joySendInterval) {
                return;
            }

            joyLastSend = now;

            fetch("/drive?left=" + left + "&right=" + right + "&_t=" + now, {
                method: "GET",
                cache: "no-store"
            })
            .then(function(response) {
                return response.text();
            })
            .then(function(data) {
                if (joyText) {
                    joyText.innerText = data;
                }
            })
            .catch(function(error) {
                if (joyText) {
                    joyText.innerText = "摇杆请求失败";
                }
                console.log(error);
            });
        }

        function forceStopDrive() {
            sendDrive(0, 0, true);

            if (joyText) {
                joyText.innerText = "停止";
            }
        }

        function resetJoystick() {
            if (!joyKnob) return;

            joyKnob.style.left = "57px";
            joyKnob.style.top = "57px";

            forceStopDrive();
        }

        function handleJoystickMove(clientX, clientY) {
            if (!joyBase || !joyKnob) return;

            var rect = joyBase.getBoundingClientRect();

            var centerX = rect.left + rect.width / 2;
            var centerY = rect.top + rect.height / 2;

            var dx = clientX - centerX;
            var dy = clientY - centerY;

            var maxRadius = 72;
            var distance = Math.sqrt(dx * dx + dy * dy);

            if (distance > maxRadius) {
                dx = dx / distance * maxRadius;
                dy = dy / distance * maxRadius;
                distance = maxRadius;
            }

            var knobCenterOffset = 38;
            joyKnob.style.left = (rect.width / 2 - knobCenterOffset + dx) + "px";
            joyKnob.style.top = (rect.height / 2 - knobCenterOffset + dy) + "px";

            var x = dx / maxRadius;
            var y = -dy / maxRadius;

            if (Math.abs(x) < 0.12) x = 0;
            if (Math.abs(y) < 0.12) y = 0;

            var baseSpeed = parseInt(document.getElementById("carSpeed").value);

            var left = y + x;
            var right = y - x;

            var maxValue = Math.max(Math.abs(left), Math.abs(right));
            if (maxValue > 1) {
                left = left / maxValue;
                right = right / maxValue;
            }

            var leftSpeed = Math.round(left * baseSpeed);
            var rightSpeed = Math.round(right * baseSpeed);

            leftSpeed = clampJs(leftSpeed, -100, 100);
            rightSpeed = clampJs(rightSpeed, -100, 100);

            sendDrive(leftSpeed, rightSpeed, false);
        }

        function initJoystick() {
            joyBase = document.getElementById("joystickBase");
            joyKnob = document.getElementById("joystickKnob");
            joyText = document.getElementById("joyText");

            if (!joyBase || !joyKnob) {
                return;
            }

            joyBase.addEventListener("pointerdown", function(event) {
                joyActive = true;
                joyBase.setPointerCapture(event.pointerId);
                handleJoystickMove(event.clientX, event.clientY);
            });

            joyBase.addEventListener("pointermove", function(event) {
                if (!joyActive) return;
                handleJoystickMove(event.clientX, event.clientY);
            });

            joyBase.addEventListener("pointerup", function(event) {
                joyActive = false;
                resetJoystick();
            });

            joyBase.addEventListener("pointercancel", function(event) {
                joyActive = false;
                resetJoystick();
            });

            joyBase.addEventListener("pointerleave", function(event) {
                if (joyActive) {
                    joyActive = false;
                    resetJoystick();
                }
            });
        }

        window.addEventListener("load", initJoystick);
    </script>
</body>
</html>
"""
    return html


# =========================================================
# HTTP 响应
# =========================================================
def send_response(client, content, content_type="text/html"):
    """
    返回 HTTP 响应，禁止浏览器缓存
    分块发送，避免页面太长时 send 一次发送不完整
    """
    response = "HTTP/1.1 200 OK\r\n"
    response += "Content-Type: " + content_type + "; charset=utf-8\r\n"
    response += "Cache-Control: no-store, no-cache, must-revalidate, max-age=0\r\n"
    response += "Pragma: no-cache\r\n"
    response += "Expires: 0\r\n"
    response += "Connection: close\r\n"
    response += "\r\n"
    response += content

    data = response.encode("utf-8")

    chunk_size = 1024
    for i in range(0, len(data), chunk_size):
        client.send(data[i:i + chunk_size])


# =========================================================
# Web 服务
# =========================================================
def start_web_server(ip):
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]

    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
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

            if path.startswith("/favicon.ico"):
                send_response(client, "", "text/plain")

            # -------------------------
            # 摇杆差速控制
            # -------------------------
            elif path.startswith("/drive"):
                left_speed = parse_query(path, "left")
                right_speed = parse_query(path, "right")

                if left_speed is None:
                    left_speed = 0
                if right_speed is None:
                    right_speed = 0

                msg = car_drive(left_speed, right_speed)
                send_response(client, msg, "text/plain")

            # -------------------------
            # 兼容旧的小车控制接口
            # -------------------------
            elif path.startswith("/car") or path.startswith("/cmd"):
                action = parse_query(path, "action")
                speed = parse_query(path, "speed")

                if action is None:
                    action = "stop"

                if speed is None:
                    speed = 60

                msg = car_action(action, speed)
                send_response(client, msg, "text/plain")

            # -------------------------
            # 激光控制
            # -------------------------
            elif path.startswith("/laser/on"):
                msg = laser_on()
                send_response(client, msg, "text/plain")

            elif path.startswith("/laser/off"):
                msg = laser_off()
                send_response(client, msg, "text/plain")

            elif path.startswith("/laser"):
                state = parse_query(path, "state")

                if state == "on":
                    msg = laser_on()
                elif state == "off":
                    msg = laser_off()
                else:
                    msg = "激光器状态：" + laser_status_text()

                send_response(client, msg, "text/plain")

            # -------------------------
            # 紧急停止
            # -------------------------
            elif path.startswith("/stop"):
                msg = emergency_stop()
                send_response(client, msg, "text/plain")

            # -------------------------
            # 舵机控制
            # -------------------------
            elif path.startswith("/base"):
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

            # -------------------------
            # 多功能跳舞
            # -------------------------
            elif path.startswith("/dance"):
                msg = dance()
                send_response(client, msg, "text/plain")

            # -------------------------
            # 兼容 /action?name=xxx
            # -------------------------
            elif path.startswith("/action"):
                name = parse_query(path, "name")

                if name is None:
                    msg = "缺少 name 参数"

                elif name == "dance":
                    msg = dance()

                elif name == "nod":
                    msg = nod()

                elif name == "shake":
                    msg = shake_head()

                elif name == "center":
                    msg = center()

                elif name == "left":
                    msg = look_left()

                elif name == "right":
                    msg = look_right()

                elif name == "up":
                    msg = look_up()

                elif name == "down":
                    msg = look_down()

                elif name == "laser_on":
                    msg = laser_on()

                elif name == "laser_off":
                    msg = laser_off()

                elif name == "stop":
                    msg = emergency_stop()

                elif name == "forward":
                    msg = car_action("forward", 60)

                elif name == "backward":
                    msg = car_action("backward", 60)

                elif name == "car_left":
                    msg = car_action("left", 60)

                elif name == "car_right":
                    msg = car_action("right", 60)

                else:
                    msg = "未知动作: " + name

                send_response(client, msg, "text/plain")

            # -------------------------
            # 首页
            # -------------------------
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

            try:
                car_stop()
                laser_off()
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

print("默认关闭激光器")
laser_off()

print("小车默认停止")
car_stop()

print("舵机回到初始位置")
center()

ip = connect_wifi()

if ip:
    start_web_server(ip)
else:
    print("WiFi 未连接，无法启动网页控制")