#!/usr/bin/env python
# coding=utf-8

import argparse
import sys
import os
from pathlib import Path

# Add the smolagents source directory to the path
smolagents_path = Path(__file__).parent.parent.parent / "smolagents" / "src"
if smolagents_path.exists():
    sys.path.insert(0, str(smolagents_path))

try:
    from smolagents import (
        DuckDuckGoSearchTool,
        GoogleSearchTool, 
        ApiWebSearchTool,
        WebSearchTool,
        VisitWebpageTool,
        WikipediaSearchTool
    )
except ImportError as e:
    print(f"Error importing smolagents: {e}")
    print("Make sure smolagents is installed and available in your path")
    sys.exit(1)


def create_duckduckgo_tool(args):
    """Create DuckDuckGoSearchTool with specified parameters."""
    kwargs = {}
    if args.max_results:
        kwargs['max_results'] = args.max_results
    if args.rate_limit is not None:
        kwargs['rate_limit'] = args.rate_limit
    return DuckDuckGoSearchTool(**kwargs)


def create_google_tool(args):
    """Create GoogleSearchTool with specified parameters."""
    kwargs = {}
    if args.provider:
        kwargs['provider'] = args.provider
    return GoogleSearchTool(**kwargs)


def create_api_tool(args):
    """Create ApiWebSearchTool with specified parameters."""
    kwargs = {}
    if args.endpoint:
        kwargs['endpoint'] = args.endpoint
    if args.api_key:
        kwargs['api_key'] = args.api_key
    if args.api_key_name:
        kwargs['api_key_name'] = args.api_key_name
    if args.rate_limit is not None:
        kwargs['rate_limit'] = args.rate_limit
    return ApiWebSearchTool(**kwargs)


def create_websearch_tool(args):
    """Create WebSearchTool with specified parameters."""
    kwargs = {}
    if args.max_results:
        kwargs['max_results'] = args.max_results
    if args.engine:
        kwargs['engine'] = args.engine
    return WebSearchTool(**kwargs)


def create_visit_tool(args):
    """Create VisitWebpageTool with specified parameters."""
    kwargs = {}
    if args.max_output_length:
        kwargs['max_output_length'] = args.max_output_length
    return VisitWebpageTool(**kwargs)


def create_wikipedia_tool(args):
    """Create WikipediaSearchTool with specified parameters."""
    kwargs = {}
    if args.user_agent:
        kwargs['user_agent'] = args.user_agent
    if args.language:
        kwargs['language'] = args.language
    if args.content_type:
        kwargs['content_type'] = args.content_type
    if args.extract_format:
        kwargs['extract_format'] = args.extract_format
    return WikipediaSearchTool(**kwargs)


def main():
    parser = argparse.ArgumentParser(
        description="CLI tool to access all smolagents web search tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # DuckDuckGo search
  python cli/search-cli.py duckduckgo "Python programming"
  
  # Google search with year filter
  python cli/search-cli.py google "machine learning" --filter-year 2023
  
  # API search (Brave by default)
  python cli/search-cli.py api "AI news"
  
  # Simple web search
  python cli/search-cli.py websearch "climate change" --engine bing
  
  # Visit a webpage
  python cli/search-cli.py visit "https://example.com"
  
  # Wikipedia search
  python cli/search-cli.py wikipedia "Python_(programming_language)" --content-type summary
        """
    )
    
    subparsers = parser.add_subparsers(dest='tool', help='Available search tools')
    
    # DuckDuckGo Search Tool
    ddg_parser = subparsers.add_parser('duckduckgo', help='DuckDuckGo web search')
    ddg_parser.add_argument('query', help='Search query')
    ddg_parser.add_argument('--max-results', type=int, default=10, help='Maximum number of results (default: 10)')
    ddg_parser.add_argument('--rate-limit', type=float, help='Queries per second (default: 1.0, None to disable)')
    
    # Google Search Tool
    google_parser = subparsers.add_parser('google', help='Google search via SerpAPI or Serper')
    google_parser.add_argument('query', help='Search query')
    google_parser.add_argument('--filter-year', type=int, help='Filter results by year')
    google_parser.add_argument('--provider', choices=['serpapi', 'serper'], default='serpapi', help='Search provider (default: serpapi)')
    
    # API Web Search Tool
    api_parser = subparsers.add_parser('api', help='API-based web search (Brave Search by default)')
    api_parser.add_argument('query', help='Search query')
    api_parser.add_argument('--endpoint', help='API endpoint URL')
    api_parser.add_argument('--api-key', help='API key for authentication')
    api_parser.add_argument('--api-key-name', help='Environment variable name for API key')
    api_parser.add_argument('--rate-limit', type=float, help='Queries per second (default: 1.0)')
    
    # Web Search Tool
    web_parser = subparsers.add_parser('websearch', help='Simple web search using HTML/RSS scrapers')
    web_parser.add_argument('query', help='Search query')
    web_parser.add_argument('--max-results', type=int, default=10, help='Maximum number of results (default: 10)')
    web_parser.add_argument('--engine', choices=['duckduckgo', 'bing'], default='duckduckgo', help='Search engine (default: duckduckgo)')
    
    # Visit Webpage Tool
    visit_parser = subparsers.add_parser('visit', help='Visit and read webpage content')
    visit_parser.add_argument('url', help='URL to visit')
    visit_parser.add_argument('--max-output-length', type=int, default=40000, help='Maximum output length (default: 40000)')
    
    # Wikipedia Search Tool
    wiki_parser = subparsers.add_parser('wikipedia', help='Search Wikipedia articles')
    wiki_parser.add_argument('query', help='Wikipedia topic to search')
    wiki_parser.add_argument('--user-agent', default='SearchCLI (smolagents)', help='User agent string')
    wiki_parser.add_argument('--language', default='en', help='Language code (default: en)')
    wiki_parser.add_argument('--content-type', choices=['summary', 'text'], default='text', help='Content type (default: text)')
    wiki_parser.add_argument('--extract-format', choices=['WIKI', 'HTML'], default='WIKI', help='Extract format (default: WIKI)')
    
    args = parser.parse_args()
    
    if not args.tool:
        parser.print_help()
        sys.exit(1)
    
    try:
        # Create the appropriate tool and execute the search
        if args.tool == 'duckduckgo':
            tool = create_duckduckgo_tool(args)
            result = tool.forward(args.query)
            
        elif args.tool == 'google':
            tool = create_google_tool(args)
            if hasattr(args, 'filter_year') and args.filter_year:
                result = tool.forward(args.query, filter_year=args.filter_year)
            else:
                result = tool.forward(args.query)
                
        elif args.tool == 'api':
            tool = create_api_tool(args)
            result = tool.forward(args.query)
            
        elif args.tool == 'websearch':
            tool = create_websearch_tool(args)
            result = tool.forward(args.query)
            
        elif args.tool == 'visit':
            tool = create_visit_tool(args)
            result = tool.forward(args.url)
            
        elif args.tool == 'wikipedia':
            tool = create_wikipedia_tool(args)
            result = tool.forward(args.query)
            
        print(result)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()