# INNFOS / MINTASCA 六轴机械臂官方控制工程说明

整理日期：2026-05-16  
本次只做源码、二进制符号、README、SDK 头文件、示例和 `parameter.db` 的静态分析；没有执行任何会使机械臂使能或运动的命令。

## 1. 仓库用途

目标仓库：`https://github.com/mintasca/innfos-gluon-controller.git`

当前工作区已有源码快照：`D:\小石头\12-CAN控制的机械臂\innfos-gluon-controller-master`

该工程是 INNFOS / MINTASCA 桌面级 6 轴机械臂的官方控制包，面向 Linux x86_64，提供：

- `robotserver`：预编译机械臂控制程序，按 `mode0` 到 `mode4` 运行。
- `setrobot`：预编译机型配置程序，内部符号显示会调用 `UpdateRobotType` 更新机器人类型。
- `parameter.db`：SQLite 参数库，保存不同机械臂构型的速度、加速度、减速比、旋向、DH 参数、动力学/补偿参数。
- `innfos-cpp-sdk`：INNFOS 执行器 C++ SDK，封装执行器查找、使能、失能、模式切换、电流/速度/位置控制、参数读写、错误读取等 API。
- `file`：示教和再现使用的轨迹文件目录。

官方路径的核心假设是：PC 通过以太网连接 ECB/ECU，ECB/ECU 再连接 HUB 和各关节执行器。SDK 公开接口不直接暴露 ZLG CAN 设备，而是通过以太网或串口通信单元发包。

## 2. 目录结构

```text
innfos-gluon-controller-master/
  README.md                         官方中文说明，含硬件连接和 mode0-mode4 用法
  environment                       Linux 动态库路径配置脚本
  robotserver                       Linux x86_64 预编译控制程序
  setrobot                          Linux x86_64 预编译机型设置程序
  parameter.db                      SQLite 参数库
  file/
    trajectory.txt                  mode1 连续示教生成，mode2 再现
    data.txt                        mode3 点位示教生成，mode4 再现
    dancing.txt/look.txt/snake.txt  示例轨迹
  sdk/lib/libkdl.so                 运动学/轨迹相关动态库
  innfos-cpp-sdk/
    README.md                       SDK 环境说明
    example/                        SDK 示例程序
    sdk/include/                    SDK 头文件
    sdk/lib/linux_x86_64/           Linux SDK 动态库
    sdk/lib/windows_x64/            Windows SDK 动态库/导入库
    tools/logtool/                  日志工具
```

## 3. 运行环境

README 和 SDK README 给出的环境要求：

- 机械臂控制程序：`linux-x86-64`。
- Linux：Ubuntu 16.04 LTS 或以上，GCC 4.8 或以上，支持 C++11，安装 CMake。
- Windows SDK 示例：Windows 7 SP1 以上 64 位，Visual Studio 2015，CMake。
- 执行器供电：README 写明执行器供电电压范围为 DC 24 V 到 45 V，机械臂常用供电 42 V。
- 官方通信链路：PC 通过网线连接 `ECB`，执行器通过 `ECB+HUB` 连接。

Linux 运行前配置动态库：

```sh
cd innfos-gluon-controller-master
. environment
```

`environment` 内容：

```sh
export LD_LIBRARY_PATH=$PWD/sdk/lib/:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$PWD/innfos-cpp-sdk/sdk/lib/linux_x86_64/:$LD_LIBRARY_PATH
```

## 4. 启动与关闭命令

进入主目录：

```sh
cd innfos-gluon-controller-master
. environment
```

官方运行格式：

```sh
./robotserver mode0
./robotserver mode1
./robotserver mode2
./robotserver mode3
./robotserver mode4
```

安全要求：

- 不要在未确认现场安全、急停、电源、机械臂空间和人员位置前执行 `mode1`、`mode2`、`mode3`、`mode4`。
- `mode0` 是关闭执行器使能的安全流程，但执行前也要先扶住机械臂，因为失能后关节可能下垂。
- 断电前，README 明确要求在机械臂停止状态下，手扶机械臂并执行 `mode0` 关闭电机使能，然后再关闭电源。

