import os
import time
import tempfile
import pathlib

import pytest
import socket

from ppadb import ClearError, InstallError


def test_install_uninstall_success(device):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    result = device.install(
        os.path.join(dir_path, "resources/apk/app-x86.apk"),
        reinstall=True,
        downgrade=True,
    )
    assert result is True

    with pytest.raises(InstallError) as excinfo:
        device.install(os.path.join(dir_path, "resources/apk/app-x86.apk"))

    assert "INSTALL_FAILED_ALREADY_EXISTS" in str(excinfo.value)

    result = device.is_installed("com.cloudmosa.helloworldapk")
    assert result is True

    result = device.uninstall("com.cloudmosa.helloworldapk")
    assert result is True

    result = device.uninstall("com.cloudmosa.helloworldapk")
    assert result is False

    result = device.is_installed("com.cloudmosa.helloworldapk")
    assert result is False


def test_uninstall_not_exist_package(device):
    result = device.uninstall("com.cloudmosa.not.exist")
    assert result is False


def test_list_features(device):
    features = device.list_features()
    assert "reqGlEsVersion" in features
    assert "android.hardware.sensor.barometer" in features

    assert features["reqGlEsVersion"] is not None
    assert features["reqGlEsVersion"] != ""
    assert features["android.hardware.sensor.barometer"] is True


def test_clear(device):
    result = device.clear("com.android.chrome")
    assert result is True

    with pytest.raises(ClearError) as excinfo:
        result = device.clear("com.android.not.exist.package")

    assert (
        "Package com.android.not.exist.package could not be cleared - [Failed]"
        in str(excinfo.value)
    )


def test_list_packages(device):
    packages = device.list_packages()

    assert "com.android.chrome" in packages
    assert "com.android.shell" in packages


def test_get_properties(device):
    properties = device.get_properties()

    assert "ro.product.device" in properties
    assert "ro.product.model" in properties


def test_list_reverses(device):
    result = device.list_reverses()
    assert result is not None


def test_reboot_than_wait_boot(device):
    result = device.reboot()
    assert device.wait_boot_complete() is True


def test_get_version_name(device):
    result = device.get_package_version_name("com.android.chrome")
    assert result is not None


def test_shell_echo_sleep_long_time(device):
    result = device.shell("sleep 30;echo passed")
    assert "passed" in result


def test_shell_echo_timeout(device):
    with pytest.raises(socket.timeout) as excinfo:
        device.shell("sleep 60;echo passed", timeout=10)

    assert "timed out" in str(excinfo.value)


def test_get_top_activity(device):
    activity = device.get_top_activity()
    assert activity is not None


def test_get_top_activities(device):
    activities = device.get_top_activities()
    assert len(activities) != 0


def test_pull(device):
    import hashlib

    device.shell("screencap -p /sdcard/screen.png")
    checksum = device.shell("md5sum -b /sdcard/screen.png").strip()

    device.pull("/sdcard/screen.png", "./screen.png")
    hash_md5 = hashlib.md5()
    with open("./screen.png", "rb") as fp:
        for chunk in iter(lambda: fp.read(4096), b""):
            hash_md5.update(chunk)

    pull_checksum = hash_md5.hexdigest()

    assert checksum == pull_checksum


def test_push_stat(device):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    apk_path = os.path.join(dir_path, "resources/apk/app-x86.apk")
    device.push(apk_path, "/sdcard/test.apk")

    stat = os.stat(apk_path)
    result = device.shell("stat /sdcard/test.apk -c %X")
    if int(device.shell("getprop ro.build.version.sdk")) >= 27:
        assert int(result) == int(stat.st_mtime)
    else:
        timestamp = int(time.time())
        assert timestamp - 10 <= int(result) <= timestamp + 10


def test_push_dir(device):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    apk_path = os.path.join(dir_path, "resources/apk")
    device.push(apk_path, "/sdcard")

    result = device.shell("ls /sdcard/apk")
    assert "app-armeabi-v7a.apk" in result
    assert "app-x86.apk" in result


def test_push_recurse_dir(device):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    apk_path = os.path.join(dir_path, "resources")
    device.push(apk_path, "/sdcard")

    result = device.shell("ls /sdcard/resources/apk")
    assert "app-armeabi-v7a.apk" in result
    assert "app-x86.apk" in result


