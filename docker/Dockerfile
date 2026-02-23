# ROS 2 Jazzy Desktop (includes RViz and common GUI tools)
FROM osrf/ros:jazzy-desktop

ENV DEBIAN_FRONTEND=noninteractive \
    ROS_DISTRO=jazzy \
    QT_X11_NO_MITSHM=1

# Core dev + colcon + rosdep + quality tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    sudo git curl wget ca-certificates \
    build-essential cmake gdb \
    python3-pip python3-venv \
    python3-colcon-common-extensions python3-rosdep python3-vcstool \
    bash-completion \
    clang-format clang-tidy \
    xauth \
    iputils-ping net-tools iproute2 \
 && rm -rf /var/lib/apt/lists/*

# Gazebo (modern "GZ") integration for ROS 2 Jazzy
# These packages provide ros-gz bridge + simulator integration.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-jazzy-ros-gz \
    ros-jazzy-ros-gz-sim \
    ros-jazzy-ros-gz-bridge \
 && rm -rf /var/lib/apt/lists/*

# rosdep init (safe if already initialized)
RUN rosdep init || true

# Create a non-root user matching host UID/GID (passed from compose)
ARG USERNAME=ros
ARG USER_UID=1000
ARG USER_GID=1000

RUN set -eux; \
    # ----- GROUP: ensure we have a group for USER_GID -----
    if getent group "${USER_GID}" >/dev/null; then \
        GROUP_NAME="$(getent group "${USER_GID}" | cut -d: -f1)"; \
        echo "Using existing group ${GROUP_NAME} (GID ${USER_GID})"; \
    else \
        groupadd --gid "${USER_GID}" "${USERNAME}"; \
        GROUP_NAME="${USERNAME}"; \
        echo "Created group ${GROUP_NAME} (GID ${USER_GID})"; \
    fi; \
    \
    # ----- USER: if UID exists, reuse that user; else create USERNAME -----
    if getent passwd "${USER_UID}" >/dev/null; then \
        EXISTING_USER="$(getent passwd "${USER_UID}" | cut -d: -f1)"; \
        echo "UID ${USER_UID} already belongs to user ${EXISTING_USER}; reusing it."; \
        USER_TO_USE="${EXISTING_USER}"; \
    else \
        USER_TO_USE="${USERNAME}"; \
        if id -u "${USER_TO_USE}" >/dev/null 2>&1; then \
            echo "User ${USER_TO_USE} already exists (but UID ${USER_UID} was free)"; \
        else \
            useradd -m -s /bin/bash --uid "${USER_UID}" --gid "${USER_GID}" "${USER_TO_USE}"; \
            echo "Created user ${USER_TO_USE} (UID ${USER_UID})"; \
        fi; \
    fi; \
    \
    # Ensure sudoers entry for whichever user we ended up using
    apt-get update && apt-get install -y --no-install-recommends sudo && rm -rf /var/lib/apt/lists/*; \
    echo "${USER_TO_USE} ALL=(root) NOPASSWD:ALL" > "/etc/sudoers.d/${USER_TO_USE}"; \
    chmod 0440 "/etc/sudoers.d/${USER_TO_USE}";

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER ${USERNAME}
WORKDIR /workspace
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]