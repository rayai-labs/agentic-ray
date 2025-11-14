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

"""Tests for basic AgentSession operations."""

import ray

from ray_agents import AgentSession
from ray_agents.adapters import _MockAdapter as MockAdapter


def test_agent_session_creation(ray_start):
    """Test basic agent session creation."""
    adapter = MockAdapter()
    session = AgentSession.remote(session_id="test_123", adapter=adapter)

    # Verify session was created
    assert session is not None

    # Verify we can get session ID
    session_id = ray.get(session.get_session_id.remote())
    assert session_id == "test_123"


def test_agent_session_run_without_tools(ray_start):
    """Test agent execution without tools."""
    adapter = MockAdapter()
    session = AgentSession.remote(session_id="test", adapter=adapter)

    # Run agent with simple message
    result = ray.get(session.run.remote("Hello, how are you?"))

    # Verify response structure
    assert "content" in result
    assert "Hello, how are you?" in result["content"]


def test_multiple_sessions_isolated(ray_start):
    """Test that multiple sessions maintain separate state."""
    adapter = MockAdapter()

    # Create two sessions
    session1 = AgentSession.remote(session_id="user_1", adapter=adapter)
    session2 = AgentSession.remote(session_id="user_2", adapter=adapter)

    # Send different messages to each
    ray.get(session1.run.remote("Message to session 1"))
    ray.get(session2.run.remote("Message to session 2"))

    # Verify histories are separate
    history1 = ray.get(session1.get_history.remote())
    history2 = ray.get(session2.get_history.remote())

    assert len(history1) == 2  # 1 user + 1 assistant
    assert len(history2) == 2  # 1 user + 1 assistant
    assert history1[0]["content"] == "Message to session 1"
    assert history2[0]["content"] == "Message to session 2"
