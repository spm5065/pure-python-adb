try:
    from asyncio import get_running_loop
except ImportError:  # pragma: no cover
    from asyncio import get_event_loop as get_running_loop  # Python 3.6 compatibility

import os
from pathlib import Path, PurePosixPath
import re

from ppadb.command.transport_async import TransportAsync
from ppadb.sync_async import SyncAsync


class DeviceAsync(TransportAsync):
    INSTALL_RESULT_PATTERN = "(Success|Failure|Error)\s?(.*)"
    UNINSTALL_RESULT_PATTERN = "(Success|Failure.*|.*Unknown package:.*)"

    def __init__(self, client, serial):
        self.client = client
        self.serial = serial

    async def create_connection(self, set_transport=True, timeout=None):
        conn = await self.client.create_connection(timeout=timeout)

        if set_transport:
            await self.transport(conn)

        return conn

    async def _push(self, src, dest, mode, progress):
        # Create a new connection for file transfer
        sync_conn = await self.sync()
        sync = SyncAsync(sync_conn)

        async with sync_conn:
            await sync.push(src, dest, mode, progress)

    async def push(self, src, dest, mode=0o644, progress=None):
        src = Path(src)
        dest = PurePosixPath(dest)
        if not src.exists():
            raise FileNotFoundError("Cannot find {}".format(src))

        if src.is_file():
            await self._push(src, dest, mode, progress)
        elif src.is_dir():
            src.resolve()
            for root, dirs, files in src.walk():
                subdir = root.relative_to(src)
                destdir = dest / src.name / subdir

                await self.shell(f'mkdir -p "{destdir}"')

                for item in files:
                    await self._push(root / item, destdir / item, mode, progress)

    async def pull(self, src, dest):
        sync_conn = await self.sync()
        sync = SyncAsync(sync_conn)

        async with sync_conn:
            return await sync.pull(src, dest)