## 5. mode0 到 mode4 作用

| 模式 | 作用 | 运动风险 |
|---|---|---|
| `mode0` | 关闭机械臂使能状态。断电前应执行。 | 会失去电机保持力，需扶住机械臂。 |
| `mode1` | 连续记录轨迹，终端输入 `start` 开始记录，`Ctrl+C` 停止，保存到 `file/trajectory.txt`。 | 示教/拖动相关，需真实设备安全确认。 |
| `mode2` | 循环再现 `mode1` 生成的 `file/trajectory.txt`，输入速度比例 0.1 到 1。 | 会运动，不可自动执行。 |
| `mode3` | 逐步记录路径点，保存到 `file/data.txt`。可选 `MOVJ`、`MOVL`、`MOVC`。 | 示教/拖动相关，需真实设备安全确认。 |
| `mode4` | 按 `mode3` 生成的 `file/data.txt` 再现。先输入速度比例，再选 `STEP`、`CYCLE`、`CONTINUOUS`。 | 会运动，不可自动执行。 |

插补模式：

- `MOVJ`：关节插补，只在关节空间规划，末端轨迹不保证为直线。
- `MOVL`：直线插补，末端轨迹为直线。
- `MOVC`：圆弧插补，需要记录辅助点和终点。

`mode4` 再现模式：

- `STEP`：单步运行，可输入 `FORWARD` 到下一点，或 `BACKWARD` 到上一点。
- `CYCLE`：单循环运行一次。
- `CONTINUOUS`：连续循环运行。

## 6. parameter.db 关键内容

`parameter.db` 是 SQLite 数据库，表结构一致：`ID, NAME, VALUE, UNITS`。

机型表：

- `FREE_COMBINATION`
- `GL_2L6_4L3`
- `GL_2P8_P6_3P3`
- `GL_4L3`
- `GL_6L3`
- `GL_6L6`
- `system_parameters`

`system_parameters` 当前值：

| 参数 | 当前值 | 含义 |
|---|---|---|
| `MECHANICAL_TYPE` | `GL_2L6_4L3` | 当前机械臂构型 |
| `FREE_FORCE_SWITCH` | `OFF` | 自由力/拖动补偿开关 |
| `FREE_FORCE_FACTOR` | `1.0` | 自由力系数 |
| `COLLISION DETECTION_SWITCH` | `OFF` | 碰撞检测开关 |
| `COLLISION DETECTION_FACTOR` | `1.0` | 碰撞检测系数 |

六轴常见表：

- `GL_6L3`：减速比 `{36,36,36,36,36,36}`，旋向 `{-1,-1,1,-1,-1,-1}`，DH 参数 `{114,174,174,79.5,80.5,43.5}`。
- `GL_6L6`：减速比 `{36,36,36,36,36,36}`，旋向 `{-1,-1,1,-1,-1,-1}`，DH 参数 `{120.5,254,254,116.5,116.5,62}`。
- `GL_2L6_4L3`：减速比 `{36,36,36,36,36,36}`，旋向 `{-1,-1,1,-1,-1,-1}`，DH 参数 `{120.5,203.5,173,116.5,79.5,42}`。

如果真实机械臂与当前 `MECHANICAL_TYPE` 不一致，应先确认机型，再考虑使用 `setrobot` 修改。`setrobot` 是二进制，未提供源码，本次没有执行。

## 7. innfos-cpp-sdk API 清单

主要头文件：`innfos-cpp-sdk/sdk/include/actuatorcontroller.h`、`actuatordefine.h`。

### 7.1 控制器生命周期和扫描

- `ActuatorController::initController()`
- `ActuatorController::getInstance()`
- `ActuatorController::processEvents()`
- `lookupActuators(ErrorsDefine &ec)`
- `hasAvailableActuator()`
- `getActuatorIdArray()`
- `getActuatorUnifiedIDArray()`
- `getUnifiedIDGroup(ipAddress)`
- `versionString()`

### 7.2 使能、失能、模式

