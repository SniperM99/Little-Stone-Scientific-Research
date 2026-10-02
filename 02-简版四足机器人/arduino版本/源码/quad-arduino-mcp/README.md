# 小智AI语音控制 Quad 四足机器人 arduino 代码

### 淘宝链接:  
小智Ai对话机器人: https://item.taobao.com/item.htm?ft=t&id=973456274597  
四足机器人: https://item.taobao.com/item.htm?ft=t&id=888872820389

### 说明:   
安装开发板和依赖库版本的时候, 直接安装最新版就可以, 不一定按下面这些版本  
如果安装最新版有问题, 再尝试回退到以下提供的版本  
以下提供的版本是测试过可用的  

### ESP32开发板 (不带C, 不带S):
 - arduino安装开发板: ESP32 (by Espressif Systems 3.3.0)  
 - arduino选择开发板: ESP32 Dev Module  

### 依赖库:
 - ESP32Servo (by Kevin Harrington 3.0.9)
 - WebSockets (by Markus Sattler 2.7.0)
 - ArduinoJson (by Benoit Blanchon 7.4.2)
 - xiaozhi-mcp (by toddpan 1.0.0)

### 需要修改的地方:  

#### 1. 修改文件夹名称
如果是从 `github` 或 `gitee` 下载 `zip` 包代码, 解压后的文件夹名称可能是 `quad-arduino-mcp-master`  
必须把 `quad-arduino-mcp-master` 重命名为 `quad-arduino-mcp`  
目录名 `quad-arduino-mcp` 与 `arduino` 主文件名 `quad-arduino-mcp.ino` 保持一致  
`arduino` 才能正确识别  

#### 2. 修改 `quad-arduino-mcp.ino`
```C++
// quad-arduino-mcp.ino
const char* WIFI_SSID = "您的wifi名称";  
const char* WIFI_PASS = "您的wifi密码";  
const char* MCP_ENDPOINT = "ws://api.xiaozhi.me/mcp/?token=<您的小智MCP接入点token>";  
```


### 补充:  
#### 1. 小智AI官网: https://xiaozhi.me/    
小智AI烧录固件, 设备配网, 绑定设备等操作可以参考小智AI`DIY教程`    

#### 2. arduino安装esp32开发板(使用国内镜像)视频说明:  
https://www.bilibili.com/video/BV1Fr84zKEma/

#### 3. 小智AI MCP_ENDPOINT 接入点获取演示:
https://www.bilibili.com/video/BV1Jq8szFEhF/

#### 4. esp32 arduino 入门视频教程:
https://www.bilibili.com/video/BV1RM4y1a7J5/
