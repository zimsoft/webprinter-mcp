# WebPrinter 云打印服务 API 文档

## 概述

WebPrinter 云打印服务提供 RESTful API 接口，支持上传文件、提交打印任务、直接打印文档。

**服务域名**：`https://any.webprinter.cn`

**传输方式**：HTTP POST (JSON)

---

## 认证说明

### 访问令牌获取

所有 API 请求都需要在 HTTP 请求头中携带访问令牌。

**授权流程**：
1. 访问授权页面获取授权码：
   ```
   https://any.webprinter.cn/mcp/client/oauth/authorize?client_id=iS9iU3gM1kB5gZ3sH6hA&redirect_uri=https%3A%2F%2Fany.webprinter.cn%2Fmcp%2Fclient%2Foauth%2Fcallback&response_type=code&scope=all
   ```
2. 完成授权后，获取访问令牌
3. 将令牌保存到环境变量供后续调用使用

**请求头格式**：
```
Authorization: Bearer <your_access_token>
```

**环境变量**：
- 变量名：`WEBPRINTER_ACCESS_TOKEN`
- 格式：令牌字符串（不含 "Bearer " 前缀，脚本会自动添加）

---

## 核心 API 接口

### 1. checkInstallProgressMCP - 检查系统安装配置进度（首次使用必做）

**接口路径**：`POST /openapi/platform/checkInstallProgressMCP`

**功能**：检查用户是否已配置云打印服务器和打印机

**请求参数**：无

**使用场景**：OAuth授权完成后，**必须**首先调用此接口检测环境配置

**返回参数**：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| hasClient | boolean | 是否有绑定的服务器或客户端。**false** 表示用户未安装打印服务器，需引导安装 |
| hasDevice | boolean | 是否有共享的打印机。**false** 表示用户未共享打印机，需引导共享 |
| hasUser | boolean | 是否为其他用户授予了应用权限（可选检查） |

**返回示例**：

```json
{
  "hasClient": false,
  "hasDevice": false,
  "hasUser": false
}
```

**处理逻辑**：
- `hasClient: false` → 引导用户安装云打印服务器，提供安装指南链接
- `hasDevice: false` → 引导用户在服务器上共享打印机
- 全部为 `true` → 环境配置完成，可正常使用打印功能

**安装指南**：https://liqdopokb8.feishu.cn/docx/A0audnVIaoolXqxWUHPcvYlUnFd

---

### 2. uploadFileMCP - 上传文件

**接口路径**：`POST /openapi/mcpClient/uploadFileMCP`

**功能**：上传文件返回一个可访问的公网文件地址

**请求格式**：`multipart/form-data`

**参数**：

| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| file | file | 是 | 要上传的文件 |

**使用场景**：
- 用户上传文件时
- 用户有本地文件需要打印时（先上传获取URL）

**返回示例**：

```json
{
  "success": true,
  "data": {
    "url": "https://any.webprinter.cn/files/abc123/document.pdf"
  }
}
```

---

### 2. createRoamingTask - 提交打印任务

**接口路径**：`POST /openapi/task/createRoamingTask`

**功能**：将文档提交到打印队列

**请求参数**：

| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| fileName | string | 是 | 文档名称 |
| url | string | 是 | 文档的访问URL |
| mediaFormat | string | 是 | 文档格式 |

**使用场景**：
- 用户说"提交打印队列"、"创建漫游任务"、"添加到打印队列"等
- **注意**：此场景无需查询打印机信息

**支持的文档格式**：
HTML, PNG, JPG, PDF, BMP, WEBP, WORD, EXCEL, PPT, TEXT, WPS, ODF, ODT, ODS, ODP, ODG, XPS, PWG

**返回值**：

⚠️ **重要**：此接口返回的是**纯字符串**（任务ID），而非JSON对象。

**返回示例**：

```
TASK_20240324_001
```

**脚本处理**：客户端脚本会自动将字符串包装为统一格式：

```json
{
  "success": true,
  "taskId": "TASK_20240324_001"
}
```

---

### 3. queryPrinters - 查询打印机列表

**接口路径**：`POST /openapi/control/queryPrinters`

**功能**：查询用户的打印机列表

**请求参数**：无

