import asyncio
import base64
import hashlib
import json
import os
import struct
import zlib

import websockets
from dotenv import load_dotenv
from from_root import from_root

load_dotenv(from_root(".env"))

# --- Config ---
BLYNK_URL = "wss://cbws.storeitcold.com/websocket"
EMAIL = os.environ.get("SIT_EMAIL")
PASSWORD = os.environ.get("SIT_PASSWORD")

# --- Command Codes ---
CMD_RESPONSE = 0x00
CMD_LOGIN = 0x02
CMD_PING = 0x06
CMD_HARDWARE = 0x14
CMD_LOAD_PROFILE_GZIPPED = 0x18

CMD_NAMES = {
    0x00: "RESPONSE",
    0x01: "REGISTER",
    0x02: "LOGIN",
    0x03: "REDEEM",
    0x04: "HARDWARE_CONNECTED",
    0x05: "GET_TOKEN",
    0x06: "PING",
    0x07: "ACTIVATE_DASHBOARD",
    0x08: "DEACTIVATE_DASHBOARD",
    0x09: "REFRESH_TOKEN",
    0x0A: "GET_GRAPH_DATA",
    0x0B: "GET_GRAPH_DATA_RESPONSE",
    0x0E: "NOTIFY",
    0x10: "HW_SYNC",
    0x11: "HW_INFO",
    0x13: "SET_WIDGET_PROPERTY",
    0x14: "HARDWARE",
    0x18: "LOAD_PROFILE_GZIPPED",
    0x19: "APP_SYNC",
    0x32: "APP_CONNECTED",
    0x47: "HARDWARE_DISCONNECTED",
}

STATUS_CODES = {
    200: "OK",
    2: "Illegal command",
    4: "Not authenticated",
    5: "Not allowed",
    6: "Device not in network",
    7: "No active dashboard",
    8: "Invalid token",
    9: "Device went offline",
    11: "Server error",
    17: "String too long",
    18: "Not supported",
    19: "Outdated application",
}

# Client → server: request full profile
PING_PACKET = struct.pack(">BHH", CMD_LOAD_PROFILE_GZIPPED, 2, 0)

# Pin assignments
PIN_SET_TEMP = 4  # setTemp — desired target temperature (°F)
PIN_FINS_SET_TEMP = 6
PIN_TOO_COLD = 16
PIN_TOO_HOT = 12


def hash_password(password: str, email: str) -> str:
    email_hash = hashlib.sha256(email.lower().encode("utf-8")).digest()
    return base64.b64encode(
        hashlib.sha256(password.encode("utf-8") + email_hash).digest()
    ).decode()


def build_login_packet(email: str, msg_id: int = 1) -> bytes:
    body = "\0".join(
        [email, hash_password(PASSWORD, email), "Other", "12220000", "Blynk"]
    )
    body_bytes = body.encode()
    header = struct.pack(">BHH", CMD_LOGIN, msg_id, len(body_bytes))
    return header + body_bytes


def build_hardware_packet(
    dashboard_id: int, device_id: int, pin: int, value, msg_id: int = 3
) -> bytes:
    body = f"{dashboard_id}-{device_id}\x00vw\x00{pin}\x00{value}".encode()
    header = struct.pack(">BHH", CMD_HARDWARE, msg_id, len(body))
    return header + body


def build_response_packet(msg_id: int, status: int = 200) -> bytes:
    return struct.pack(">BHH", CMD_RESPONSE, msg_id, status)


def parse_packet(data: bytes) -> dict:
    if len(data) < 5:
        return {"error": f"Packet too short ({len(data)} bytes)", "raw": data.hex()}

    cmd, msg_id, field = struct.unpack(">BHH", data[:5])
    cmd_name = CMD_NAMES.get(cmd, f"UNKNOWN(0x{cmd:02X})")
    result = {"command": cmd, "command_name": cmd_name, "msg_id": msg_id}

    if cmd == CMD_RESPONSE:
        result["status"] = field
        result["status_text"] = STATUS_CODES.get(field, f"Unknown ({field})")
        result["success"] = field == 200
    elif cmd == CMD_LOAD_PROFILE_GZIPPED:
        body_bytes = data[5 : 5 + field]
        try:
            decompressed = zlib.decompress(body_bytes)
            result["profile"] = json.loads(decompressed)
        except Exception as e:
            result["body_raw"] = body_bytes.hex()
            result["decompress_error"] = str(e)
    else:
        body_bytes = data[5 : 5 + field]
        body_str = body_bytes.decode("utf-8", errors="replace")
        parts = body_str.split("\0")
        result["body"] = body_str
        result["parts"] = parts
        if cmd == CMD_HARDWARE and len(parts) >= 3:
            result["device_ref"] = parts[0]
            result["pin_type"] = parts[1]
            result["pin"] = parts[2]
            result["value"] = parts[3:]

    return result


