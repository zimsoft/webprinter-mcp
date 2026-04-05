# WebPrinter MCP

`webprinter_mcp` 是一个用于云打印的 MCP Server。  
如果你的 MCP 客户端支持 `stdio` 类型的 MCP，就可以通过它完成文件上传、查询打印机、提交打印任务和直接打印。

## 它可以帮你做什么

你可以把它理解成一个“会帮你处理打印任务的工具”。

比如你可以对接入了这个 MCP 的 AI 说：

- “帮我看看现在有没有可用打印机”
- “把这个文件上传一下，准备打印”
- “把这个文件加入打印队列”
- “直接打印到办公室那台打印机”
- “把刚才那个任务改成双面”

## 使用前先准备

你需要先拿到 WebPrinter 的访问令牌。

获取地址：

- `http://get-ai-token.webprinter.cn`

拿到 token 之后，设置环境变量：

- `WEBPRINTER_ACCESS_TOKEN`：必填

## 安装

### 用 pip 安装

```bash
pip install webprinter_mcp
```

### 或者从源码安装

```bash
pip install .
```

## 启动方式

如果你只是想确认它在本地能不能启动，可以运行：

```bash
webprinter_mcp
```

或者：

```bash
python -m webprinter_mcp
```

注意：这个命令启动后通常不会主动打印提示信息。  
它会进入等待 MCP 客户端连接的状态，这是正常现象。

## 在 MCP 客户端里怎么配置

当前这个项目更适合以 `stdio` 方式接入。

### 本地 Python 方式

如果你已经在本机装好了这个包，推荐这样配：

```json
{
  "type": "stdio",
  "config": {
    "mcpServers": {
      "webprinter": {
        "type": "stdio",
        "command": "webprinter_mcp",
        "args": [],
        "env": {
          "WEBPRINTER_ACCESS_TOKEN": "your-access-token"
        }
      }
    }
  }
}
```

### npx 方式

如果你的客户端支持 `npx` 风格，也可以这样配：

```json
{
  "type": "stdio",
  "config": {
    "mcpServers": {
      "webprinter": {
        "type": "npx",
        "command": "npx",
        "args": ["-y", "webprinter_mcp"],
        "env": {
          "WEBPRINTER_ACCESS_TOKEN": "your-access-token"
        }
      }
    }
  }
}
```

注意：如果你用 `npx webprinter_mcp`，本机依然需要有可用的 Python 运行环境。

## 第一次接入建议怎么试

第一次使用时，建议这样一步一步来：

### 先检查当前账号是不是已经具备云打印条件

你可以这样理解：

- “先帮我检查一下当前环境能不能正常用云打印”

如果返回里显示客户端或设备还没准备好，那就先完成 WebPrinter 侧安装和共享配置。

### 再让它列出当前可用打印机

你可以这样说：

- “帮我看看现在都有哪些打印机”

这一步通常能拿到：

- 打印机名称
- 打印机别名
- 在线状态
- 控制端编号

### 如果你有本地文件，先上传

你可以理解成：

- “把我本地这个 PDF 上传一下，给我一个可打印地址”

本地调试时，常见参数长这样：

```json
{
  "file_path": "C:\\\\docs\\\\report.pdf"
}
```

### 然后决定是“加入队列”还是“直接打印”

如果你只是想先进入打印队列，可以这样理解：

- “把这个文件加入打印队列”

如果你要立刻打到某台打印机，可以这样理解：

- “直接把这个文件打到办公室那台 HP 打印机”

## 更口语化的使用示例

下面这些说法，都是这个 MCP 比较适合处理的：

- “帮我检查一下当前云打印环境能不能用”
- “帮我看看有哪些可用打印机”
- “把我桌面上的 PDF 上传一下”
- “把这个网页加入打印队列”
- “直接打印到前台那台打印机”
- “把刚才那个任务改成双面”

## 常见问题

### 为什么我运行 `webprinter_mcp` 后没反应

这是正常的。  
它启动后会一直等待 MCP 客户端通过 `stdio` 连接，不会像普通命令行工具那样立刻打印很多信息。

### 启动时报 token 相关错误怎么办

请先去这里拿 token：

- `http://get-ai-token.webprinter.cn`

然后确认你已经设置了：

- `WEBPRINTER_ACCESS_TOKEN`

### 命令已经安装了，但找不到 `webprinter_mcp`

通常是 Python 的 `Scripts` 目录还没加入 PATH。  
这时你可以先直接使用：

```bash
python -m webprinter_mcp
```
