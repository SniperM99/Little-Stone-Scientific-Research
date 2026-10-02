from machine import Pin, PWM
import time

SERVO_PIN = 13
pwm = PWM(Pin(SERVO_PIN), freq=50)

def set_angle(angle):
    if angle < 0:
        angle = 0
    if angle > 180:
        angle = 180

    min_duty = 30
    max_duty = 120
    duty = int(min_duty + (max_duty - min_duty) * angle / 180)
    pwm.duty(duty)
    print("当前角度:", angle, "占空比:", duty)

print("等待电源稳定")
time.sleep(3)

print("先测试 45 度")
set_angle(45)
time.sleep(3)

print("再到 90 度")
set_angle(90)
time.sleep(3)

while True:
    time.sleep(1)