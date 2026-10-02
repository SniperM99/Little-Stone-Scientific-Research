from machine import Pin, PWM
import time

# 底部舵机 GPIO13
base_pwm = PWM(Pin(13), freq=50)

# 头部舵机 GPIO25
head_pwm = PWM(Pin(25), freq=50)

def set_angle(pwm, angle):
    if angle < 0:
        angle = 0
    if angle > 180:
        angle = 180

    min_duty = 26
    max_duty = 128
    duty = int(min_duty + (max_duty - min_duty) * angle / 180)
    pwm.duty(duty)

def set_base(angle):
    # 底部舵机安全范围
    if angle < 40:
        angle = 40
    if angle > 140:
        angle = 140
    set_angle(base_pwm, angle)
    print("底部舵机:", angle)

def set_head(angle):
    # 头部舵机安全范围 0~100
    if angle < 0:
        angle = 0
    if angle > 100:
        angle = 100
    set_angle(head_pwm, angle)
    print("头部舵机:", angle)

def move(base_angle, head_angle, delay_time=0.4):
    set_base(base_angle)
    set_head(head_angle)
    time.sleep(delay_time)

print("等待电源稳定")
time.sleep(2)

print("两个舵机回到初始 90 度")
move(90, 90, 1)

print("开始舞蹈动作")

# 第一段：左右摇摆
for _ in range(2):
    move(70, 90, 0.4)
    move(110, 90, 0.4)

# 第二段：上下点头
for _ in range(2):
    move(90, 70, 0.4)
    move(90, 100, 0.4)

# 第三段：交叉联动
for _ in range(2):
    move(70, 70, 0.4)
    move(110, 100, 0.4)
    move(70, 100, 0.4)
    move(110, 70, 0.4)

# 第四段：快速抖动
for _ in range(3):
    move(80, 85, 0.2)
    move(100, 95, 0.2)

# 第五段：回中旋律动作
move(90, 70, 0.4)
move(70, 85, 0.4)
move(110, 85, 0.4)
move(90, 100, 0.4)
move(90, 90, 0.6)

print("舞蹈结束，恢复到 90 度")
move(90, 90, 1)

print("完成")