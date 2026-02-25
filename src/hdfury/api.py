"""HDFury Client API."""

import asyncio
import json
import time
from asyncio import TimeoutError
from typing import Literal, cast

import aiohttp
from aiohttp import ClientError, ClientResponseError, ClientTimeout

from .exceptions import HDFuryConnectionError, HDFuryParseError


class HDFuryAPI:
    """Asynchronous API client for HDFury devices."""

    def __init__(self, host: str, session: aiohttp.ClientSession | None = None) -> None:
        """HDFury API Client."""
        self.host: str = host
        self._session: aiohttp.ClientSession = session or aiohttp.ClientSession()
        self._last_command_time: float = 0
        self._debounce_delay: int = 2  # seconds

    @staticmethod
    def _normalize_state(state: str, output: Literal["text", "number"] = "text") -> str:
        """Normalize state and optionally convert return type."""
        state = state.lower()

        if state in ("1", "on"):
            return "on" if output == "text" else "1"

        if state in ("0", "off"):
            return "off" if output == "text" else "0"

        raise HDFuryParseError(f"Invalid state: {state}")

    async def _wait_for_debounce(self) -> None:
        """Wait until at least `_debounce_delay` seconds have passed since the last command."""
        elapsed = time.time() - self._last_command_time
        if elapsed < self._debounce_delay:
            wait_time = self._debounce_delay - elapsed
            await asyncio.sleep(wait_time)

    async def _request(self, endpoint: str) -> str:
        """Handle a request to the HDFury device."""
        url = f"http://{self.host}{endpoint}"

        try:
            async with self._session.get(url, timeout=ClientTimeout(total=10)) as response:
                if response.status != 200:
                    raise HDFuryConnectionError(
                        f"Unexpected response from: {url} (Status: {response.status})"
                    )

                return await response.text()
        except TimeoutError as err:
            raise HDFuryConnectionError(f"Timeout while fetching: {url}") from err
        except (ClientError, ClientResponseError) as err:
            raise HDFuryConnectionError(f"Request failed ({url}): {err}") from err
        except Exception as err:
            raise HDFuryConnectionError(f"Unexpected error ({url}): {err}") from err

    async def _request_json(self, path: str) -> dict[str, str]:
        """Handle a request to the HDFury device and parse JSON."""
        response = await self._request(path)
        try:
            return cast(dict[str, str], json.loads(response))
        except json.JSONDecodeError as err:
            raise HDFuryParseError(f"Unable to decode JSON: {err}") from err

    async def get_board(self) -> dict[str, str]:
        """Fetch board info."""
        await self._wait_for_debounce()
        response = await self._request_json("/ssi/brdinfo.ssi")
        return response

    async def get_info(self) -> dict[str, str]:
        """Fetch device info."""
        await self._wait_for_debounce()
        response = await self._request_json("/ssi/infopage.ssi")
        return response

    async def get_config(self) -> dict[str, str]:
        """Fetch device configuration."""
        await self._wait_for_debounce()
        config_response = await self._request_json("/ssi/confpage.ssi")

        try:
            cec_response = await self._request_json("/ssi/cecpage.ssi")
        except HDFuryConnectionError:
            cec_response = {}
        except HDFuryParseError:
            cec_response = {}

        return {**cec_response, **config_response}

    async def _send_command(self, command: str, option: str = "") -> None:
        """Send a command to the device."""
        await self._request(f"/cmd?{command}={option}")
        self._last_command_time = time.time()

    async def issue_reboot(self) -> None:
        """Send reboot command to the device."""
        await self._send_command("reboot")

    async def issue_hotplug(self) -> None:
        """Send hotplug command to the device."""
        await self._send_command("hotplug")

    async def set_operation_mode(self, mode: str) -> None:
        """Send operation mode command to the device."""
        await self._send_command("opmode", mode)

    async def set_port_selection(self, tx0: str, tx1: str) -> None:
        """Send operation mode command to the device."""
        await self._send_command("insel", f"{tx0}%20{tx1}")

    async def set_auto_switch_inputs(self, state: str) -> None:
        """Send auto switch inputs command to the device."""
        await self._send_command("autosw", self._normalize_state(state, output="text"))

    async def set_audio_unmute(self, state: str) -> None:
        """Send audio unmute (milliseconds) command to the device."""
        await self._send_command("unmutecnt", state)

    async def set_earc_unmute(self, state: str) -> None:
        """Send earc unmute (milliseconds) command to the device."""
        await self._send_command("earcunmutecnt", state)

    async def set_htpc_mode_rx0(self, state: str) -> None:
        """Send htpc mode rx0 command to the device."""
        await self._send_command("htpcmode0", self._normalize_state(state, output="text"))

    async def set_htpc_mode_rx1(self, state: str) -> None:
        """Send htpc mode rx1 command to the device."""
        await self._send_command("htpcmode1", self._normalize_state(state, output="text"))

    async def set_htpc_mode_rx2(self, state: str) -> None:
        """Send htpc mode rx2 command to the device."""
        await self._send_command("htpcmode2", self._normalize_state(state, output="text"))

    async def set_htpc_mode_rx3(self, state: str) -> None:
        """Send htpc mode rx3 command to the device."""
        await self._send_command("htpcmode3", self._normalize_state(state, output="text"))

    async def set_mute_tx0_audio(self, state: str) -> None:
        """Send mute tx0 audio command to the device."""
        await self._send_command("mutetx0audio", self._normalize_state(state, output="text"))

    async def set_mute_tx1_audio(self, state: str) -> None:
        """Send mute tx1 audio command to the device."""
        await self._send_command("mutetx1audio", self._normalize_state(state, output="text"))

    async def set_tx0_force_5v(self, state: str) -> None:
        """Send tx0 force +5v command to the device."""
        await self._send_command("tx0plus5", self._normalize_state(state, output="text"))

    async def set_tx1_force_5v(self, state: str) -> None:
        """Send tx1 force +5v command to the device."""
        await self._send_command("tx1plus5", self._normalize_state(state, output="text"))

    async def set_oled(self, state: str) -> None:
        """Send oled command to the device."""
        await self._send_command("oled", self._normalize_state(state, output="text"))

    async def set_oled_fade(self, state: str) -> None:
        """Send oled fade (seconds) command to the device."""
        await self._send_command("oledfade", state)

    async def set_ir_active(self, state: str) -> None:
        """Send ir active command to the device."""
        await self._send_command("iractive", self._normalize_state(state, output="text"))

    async def set_relay(self, state: str) -> None:
        """Send relay command to the device."""
        await self._send_command("relay", self._normalize_state(state, output="text"))

    async def set_cec(self, state: str) -> None:
        """Send cec command to the device."""
        await self._send_command("cec", self._normalize_state(state, output="text"))

    async def set_cec_rx0(self, state: str) -> None:
        """Send cec enable 0 command to the device."""
        await self._send_command("cec0en", self._normalize_state(state, output="number"))

    async def set_cec_rx1(self, state: str) -> None:
        """Send cec enable 1 command to the device."""
        await self._send_command("cec1en", self._normalize_state(state, output="number"))

    async def set_cec_rx2(self, state: str) -> None:
        """Send cec enable 2 command to the device."""
        await self._send_command("cec2en", self._normalize_state(state, output="number"))

    async def set_cec_rx3(self, state: str) -> None:
        """Send cec enable 3 command to the device."""
        await self._send_command("cec3en", self._normalize_state(state, output="number"))

    async def set_reboot_timer(self, state: str) -> None:
        """Send reboot timer (hours) command to the device."""
        await self._send_command("reboottimer", state)

    async def close(self) -> None:
        """Close open client session."""
        if self._session:
            await self._session.close()