async def blynk_login(ws) -> bool:
    login_packet = build_login_packet(EMAIL)
    await ws.send(login_packet)
    resp = await ws.recv()
    resp_bytes = resp if isinstance(resp, bytes) else resp.encode()
    parsed = parse_packet(resp_bytes)
    return parsed.get("success", False)


async def updateCoolbot(temperature: int) -> None:
    """Connect to the Coolbot via WebSocket, set the target temperature, and disconnect."""
    async with websockets.connect(BLYNK_URL) as ws:
        if not await blynk_login(ws):
            raise RuntimeError("Coolbot login failed")

        await ws.send(PING_PACKET)

        while True:
            raw = await ws.recv()
            data = raw if isinstance(raw, bytes) else raw.encode()
            parsed = parse_packet(data)
            cmd = parsed.get("command")

            if cmd == CMD_PING:
                await ws.send(build_response_packet(parsed["msg_id"], 200))

            elif cmd == CMD_LOAD_PROFILE_GZIPPED:
                profile = parsed.get("profile")
                if not profile:
                    raise RuntimeError(
                        f"Failed to load profile: {parsed.get('decompress_error')}"
                    )
                dashboards = profile.get("dashBoards", [])
                if not dashboards:
                    raise RuntimeError("No dashboards found in profile")
                dashboard_id = dashboards[0]["id"]
                devices = dashboards[0].get("devices", [])
                device_id = devices[0]["id"] if devices else 0

                pkt = build_hardware_packet(
                    dashboard_id, device_id, PIN_SET_TEMP, temperature
                )
                await ws.send(pkt)
                return


def change_setpoint(updated_value: int) -> None:
    """Set the CoolBot target temperature via WebSocket."""
    try:
        print(f"Temperature setpoint changed to {updated_value}")
        asyncio.run(updateCoolbot(updated_value))
    except Exception as e:
        print(f"An error occurred in coolbot/change_setpoint function:\n {e}")


async def readCoolbot(pin: int = PIN_SET_TEMP) -> float | None:
    """Fetch the last-written value for a virtual pin from the dashboard's pinsStorage.

    The server caches every vw write in pinsStorage keyed as "{device_id}-v{pin}",
    so no vr round-trip to the hardware is needed.
    """
    async with websockets.connect(BLYNK_URL) as ws:
        if not await blynk_login(ws):
            raise RuntimeError("Coolbot login failed")

        await ws.send(PING_PACKET)

        while True:
            raw = await ws.recv()
            data = raw if isinstance(raw, bytes) else raw.encode()
            parsed = parse_packet(data)
            cmd = parsed.get("command")

            if cmd == CMD_PING:
                await ws.send(build_response_packet(parsed["msg_id"], 200))

            elif cmd == CMD_LOAD_PROFILE_GZIPPED:
                profile = parsed.get("profile")
                if not profile:
                    raise RuntimeError(
                        f"Failed to load profile: {parsed.get('decompress_error')}"
                    )
                dashboards = profile.get("dashBoards", [])
                if not dashboards:
                    raise RuntimeError("No dashboards found in profile")
                devices = dashboards[0].get("devices", [])
                device_id = devices[0]["id"] if devices else 0

                pins_storage = dashboards[0].get("pinsStorage", {})
                key = f"{device_id}-v{pin}"
                raw_value = pins_storage.get(key)
                if raw_value is None:
                    raise RuntimeError(
                        f"Pin {pin} not found in pinsStorage (key={key!r})"
                    )
                try:
                    return float(raw_value)
                except ValueError:
                    return raw_value


def get_coolbot_temp() -> float | None:
    """Read the current CoolBot set temperature via WebSocket."""
    try:
        return asyncio.run(readCoolbot(PIN_SET_TEMP))
    except Exception as e:
        print(f"An error occurred in coolbot/get_coolbot_temp function:\n {e}")
        return None


def get_sensor_temp() -> float:
    """Read external temperature sensor from EasyLogCloud.

    NOTE: EasyLogCloud integration has been removed along with Selenium.
    Returns None; callers should handle this gracefully.
    """
    print("get_sensor_temp: EasyLogCloud integration not available, returning None")
    return None
