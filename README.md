# 智睦云打印MCP

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
你需要先安装智睦云打印服务器，并完成打印机的共享。请从智睦云打印获取安装包：
- `https://any.webprinter.cn`

然后，你需要拿到云打印访问令牌(token)。

获取地址：

- `[https://any.webprinter.cn/get-ai-server-token](https://any.webprinter.cn/get-ai-server-token)`

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

### 直接使用 `mcpServers` 配置

如果你的 MCP 客户端直接接收 `mcpServers` 结构，也可以直接使用下面这段配置：

```json
{
  "mcpServers": {
    "webprinter": {
      "args": [
        "-y",
        "webprinter_mcp"
      ],
      "command": "npx",
      "env": {
        "WEBPRINTER_ACCESS_TOKEN": "your-access-token"
      },
      "type": "npx"
    }
  }
}
```

其中：

- `WEBPRINTER_ACCESS_TOKEN`
  - 需要先从 `https://any.webprinter.cn/get-ai-server-token` 获取
- `command` 和 `args`
  - 表示通过 `npx webprinter_mcp` 启动 MCP Server
- `type`
  - 表示当前客户端使用 `npx` 方式接入

## 工具列表

当前 MCP Server 提供以下工具：

- `check_install_progress`
  - 检查当前账号和设备环境是否已经具备云打印能力
- `query_printers`
  - 查询当前账号可用的打印机列表
- `query_printer_detail`
  - 查询指定打印机或共享设备的详细能力信息
- `upload_file`
  - 上传本地文件，并返回可用于打印的公网地址
- `create_roaming_task`
  - 根据文件 URL 创建漫游打印任务
- `update_printer_side`
  - 修改漫游打印任务的单双面设置
- `update_printer_color`
  - 修改漫游打印任务的彩色/黑白设置
- `update_printer_copies`
  - 修改漫游打印任务的打印份数
- `update_printer_paper`
  - 修改漫游打印任务的纸张大小，支持 `A3`、`A4` 等预设纸型，也支持自定义宽高
- `direct_print_document`
  - 把文件直接发送到指定打印机进行打印

你也可以把它理解成一套完整的打印流程能力：

1. 先检查环境：`check_install_progress`
2. 再查看打印机：`query_printers` / `query_printer_detail`
3. 上传文件：`upload_file`
4. 创建漫游打印：`create_roaming_task`
5. 按需调整任务参数：`update_printer_side` / `update_printer_color` / `update_printer_copies` / `update_printer_paper`
6. 或者直接打印：`direct_print_document`

## 工具说明

下面按“用途、行为、关键参数、使用建议”的方式说明每个工具，方便在 MCP 平台、目录站和接入文档里展示。

### `check_install_progress`

- 用途
  - 检查当前账号、客户端和打印环境是否已经具备可用的云打印能力
- 什么时候用
  - 第一次接入时先调用
  - 遇到无法打印、查不到打印机、任务提交失败时优先调用
- 行为
  - 向云打印平台查询当前安装和配置状态
  - 不修改任何打印任务
- 参数
  - 无
- 返回结果
  - 返回当前环境检查结果，通常可用于判断客户端、设备或共享配置是否完成
- 使用建议
  - 推荐把它作为所有打印流程的第一步
- 示例说法
  - “先检查一下当前环境能不能用云打印”

### `query_printers`

- 用途
  - 查询当前账号下可用的打印机列表
- 什么时候用
  - 用户想查看可用打印机时
  - 直接打印前先确认目标打印机是否存在时
- 行为
  - 返回打印机列表
  - 对隐藏打印机会标记为仅支持漫游打印任务
- 参数
  - 无
- 返回结果
  - 常见字段包括打印机名称、别名、在线状态、控制端编号、是否隐藏等
- 使用建议
  - 如果用户说“打印到某台打印机”，建议先调用这个工具确认设备名称和控制编号
- 示例说法
  - “帮我看看当前有哪些可用打印机”

### `query_printer_detail`

- 用途
  - 查询某台打印机或共享设备的详细能力信息
