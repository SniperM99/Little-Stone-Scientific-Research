
STC89C52RC 智能小车程序说明
==========================

文件：
- main.c：Keil C51 工程主程序

推荐编译环境：
- Keil uVision + C51
- 芯片型号：STC89C52RC / STC89C52RC-LQFP/DIP40
- 晶振：11.0592MHz

默认引脚：
- L298N 电机驱动：
  ENA=P1.0, IN1=P1.1, IN2=P1.2, IN3=P1.3, IN4=P1.4, ENB=P1.5
- 左红外避障：P3.6
- 右红外避障：P3.7
- 左循迹：P3.4
- 右循迹：P3.5
- 超声波 Trig：P2.0
- 超声波 Echo：P2.1
- 蜂鸣器：P2.2
- 舵机：P2.3
- 用户按键：P3.2

烧录流程：
1. Keil 新建工程，选择 AT89C52 或兼容 8052。
2. 添加 main.c。
3. Options for Target -> Output -> 勾选 Create HEX File。
4. 编译生成 .hex 文件。
5. 打开 STC-ISP，型号选 STC89C52RC/LE52RC。
6. 串口选 USB-SERIAL CH340 对应的 COM 口。
7. 打开程序文件，选择 Keil 生成的 .hex。
8. 小车断电。
9. 点“下载/编程”。
10. 给小车重新上电。

调试注意：
- 第一次烧录前请把小车架空，避免轮子乱转。
- 如果电机方向反了，交换电机线，或修改 motor_forward/motor_back 函数。
- 如果循迹逻辑反了，修改 main.c 里的 TRACK_BLACK 宏。
- 如果红外避障逻辑反了，修改 main.c 里的 IR_DETECTED 宏。
