from machine import Pin, PWM
import time

# =========================
# 双舵机同步测试
# 底部舵机: GPIO13
# 头部舵机: GPIO25
# =========================

BASE_PIN = 13
HEAD_PIN = 25

base_pwm = PWM(Pin(BASE_PIN), freq=50)
head_pwm = PWM(Pin(HEAD_PIN), freq=50)

MIN_DUTY = 26
MAX_DUTY = 128

base_angle = 90
head_angle = 90


def angle_to_duty(angle):
    return int(MIN_DUTY + (MAX_DUTY - MIN_DUTY) * angle / 180)


def set_base(angle):
    global base_angle
    if angle < 0:
        angle = 0
    if angle > 180:
        angle = 180
    base_pwm.duty(angle_to_duty(angle))
    base_angle = angle
    print("底部舵机:", angle, "占空比:", angle_to_duty(angle))


def set_head(angle):
    global head_angle
    if angle < 0:
        angle = 0
    if angle > 100:
        angle = 100
    head_pwm.duty(angle_to_duty(angle))
    head_angle = angle
    print("头部舵机:", angle, "占空比:", angle_to_duty(angle))


def set_both(base_a, head_a):
    set_base(base_a)
    set_head(head_a)


def move_both_slow(base_start, base_end, head_start, head_end, delay=0.06):
    steps = max(abs(base_end - base_start), abs(head_end - head_start))
    if steps == 0:
        set_both(base_start, head_start)
        return

    for i in range(steps + 1):
        b = int(base_start + (base_end - base_start) * i / steps)
        h = int(head_start + (head_end - head_start) * i / steps)
        set_both(b, h)
        time.sleep(delay)


print("等待电源稳定")
time.sleep(2)

print("两个舵机先回到 90 度")
set_both(90, 90)
time.sleep(2)

print("同步小角度测试 1")
move_both_slow(90, 85, 90, 85, delay=0.08)
time.sleep(1)
move_both_slow(85, 90, 85, 90, delay=0.08)
time.sleep(1)

print("同步小角度测试 2")
move_both_slow(90, 95, 90, 95, delay=0.08)
time.sleep(1)
move_both_slow(95, 90, 95, 90, delay=0.08)
time.sleep(1)

print("交叉联动测试")
move_both_slow(90, 85, 90, 95, delay=0.08)
time.sleep(1)
move_both_slow(85, 90, 95, 90, delay=0.08)
time.sleep(1)

print("测试结束，回到 90 度")
set_both(90, 90)
time.sleep(1)