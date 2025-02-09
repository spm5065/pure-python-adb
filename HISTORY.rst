0.3.0 (Unreleased)
--------------------

* Fixes #111: Invalid escape sequence via @eamanu and @mib1185
* Fixes #110: Add ability to pass extra arguments to `screencap` commands for waydroid via @CloCkWeRX
* Fixes #88: missing return in ppadb.command.transport: Transport.shell() for custom handler via @roxen
* Adds #85: Include LICENSE in pip package via @jan-janssen
* Adds #57: Recursive directory push for DeviceAsync class via @JeffLIrion
* Adds #89: Call disable-user if app is device-admin via @eybisi
* Change: Device#install and DeviceAsync#install changes param from `grand_all_permissions` to `grant_all_permissions`


0.2.1 (2019-10-14)
--------------------

* Fixes #21: Rename the package name from "adb" to "ppadb"
* Fixes #23: Support push dir to device
* Fixes #25: Don't call logging.basicConfig() in the module


0.1.6 (2019-01-21)
-------------------

* Fix #4 push does not preserve original timestap unlike equiv adb push from command line
* Fix #6 forward_list should also check serial
* Fix #8: adb/command/host/__init__.py can take an exception parsing "devices" data


0.1.0 (2018-06-23)
-------------------

* First release on PyPI.

