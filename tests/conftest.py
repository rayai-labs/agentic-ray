# Copyright (c) 2025 Ray AI Technologies, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Shared fixtures for ray_agents tests."""

import pytest
import ray


@pytest.fixture
def ray_start():
    """Start Ray for testing."""

    # The package should already be installed in the environment (via uv/pip install -e .)
    ray.init(ignore_reinit_error=True, num_cpus=4)
    yield
    ray.shutdown()
