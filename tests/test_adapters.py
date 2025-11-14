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

"""Tests for AgentAdapter implementations."""

import pytest
import ray

from ray_agents import AgentSession
from ray_agents.adapters import AgentAdapter


def test_adapter_must_return_content_key(ray_start):
    """Test that adapter must return dict with 'content' key."""

    class BadAdapter(AgentAdapter):
        """Adapter that returns invalid response."""

        async def run(self, message, messages, tools):
            return {"response": "missing content key"}

    adapter = BadAdapter()
    session = AgentSession.remote(session_id="test", adapter=adapter)

    # This should raise ValueError
    with pytest.raises(ray.exceptions.RayTaskError) as exc_info:
        ray.get(session.run.remote("Test"))

    # Verify error message mentions 'content' key
    assert "content" in str(exc_info.value).lower()