- 什么时候用
  - 用户需要确认设备支持的能力时
  - 在打印前确认设备类型、共享编号或详细参数时
- 行为
  - 根据打印机名称、共享编号或设备类型返回详细信息
- 参数
  - `printer_name`
    - 打印机名称，可选
  - `share_sn`
    - 共享设备编号，可选
  - `device_type`
    - 设备类型，可选，支持 `printer`、`scanner`、`camera`
- 返回结果
  - 返回指定设备的详细能力或配置数据
- 使用建议
  - 至少提供一个过滤条件，避免查询范围过大
- 示例说法
  - “帮我看看前台那台打印机支持什么能力”

### `upload_file`

- 用途
  - 上传本地文件，并换取后续打印可使用的公网 URL
- 什么时候用
  - 源文件在本地磁盘上时
  - 漫游打印或直接打印前还没有公网文件地址时
- 行为
  - 读取本地文件并上传到云端
  - 返回一个可被打印服务读取的文件地址
- 参数
  - `file_path`
    - 本地文件路径，必填
- 返回结果
  - 返回上传后的文件信息和可访问地址
- 使用建议
  - 如果文件已经是公网 URL，可以跳过这个步骤
- 示例说法
  - “把我桌面上的 PDF 上传一下，给我一个可打印地址”

### `create_roaming_task`

- 用途
  - 创建漫游打印任务，让文件进入打印队列等待后续处理
- 什么时候用
  - 用户想先生成打印任务，而不是立刻打印到某一台设备时
- 行为
  - 根据文件名、文件 URL 和文件类型创建一个漫游打印任务
  - 成功后返回任务 ID
- 参数
  - `file_name`
    - 文件显示名称，必填
  - `url`
    - 文件公网地址，必填
  - `media_format`
    - 文件格式，必填，支持 `PDF`、`PNG`、`JPG`、`WORD`、`EXCEL`、`PPT` 等
- 返回结果
  - 返回新创建的漫游任务 ID
- 使用建议
  - 后续如果要改单双面、颜色、份数、纸张，都需要先有这个任务 ID
- 示例说法
  - “把这个文件提交成一个漫游打印任务”

### `update_printer_side`

- 用途
  - 修改漫游打印任务的单双面设置
- 什么时候用
  - 用户明确说单面、双面、长边翻转、短边翻转时
- 行为
  - 根据任务 ID 更新任务的打印面设置
- 参数
  - `task_id`
    - 漫游任务 ID，必填
  - `side`
    - 可选值：`ONESIDE`、`DUPLEX`、`TUMBLE`
- 返回结果
  - 返回更新结果
- 使用建议
  - 适用于已经创建好的漫游任务，不用于直接打印任务
- 示例说法
  - “把任务 123 改成双面打印”

### `update_printer_color`

- 用途
  - 修改漫游打印任务的颜色模式
- 什么时候用
  - 用户明确说彩色、黑白、灰度打印时
- 行为
  - 根据任务 ID 更新颜色模式
- 参数
  - `task_id`
    - 漫游任务 ID，必填
  - `color`
    - 可选值：`COLOR`、`MONOCHROME`
- 返回结果
  - 返回更新结果
- 使用建议
  - 当用户说“黑白打印”时应转换为 `MONOCHROME`
- 示例说法
  - “把任务 123 改成黑白打印”

### `update_printer_copies`

- 用途
  - 修改漫游打印任务的打印份数
- 什么时候用
  - 用户说“打印 2 份”“打印 3 份”时
- 行为
  - 根据任务 ID 更新打印份数
- 参数
  - `task_id`
    - 漫游任务 ID，必填
  - `copies`
    - 打印份数，必填，且必须大于等于 `1`
- 返回结果
  - 返回更新结果
- 使用建议
  - 如果用户没有明确说份数，默认不要擅自修改
- 示例说法
  - “把任务 123 改成打印 3 份”

### `update_printer_paper`

- 用途
  - 修改漫游打印任务的纸张尺寸
