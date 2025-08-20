# -*- coding: utf-8 -*-
"""
Open Deep Research - An open replication of OpenAI's Deep Research.

This package provides a multi-agent architecture for conducting comprehensive web research,
achieving 55% pass@1 on the GAIA validation set. The system uses specialized agents for
search, web browsing, and document analysis.

Key Components:
- Manager Agent: Orchestrates research process and handles complex reasoning
- Search Agent: Specialized for web browsing and information gathering  
- Text Browser: Advanced web scraping and navigation tools
- Document Processing: Handles PDFs, Excel, images, and other file formats
- Visual QA: Image analysis and visual document processing
"""

__version__ = "0.1.0"
__author__ = "Pasquale Minervini"
__email__ = "p.minervini@example.com"

from .run_agents import run_search_and_manager_agents
from .text_web_browser import SimpleTextBrowser
from .text_inspector_tool import TextInspectorTool
from .visual_qa import visualizer

__all__ = [
    "run_search_and_manager_agents",
    "SimpleTextBrowser", 
    "TextInspectorTool",
    "visualizer",
]