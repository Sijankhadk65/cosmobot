# ROS 2 Jazzy Desktop (includes RViz and common GUI tools)
FROM osrf/ros:jazzy-desktop

ENV DEBIAN_FRONTEND=noninteractive \
  ROS_DISTRO=jazzy \
  QT_X11_NO_MITSHM=1

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Core dev + colcon + rosdep + quality tools
RUN set -eux; \
  apt-get update; \
  apt-get install -y --no-install-recommends \
  sudo git curl wget ca-certificates \
  build-essential cmake gdb pkg-config \
  python3-pip python3-venv \
  python3-colcon-common-extensions python3-rosdep python3-vcstool \
  bash-completion \
  clang-format clang-tidy \
  xauth \
  iputils-ping net-tools iproute2 \
  \
  # --- Astra/Orbbec USB + permissions essentials (needed for Docker) ---
  udev usbutils \
  libusb-1.0-0 libusb-1.0-0-dev \
  \
  # (often useful with camera + rviz stacks)
  v4l-utils \
  ; \
  rm -rf /var/lib/apt/lists/*

# Gazebo Harmonic + ROS 2 Jazzy integration
RUN set -eux; \
  apt-get update; \
  apt-get install -y --no-install-recommends \
  ros-jazzy-ros-gz \
  ros-jazzy-ros-gz-sim \
  ros-jazzy-ros-gz-bridge \
  ros-jazzy-ros-gz-interfaces \
  ros-jazzy-gz-ros2-control \
  ; \
  rm -rf /var/lib/apt/lists/*

# Joint State packages
RUN set -eux; \
  apt-get update; \
  apt-get install -y --no-install-recommends \
  ros-jazzy-joint-state-publisher \
  ros-jazzy-joint-state-publisher-gui \
  ; \
  rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
  libgflags-dev \
  ros-jazzy-image-geometry \
  ros-jazzy-camera-info-manager \
  ros-jazzy-image-transport \
  ros-jazzy-image-publisher \
  libgoogle-glog-dev \
  libeigen3-dev \
  nlohmann-json3-dev \
  libuvc-dev \
  git \
  cmake \
  build-essential \
  && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
  ros-jazzy-cv-bridge ros-jazzy-usb-cam \
  ros-jazzy-image-view ros-jazzy-rqt-image-view ros-jazzy-vision-opencv \
  ros-jazzy-vision-msgs ros-jazzy-apriltag-ros ros-jazzy-perception-pcl \
  ros-jazzy-tf2-tools ros-jazzy-tf2-ros ros-jazzy-tf2-geometry-msgs ros-jazzy-tf-transformations \
  git \
  cmake \
  build-essential \
  && rm -rf /var/lib/apt/lists/*

# Robot description and control packages
RUN apt-get update && apt-get install -y --no-install-recommends \
  ros-jazzy-robot-state-publisher ros-jazzy-xacro \
  ros-jazzy-ros2-control ros-jazzy-ros2-controllers \
  ros-jazzy-ros2controlcli ros-jazzy-controller-manager \
  ros-jazzy-controller-interface ros-jazzy-hardware-interface \
  ros-jazzy-hardware-interface-testing ros-jazzy-ros2-control-test-assets \
  ros-jazzy-joint-state-broadcaster ros-jazzy-joint-trajectory-controller \
  ros-jazzy-position-controllers ros-jazzy-forward-command-controller \
  ros-jazzy-velocity-controllers ros-jazzy-effort-controllers \
  ros-jazzy-diff-drive-controller ros-jazzy-gripper-controllers \
  ros-jazzy-imu-sensor-broadcaster ros-jazzy-force-torque-sensor-broadcaster \
  ros-jazzy-control-msgs ros-jazzy-realtime-tools \
  && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
  ros-jazzy-moveit ros-jazzy-moveit-setup-assistant ros-jazzy-moveit-configs-utils \
  ros-jazzy-moveit-ros-visualization ros-jazzy-moveit-visual-tools \
  ros-jazzy-moveit-ros-planning-interface ros-jazzy-moveit-py \
  ros-jazzy-moveit-ros-perception ros-jazzy-moveit-ros-move-group \
  ros-jazzy-moveit-kinematics ros-jazzy-moveit-planners-ompl \
  ros-jazzy-moveit-simple-controller-manager \
  git \
  cmake \
  build-essential \
  && rm -rf /var/lib/apt/lists/*

# --- Orbbec/Astra udev rule ---
# Vendor id for Orbbec/Astra devices is commonly 2bc5.
# Note: host udev rules are still recommended; this helps in many setups and documents intent.
RUN set -eux; \
  groupadd -f -r video; \
  groupadd -f -r plugdev; \
  printf '%s\n' \
  'SUBSYSTEM=="usb", ATTR{idVendor}=="2bc5", MODE:="0666", GROUP="video"' \
  > /etc/udev/rules.d/99-orbbec.rules

# rosdep init (safe if already initialized)
RUN rosdep init || true

# Create a non-root user matching host UID/GID (passed from compose)
ARG USERNAME=ros
ARG USER_UID=1000
ARG USER_GID=1000

RUN set -eux; \
  # Ensure groups exist
  groupadd -f -r video; \
  groupadd -f -r plugdev; \
  \
  # If USER_GID already exists, reuse it; otherwise create it
  if ! getent group "${USER_GID}" >/dev/null; then \
  groupadd --gid "${USER_GID}" "${USERNAME}" || groupadd "${USERNAME}"; \
  fi; \
  \
  # If USER_UID already exists, reuse that existing user instead of creating a new one
  if getent passwd "${USER_UID}" >/dev/null; then \
  existing_user="$(getent passwd "${USER_UID}" | cut -d: -f1)"; \
  echo "UID ${USER_UID} already exists as user: ${existing_user}. Reusing it."; \
  usermod -aG video,plugdev "${existing_user}"; \
  echo "${existing_user} ALL=(root) NOPASSWD:ALL" > "/etc/sudoers.d/${existing_user}"; \
  chmod 0440 "/etc/sudoers.d/${existing_user}"; \
  else \
  useradd -m -s /bin/bash --uid "${USER_UID}" --gid "${USER_GID}" "${USERNAME}"; \
  usermod -aG video,plugdev "${USERNAME}"; \
  echo "${USERNAME} ALL=(root) NOPASSWD:ALL" > "/etc/sudoers.d/${USERNAME}"; \
  chmod 0440 "/etc/sudoers.d/${USERNAME}"; \
  fi

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER ${USERNAME}
WORKDIR /workspace
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]