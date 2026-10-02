import asyncio
import json
import logging
import os
import signal
import subprocess
import sys
from typing import Optional

import websockets


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - MCP_PIPE - %(levelname)s - %(message)s",
)

logger = logging.getLogger("MCP_PIPE")
mcp_key = """
wss://api.xiaozhi.me/mcp/?token=YOUR_MCP_TOKEN
"""

def get_mcp_endpoint() -> str:
    endpoint = os.environ.get("MCP_ENDPOINT", mcp_key).strip()
    print(endpoint)
    if not endpoint:
        logger.error("环境变量 MCP_ENDPOINT 没有设置")
        logger.error("请先执行：$env:MCP_ENDPOINT=\"你的小智MCP接入点\"")
        sys.exit(1)

    return endpoint


def get_server_command() -> list[str]:
    if len(sys.argv) < 2:
        logger.error("请指定 MCP Server 文件")
        logger.error("示例：python mcp_pipe.py servo_robot_mcp.py")
        sys.exit(1)

    server_script = sys.argv[1]

    if not os.path.exists(server_script):
        logger.error("找不到 MCP Server 文件: %s", server_script)
        sys.exit(1)

    return [sys.executable, server_script]


async def websocket_to_process(websocket, process: subprocess.Popen):
    """
    小智 WebSocket -> 本地 MCP Server stdin
    """
    try:
        async for message in websocket:
            if isinstance(message, bytes):
                message = message.decode("utf-8")

            logger.info("WebSocket -> MCP Server: %s", message[:200])

            if process.stdin is None:
                logger.error("MCP Server stdin 不可用")
                break

            process.stdin.write(message + "\n")
            process.stdin.flush()

    except websockets.exceptions.ConnectionClosed as e:
        logger.warning("WebSocket 连接关闭: %s", e)

    except Exception as e:
        logger.exception("websocket_to_process 出错: %s", e)


async def process_to_websocket(websocket, process: subprocess.Popen):
    """
    本地 MCP Server stdout -> 小智 WebSocket
    """
    loop = asyncio.get_running_loop()

    try:
        while True:
            if process.stdout is None:
                logger.error("MCP Server stdout 不可用")
                break

            line = await loop.run_in_executor(None, process.stdout.readline)

            if not line:
                logger.warning("MCP Server stdout 已关闭")
                break

            line = line.strip()

            if not line:
                continue

            logger.info("MCP Server -> WebSocket: %s", line[:200])

            await websocket.send(line)

    except websockets.exceptions.ConnectionClosed as e:
        logger.warning("WebSocket 连接关闭: %s", e)

    except Exception as e:
        logger.exception("process_to_websocket 出错: %s", e)


async def read_process_stderr(process: subprocess.Popen):
    """
    读取 MCP Server stderr，用于显示日志
    注意：MCP Server 里不要 print，日志通常会走 stderr
    """
    loop = asyncio.get_running_loop()

    try:
        while True:
            if process.stderr is None:
                break

            line = await loop.run_in_executor(None, process.stderr.readline)

            if not line:
                break

            line = line.strip()
            if line:
                logger.info("MCP Server stderr: %s", line)

    except Exception as e:
        logger.exception("读取 MCP Server stderr 出错: %s", e)


def stop_process(process: Optional[subprocess.Popen]):
    if process is None:
        return

    if process.poll() is not None:
        return

    logger.info("正在停止 MCP Server 进程")

    try:
        process.terminate()
        process.wait(timeout=5)
    except Exception:
        try:
            process.kill()
        except Exception:
            pass


async def run_pipe():
    endpoint = get_mcp_endpoint()
    command = get_server_command()

    logger.info("Connecting to WebSocket server...")
    logger.info("MCP endpoint: %s", endpoint)

    process: Optional[subprocess.Popen] = None

    try:
        async with websockets.connect(
            endpoint,
            ping_interval=20,
            ping_timeout=20,
            proxy=None,
        ) as websocket:
            logger.info("Successfully connected to WebSocket server")

            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )

            logger.info("Started MCP server process: %s", " ".join(command))

            task_ws_to_proc = asyncio.create_task(
                websocket_to_process(websocket, process)
            )
            task_proc_to_ws = asyncio.create_task(
                process_to_websocket(websocket, process)
            )
            task_stderr = asyncio.create_task(
                read_process_stderr(process)
            )

            done, pending = await asyncio.wait(
                [task_ws_to_proc, task_proc_to_ws, task_stderr],
                return_when=asyncio.FIRST_COMPLETED,
            )

            for task in pending:
                task.cancel()

    finally:
        stop_process(process)


def main():
    try:
        asyncio.run(run_pipe())
    except KeyboardInterrupt:
        logger.info("用户中断，程序退出")
    except Exception as e:
        logger.exception("mcp_pipe 运行失败: %s", e)


if __name__ == "__main__":
    main()