**使用场景**：
- 用户明确说"直接打印"、"立即打印"、"打印出来"时（需要指定打印机）

**返回字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | 是否调用成功 |
| data | array | 打印机列表 |
| sn | string | 打印机所在的服务器或共享端SN |
| printerName | string | 打印机名称 |
| deviceType | string | 设备类型（printer/scanner/camera） |
| printerAlias | string | 打印机别名 |
| onlineStatus | string | 打印机在线状态 |

**返回示例**：

```json
{
  "success": true,
  "data": [
    {
      "sn": "SERVER123456",
      "printerName": "HP LaserJet Pro",
      "deviceType": "printer",
      "printerAlias": "办公室打印机",
      "onlineStatus": "ONLINE"
    }
  ]
}
```

---

### 4. directPrintDocumentMCP - 直接打印文档

**接口路径**：`POST /openapi/task/directPrintDocumentMCP`

**功能**：直接打印文档到指定打印机

**请求参数**：

| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| fileName | string | 是 | 文档名称 |
| url | string | 是 | 文档的访问URL |
| mediaFormat | string | 是 | 文档格式 |
| deviceName | string | 是 | 打印机名称（从queryPrinters获取） |
| controlSn | string | 是 | 服务器SN（从queryPrinters获取） |

**使用场景**：
- 用户明确说"直接打印"、"立即打印"、"打印出来"等
- 需要先调用 queryPrinters 获取打印机信息

**返回示例**：

```json
{
  "success": true,
  "data": {
    "jobId": "PRINT_20240324_001",
    "status": "QUEUED"
  }
}
```

---

## 辅助 API 接口（按需调用）

### 5. queryPrinterDetail - 查询打印机能力

**接口路径**：`POST /openapi/control/queryPrinterDetail`

**功能**：查询打印机支持的参数

**使用场景**：仅当用户明确说"查询打印机能力"、"打印机支持什么功能"时调用

---

### 6. updatePrinterSideMCP - 配置打印参数

**接口路径**：`POST /openapi/task/config/updatePrinterSideMCP`

**功能**：更新打印任务的单双面设置

**使用场景**：仅当用户明确说"设置双面打印"、"配置打印参数"时调用

---

## 使用流程

### 流程1：上传文件
适用场景：用户上传文件

1. 调用 `uploadFileMCP` 上传文件
2. 返回文件的公网访问URL

### 流程2：提交打印任务（队列打印）
适用场景：用户说"提交打印队列"、"创建漫游任务"等（非直接打印）

1. 如果是本地文件：调用 `uploadFileMCP` 上传文件获取URL
2. 调用 `createRoamingTask` 提交到打印队列
3. **注意**：无需查询打印机信息

### 流程3：直接打印
适用场景：用户明确说"直接打印"、"立即打印"、"打印出来"

1. 调用 `queryPrinters` 查询打印机列表
2. 如果是本地文件：调用 `uploadFileMCP` 上传文件获取URL
3. 调用 `directPrintDocumentMCP` 直接打印到指定打印机

---

## 决策指南

| 用户表达 | 调用接口 | 说明 |
|---------|---------|------|
| "上传这个文件" | uploadFileMCP | 仅上传文件 |
| "提交打印队列"、"创建漫游任务" | uploadFileMCP + createRoamingTask | 不查打印机 |
| "直接打印"、"立即打印"、"打印出来" | queryPrinters + uploadFileMCP + directPrintDocumentMCP | 需查打印机 |
| "查询打印机能力" | queryPrinterDetail | 仅用户明确需要时 |
| "设置双面打印" | updatePrinterSideMCP | 仅用户明确需要时 |

---

## 错误处理

### 错误响应格式

```json
{
  "success": false,
  "code": "ERROR_CODE",
  "message": "错误描述"
}
```

### 常见错误码

| 错误码 | 说明 |
|--------|------|
| 401 | 未授权，缺少或无效的访问令牌 |
| 403 | 禁止访问，无权限访问该资源 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 注意事项

- 所有操作需要有效的访问令牌
- 区分用户意图：是"提交队列"还是"直接打印"
- queryPrinterDetail 和 updatePrinterSideMCP 仅在用户明确需要时调用
- 打印文档格式需在支持的格式列表中
