======================
Pure Python ADB Reborn
======================

Pure Python ADB was originially created by `@swind`_.
When it was no longer being maintained, it was forked to create Pure Python ADB Reborn.

1.0.0
-----
* Fixes #6: Fix looping in uninstall if uninstall fails due to device admin
* Fixes swind#111: Invalid escape sequence via `@eamanu`_ and `@mib1185`_
* Fixes swind#110: Add ability to pass extra arguments to ``screencap`` commands for waydroid via `@CloCkWeRX`_
* Fixes swind#88: Missing return in ``ppadb.command.transport`` : ``Transport.shell()`` for custom handler via `@roxen`_
* Fixes swind#60: Close socket if the connection fails via `@JeffLIrion`_
* Fixes swind#64: ADB reverse command via `@Hamz-a`_
* Fixes swind#92: incorrect timestamp type in asynchronous push via `@slicen`_ and `@GeekDuanLian`_
* Adds #2: Pull directory via `@ACButcher`_
* Adds swind#65: Added support to remove reverses via `@Hamz-a`_
* Adds swind#67: asynchronous install and uninstall commands via `@slicen`_
* Adds swind#85: Include LICENSE in pip package via `@jan-janssen`_
* Adds swind#57: Recursive directory push for DeviceAsync class via `@JeffLIrion`_
* Adds swind#89: Call disable-user if app is device-admin via `@eybisi`_
* Change swind#94: Device#install and DeviceAsync#install changes param from ``grand_all_permissions`` to ``grant_all_permissions``


Pure Python ADB (Legacy)
========================

0.3.0 (Unreleased)
------------------

* Fixes swind#53: Check length of screenshot before indexing into it `@JeffLIrion`_
* Adds swind#47: Async support `@JeffLIrion`_

0.2.1 (2019-10-14)
------------------

* Fixes swind#21: Rename the package name from "adb" to "ppadb"
* Fixes swind#23: Support push dir to device
* Fixes swind#25: Don't call logging.basicConfig() in the module


0.1.6 (2019-01-21)
------------------

* Fix swind#4: push does not preserve original timestap unlike equiv adb push from command line
* Fix swind#6: forward_list should also check serial
* Fix swind#8: adb/command/host/__init__.py can take an exception parsing "devices" data


0.1.0 (2018-06-23)
------------------

* First release on PyPI.


Contributors
============

*`@ACButcher`_
*`@CloCkWeRX`_
*`@eamanu`_
*`@eybisi`_
*`@GeekDuanLian`_
*`@Hamz-a`_
*`@jan-janssen`_
*`@JeffLIrion`_
*`@mib1185`_
*`@roxen`_
*`@slicen`_
*`@swind`_

.. _@ACButcher: https://githib.com/ACButcher
.. _@CloCkWeRX: https://github.com/CloCkWeRX
.. _@eamanu: https://github.com/eamanu
.. _@eybisi: https://github.com/eybisi
.. _@GeekDuanLian: https://github.com/GeekDuanLian
.. _@Hamz-a: https://github.com/Hamz-a
.. _@jan-janssen: https://github.com/jan-janssen
.. _@JeffLIrion: https://github.com/JeffLIrion
.. _@mib1185: https://github.com/mib1185
.. _@roxen: https://github.com/roxen
.. _@slicen: https://github.com/slicen
.. _@swind: https://github.com/swind
