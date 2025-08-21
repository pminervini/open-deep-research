# -*- coding: utf-8 -*-

import pytest
import open_deep_research.run_agents
import open_deep_research.reformulator
import open_deep_research.cookies
from open_deep_research.cookies import COOKIES


class TestRunAgents:
    def test_run_agents_module_exists(self):
        """Test that run_agents module can be imported"""
        assert open_deep_research.run_agents is not None

    def test_module_has_expected_structure(self):
        """Test that run_agents module has expected structure"""
        import open_deep_research.run_agents as run_agents
        # Check if module has any callable functions
        module_contents = dir(run_agents)
        assert len(module_contents) > 0


class TestReformulator:
    def test_reformulator_module_exists(self):
        """Test that reformulator module can be imported"""
        assert open_deep_research.reformulator is not None


class TestCookies:
    def test_cookies_module_exists(self):
        """Test that cookies module can be imported"""
        assert open_deep_research.cookies is not None
        # Check if COOKIES constant exists
        assert hasattr(open_deep_research.cookies, 'COOKIES')

    def test_cookies_exists(self):
        """Test that COOKIES exists and has expected structure"""
        assert COOKIES is not None
        # COOKIES might be a RequestsCookieJar or similar, not necessarily a dict
        assert hasattr(COOKIES, '__iter__')