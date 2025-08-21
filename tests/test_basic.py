# -*- coding: utf-8 -*-

import pytest
import sys
import os
import open_deep_research


class TestBasicFunctionality:
    def test_import_package(self):
        """Test that the main package can be imported"""
        import open_deep_research
        assert open_deep_research is not None

    def test_package_structure(self):
        """Test that expected modules exist in the package"""
        import open_deep_research
        package_path = open_deep_research.__file__.replace('__init__.py', '')
        
        expected_files = [
            'cookies.py',
            'reformulator.py', 
            'run_agents.py',
            'visual_qa.py'
        ]
        
        for file in expected_files:
            file_path = os.path.join(package_path, file)
            assert os.path.exists(file_path), f"Expected file {file} not found"

    def test_python_version(self):
        """Test that we're running on a supported Python version"""
        assert sys.version_info >= (3, 8), "Python 3.8+ required"

    def test_cli_files_exist(self):
        """Test that CLI files exist"""
        base_dir = os.path.dirname(os.path.dirname(__file__))
        cli_dir = os.path.join(base_dir, 'cli')
        
        expected_cli_files = [
            'research-agent-cli.py',
            'gaia-eval-cli.py',
            'search-cli.py'
        ]
        
        for file in expected_cli_files:
            file_path = os.path.join(cli_dir, file)
            assert os.path.exists(file_path), f"Expected CLI file {file} not found"

    def test_requirements_file_exists(self):
        """Test that requirements.txt exists"""
        base_dir = os.path.dirname(os.path.dirname(__file__))
        requirements_path = os.path.join(base_dir, 'requirements.txt')
        assert os.path.exists(requirements_path), "requirements.txt not found"