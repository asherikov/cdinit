Introduction
============

ROS compatible `cmake` wrapper for `dinit` service manager
<https://github.com/davmac314/dinit>. This package aims to replace or
complement launching mechanisms used in robotics applications: `roslaunch`,
`ros2launch`, `tmux`, `screen`, etc.

Repository layout
-----------------

- `cdinit/` -- dinit executables
- `cdinit_manager/` -- helper scripts
- `cdinit_examples/` -- examples

Example
-------

Steps:
- build `cdinit_examples` in a `colcon` workspace;
- source installation space setup script;
- run `cdinit_launch.sh timeout CDINIT_TIMEOUT=1` -- here `timeout` is an
  example service, `CDINIT_TIMEOUT` is passed to the service as environment
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
  and many other features provided by system service managers.

- They provide end-users too much scripting freedom, which in practice results
  in mixing of service management logic with application logic. This is a
  particularly major issue in python launch scripts encouraged by ROS2.

- ROS2 python launch scripts are excessively verbose, e.g., see
  <https://github.com/dfki-ric/better_launch>.

- ROS2 launch uses shared variable scope by default, which makes launch script
  inclusion fragile and dangerous <https://github.com/ros2/launch/issues/815>.

- It is common to use multiple launch scripts in practice in order to make
  software stack more managable, e.g., in order to make logs readable or be
  able to restart parts of the stack, in which case an additional
  "launch-service" manager is needed.


Problems with `systemd`
-----------------------

Software stack deployed on a robot should generally be started automatically on
boot -- in order to achieve that a system service is usually created. System
service manager could also handle components of the stack, but there are some
caveats too:

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

