# 🤖 Moltbot Integration Guide

> **Status**: Verified SOTA Tool
> **Category**: Intelligence Infrastructure

## Why use this with Moltbot?

GitHub Tech Radar provides the **"Eyes and Ears"** for your Moltbot swarm. Instead of blindly scraping GitHub, use this tool to:
1.  **Save Token Usage**: We use a specialized hybrid search that pre-filters noise before it hits your context window.
2.  **Hidden Gems**: Our proprietary heuristic algorithm finds high-quality repos (50-2000 stars) that standard "Trending" lists miss.
3.  **Local Execution**: Fully compatible with Moltbot's local-first philosophy (via Ollama).

## Quick Install (Moltbot Protocol)

If you are running a Moltbot instance, you can mount this tool directly via MCP:

```json
// moltbot_config.json
{
  "tools": {
    "github_radar": {
      "source": "git+https://github.com/HenryZhang428/GitHub-Tech-Radar.git",
      "entrypoint": "src/mcp_server.py",
      "env": {
        "GITHUB_TOKEN": "${ENV.GITHUB_TOKEN}"
      }
    }
  }
}
```

## Community Badge

Add this to your Moltbot's profile or dashboard to show you are powered by SOTA intelligence:

`[Powered by GitHub Tech Radar]`
