Introduction
============

`cmake`/`catkin` wrapper for `dinit` service manager
(https://github.com/davmac314/dinit). The purpose of this package is to provide
an intermediate service manager working between `systemd` (or a system service
manager in general) and `roslaunch` in `ROS` environments. Motivation,
technical details, and alternatives are discussed below.

Scripts assume that they are executed in https://github.com/asherikov/colcon_workspace
environment.



Examples
========

* `rosrun cdinit launch.sh roscore timeout CDINIT_TIMEOUT=17` -- runs `roscore`
  and `timeout` services (see `dinit_services` directory) and sets
  `CDINIT_TIMEOUT` environment variable used by `timeout` service.
* `rosrun cdinit ctl.sh ...` can be used to list/control services.


Terminology
===========

1. 'service' -- a software process, in particular a 'ROS' node.
2. 'service manager' -- an utility that supervises execution of services.
3. 'system service manager' -- service manager that supervises system services,
   e.g., `systemd`, `rc`.
4. 'stack' -- a robot specific set of packages providing one or more services.
5. 'stack profile' -- a version of the stack intended for a specific purpose,
   e.g., for simulation, deployments, HiL (Hardware in the Loop) testing.
6. 'stack service manager' -- service manager that supervises execution of
   a stack, can be the same as 'system service manager'.



General approach to service management with ROS
===============================================

roslaunch
---------

ROS services (nodes) are usually started and supervised by `roslaunch` utility,
which works differently in ROS1 and ROS2:

1. ROS1 `roslaunch` uses a hierarchy of XML startup scripts, where nodes and
   their parameters are declared. ROS2 encourages using python scripts instead
   of XML (http://design.ros2.org/articles/roslaunch_xml.html) and implementing
   service management logic using roslaunch API. This approach effectively
   dilutes the boundaries between launch script, node, and roslaunch itself.

2. `roslaunch` performs startup in three implicit steps:
    1. Starting of `roscore`, which, in particular, provides parameter server
       functionality [dropped in ROS2].
    2. Uploading of parameters to the parameter server in the order of their
       appearance in launch files [dropped in ROS2].
    3. Starting of user provided nodes in arbitrary, non-deterministic order.
       ROS2 design documents suggest that service ordering and dependencies can
       be introduced ->
       https://github.com/ros2/design/blob/gh-pages/articles/150_roslaunch.md#deterministic-startup,
       but I could not find any indication that such functionality has actually
       been implemented.

3. Node termination handling is controlled by three parameters: `required`,
   `respawn`, `respawn_delay`, termination of 'required' node implies
   termination of the whole stack, `respawn*` parameters control restarting of
   the node. ROS2 launch provides similar functionality, but only in python,
   see https://github.com/ros2/launch/pull/426,
   https://ubuntu.com/blog/ros2-launch-required-nodes

4. Running ROS nodes can be listed with `rosnode list`. control over node
   execution is limited to `rosnode kill`, which potentially can be used to
   restart node if it is declared as respawnable. Individual nodes cannot be
   killed in ROS2 in general ->
   https://answers.ros.org/question/323329/how-to-kill-nodes-in-ros2/, i.e.,
   only ROS-aware nodes can be controlled.


In my opinion ROS2 launch has a number of design flaws:
- requires more boilerplate scripting;
- introduces tight coupling between the services and launching system;
- provides insufficient control over node execution even compared with ROS1.


System service manager
----------------------

Software stack deployed on a robot should generally be started automatically on
boot -- in order to achieve that a system service is created which starts a
roslaunch script.


Issues
------

- ROS assumption that startup ordering is not relevant does not hold in
  practice, often it is necessary to run services sequentially, for example in
  order to generate configurations, create fake devices in simulation, etc.

- Startup scripts may also get fragmented in order to share parts of the stack
  between different profiles, e.g., HAL (hardware abstraction layer) and high
  level logic.

- System service manager could be perfect for managing such fragmented scripts,
  but there are some caveats too:

  - Startup scripts usually must be installed to predefined locations in the
    system, or in user home directory
    (https://wiki.archlinux.org/index.php/Systemd/User). This is inconvenient
    for development and testing.

  - Service managers may not be adapted to be running in user space or inside
    `docker` containers, e.g.,
    https://serverfault.com/questions/607769/running-systemd-inside-a-docker-container-arch-linux

These issues can be addressed by introducing an additional stack service manager.
