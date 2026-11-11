#!/usr/bin/env python3
"""
FastMCP Server for Six Thinking Hats Reasoning in Antigravity Web Hub.
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

from six_hats import format_six_hats_prompt

EAGER_TOOL_META = {"antigravity/alwaysLoad": True}

mcp = FastMCP("six_hats_evaluator_mcp")

@mcp.tool()
def evaluate_architecture_six_hats(topic: str, context: str = "") -> str:
    """Generates a comprehensive 360-degree Six Thinking Hats audit template to pressure-test code, API designs, or architectures."""
    return format_six_hats_prompt(topic, context)

if __name__ == "__main__":
    mcp.run()
