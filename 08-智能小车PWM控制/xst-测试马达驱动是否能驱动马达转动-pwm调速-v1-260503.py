from machine import Pin, PWM
import time

# =========================
# 可选：关闭舵机云台信号，避免小车测试时云台乱动
# 如果你的舵机还接在 GPIO13 和 GPIO25，可以保留这段
# 如果舵机已经拔掉，也可以保留，不影响小车
# =========================
SERVO_BASE_PIN = 13
SERVO_HEAD_PIN = 25

servo_base = Pin(SERVO_BASE_PIN, Pin.OUT)
servo_head = Pin(SERVO_HEAD_PIN, Pin.OUT)

servo_base.value(0)
servo_head.value(0)

time.sleep(0.5)

# =========================
# L298N 方向控制引脚
# =========================
IN1 = Pin(16, Pin.OUT)
IN2 = Pin(17, Pin.OUT)
IN3 = Pin(18, Pin.OUT)
IN4 = Pin(19, Pin.OUT)

# =========================
# L298N 速度控制引脚
# ENA -> GPIO21
# ENB -> GPIO23
# =========================
ENA = PWM(Pin(21), freq=1000)
ENB = PWM(Pin(23), freq=1000)


def speed_to_duty(speed):
    """
    speed: 0~100
    ESP32 MicroPython PWM duty: 0~1023
    """
    if speed < 0:
        speed = 0
    if speed > 100:
        speed = 100

    return int(speed * 1023 / 100)


def set_speed(speed):
    duty = speed_to_duty(speed)
    ENA.duty(duty)
    ENB.duty(duty)
    print("当前速度:", speed, "%", "PWM:", duty)


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


# =========================
# 上电先停止
# =========================
stop()
time.sleep(2)

# =========================
# 调速测试
# =========================
print("低速前进")
forward(35)
time.sleep(2)

print("中速前进")
forward(60)
time.sleep(2)

print("高速前进")
forward(90)
time.sleep(2)

stop()
time.sleep(1)

print("中速后退")
backward(60)
time.sleep(2)

stop()
time.sleep(1)

print("左转")
left(60)
time.sleep(1.5)

stop()
time.sleep(1)

print("右转")
right(60)
time.sleep(1.5)

stop()
print("调速测试完成")