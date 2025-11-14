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

"""Tests for AgentSession conversation history management."""

import ray

from ray_agents import AgentSession
from ray_agents.adapters import _MockAdapter as MockAdapter


def test_agent_session_conversation_history(ray_start):
    """Test conversation history is maintained."""
    adapter = MockAdapter()
    session = AgentSession.remote(session_id="test", adapter=adapter)

    # Send multiple messages
    ray.get(session.run.remote("First message"))
    ray.get(session.run.remote("Second message"))
    ray.get(session.run.remote("Third message"))

    # Get history
    history = ray.get(session.get_history.remote())

    # Verify history structure
    assert len(history) == 6  # 3 user + 3 assistant messages
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "First message"
    assert history[1]["role"] == "assistant"
    assert history[2]["role"] == "user"
    assert history[2]["content"] == "Second message"


def test_agent_session_clear_history(ray_start):
    """Test clearing conversation history."""
    adapter = MockAdapter()
    session = AgentSession.remote(session_id="test", adapter=adapter)

    # Send messages
    ray.get(session.run.remote("Message 1"))
    ray.get(session.run.remote("Message 2"))

    # Clear history
    ray.get(session.clear_history.remote())

    # Verify history is empty
    history = ray.get(session.get_history.remote())
    assert len(history) == 0
