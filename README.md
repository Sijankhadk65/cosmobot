# Installation Steps

## Docker
> > xhost +local:
> > sudo usermod -aG docker $USER
> > newgrp docker
> > chmod +X docker/scripts/*.sh
> > docker/script/build.sh
> > docker/script/run.sh

### Inside the container

> > cd robot_ws
> > rosdep update
> > rosdep install --from-paths src -y --ignore-src
> > colcon build --symlink-install
> > source install/setup.bash

### Create a ROS package
> > ros2 pkg create "PACKAGE_NAME" --build-type ament_cmake / ament_python

### Running the bringup pacakage
> > ros2 launch robot_bringup bringup.launch.py use_camera:=true use_perception:=true use_jsp_gui:=false

### Generating rviz config
Just save a config by only running 'rviz2' adding a 'tf' with the target frame as 'base'
