
/*
 * STC89C52RC 智能小车综合控制程序
 * 适用：STC89C52RC-DIP40 + L298N 电机驱动 + 红外循迹 + 红外避障 + HC-SR04 超声波
 *
 * 编译环境：Keil C51
 * 晶振：11.0592MHz
 *
 * 重要：
 * 1. 电机驱动引脚每个小车可能不同，先修改“引脚定义区”。
 * 2. 烧录前建议把小车架空，避免程序方向反了导致乱跑。
 * 3. 若电机方向反了，优先交换电机两根线，或调整 motor_xxx() 函数里的 IN1/IN2。
 */

#include <REG52.H>

typedef unsigned char u8;
typedef unsigned int  u16;
typedef unsigned long u32;

/* ===================== 引脚定义区：根据你的接线改这里 ===================== */

/*
 * L298N 电机驱动，默认用 P1.0~P1.5。
 * 常见接法：
 * ENA -> P1.0
 * IN1 -> P1.1
 * IN2 -> P1.2
 * IN3 -> P1.3
 * IN4 -> P1.4
 * ENB -> P1.5
 */
sbit ENA = P1^0;
sbit IN1 = P1^1;
sbit IN2 = P1^2;
sbit IN3 = P1^3;
sbit IN4 = P1^4;
sbit ENB = P1^5;

/*
 * 板子资料图里标注：
 * 左红外避障接口：P36
 * 右红外避障接口：P37
 * 红外循迹接口：P34 / P35
 * 超声波接口：P20 / P21
 * 蜂鸣器：P22
 * 舵机：P23
 * 用户按键：P32
 */
sbit IR_LEFT_OBS  = P3^6;   // 左红外避障，常见：检测到障碍为 0
sbit IR_RIGHT_OBS = P3^7;   // 右红外避障，常见：检测到障碍为 0

sbit TRACK_LEFT   = P3^4;   // 左循迹
sbit TRACK_RIGHT  = P3^5;   // 右循迹

sbit ULTR_TRIG    = P2^0;   // HC-SR04 Trig
sbit ULTR_ECHO    = P2^1;   // HC-SR04 Echo

sbit BUZZER       = P2^2;   // 蜂鸣器，若逻辑反了，改 beep() 函数
sbit SERVO        = P2^3;   // 舵机信号，本程序暂未启用
sbit KEY          = P3^2;   // 用户按键，本程序暂未启用

/* ===================== 参数区 ===================== */

// 速度：0~100
#define SPEED_BASE      65
#define SPEED_TURN      55
#define SPEED_BACK      55

// 超声波避障距离阈值，单位 cm
#define OBSTACLE_CM     20

// 红外模块逻辑：大多数模块“检测到障碍/黑线”为 0。
// 如果你的模块相反，把下面两个宏改一下。
#define IR_DETECTED(x)      ((x) == 0)
#define TRACK_BLACK(x)      ((x) == 0)

/* ===================== 全局变量 ===================== */

volatile u8 pwm_count = 0;
volatile u8 left_speed = 0;
volatile u8 right_speed = 0;

/* ===================== 延时函数 ===================== */

void delay_us(u16 us)
{
    while(us--);
}

void delay_ms(u16 ms)
{
    u16 i, j;
    for(i = 0; i < ms; i++)
        for(j = 0; j < 120; j++);
}

/* ===================== 蜂鸣器 ===================== */

void beep(u16 ms)
{
    BUZZER = 0;      // 若蜂鸣器不响或常响，把这里和下面的 1/0 对调
    delay_ms(ms);
    BUZZER = 1;
}

/* ===================== PWM：Timer0 中断 ===================== */

void timer0_init(void)
{
    TMOD &= 0xF0;
    TMOD |= 0x01;        // Timer0，16位定时器模式

    // 11.0592MHz 下约 100us 中断一次
    TH0 = 0xFF;
    TL0 = 0xA4;

    ET0 = 1;
    EA  = 1;
    TR0 = 1;
}

void timer0_isr(void) interrupt 1
{
    TH0 = 0xFF;
    TL0 = 0xA4;

    pwm_count++;
    if(pwm_count >= 100)
        pwm_count = 0;

    ENA = (pwm_count < left_speed) ? 1 : 0;
    ENB = (pwm_count < right_speed) ? 1 : 0;
}

/* ===================== 电机控制 ===================== */

