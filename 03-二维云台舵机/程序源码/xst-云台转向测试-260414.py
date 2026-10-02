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
        angle = 1
        80

    min_duty = 26
    max_duty = 128
    duty = int(min_duty + (max_duty - min_duty) * angle / 180)
    pwm.duty(duty)
    print("设置角度:", angle, "占空比:", duty)

def set_base(angle):
    # 底部舵机设置安全范围
    if angle < 30:
        angle = 30
    if angle > 150:
        angle = 150
    print("底部舵机 ->", angle)
    set_angle(base_pwm, angle)

def set_head(angle):
    # 头部舵机严格限制 0~100 度
    if angle < 0:
        angle = 0
    if angle > 100:
        angle = 100
    print("头部舵机 ->", angle)
    set_angle(head_pwm, angle)

print("等待电源稳定")
time.sleep(2)

print("两个舵机先回到 90 度")
set_base(90)
set_head(90)
time.sleep(2)

print("开始测试底部舵机")
set_base(80)
time.sleep(2)
set_base(100)
time.sleep(2)
set_base(90)
time.sleep(2)

print("开始测试头部舵机")
set_head(80)
time.sleep(2)
set_head(100)
time.sleep(2)
set_head(90)
time.sleep(2)

print("测试结束，两个舵机恢复到 90 度")
set_base(90)
set_head(90)
time.sleep(2)

print("完成")