Introduction
============

ROS compatible `cmake` wrapper for `dinit` service manager
<https://github.com/davmac314/dinit>. This tool aims at replacing or
complementing launching mechanisms used in robotics applications: `roslaunch`,
`ros2launch`, `tmux`, `screen`, etc.

Packages
--------

- `cdinit/` -- dinit executables with management scripts
- `cdinit_ros2/` -- ROS2 common unit scripts

Example
-------

Steps:
- build `cdinit` in a `colcon` workspace;
- source setup script;
- run `cdinit.sh start cdinit_timeout@1`.

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

- ROS launch is hierarchical in nature and relies on script inclusion, which is
  fragile and dangerous in ROS2 due to shared scope
  <https://github.com/ros2/launch/issues/815>.

- Combination of scripting and hierarchical inclusions results in strongly
  coupled startup scripts with obscure interdependencies. This, in turn,
  prohibits fine control over individual nodes, such as stopping, restarting,
  etc.

- ROS2 python launch scripts are excessively verbose, e.g., see discussion at
  <https://github.com/dfki-ric/better_launch>.

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

`cdinit.sh` finds directories named `cdinit/service` under
`CDINIT_INSTALL_ROOT` and other `ROS`/`ament` paths, and passes them to `dinit`
when it is started for the first time. Service names should be prefixed by the
package name in order to avoid collisions.


Extra features
--------------

- `cdinit.sh listall` lists all services found in cdinit service directories.
- `cdinit.sh graph [services]` outputs service dependency graph in hiearch
  (<https://github.com/asherikov/hiearch>) format using `dinit_graph` utility
  (<https://github.com/asherikov/dinit_graph>).


Predefined services
-------------------

### `cdinit` package

- `cdinit_main` -- dummy main service;
- `cdinit_log@<service>` -- consumes output of another service and writes it to
  a log file with timestamps;
- `cdinit_sessionsync` -- periodically runs `sync` on the session root folder
  in order to minimize losses;
- `cdinit_shutdown` -- shutdowns cdinit, to be used by other services, e.g., on
  failures;
- `cdinit_timeout@<duration>` -- shutdown cdinit with a given timeout;
- `cdinit_log_follow@<service>` -- follow log file of the given service and
  output it to the terminal;
- `cdinit_print_env` -- prints environment of the current cdinit session.

### `cdinit_ros2` package

- `cdinit_ros2_bag` records most of ROS2 topics to an MCAP bag file, tries to
  exclude heavy visual topics.


TODO
====

A few things that would be nice to see implemented in dinit:

- Automatically generated log file names, e.g., `<prefix specified via command
  line>/<service name>.log`, to avoid boilerplate parameters in service files.
- Timestamped log messages.
- `dinitctl` to optionally wait for control socket to be created.
- Introduce a naming convention, e.g., '@' suffix, to separate parametrized
  services from basic ones: currently service file needs top be checked for
  parameter substitutions. Similar to systemd service templates.


Bookmarks
=========

- https://github.com/Supervisor/supervisor uses a single configration file.
- https://shepherding.services/ Guile Scheme.
- https://github.com/immortal/immortal