- `enableAllActuators()`
- `disableAllActuators()`
- `enableActuator(id, ipAddress)`
- `enableActuatorInBatch(unifiedIDArray)`
- `disableActuator(id, ipAddress)`
- `activateActuatorMode(id, nMode, ipAddress)`
- `activateActuatorModeInBantch(idArray, nMode)`
- `getActuatorMode(id, ipAddress)`
- `isEnable(id, ipAddress)`

执行器模式枚举：

| 枚举 | 值 | 作用 |
|---|---:|---|
| `Mode_None` | 0 | 无模式 |
| `Mode_Cur` | 1 | 电流模式 |
| `Mode_Vel` | 2 | 速度模式 |
| `Mode_Pos` | 3 | 位置模式 |
| `Mode_Teaching` | 4 | 教学模式，头文件标注暂未实现 |
| `Mode_Profile_Pos` | 6 | Profile 位置模式，有加减速 |
| `Mode_Profile_Vel` | 7 | Profile 速度模式，有加减速 |
| `Mode_Homing` | 8 | 归零模式 |

### 7.3 位置控制

- `setPosition(id, pos, ipAddress)`，单位：圈数。
- `getPosition(id, bRefresh, ipAddress)`，单位：圈数。
- `setPositionKp/Ki/Kd()`、`getPositionKp/Ki/Kd()`
- `setPositionUmax/Umin()`、`getPositionUmax/Umin()`
- `setPositionOffset()`、`getPositionOffset()`
- `setMaximumPosition()`、`getMaximumPosition()`
- `setMinimumPosition()`、`getMinimumPosition()`
- `enablePositionLimit()`、`isPositionLimitEnable()`
- `setHomingPosition()`、`clearHomingInfo()`
- `enablePositionFilter()`、`isPositionFilterEnable()`
- `setPositionCutoffFrequency()`、`getPositionCutoffFrequency()`
- `setProfilePositionAcceleration()`、`getProfilePositionAcceleration()`
- `setProfilePositionDeceleration()`、`getProfilePositionDeceleration()`
- `setProfilePositionMaxVelocity()`、`getProfilePositionMaxVelocity()`

### 7.4 速度控制

- `setVelocity(id, vel, ipAddress)`，单位：转/分钟。
- `getVelocity(id, bRefresh, ipAddress)`
- `setVelocityKp/Ki()`、`getVelocityKp/Ki()`
- `setVelocityUmax/Umin()`、`getVelocityUmax/Umin()`
- `getVelocityRange()`
- `enableVelocityFilter()`、`isVelocityFilterEnable()`
- `setVelocityCutoffFrequency()`、`getVelocityCutoffFrequency()`
- `setVelocityLimit()`、`getVelocityLimit()`
- `setProfileVelocityAcceleration()`、`getProfileVelocityAcceleration()`
- `setProfileVelocityDeceleration()`、`getProfileVelocityDeceleration()`

### 7.5 电流控制

- `setCurrent(id, current, ipAddress)`
- `getCurrent(id, bRefresh, ipAddress)`
- `getCurrentKp()`、`getCurrentKi()`
- `getCurrentRange()`
- `enableCurrentFilter()`、`isCurrentFilterEnable()`
- `setCurrentCutoffFrequency()`、`getCurrentCutoffFrequency()`
- `setCurrentLimit()`、`getCurrentLimit()`

### 7.6 参数、状态、错误、回调

- `saveAllParams(id, ipAddress)`
- `getVoltage()`
- `getLockEnergy()`、`setLockEnergy()`
- `getMotorTemperature()`、`getInverterTemperature()`
- `getMotorProtectedTemperature()`、`setMotorProtectedTemperature()`
- `getMotorRecoveryTemperature()`、`setMotorRecoveryTemperature()`
- `getInverterProtectedTemperature()`、`setInverterProtectedTemperature()`
- `getInverterRecoveryTemperature()`、`setInverterRecoveryTemperature()`
- `isOnline()`
- `enableHeartbeat()`、`disableHeartbeat()`
- `setActuatorID()`
- `getActuatorSerialNumber()`
- `getErrorCode()`
- `getErrorHistory()`
- `clearError()`
- `reconnect()`
- `regainAttribute()`
- `requestCVPValue()`，一次请求电流、速度、位置。
- `setActuatorAttribute()`、`getActuatorAttribute()`
- `addParaRequestCallback()`、`addErrorCallback()`、`clearCallbackHandlers()`

