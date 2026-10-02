from machine import Pin
import time

# =========================
# 你的实际接线
# =========================
IN1 = Pin(16, Pin.OUT)
IN2 = Pin(17, Pin.OUT)
IN3 = Pin(18, Pin.OUT)
IN4 = Pin(19, Pin.OUT)

def stop():
    IN1.value(0)
    IN2.value(0)
    IN3.value(0)
    IN4.value(0)
    print("停止")

def forward():
    # 左电机正转，右电机正转
    IN1.value(1)
    IN2.value(0)
    IN3.value(1)
    IN4.value(0)
    print("前进")

def backward():
    # 左电机反转，右电机反转
    IN1.value(0)
    IN2.value(1)
    IN3.value(0)
    IN4.value(1)
    print("后退")

def left():
    # 左电机后退，右电机前进，原地左转
    IN1.value(0)
    IN2.value(1)
    IN3.value(1)
    IN4.value(0)
    print("左转")

def right():
    # 左电机前进，右电机后退，原地右转
    IN1.value(1)
    IN2.value(0)
    IN3.value(0)
    IN4.value(1)
    print("右转")

# =========================
# 上电先停止
# =========================
stop()
time.sleep(2)

# =========================
# 测试动作
# =========================
forward()
time.sleep(2)

stop()
time.sleep(1)

backward()
time.sleep(2)

stop()
time.sleep(1)

left()
time.sleep(1.5)

stop()
time.sleep(1)

right()
time.sleep(1.5)

stop()
print("测试完成")