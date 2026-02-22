# CI helpers

These scripts are used by GitHub Actions and can also be run locally.

- `ci/run_in_docker.sh "<cmd>"` runs any command inside the ROS container.
- `ci/colcon_build_test.sh` builds + runs tests using colcon inside the ROS container.

Adjust defaults in `ci/env.sh`.