### 7.7 图表/日志相关

- `setChartFrequency()`、`getChartFrequency()`
- `setChartThreshold()`、`getChartThreshold()`
- `enableChart()`、`isChartEnable()`
- `openChartChannel()`、`closeChartChannel()`
- `setCurrentChartMode()`

## 8. 6 轴控制流程

官方 SDK 示例给出的最小流程：

1. 初始化：

```cpp
ActuatorController *pController = ActuatorController::initController();
```

2. 查找执行器：

```cpp
Actuator::ErrorsDefine ec;
std::vector<ActuatorController::UnifiedID> ids = pController->lookupActuators(ec);
```

3. 确认找到 6 个执行器，记录每个执行器的 `actuatorID` 和 `ipAddress`。

4. 批量使能：

```cpp
pController->enableActuatorInBatch(ids);
```

5. 激活目标模式。常见选择：

```cpp
pController->activateActuatorMode(id, Actuator::Mode_Profile_Pos, ip);
```

6. 控制每个执行器。位置控制示例：

```cpp
pController->setPosition(id, target_revolutions, ip);
```

7. 持续读取状态和错误：

```cpp
pController->requestCVPValue(id, ip);
double pos = pController->getPosition(id, true, ip);
uint32_t err = pController->getErrorCode(id, ip);
```

8. 停止时关闭使能：

```cpp
pController->disableAllActuators();
```

关节角到执行器圈数的换算需要结合 `parameter.db`：

```text
motor_revolutions = joint_degrees / 360 * REDUCTION_GEAR_RATIO[j] * ROTATION_DIRECT[j]
```

例如 `GL_6L3` / `GL_6L6` 的六轴减速比均为 36，旋向为 `{-1,-1,1,-1,-1,-1}`。

## 9. 是否可以绕过 ECB，用 ZLG USBCANFD-200U 直连 CAN

结论：可以作为工程方向继续做，但不能仅靠本仓库直接完成。

依据：

- README 明确机械臂官方连接方式是 PC 以太网连接 ECB，ECB/HUB 再连接执行器。
- SDK 的公开通信类型只有 `Via_Ethernet` 和 `Via_Serialport`，公开类有 `EthernetCommunication`、`SerialCommunication`，没有 ZLG、SocketCAN 或通用 CAN 适配层。
- SDK 头文件里存在大量执行器协议指令枚举，例如 `D_SET_MODE=0x07`、`D_SET_CURRENT=0x08`、`D_SET_VELOCITY=0x09`、`D_SET_POSITION=0x0a`、`D_SET_SWITCH_MOTORS=0x2a`、`D_CAN_CONNECT=0x44`、`D_READ_ACTUAL_CVP=0x94`、`D_CLEAR_ERROR=0xfe`。这些说明执行器底层确实有可映射的指令层。
- `IData` / `InnfosProxy` 显示 SDK 会构造带头尾和 CRC 的代理协议包，但头文件没有给出 `AddProxyBegin`、`AddCRCCode` 的实现，核心打包逻辑在闭源动态库中。

因此，绕过 ECB 的路线是：

1. 先用 ZCANPRO 抓取或手工验证直连 CAN 帧。
2. 固化帧格式、CAN ID 规则、大小端、数据缩放、CRC 或校验。
3. 用 ZLG 官方 DLL/API 发送同样的帧。
4. 在 Python 中封装成 `enable/disable/set_mode/set_position/set_velocity/set_current/read_cvp/read_error`。

风险：

- 官方 `robotserver` 和 SDK 不会直接调用 USBCANFD-200U。
- 如果绕过 ECB，`parameter.db` 中的运动学、限速、插补、碰撞检测等上层保护不会自动生效。
- Python/ZLG API 必须自己实现限位、速度限制、急停后的状态恢复、错误清除和失能流程。

## 10. 用户已用 ZCANPRO 验证成功的 CAN 协议帧

当前工作区没有找到 ZCANPRO 导出的文本日志、截图或包含原始 CAN 帧的说明文件；本次无法从仓库静态内容确认“用户已验证成功”的具体帧。

