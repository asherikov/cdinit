Introduction
============

ROS compatible `cmake` wrapper for `dinit` service manager
<https://github.com/davmac314/dinit>. This tool aims at replacing or
complementing launching mechanisms used in robotics applications: `roslaunch`,
`ros2launch`, `tmux`, `screen`, etc.

Packages
--------

- `cdinit/` -- dinit executables
- `cdinit_manager/` -- helper scripts
- `cdinit_examples/` -- examples

Example
-------

Steps:
- build `cdinit_examples` in a `colcon` workspace;
- source setup script;
- run `cdinit.sh start cdinit_timeout CDINIT_TIMEOUT=1` -- here `timeout` is an
  example service, `CDINIT_TIMEOUT` is passed to the service as an environment
  variable.

Dependencies
------------

- `cmake` and C++ compiler.
- there are no ROS dependencies, helper scripts may use ROS environment
  variables if defined.


Motivation
==========

Problems with `roslaunch`
-------------------------

Neither ROS1/ROS2 launch nor their conceptually similar alternatives are well
designed for service management:

- They lack startup ordering, runtime dependencies, advanced failure handling,
  and many other features provided by system service managers such as
  `systemd`.

- They favor scripting to declarative syntax, which essentially the same as
  using old-school RC scripts instead of `systemd`-like service units. In
  practice this results in application logic leaks into startup scripts,
  turning the whole system into a spaghetti monster.

- ROS2 python launch scripts are excessively verbose, e.g., see discussion at
  <https://github.com/dfki-ric/better_launch>.

- ROS launch relies on script inclusion, which is fragile and dangerous in ROS2
  due to shared scope <https://github.com/ros2/launch/issues/815>.

- It is common to use multiple launch scripts in order to make software stack
  more manageable, e.g., in order to make logs readable or be able to restart
  parts of the stack. In this case an additional "launch-service" manager is
  needed.


Problems with `systemd`
-----------------------

Software stack deployed on a robot should generally be started automatically on
boot -- in order to achieve that a system service is usually created. System
service manager could also handle components of the stack individually, but
there are some caveats:

- Startup scripts usually must be installed to predefined locations in the
  system, or in user home directory
  (<https://wiki.archlinux.org/index.php/Systemd/User>). This is inconvenient
  for development and testing.

- Service managers may not be able to run in user space or inside `docker`
  containers, e.g.,
  <https://serverfault.com/questions/607769/running-systemd-inside-a-docker-container-arch-linux>.


Advantages of `dinit`
---------------------

- It is a full-blown service manager capable of booting `Linux` systems and is
  already used in some distributions. At the same time it can operate in user
  space and inside containers.

- `dinit` implements unit-based design similar to `systemd`, that reasonably
  limits scripting capabilities.

- `dinit` is a compact application without any heavy dependencies.


Design
======

`cdinit.sh` provides cli user interface to the service manager. The script
wraps both `dinit` and `dinitctl` tools and performs various tasks to
facilitate their usage.

Environment variables
---------------------

`cdinit.sh` sets environment variables which are going to be available for all
services.

The following are set automatically:

- `CDINIT_INSTALL_ROOT` -- installation root deduced based on location of
  `cdinit.sh`.
- `CDINIT_WORKING_ROOT` -- working directory, which can be controlled by other
  environment variables such as `ROS_LOG_DIR`, must be writable. `dinit`
  control socket is created in this directory.
- `CDINIT_SESSION_ID` -- unique session id, that can be used to identify
  particular runs.
- `CDINIT_SESSION_ROOT` -- `CDINIT_WORKING_ROOT/CDINIT_SESSION_ID` directory,
  recommended location for log files.

Additional environment variables can be provided by the user, e.g., `cdinit.sh
VARIABLE=VALUE`.


Dummy service
-------------

`cdinit.sh` automatically launches `dinit` with a dummy `cdinit_main` service
if it is not present. Dummy service helps to persist service manager state:
environment variables, session, etc. The rest of the command line arguments are
passed to `dinitctl` if provided.


Service directories
-------------------

`cdinit.sh` finds directories named `cdinit_services` under
`CDINIT_INSTALL_ROOT` and other `ROS`/`ament` paths, and passes them to `dinit`
when it is started for the first time. Service names should be prefixed by the
package name in order to avoid collisions.


TODO
====

I would like to see a few features implemented in `dinit`, but the author only
accepts pull requests:

- Automatically generated log file names, e.g., `<prefix specified via command
  line>/<service name>.log`, to avoid boilerplate parameters in service files.
- Timestamp log messages.
- `dinitctl` to optionally wait for control socket to be created.