- 什么时候用
  - 用户说 A3、A4、A5、Letter 等纸型时
  - 用户直接给出宽高时
- 行为
  - 支持标准纸张名称自动转换为毫米宽高
  - 也支持直接传入自定义 `width` 和 `height`
- 参数
  - `task_id`
    - 漫游任务 ID，必填
  - `paper`
    - 可传纸型名称，如 `A4`
    - 也可传对象，如 `{"width": 210, "height": 297}`
- 返回结果
  - 返回更新结果
- 使用建议
  - 宽高单位统一为毫米
  - 当前支持的预设包括 `A0-A6`、`B4`、`B5`、`LETTER`、`LEGAL`、`TABLOID`
- 示例说法
  - “把任务 123 改成 A4 纸”
  - “把任务 123 改成宽 210、高 297 的纸张”

### `direct_print_document`

- 用途
  - 直接把文件发送到指定打印机
- 什么时候用
  - 用户明确指定要立刻打印到某一台打印机时
- 行为
  - 根据文件信息和目标设备信息直接发起打印
  - 如果目标打印机是隐藏打印机，会阻止直接打印，并提示改用漫游任务
- 参数
  - `file_name`
    - 文件显示名称，必填
  - `url`
    - 文件公网地址，必填
  - `media_format`
    - 文件格式，必填
  - `device_name`
    - 目标打印机名称，必填
  - `control_sn`
    - 目标打印机控制端编号，必填
- 返回结果
  - 返回直接打印结果
- 使用建议
  - 建议先调用 `query_printers` 确认目标打印机名称和控制端编号
  - 如果是本地文件，先调用 `upload_file`
- 示例说法
  - “直接把这个文件打印到前台那台打印机”

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

### 然后决定是“漫游打印”还是“直接打印”

如果你只是想先进入打印队列，可以这样理解：
- "把这个文件提交漫游打印"
或
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

- `[https://get-ai-token.webprinter.cn](https://any.webprinter.cn/get-ai-server-token)`

然后确认你已经设置了：

- `WEBPRINTER_ACCESS_TOKEN`

### 命令已经安装了，但找不到 `webprinter_mcp`

通常是 Python 的 `Scripts` 目录还没加入 PATH。  
这时你可以先直接使用：

```bash
python -m webprinter_mcp
```

## 任务配置工具

对于已经创建好的漫游打印任务，现在可以继续修改下面这些配置：

- `update_printer_side(task_id, side)`
- `update_printer_color(task_id, color)`
- `update_printer_copies(task_id, copies)`
- `update_printer_paper(task_id, paper)`

### 参数说明

- `task_id`
  - 漫游打印任务 ID
- `side`
  - 可选值：`ONESIDE`、`DUPLEX`、`TUMBLE`
  - 分别表示：单面、双面长边翻转、双面短边翻转
- `color`
  - 可选值：`COLOR`、`MONOCHROME`
  - 分别表示：彩色、黑白
- `copies`
  - 整数
  - 必须大于等于 `1`
- `paper`
  - 可以直接传纸张类型名称，比如 `A3`、`A4`、`A5`、`LETTER`
  - 也可以传自定义对象：`{"width": 210, "height": 297}`
  - 宽高单位为毫米

### 使用示例

如果你是在 MCP 客户端里通过自然语言调用，可以这样说：

- “把任务 `123` 改成双面打印”
- “把任务 `123` 改成黑白打印”
- “把任务 `123` 改成打印 3 份”
- “把任务 `123` 改成 A4 纸”
- “把任务 `123` 改成宽 210 高 297 的纸张”

如果你是在本地 CLI 里调试，可以这样用：

```bash
python scripts/mcp_client.py update-printer-side --task-id 123 --side DUPLEX
python scripts/mcp_client.py update-printer-color --task-id 123 --color MONOCHROME
python scripts/mcp_client.py update-printer-copies --task-id 123 --copies 3
python scripts/mcp_client.py update-printer-paper --task-id 123 --paper A4
python scripts/mcp_client.py update-printer-paper --task-id 123 --width 210 --height 297
```