建议把已验证帧按下面格式补入本文档或单独保存为 `zcanpro_verified_frames.md`：

| 功能 | CAN ID | DLC | DATA | 现象 | 备注 |
|---|---:|---:|---|---|---|
| 查询版本/握手 | 待补充 | 待补充 | 待补充 | 执行器回复 | 对应 SDK `D_HANDSHAKE=0x00` 或 `D_READ_VERSION=0x01` |
| 读取当前位置 | 待补充 | 待补充 | 待补充 | 返回位置 | 对应 `D_READ_CUR_POSITION=0x06` 或属性 `ACTUAL_POSITION=0x1a` |
| 读取电流/速度/位置 | 待补充 | 待补充 | 待补充 | 返回 CVP | 对应 `D_READ_ACTUAL_CVP=0x94` |
| 设置模式 | 待补充 | 待补充 | 待补充 | 模式改变 | 对应 `D_SET_MODE=0x07` |
| 使能/失能 | 待补充 | 待补充 | 待补充 | LED/保持力变化 | 对应 `D_SET_SWITCH_MOTORS=0x2a` 或属性 `ACTUATOR_SWITCH=0x3b` |
| 设置位置 | 待补充 | 待补充 | 待补充 | 关节运动 | 对应 `D_SET_POSITION=0x0a` |
| 设置速度 | 待补充 | 待补充 | 待补充 | 速度模式运动 | 对应 `D_SET_VELOCITY=0x09` |
| 设置电流 | 待补充 | 待补充 | 待补充 | 电流模式输出 | 对应 `D_SET_CURRENT=0x08` |
| 清错 | 待补充 | 待补充 | 待补充 | 错误清除 | 对应 `D_CLEAR_ERROR=0xfe` |

## 11. 后续封装 Python/ZLG 控制 API

建议工程结构：

```text
zlg_innfos/
  __init__.py
  zlg_device.py          封装 ZLG USBCANFD DLL 打开、关闭、收发
  innfos_frame.py        封装 CAN ID、DATA、校验、缩放
  actuator.py            单执行器 API
  arm6.py                六轴 API，加入限速、旋向、减速比
  safety.py              限位、速度限制、急停状态、失能流程
  examples/
    01_read_state.py
    02_disable_all.py
    03_enable_hold.py
    04_joint_jog_low_speed.py
```

优先封装的 Python API：

```python
class ZlgInnfosBus:
    def open(self, device_index=0, channel=0, bitrate=1000000): ...
    def close(self): ...
    def send(self, can_id: int, data: bytes): ...
    def recv(self, timeout_ms=100): ...

class InnfosActuator:
    def ping(self) -> bool: ...
    def read_cvp(self) -> tuple[float, float, float]: ...
    def read_error(self) -> int: ...
    def clear_error(self): ...
    def set_mode(self, mode: int): ...
    def enable(self): ...
    def disable(self): ...
    def set_position_rev(self, rev: float): ...
    def set_velocity_rpm(self, rpm: float): ...
    def set_current_amp(self, amp: float): ...

class InnfosArm6:
    def disable_all(self): ...
    def enable_all_hold(self): ...
    def read_joint_degrees(self) -> list[float]: ...
    def move_joint_degrees(self, degrees: list[float], speed_scale=0.1): ...
```

安全策略建议：

- 默认上电后只允许读状态和清错。
- `enable_all_hold()` 必须先读 6 轴当前位置，再把当前位置作为保持目标，避免突然跳变。
- `move_joint_degrees()` 默认速度比例不超过 0.1，第一次运行必须单轴、低速、小角度。
- 所有运动命令前检查目标角度、速度、电流、错误码、急停状态。
- `disable_all()` 执行前提示操作者扶住机械臂。
- 加入日志：每条发送帧、回复帧、解析值、错误码都落盘。

## 12. 本次未执行内容

- 未执行 `robotserver mode0` 到 `mode4`。
- 未执行 `setrobot`。
- 未连接真实机械臂。
- 未发送任何 CAN 帧。
- 未运行会使机械臂使能或运动的 SDK 示例。

