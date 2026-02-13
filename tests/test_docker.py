"""Tests for Docker configuration files."""

import os
import unittest


REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')


class TestDockerFiles(unittest.TestCase):
    """Test that Docker configuration files exist and have valid structure."""

    def test_dockerfile_exists(self):
        """Test that Dockerfile exists."""
        self.assertTrue(os.path.exists(os.path.join(REPO_ROOT, 'Dockerfile')))

    def test_dockerfile_has_required_instructions(self):
        """Test that Dockerfile has required instructions."""
        with open(os.path.join(REPO_ROOT, 'Dockerfile'), 'r') as f:
            content = f.read()
        self.assertIn('FROM', content)
        self.assertIn('WORKDIR', content)
        self.assertIn('COPY', content)
        self.assertIn('ENTRYPOINT', content)
        # Must install JDK and Python
        self.assertIn('openjdk', content)
        self.assertIn('python3', content)

    def test_dockerfile_uses_ubuntu_base(self):
        """Test that Dockerfile uses Ubuntu as base image."""
        with open(os.path.join(REPO_ROOT, 'Dockerfile'), 'r') as f:
            first_line = f.readline().strip()
        self.assertTrue(first_line.startswith('FROM ubuntu'))

    def test_docker_compose_exists(self):
        """Test that docker-compose.yml exists."""
        self.assertTrue(os.path.exists(os.path.join(REPO_ROOT, 'docker-compose.yml')))

    def test_docker_compose_has_service(self):
        """Test that docker-compose.yml defines the pgs4a service."""
        with open(os.path.join(REPO_ROOT, 'docker-compose.yml'), 'r') as f:
            content = f.read()
        self.assertIn('pgs4a', content)
        self.assertIn('volumes', content)
        self.assertIn('pgs4a-sdk', content)
        self.assertIn('pgs4a-ant', content)

    def test_entrypoint_exists(self):
        """Test that entrypoint.sh exists."""
        path = os.path.join(REPO_ROOT, 'docker', 'entrypoint.sh')
        self.assertTrue(os.path.exists(path))

    def test_entrypoint_is_executable_script(self):
        """Test that entrypoint.sh starts with a shebang."""
        with open(os.path.join(REPO_ROOT, 'docker', 'entrypoint.sh'), 'r') as f:
            first_line = f.readline().strip()
        self.assertEqual(first_line, '#!/bin/bash')

    def test_entrypoint_handles_commands(self):
        """Test that entrypoint.sh handles all expected commands."""
        with open(os.path.join(REPO_ROOT, 'docker', 'entrypoint.sh'), 'r') as f:
            content = f.read()
        for cmd in ['installsdk', 'configure', 'build', 'test', 'shell', 'help']:
            self.assertIn(cmd, content,
                "entrypoint.sh should handle '{}' command".format(cmd))

    def test_entrypoint_sets_pgs4a_no_terms(self):
        """Test that entrypoint.sh sets PGS4A_NO_TERMS for non-interactive SDK install."""
        with open(os.path.join(REPO_ROOT, 'docker', 'entrypoint.sh'), 'r') as f:
            content = f.read()
        self.assertIn('PGS4A_NO_TERMS', content)

    def test_dockerignore_exists(self):
        """Test that .dockerignore exists."""
        self.assertTrue(os.path.exists(os.path.join(REPO_ROOT, '.dockerignore')))

    def test_dockerignore_excludes_sdk(self):
        """Test that .dockerignore excludes the SDK directory."""
        with open(os.path.join(REPO_ROOT, '.dockerignore'), 'r') as f:
            content = f.read()
        self.assertIn('android-sdk/', content)
        self.assertIn('apache-ant/', content)


if __name__ == "__main__":
    unittest.main()
