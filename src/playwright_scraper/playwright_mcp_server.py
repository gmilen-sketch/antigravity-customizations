#!/usr/bin/env python3
"""
FastMCP Server for Headless Browser Navigation & DOM Scraping in Antigravity Web Hub.
"""

import os
import sys
import json
import logging

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.dirname(_HERE)
for _p in (_HERE, _SRC):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from mcp_servers.stdio_fastmcp_compat import FastMCP

from playwright_scraper import fetch_page_markdown

EAGER_TOOL_META = {"antigravity/alwaysLoad": True}

mcp = FastMCP("playwright_scraper_mcp")

@mcp.tool()
def browse_webpage(url: str) -> str:
    """Navigates to a public web page and extracts its content as structured markdown text."""
    return fetch_page_markdown(url)

if __name__ == "__main__":
    mcp.run()
