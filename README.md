# WebPrinter MCP

`webprinter-mcp` 是一个标准 `stdio` 形态的 MCP 服务，用于把智睦云 / WebPrinter 的云打印能力暴露为 MCP 工具，方便发布到 PyPI、上传到 MCPWorld，或接入任意支持 MCP 的客户端。

[![CI](https://img.shields.io/badge/CI-ready-blue)](#)
[![PyPI](https://img.shields.io/badge/PyPI-ready-blue)](#)
[![npm](https://img.shields.io/badge/npm-ready-blue)](#)

## Overview

This package exposes Zhimuyun / WebPrinter cloud printing APIs as a standard Model Context Protocol server over `stdio`.

## 功能

- 检查安装状态
- 查询打印机列表
- 查询打印机详情
- 上传本地文件
- 创建漫游打印任务
- 更新单双面设置
- 直接发送打印任务到指定打印机

## 环境变量

- `WEBPRINTER_ACCESS_TOKEN`: 必填，智睦云访问令牌
- `WEBPRINTER_BASE_URL`: 可选，默认 `https://any.webprinter.cn`

## Installation

```bash
pip install webprinter-mcp
```

也支持通过 npm 分发一个轻量启动包装层：

```bash
npm install -g webprinter-mcp
```

注意：npm 包本身是一个 Node 启动器，真正的 MCP 服务仍由 Python 包提供，所以运行前仍需要：

```bash
pip install webprinter-mcp
```

## 本地运行

设置好环境变量后：

```bash
webprinter-mcp
```

或：

```bash
pip install .
webprinter-mcp
```

## MCPWorld 提交建议

MCPWorld 提交页支持 `stdio` 配置。当前项目已经按这个方向整理，并附带了示例文件 [mcpworld.json](/D:/workspaces/mcp/智睦云打印/mcpworld.json)。

示例核心配置，使用 `npx`：

```json
{
  "type": "stdio",
  "config": {
    "mcpServers": {
      "webprinter": {
        "type": "npx",
        "command": "npx",
        "args": ["-y", "webprinter-mcp"],
        "env": {
          "WEBPRINTER_ACCESS_TOKEN": "your-access-token"
        }
      }
    }
  }
}
```

如果你更偏向 Python 生态，也可以继续用 `uvx` 或本地 `python -m` 方式：

```json
{
  "type": "stdio",
  "config": {
    "mcpServers": {
      "webprinter": {
        "type": "uvx",
        "command": "uvx",
        "args": ["webprinter-mcp"],
        "env": {
          "WEBPRINTER_ACCESS_TOKEN": "your-access-token"
        }
      }
    }
  }
}
```

或者：

```json
{
  "type": "stdio",
  "config": {
    "mcpServers": {
      "webprinter": {
        "type": "stdio",
        "command": "python",
        "args": ["-m", "webprinter_mcp"],
        "env": {
          "WEBPRINTER_ACCESS_TOKEN": "your-access-token"
        }
      }
    }
  }
}
```

## 工具列表

- `check_install_progress`
- `query_printers`
- `query_printer_detail`
- `upload_file`
- `create_roaming_task`
- `update_printer_side`
- `direct_print_document`

## 认证说明

WebPrinter 接口需要 Bearer Token。拿到 token 后，写入 `WEBPRINTER_ACCESS_TOKEN` 即可。

## 发布到 PyPI

仓库内已经补好了 PyPI 所需的基础打包文件：

- [pyproject.toml](/D:/workspaces/mcp/智睦云打印/pyproject.toml)
- [MANIFEST.in](/D:/workspaces/mcp/智睦云打印/MANIFEST.in)
- [release.ps1](/D:/workspaces/mcp/智睦云打印/scripts/release.ps1)

标准流程：

```powershell
python -m pip install --upgrade pip
python -m pip install build twine
python -m build
python -m twine check dist/*
python -m twine upload dist/*
```

也可以直接使用：

```powershell
.\scripts\release.ps1
.\scripts\release.ps1 -Upload
```

发布前你需要把 `pyproject.toml` 里的仓库地址改成真实地址。

## 发布到 npm

仓库里已经补了 npm 包入口文件：

- [package.json](/D:/workspaces/mcp/智睦云打印/package.json)
- [webprinter-mcp.js](/D:/workspaces/mcp/智睦云打印/bin/webprinter-mcp.js)

标准流程：

```powershell
npm login
npm pack --dry-run
npm publish
```

这个 npm 包的作用是提供 `npx webprinter-mcp` / 全局命令启动体验。它会尝试调用本机的 `python` 或 `py` 去启动 `python -m webprinter_mcp`。

## 自动发布

仓库里已经补了 GitHub Actions：

- [.github/workflows/ci.yml](/D:/workspaces/mcp/智睦云打印/.github/workflows/ci.yml)
- [.github/workflows/release.yml](/D:/workspaces/mcp/智睦云打印/.github/workflows/release.yml)

默认策略：

- `push` / `pull_request` 时做 Python 构建检查和 npm 打包检查
- 推送 `v*` tag 时发布到 PyPI 和 npm
- 也支持手动触发发布工作流

发布前需要在 GitHub 仓库里配置这些 secrets：

- `PYPI_API_TOKEN`
- `NPM_TOKEN`

更细的发布准备事项见 [RELEASE_CHECKLIST.md](/D:/workspaces/mcp/智睦云打印/RELEASE_CHECKLIST.md)。

## 目录说明

- `src/webprinter_mcp/client.py`: WebPrinter API 封装
- `src/webprinter_mcp/server.py`: MCP server 入口
- `scripts/mcp_client.py`: 保留的命令行调试入口
- `references/mcp_api.md`: 原始接口参考
