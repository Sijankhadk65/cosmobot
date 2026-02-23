# Installation Steps

## Docker

> > sudo usermod -aG docker $USER
> > newgrp docker
> > chmod +X docker/scripts/*.sh
> > docker/script/build.sh
> > docker/script/run.sh

### Inside the container

> > cd robot_ws
> > rosdep update
> > rosdep install --from-paths src -y --ignore-src
> > colcon build
> > source install/setup.bash
