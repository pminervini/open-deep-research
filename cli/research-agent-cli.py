#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Research Agent CLI - A powerful command-line tool for conducting web research using AI agents.

This script creates a research agent that can search the internet, visit webpages, and analyze content
to answer complex questions. The agent uses a manager-worker architecture with specialized search
and browsing capabilities.

Features:
- Multiple search engines (Google, DuckDuckGo, Wikipedia, etc.)
- Web browsing and content analysis
- PDF and video content inspection
- Multi-step research planning
- Support for various AI models

Examples:
    Basic usage:
        python cli/research-agent-cli.py "What are the latest developments in quantum computing?"
    
    Using a specific model:
        python cli/research-agent-cli.py "Compare Tesla and BYD electric vehicle sales in 2024" --model openai/gpt-oss:20b
    
    With custom API endpoint:
        python cli/research-agent-cli.py "Find the population of Tokyo in 2023" --api-base http://localhost:11434/v1 --api-key api-key
    
    Using specific search tools:
        python cli/research-agent-cli.py "Latest AI research papers" --search-tools duckduckgo,wikipedia
    
    With different agent types:
        python cli/research-agent-cli.py "Climate change impact on agriculture" --manager-agent-type ToolCallingAgent --search-agent-type CodeAgent
"""


import argparse
import os
import threading

from dotenv import load_dotenv
from huggingface_hub import login

from smolagents import (
    ApiWebSearchTool,
    CodeAgent,
    DuckDuckGoSearchTool,
    GoogleSearchTool,
    LiteLLMModel,
    ToolCallingAgent,
    WebSearchTool,
    WikipediaSearchTool,
)
from src.open_deep_research.text_inspector_tool import TextInspectorTool
from src.open_deep_research.text_web_browser import (
    ArchiveSearchTool,
    FinderTool,
    FindNextTool,
    PageDownTool,
    PageUpTool,
    SimpleTextBrowser,
    VisitTool,
)
from src.open_deep_research.visual_qa import visualizer


load_dotenv(override=True)
login(os.getenv("HF_TOKEN"))

append_answer_lock = threading.Lock()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "question", type=str, help="for example: 'How many studio albums did Mercedes Sosa release before 2007?'"
    )
    parser.add_argument("--model", '-m', type=str, default="openai/gpt-oss:20b")
    parser.add_argument(
        "--api-base", type=str, help="Base URL for the API endpoint", default="http://localhost:11434/v1"
    )
    parser.add_argument("--api-key", type=str, help="API key for authentication", default="api-key")
    parser.add_argument(
        "--manager-agent-type",
        type=str,
        choices=["CodeAgent", "ToolCallingAgent"],
        default="CodeAgent",
        help="Type of agent to use for the manager (default: CodeAgent)",
    )
    parser.add_argument(
        "--search-agent-type",
        type=str,
        choices=["CodeAgent", "ToolCallingAgent"],
        default="ToolCallingAgent",
        help="Type of agent to use for the search agent (default: ToolCallingAgent)",
    )
    parser.add_argument(
        "--search-tools",
        "-s",
        nargs="+",
        choices=["google", "duckduckgo", "wikipedia", "brave", "websearch"],
        default=["google"],
        help="Search tools to use (default: google). Can specify multiple tools. Options: google (requires SERPAPI/SERPER API key), duckduckgo, wikipedia, brave (requires BRAVE API key), websearch (simple scraper). Example: --search-tools google duckduckgo wikipedia",
    )
    return parser.parse_args()


custom_role_conversions = {"tool-call": "assistant", "tool-response": "user"}

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"

BROWSER_CONFIG = {
    "viewport_size": 1024 * 5,
    "downloads_folder": "downloads_folder",
    "request_kwargs": {
        "headers": {"User-Agent": user_agent},
        "timeout": 300,
    },
    "serpapi_key": os.getenv("SERPAPI_API_KEY"),
}

os.makedirs(f"./{BROWSER_CONFIG['downloads_folder']}", exist_ok=True)


def create_search_tool(search_tool_type):
    """Create and return a single search tool instance."""
    try:
        if search_tool_type == "google":
            # GoogleSearchTool requires SERPAPI_API_KEY or SERPER_API_KEY
            return GoogleSearchTool(provider="serper")
        elif search_tool_type == "duckduckgo":
            # DuckDuckGoSearchTool requires no API key
            return DuckDuckGoSearchTool()
        elif search_tool_type == "wikipedia":
            # WikipediaSearchTool requires no API key
            return WikipediaSearchTool(user_agent="OpenDeepResearch/1.0 (research@example.com)")
        elif search_tool_type == "brave":
            # ApiWebSearchTool requires BRAVE_API_KEY
            return ApiWebSearchTool()
        elif search_tool_type == "websearch":
            # WebSearchTool requires no API key (uses simple scrapers)
            return WebSearchTool()
        else:
            raise ValueError(f"Unknown search tool type: {search_tool_type}")
    except Exception as e:
        print(f"Error creating search tool '{search_tool_type}': {e}")
        print("Hint: Check that you have the required API key set as an environment variable.")
        if search_tool_type == "google":
            print("For Google search, you need SERPAPI_API_KEY or SERPER_API_KEY")
        elif search_tool_type == "brave":
            print("For Brave search, you need BRAVE_API_KEY")
        raise


def create_search_tools(search_tool_types):
    """Create and return multiple search tool instances."""
    search_tools = []
    failed_tools = []

    # Remove duplicates while preserving order
    unique_tool_types = list(dict.fromkeys(search_tool_types))

    for tool_type in unique_tool_types:
        try:
            tool = create_search_tool(tool_type)
            search_tools.append(tool)
            print(f"✓ Successfully created {tool_type} search tool")
        except Exception as e:
            failed_tools.append((tool_type, str(e)))
            print(f"✗ Failed to create {tool_type} search tool: {e}")

    if not search_tools:
        raise ValueError(f"Failed to create any search tools. Errors: {failed_tools}")

    if failed_tools:
        print(
            f"Warning: {len(failed_tools)} search tool(s) failed to initialize. Continuing with {len(search_tools)} working tool(s)."
        )

    return search_tools


def create_agent(
    model="openai/gpt-oss:20b",
    api_base=None,
    api_key=None,
    manager_agent_type="CodeAgent",
    search_agent_type="ToolCallingAgent",
    search_tools=None,
):
    model_params = {
        "model_id": model,
        "custom_role_conversions": custom_role_conversions,
        "max_completion_tokens": 8192,
    }

    if api_base:
        model_params["api_base"] = api_base
    if api_key:
        model_params["api_key"] = api_key
    if model == "o1":
        model_params["reasoning_effort"] = "high"

    model = LiteLLMModel(**model_params)

    if search_tools is None:
        search_tools = ["google"]

    text_limit = 100000
    browser = SimpleTextBrowser(**BROWSER_CONFIG)
    search_tool_instances = create_search_tools(search_tools)

    # Build web tools list with all search tools
    WEB_TOOLS = []
    WEB_TOOLS.extend(search_tool_instances)  # Add all search tools
    WEB_TOOLS.extend(
        [
            VisitTool(browser),
            PageUpTool(browser),
            PageDownTool(browser),
            FinderTool(browser),
            FindNextTool(browser),
            ArchiveSearchTool(browser),
            TextInspectorTool(model, text_limit),
        ]
    )

    # Create search agent based on specified type
    search_agent_config = {
        "model": model,
        "max_steps": 20,
        "verbosity_level": 2,
        "planning_interval": 4,
        "name": "search_agent",
        "description": """A team member that will search the internet to answer your question.
    Ask him for all your questions that require browsing the web.
    Provide him as much context as possible, in particular if you need to search on a specific timeframe!
    And don't hesitate to provide him with a complex search task, like finding a difference between two webpages.
    Your request must be a real sentence, not a google search! Like "Find me this information (...)" rather than a few keywords.
    """,
        "provide_run_summary": True,
    }

    if search_agent_type == "ToolCallingAgent":
        search_agent_config["tools"] = WEB_TOOLS
        text_webbrowser_agent = ToolCallingAgent(**search_agent_config)
    else:  # CodeAgent
        search_agent_config["tools"] = WEB_TOOLS
        search_agent_config["additional_authorized_imports"] = ["*"]
        text_webbrowser_agent = CodeAgent(**search_agent_config)

    text_webbrowser_agent.prompt_templates["managed_agent"]["task"] += """You can navigate to .txt online files.
    If a non-html page is in another format, especially .pdf or a Youtube video, use tool 'inspect_file_as_text' to inspect it.
    Additionally, if after some searching you find out that you need more information to answer the question, you can use `final_answer` with your request for clarification as argument to request for more information."""

    # Create manager agent based on specified type
    manager_agent_config = {
        "model": model,
        "tools": [visualizer, TextInspectorTool(model, text_limit)],
        "max_steps": 12,
        "verbosity_level": 2,
        "planning_interval": 4,
        "managed_agents": [text_webbrowser_agent],
    }

    if manager_agent_type == "CodeAgent":
        manager_agent_config["additional_authorized_imports"] = ["*"]
        manager_agent = CodeAgent(**manager_agent_config)
    else:  # ToolCallingAgent
        manager_agent = ToolCallingAgent(**manager_agent_config)

    return manager_agent


def main():
    args = parse_args()

    agent = create_agent(
        model=args.model,
        api_base=args.api_base,
        api_key=args.api_key,
        manager_agent_type=args.manager_agent_type,
        search_agent_type=args.search_agent_type,
        search_tools=args.search_tools,
    )

    answer = agent.run(args.question)

    print(f"Got this answer: {answer}")


if __name__ == "__main__":
    main()
