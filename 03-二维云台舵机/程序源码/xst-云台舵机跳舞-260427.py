from machine import Pin, PWM
import time
import gc

# =========================
# 舵机引脚配置
# =========================
BASE_SERVO_PIN = 13   # 底部舵机
HEAD_SERVO_PIN = 25   # 头部舵机

# =========================
# 舵机安全角度范围
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
    限制角度范围
    """
    if value < min_value:
        return min_value
    if value > max_value:
        return max_value
    return value


def angle_to_duty(angle):
    """
    将角度转换为 MicroPython PWM duty
    适用于常见 180 度舵机
    如果舵机角度不准，可以微调 min_duty 和 max_duty
    """
    min_duty = 26
    max_duty = 128
    duty = int(min_duty + (max_duty - min_duty) * angle / 180)
    return duty


def write_servo(pwm, angle):
    """
    写入舵机角度
    """
    duty = angle_to_duty(angle)
    pwm.duty(duty)


def set_base(angle):
    """
    设置底部舵机角度
    """
    global base_current
    angle = clamp(angle, BASE_MIN, BASE_MAX)
    base_current = angle
    write_servo(base_pwm, angle)
    print("底部舵机:", angle)


def set_head(angle):
    """
    设置头部舵机角度
    """
    global head_current
    angle = clamp(angle, HEAD_MIN, HEAD_MAX)
    head_current = angle
    write_servo(head_pwm, angle)
    print("头部舵机:", angle)


def smooth_move(target_base, target_head, step=2, delay_time=0.025):
    """
    两个舵机平滑移动到目标角度
    step 越小越平滑
    delay_time 越大越慢
    """
    global base_current, head_current

    target_base = clamp(target_base, BASE_MIN, BASE_MAX)
    target_head = clamp(target_head, HEAD_MIN, HEAD_MAX)

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


def move(base_angle, head_angle, hold_time=0.3):
    """
    移动到指定姿态，并停留一小段时间
    """
    smooth_move(base_angle, head_angle)
    time.sleep(hold_time)
    gc.collect()


def center(hold_time=0.8):
    """
    回到中间位置
    """
    print("回到中间")
    move(90, 90, hold_time)


def dance_intro():
    """
    开场动作：左右看一看
    """
    print("开场动作")

    move(90, 90, 0.4)
    move(70, 90, 0.3)
    move(110, 90, 0.3)
    move(90, 90, 0.3)


def dance_nod():
    """
    点头动作
    """
    print("点头动作")

    for _ in range(2):
        move(90, 65, 0.25)
        move(90, 95, 0.25)

    move(90, 90, 0.3)


def dance_swing():
    """
    左右摇摆
    """
    print("左右摇摆")

    for _ in range(3):
        move(65, 85, 0.25)
        move(115, 95, 0.25)

    move(90, 90, 0.3)


def dance_cross():
    """
    交叉联动动作
    """
    print("交叉联动")

    for _ in range(2):
        move(70, 70, 0.25)
        move(110, 100, 0.25)
        move(70, 100, 0.25)
        move(110, 70, 0.25)

    move(90, 90, 0.3)


def dance_shake():
    """
    小幅快速抖动
    """
    print("快速抖动")

    for _ in range(4):
        move(82, 86, 0.12)
        move(98, 94, 0.12)

    move(90, 90, 0.3)


def dance_wave():
    """
    波浪动作
    """
    print("波浪动作")

    actions = [
        (60, 90),
        (75, 75),
        (90, 60),
        (105, 75),
        (120, 90),
        (105, 100),
        (90, 95),
        (75, 100),
        (60, 90),
        (90, 90),
    ]

    for base_angle, head_angle in actions:
        move(base_angle, head_angle, 0.18)


def dance_finale():
    """
    结束动作
    """
    print("结束动作")

    move(70, 90, 0.25)
    move(110, 90, 0.25)
    move(80, 75, 0.25)
    move(100, 100, 0.25)
    move(90, 90, 0.6)


def dance():
    """
    完整舞蹈流程
    """
    print("开始舞蹈")

    dance_intro()
    dance_nod()
    dance_swing()
    dance_cross()
    dance_shake()
    dance_wave()
    dance_finale()

    print("舞蹈结束")
    center()


# =========================
# 主程序
# =========================
print("等待电源稳定")
time.sleep(2)

center()

dance()

print("完成")