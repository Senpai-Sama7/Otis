"""Tests for sandbox runner."""

import pytest
from unittest.mock import MagicMock, patch

from src.runner.sandbox import exec_in_sandbox, SandboxExecutor


class TestSandbox:
    """Test sandbox execution."""

    @patch("src.runner.sandbox.docker.from_env")
    def test_exec_in_sandbox_success(self, mock_docker):
        """Test successful code execution in sandbox."""
        # Mock Docker client
        mock_client = MagicMock()
        mock_docker.return_value = mock_client
        mock_client.containers.run.return_value = b"Hello, World!"

        # Execute code
        result = exec_in_sandbox(
            code='print("Hello, World!")',
            lang="python",
            timeout=20,
            net=False,
        )

        assert result["success"] is True
        assert "Hello, World!" in result["output"]
        assert result["exit_code"] == 0

    @patch("src.runner.sandbox.docker.from_env")
    def test_exec_in_sandbox_network_disabled_by_default(self, mock_docker):
        """Test network is disabled by default."""
        mock_client = MagicMock()
        mock_docker.return_value = mock_client
        mock_client.containers.run.return_value = b"Test"

        result = exec_in_sandbox(code="print('test')", lang="python")

        # Check that network_mode was set to "none"
        call_kwargs = mock_client.containers.run.call_args.kwargs
        assert call_kwargs["network_mode"] == "none"

    @patch("src.runner.sandbox.docker.from_env")
    def test_exec_in_sandbox_network_enabled_after_approval(self, mock_docker):
        """Test network can be enabled after approval."""
        mock_client = MagicMock()
        mock_docker.return_value = mock_client
        mock_client.containers.run.return_value = b"Test"

        result = exec_in_sandbox(code="print('test')", lang="python", net=True)

        # Check that network_mode was set to "host"
        call_kwargs = mock_client.containers.run.call_args.kwargs
        assert call_kwargs["network_mode"] == "host"

    def test_exec_in_sandbox_empty_code(self):
        """Test handling of empty code."""
        result = exec_in_sandbox(code="", lang="python")

        assert result["success"] is False
        assert "Empty code" in result["error"]

    def test_exec_in_sandbox_denylist_violation(self):
        """Test denylist blocks dangerous operations."""
        dangerous_code = "docker run --privileged"

        result = exec_in_sandbox(code=dangerous_code, lang="bash")

        assert result["success"] is False
        assert "blocked by security policy" in result["error"]

    def test_exec_in_sandbox_readonly_filesystem(self):
        """Test read-only filesystem constraint."""
        with patch("src.runner.sandbox.docker.from_env") as mock_docker:
            mock_client = MagicMock()
            mock_docker.return_value = mock_client
            mock_client.containers.run.return_value = b"Test"

            exec_in_sandbox(code="print('test')", lang="python")

            call_kwargs = mock_client.containers.run.call_args.kwargs
            assert call_kwargs["read_only"] is True

    def test_exec_in_sandbox_memory_limit(self):
        """Test memory limit is enforced."""
        with patch("src.runner.sandbox.docker.from_env") as mock_docker:
            mock_client = MagicMock()
            mock_docker.return_value = mock_client
            mock_client.containers.run.return_value = b"Test"

            exec_in_sandbox(code="print('test')", lang="python")

            call_kwargs = mock_client.containers.run.call_args.kwargs
            assert call_kwargs["mem_limit"] == "512m"

    def test_sandbox_executor_class(self):
        """Test SandboxExecutor class."""
        executor = SandboxExecutor(default_lang="python", default_timeout=30)
        assert executor.default_lang == "python"
        assert executor.default_timeout == 30
        assert executor.allow_net_by_default is False

    @patch("src.runner.sandbox.exec_in_sandbox")
    def test_sandbox_executor_execute(self, mock_exec):
        """Test SandboxExecutor execute method."""
        mock_exec.return_value = {"success": True, "output": "Test"}

        executor = SandboxExecutor()
        result = executor.execute(code="print('test')")

        assert result["success"] is True
        mock_exec.assert_called_once()
