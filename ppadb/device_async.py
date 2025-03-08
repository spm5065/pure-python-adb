from pathlib import Path, PurePosixPath
import re

from ppadb import InstallError
from ppadb.command.transport_async import TransportAsync
from ppadb.sync_async import SyncAsync
from ppadb.utils.logger import AdbLogging

try:
    from shlex import quote as cmd_quote
except ImportError:
    from pipes import quote as cmd_quote


logger = AdbLogging.get_logger(__name__)


class DeviceAsync(TransportAsync):
    INSTALL_RESULT_PATTERN = r"(Success|Failure|Error)\s?(.*)"
    UNINSTALL_RESULT_PATTERN = r"(Success|Failure.*|.*Unknown package:.*)"

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

    async def _pull(self, src, dest):
        sync_conn = await self.sync()
        sync = SyncAsync(sync_conn)

        async with sync_conn:
            return await sync.pull(src, dest)

    async def pull(self, src, dest):
        src = PurePosixPath(src)
        dest = Path(dest)

        dir_string = "IS_DIR"
        res = await self.shell(f"[ -d {src} ] && echo {dir_string}")
        if dir_string in res:
            # Get all files in the dir
            # Pull each
            dest.mkdir(exist_ok=True)
            cmd = f"ls -1a {src}"
            res = await self.shell(cmd)
            contents_list = res.split("\n")
            contents_list = [
                x for x in contents_list if x != "." and x != ".." and x != ""
            ]
            for element in contents_list:
                element_src = src / element
                element_dest = dest / element
                await self.pull(element_src, element_dest)
        else:
            file_string = "IS_FILE"
            res = await self.shell(f"[ -f {src} ] && echo {file_string}")
            if file_string not in res:
                raise FileNotFoundError(f"Cannot find {src} on device")
            await self._pull(str(src), str(dest))

    async def install(
        self,
        path,
        forward_lock=False,  # -l
        reinstall=False,  # -r
        test=False,  # -t
        installer_package_name="",  # -i {installer_package_name}
        shared_mass_storage=False,  # -s
        internal_system_memory=False,  # -f
        downgrade=False,  # -d
        grant_all_permissions=False,  # -g
    ):
        dest = SyncAsync.temp(path)

        try:
            await self.push(path, dest)
        except Exception:
            raise InstallError("file transfer to device failed")

        parameters = []
        if forward_lock:
            parameters.append("-l")
        if reinstall:
            parameters.append("-r")
        if test:
            parameters.append("-t")
        if len(installer_package_name) > 0:
            parameters.append("-i {}".format(installer_package_name))
        if shared_mass_storage:
            parameters.append("-s")
        if internal_system_memory:
            parameters.append("-f")
        if downgrade:
            parameters.append("-d")
        if grant_all_permissions:
            parameters.append("-g")

        try:
            result = await self.shell(
                "pm install {} {}".format(" ".join(parameters), cmd_quote(dest))
            )
            match = re.search(self.INSTALL_RESULT_PATTERN, result)

            if match and match.group(1) == "Success":
                return True
            elif match:
                groups = match.groups()
                raise InstallError(dest, groups[1])
            else:
                raise InstallError(dest, result)
        finally:
            await self.shell("rm -f {}".format(dest))

    async def uninstall(self, package):
        attempts_remaining = 2
        while attempts_remaining > 0:
            attempts_remaining -= 1

            result = await self.shell("pm uninstall {}".format(package))
            m = re.search(self.UNINSTALL_RESULT_PATTERN, result)

            if m and m.group(1) == "Success":
                return True
            elif m:
                if (
                    "DELETE_FAILED_DEVICE_POLICY_MANAGER" in m.group(1)
                    and attempts_remaining > 0
                ):
                    logger.warn(m.group(1))
                    logger.info("App is device-admin, calling disable-user")
                    await self.shell("pm disable-user {}".format(package))
                else:
                    logger.error(m.group(1))
                    return False
            else:
                logger.error("There is no message after uninstalling")
                return False

        return False