def test_push_with_progress(device):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    apk_path = os.path.join(dir_path, "resources/apk/app-x86.apk")

    result = []

    def progress(file_name, total_size, sent_size):
        result.append(
            {"file_name": file_name, "total_size": total_size, "sent_size": sent_size}
        )

    device.push(apk_path, "/sdcard/test.apk", progress=progress)

    assert result
    assert result[-1]["total_size"] == result[-1]["sent_size"]


@pytest.fixture(scope="function")
def test_filepaths():
    filepaths = [
        "toplevel/test1.txt",
        "toplevel/test2.txt",
        "toplevel/subdir1/test3.txt",
        "toplevel/subdir1/test4.txt",
        "toplevel/subdir1/subdir2/test5.txt",
        "toplevel/subdir1/subdir2/test6.txt",
    ]
    yield filepaths


@pytest.fixture(scope="function")
def populated_device(device, test_filepaths):
    dirpath = "toplevel/subdir1/subdir2"

    device.shell(f"mkdir -p {dirpath}")
    for path in test_filepaths:
        device.shell(f"echo {path} > /data/local/tmp/{path}")

    yield device

    device.shell("rm -rf /data/local/tmp/toplevel")


@pytest.fixture(scope="function")
def working_dir():
    with tempfile.TemporaryDirectory() as f:
        yield pathlib.Path(f)


def test_pull_file(populated_device, working_dir):
    populated_device.pull(
        "/data/local/tmp/toplevel/test1.txt", working_dir / "test1.txt"
    )
    dest_path = working_dir / "test1.txt"
    assert dest_path.is_file()
    assert dest_path.read_text() == "toplevel/test1.txt"


def test_pull_dir(populated_device, working_dir):
    populated_device.pull(
        "/data/local/tmp/toplevel/subdir1/subdir2", working_dir / "subdir2"
    )
    dest_path = working_dir / "subdir2"
    filepath1 = dest_path / "test5.txt"
    filepath2 = dest_path / "test6.txt"
    assert dest_path.is_dir()
    assert filepath1.is_file()
    assert filepath2.read_text() == "toplevel/subdir1/subdir2/test5.txt"
    assert filepath2.is_file()
    assert filepath2.read_text() == "toplevel/subdir1/subdir2/test5.txt"


def test_pull_recursive_dir(populated_device, working_dir, test_filepaths):
    populated_device.pull("data/local/tmp/toplevel", working_dir / "toplevel")
    assert (working_dir / "toplevel").is_dir()
    assert (working_dir / "toplevel" / "subdir1").is_dir()
    for path in test_filepaths:
        to_check = working_dir / path
        assert to_check.is_file()
        assert to_check.read_text() == path


def test_forward(device):
    device.killforward_all()
    forward_map = device.list_forward()
    assert not forward_map

    device.forward("tcp:6000", "tcp:7000")
    device.forward("tcp:6001", "tcp:7001")
    device.forward("tcp:6002", "tcp:7002")

    forward_map = device.list_forward()
    assert forward_map["tcp:6000"] == "tcp:7000"
    assert forward_map["tcp:6001"] == "tcp:7001"
    assert forward_map["tcp:6002"] == "tcp:7002"

    device.killforward("tcp:6000")
    forward_map = device.list_forward()
    assert "tcp:6000" not in forward_map
    assert forward_map["tcp:6001"] == "tcp:7001"
    assert forward_map["tcp:6002"] == "tcp:7002"

    device.killforward_all()
    forward_map = device.list_forward()
    assert not forward_map


@pytest.mark.skip
def test_killforward_all(client, device):
    """
    This testcase need two emulators for testing,
    But the android docker container can'd execute two emulators at the same time.
    If you want to execute this testcase,
    you need to start two emulators 'emulator-5554' and 'emualtor-5556' on your machine.
    """
    device2 = client.device("emulator-5556")

    device.forward("tcp:6001", "tcp:6001")
    device2.forward("tcp:6002", "tcp:6002")

    forward_map = device.list_forward()
    assert forward_map["tcp:6001"] == "tcp:6001"
    assert "tcp:6002" not in forward_map

    device.killforward_all()
    forward_map = device.list_forward()
    assert "tcp:6001" not in forward_map

    forward_map = client.list_forward()
    assert "emulator-5556" in forward_map
    assert forward_map["emulator-5556"]["tcp:6002"] == "tcp:6002"

    client.killforward_all()
    forward_map = client.list_forward()
    assert not forward_map
