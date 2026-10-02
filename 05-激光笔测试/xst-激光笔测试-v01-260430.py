from machine import Pin
import time

RELAY_PIN = 26

relay = Pin(RELAY_PIN, Pin.OUT)

def laser_on():
    relay.value(1)
    print("激光器开启")

def laser_off():
    relay.value(0)
    print("激光器关闭")

# 默认关闭
laser_off()
time.sleep(2)

while True:
    laser_on()
    time.sleep(5)

    laser_off()
    time.sleep(2)