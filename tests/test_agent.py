#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test for research agent using DuckDuckGo search engine.

This test validates the research agent's ability to search for and analyze
academic papers using DuckDuckGo as the search backend.
"""

import os
import threading
from dotenv import load_dotenv
from huggingface_hub import login

from smolagents import (
    CodeAgent,
    DuckDuckGoSearchTool,
    LiteLLMModel,
    ToolCallingAgent,
)
from open_deep_research.text_inspector_tool import TextInspectorTool
from open_deep_research.text_web_browser import (
    ArchiveSearchTool,
    FinderTool,
    FindNextTool,
    PageDownTool,
    PageUpTool,
    SimpleTextBrowser,
    VisitTool,
)
from open_deep_research.visual_qa import visualizer


def test_research_agent_duckduckgo():
    """Test research agent with DuckDuckGo search for latest Pasquale Minervini paper on arxiv."""
    
    # Load environment variables
    load_dotenv(override=True)
    if os.getenv("HF_TOKEN"):
        login(os.getenv("HF_TOKEN"))

    # Configuration
    model_id = "openai/qwen/qwen3-coder-30b"
    api_base = "http://localhost:1234/v1"
    api_key = "api-key"
    
    custom_role_conversions = {"tool-call": "assistant", "tool-response": "user"}
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"
    
    browser_config = {
        "viewport_size": 1024 * 5,
        "downloads_folder": "downloads_folder",
        "request_kwargs": {
            "headers": {"User-Agent": user_agent},
            "timeout": 300,
        },
        "serpapi_key": os.getenv("SERPAPI_API_KEY"),
    }
    
    os.makedirs(f"./{browser_config['downloads_folder']}", exist_ok=True)
    
    # Create model
    model = LiteLLMModel(
        model_id=model_id,
        api_base=api_base,
        api_key=api_key,
        custom_role_conversions=custom_role_conversions,
        max_completion_tokens=8192,
    )
    
    # Set up browser and tools
    text_limit = 100000
    browser = SimpleTextBrowser(**browser_config)
    
    # Create web tools with DuckDuckGo search
    web_tools = [
        DuckDuckGoSearchTool(),
        VisitTool(browser),
        PageUpTool(browser),
        PageDownTool(browser),
        FinderTool(browser),
        FindNextTool(browser),
        ArchiveSearchTool(browser),
        TextInspectorTool(model, text_limit),
    ]
    
    # Create search agent
    search_agent = ToolCallingAgent(
        model=model,
        tools=web_tools,
        max_steps=20,
        verbosity_level=2,
        planning_interval=4,
        name="search_agent",
        description="""A team member that will search the internet to answer your question.
Ask him for all your questions that require browsing the web.
Provide him as much context as possible, in particular if you need to search on a specific timeframe!
And don't hesitate to provide him with a complex search task, like finding a difference between two webpages.
Your request must be a real sentence, not a google search! Like "Find me this information (...)" rather than a few keywords.
""",
        provide_run_summary=True,
    )
    
    # Add custom prompt template
    search_agent.prompt_templates["managed_agent"]["task"] += """You can navigate to .txt online files.
If a non-html page is in another format, especially .pdf or a Youtube video, use tool 'inspect_file_as_text' to inspect it.
Additionally, if after some searching you find out that you need more information to answer the question, you can use `final_answer` with your request for clarification as argument to request for more information."""
    
    # Create manager agent
    manager_agent = CodeAgent(
        model=model,
        tools=[visualizer, TextInspectorTool(model, text_limit)],
        max_steps=12,
        verbosity_level=2,
        planning_interval=4,
        managed_agents=[search_agent],
        additional_authorized_imports=["*"],
    )
    
    # Run the research task
    question = "What's the latest paper by Pasquale Minervini on arxiv?"
    answer = manager_agent.run(question)
    
    # Assertions
    assert isinstance(answer, str)
    assert len(answer) > 0
    
    # Check that the answer contains relevant information about papers/research
    answer_lower = answer.lower()
    assert any(keyword in answer_lower for keyword in ["paper", "arxiv", "research", "publication", "minervini"])
    
    print(f"Research completed successfully. Answer: {answer}")