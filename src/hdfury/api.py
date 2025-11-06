"""HDFury Client API."""

from asyncio import TimeoutError
import json

import aiohttp
from aiohttp import ClientError, ClientResponseError

from .exceptions import HDFuryConnectionError, HDFuryParseError


class HDFuryAPI:
    """Asynchronous API client for HDFury devices."""

    def __init__(self, host: str, session: aiohttp.ClientSession | None = None) -> None:
        self.host = host
        self._session = session or aiohttp.ClientSession()

    async def _request(self, endpoint: str) -> str:
        """Handle a request to the HDFury device."""
        url = f"http://{self.host}{endpoint}"

        try:
            async with self._session.get(url, timeout=10) as response:
                if response.status != 200:
                    raise HDFuryConnectionError(f"Unexpected response from: {url} (Status: {response.status})")

                return await response.text()
        except TimeoutError:
            raise HDFuryConnectionError(f"Timeout while fetching: {url}")
        except (ClientError, ClientResponseError) as err:
            raise HDFuryConnectionError(f"Request failed ({url}): {err}") from err
        except Exception as err:
            raise HDFuryConnectionError(f"Unexpected error ({url}): {err}") from err

    async def get_board(self) -> dict:
        """Fetch board info."""
        response = await self._request("/ssi/brdinfo.ssi")
        try:
            return json.loads(response)
        except json.JSONDecodeError as err:
            raise HDFuryParseError(f"Unable to decode JSON: {err}") from err

    async def get_info(self) -> dict:
        """Fetch device info."""
        response = await self._request("/ssi/infopage.ssi")
        try:
            return json.loads(response)
        except json.JSONDecodeError as err:
            raise HDFuryParseError(f"Unable to decode JSON: {err}") from err

    async def get_config(self) -> dict:
        """Fetch device configuration."""
        response = await self._request("/ssi/confpage.ssi")
        try:
            return json.loads(response)
        except json.JSONDecodeError as err:
            raise HDFuryParseError(f"Unable to decode JSON: {err}") from err

    async def _send_command(self, command: str, option: str = "") -> None:
        """Send a command to the device."""
        await self._request(f"/cmd?{command}={option}")

    async def issue_reboot(self) -> None:
        """Send reboot command to the device."""
        await self._send_command("reboot")

    async def issue_hotplug(self) -> None:
        """Send hotplug command to the device."""
        await self._send_command("hotplug")

    async def set_operation_mode(self, mode: str) -> None:
        """Send operation mode command to the device."""
        await self._send_command("opmode", mode)

    async def set_auto_switch_inputs(self, state: str) -> None:
        """Send auto switch inputs command to the device."""
        await self._send_command("autosw", state)

    async def set_htpc_mode_rx0(self, state: str) -> None:
        """Send htpc mode rx0 command to the device."""
        await self._send_command("htpcmode0", state)

    async def set_htpc_mode_rx1(self, state: str) -> None:
        """Send htpc mode rx1 command to the device."""
        await self._send_command("htpcmode1", state)

    async def set_htpc_mode_rx2(self, state: str) -> None:
        """Send htpc mode rx2 command to the device."""
        await self._send_command("htpcmode2", state)

    async def set_htpc_mode_rx3(self, state: str) -> None:
        """Send htpc mode rx3 command to the device."""
        await self._send_command("htpcmode3", state)

    async def set_mute_tx0_audio(self, state: str) -> None:
        """Send mute tx0 audio command to the device."""
        await self._send_command("mutetx0audio", state)

    async def set_mute_tx1_audio(self, state: str) -> None:
        """Send mute tx1 audio command to the device."""
        await self._send_command("mutetx1audio", state)

    async def set_oled(self, state: str) -> None:
        """Send oled command to the device."""
        await self._send_command("oled", state)

    async def set_ir_active(self, state: str) -> None:
        """Send ir active command to the device."""
        await self._send_command("iractive", state)

    async def set_relay(self, state: str) -> None:
        """Send relay command to the device."""
        await self._send_command("relay", state)

    async def close(self) -> None:
        """Close open client session."""
        if self._session:
            await self._session.close()