void motor_set_speed(u8 left, u8 right)
{
    if(left > 100) left = 100;
    if(right > 100) right = 100;

    left_speed = left;
    right_speed = right;
}

void motor_stop(void)
{
    motor_set_speed(0, 0);
    IN1 = 0; IN2 = 0;
    IN3 = 0; IN4 = 0;
}

void motor_forward(u8 speed)
{
    motor_set_speed(speed, speed);

    // 左电机正转
    IN1 = 1; IN2 = 0;

    // 右电机正转
    IN3 = 1; IN4 = 0;
}

void motor_back(u8 speed)
{
    motor_set_speed(speed, speed);

    IN1 = 0; IN2 = 1;
    IN3 = 0; IN4 = 1;
}

void motor_left(u8 speed)
{
    motor_set_speed(speed, speed);

    // 原地左转：左轮后退，右轮前进
    IN1 = 0; IN2 = 1;
    IN3 = 1; IN4 = 0;
}

void motor_right(u8 speed)
{
    motor_set_speed(speed, speed);

    // 原地右转：左轮前进，右轮后退
    IN1 = 1; IN2 = 0;
    IN3 = 0; IN4 = 1;
}

void motor_soft_left(void)
{
    // 差速左转：左慢右快
    motor_set_speed(35, SPEED_BASE);
    IN1 = 1; IN2 = 0;
    IN3 = 1; IN4 = 0;
}

void motor_soft_right(void)
{
    // 差速右转：左快右慢
    motor_set_speed(SPEED_BASE, 35);
    IN1 = 1; IN2 = 0;
    IN3 = 1; IN4 = 0;
}

/* ===================== HC-SR04 超声波测距 ===================== */

u16 ultrasonic_get_cm(void)
{
    u16 time_count = 0;
    u16 timeout = 0;
    u16 distance = 999;

    ULTR_TRIG = 0;
    delay_us(20);
    ULTR_TRIG = 1;
    delay_us(120);       // 给一个大于 10us 的触发脉冲
    ULTR_TRIG = 0;

    // 等待 Echo 拉高，防止死等
    timeout = 60000;
    while(!ULTR_ECHO && timeout--);

    if(timeout == 0)
        return 999;

    // Echo 高电平计时，粗略测距
    time_count = 0;
    while(ULTR_ECHO)
    {
        delay_us(10);
        time_count++;

        if(time_count > 3000)   // 超时，约对应很远距离
            break;
    }

    // 粗略换算：该 delay_us 非严格微秒，实际距离可能需要校准
    // 对避障来说，只需要一个近距离阈值即可
    distance = time_count / 6;

    return distance;
}

/* ===================== 行为逻辑 ===================== */

bit has_obstacle(void)
{
    u16 cm;

    if(IR_DETECTED(IR_LEFT_OBS))  return 1;
    if(IR_DETECTED(IR_RIGHT_OBS)) return 1;

    cm = ultrasonic_get_cm();
    if(cm < OBSTACLE_CM) return 1;

    return 0;
}

void avoid_obstacle(void)
{
    motor_stop();
    beep(80);
    delay_ms(100);

    motor_back(SPEED_BACK);
    delay_ms(350);

    motor_stop();
    delay_ms(80);

    // 简单避障策略：优先右转
    motor_right(SPEED_TURN);
    delay_ms(450);

    motor_stop();
    delay_ms(80);
}

void line_tracking(void)
{
    bit left_black;
    bit right_black;

    left_black  = TRACK_BLACK(TRACK_LEFT);
    right_black = TRACK_BLACK(TRACK_RIGHT);

    /*
     * 两路循迹逻辑：
     * 左黑右黑：直行
     * 左黑右白：向左修正
     * 左白右黑：向右修正
     * 左白右白：直行/寻找线
     *
     * 如果你的模块黑白逻辑相反，改 TRACK_BLACK 宏。
     */
    if(left_black && right_black)
    {
        motor_forward(SPEED_BASE);
    }
    else if(left_black && !right_black)
    {
        motor_soft_left();
    }
    else if(!left_black && right_black)
    {
        motor_soft_right();
    }
    else
    {
        motor_forward(45);
    }
}

/* ===================== 主函数 ===================== */

void main(void)
{
    BUZZER = 1;
    motor_stop();
    timer0_init();

    beep(100);
    delay_ms(500);

    while(1)
    {
        if(has_obstacle())
        {
            avoid_obstacle();
        }
        else
        {
            line_tracking();
        }

        delay_ms(20);
    }
}
