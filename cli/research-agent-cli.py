#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import threading

from dotenv import load_dotenv
from huggingface_hub import login
from src.open_deep_research.text_inspector_tool import TextInspectorTool
from src.open_deep_research.text_web_browser import ArchiveSearchTool, FinderTool, FindNextTool, PageDownTool, PageUpTool, SimpleTextBrowser, VisitTool
from src.open_deep_research.visual_qa import visualizer

from smolagents import CodeAgent, GoogleSearchTool, LiteLLMModel, ToolCallingAgent

load_dotenv(override=True)
login(os.getenv("HF_TOKEN"))

append_answer_lock = threading.Lock()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "question", type=str, help="for example: 'How many studio albums did Mercedes Sosa release before 2007?'"
    )
    parser.add_argument("--model", type=str, default="o1")
    parser.add_argument("--api-base", type=str, help="Base URL for the API endpoint")
    parser.add_argument("--api-key", type=str, help="API key for authentication")
    parser.add_argument(
        "--manager-agent-type", 
        type=str, 
        choices=["CodeAgent", "ToolCallingAgent"], 
        default="CodeAgent",
        help="Type of agent to use for the manager (default: CodeAgent)"
    )
    parser.add_argument(
        "--search-agent-type", 
        type=str, 
        choices=["CodeAgent", "ToolCallingAgent"], 
        default="ToolCallingAgent",
        help="Type of agent to use for the search agent (default: ToolCallingAgent)"
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

def create_agent(model="o1", api_base=None, api_key=None, manager_agent_type="CodeAgent", search_agent_type="ToolCallingAgent"):
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

    text_limit = 100000
    browser = SimpleTextBrowser(**BROWSER_CONFIG)
    WEB_TOOLS = [
        GoogleSearchTool(provider="serper"),
        VisitTool(browser),
        PageUpTool(browser),
        PageDownTool(browser),
        FinderTool(browser),
        FindNextTool(browser),
        ArchiveSearchTool(browser),
        TextInspectorTool(model, text_limit),
    ]
    
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

    agent = create_agent(model=args.model, api_base=args.api_base, api_key=args.api_key, manager_agent_type=args.manager_agent_type, search_agent_type=args.search_agent_type)

    answer = agent.run(args.question)

    print(f"Got this answer: {answer}")

if __name__ == "__main__":
    main()
