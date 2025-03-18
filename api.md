
# DeepAnalyze API 文档

本文档描述了 DeepAnalyze 平台的 API 接口，包括 HTTP REST API 和 WebSocket 实时通信接口。

## 基础信息

- 基础URL: `http://127.0.0.1:8000`
- WebSocket URL: `ws://127.0.0.1:8000/ws`
- API 版本: v1
- 内容类型: `application/json`

## HTTP REST API

### 认证与配置

#### 获取系统状态

检查系统是否正常运行及当前配置状态。

```
GET /api/status
```

**响应**:

```json
{
  "status": "running",
  "model": {
    "type": "openai",
    "status": "connected"
  },
  "version": "1.0.0"
}
```

#### 更新配置

更新系统配置。

```
PUT /api/config
```

**请求体**:

```json
{
  "model": {
    "type": "openai",
    "api_key": "your-api-key",
    "endpoint": "https://api.openai.com/v1"
  },
 
}
```

**响应**:

```json
{
  "status": "success",
  "message": "配置已更新"
}
```

### 文件系统操作

#### 设置工作目录

```
POST /api/workspace
```

**请求体**:

```json
{
  "path": "D:/my_data_folder"
}
```

**响应**:

```json
{
  "status": "success",
  "workspace": "D:/my_data_folder",
  "files_count": 15
}
```

#### 获取文件目录结构

```
GET /api/files
```

**查询参数**:
- `path` (可选): 指定子目录路径

**响应**:

```json
{
  "path": "D:/my_data_folder",
  "items": [
    {
      "name": "data.csv",
      "type": "file",
      "size": 1024,
      "last_modified": "2023-05-20T14:30:00Z",
      "extension": "csv"
    },
    {
      "name": "images",
      "type": "directory",
      "items_count": 5
    }
  ]
}
```

#### 获取文件内容预览

```
GET /api/files/preview
```

**查询参数**:
- `path`: 文件路径
- `max_size` (可选): 最大预览大小，默认 10KB

**响应**:

```json
{
  "name": "data.csv",
  "type": "csv",
  "size": 1024,
  "preview": "id,name,value\n1,A,10\n2,B,20\n...",
  "truncated": false
}
```

### 对话管理





#### 创建新对话

```
POST /api/conversations
```

**请求体**:

```json
{
  "title": "新的数据分析项目"
}
```

**响应**:

```json
{
  "id": "conv_125",
  "title": "新的数据分析项目",
  "created_at": "2023-05-22T09:00:00Z"
}
```




## WebSocket API

WebSocket 连接用于实时通信，包括代码执行结果、文件系统变更和对话更新等。

### 连接建立

```
ws://127.0.0.1:8000/ws
```

### 消息格式

所有 WebSocket 消息都使用 JSON 格式，包含 `type` 字段指明消息类型。

```json
{
  "type": "message_type",
  "data": {
    // 消息内容
  }
}
```

### 客户端发送的消息类型

#### 订阅执行结果



#### 发送用户消息

```json
{
  "type": "user_message",
  "data": {
    "conversation_id": "conv_123",
    "content": "分析这个CSV文件中的销售数据，找出销售额最高的前5个产品"
  }
}
```



### 服务器发送的消息类型
#### 成功建立连接
```json
"type": "connection_established",
 "data": {
          "message": "WebSocket连接已建立"
           }

```
#### 工具调用开始通知
```json
{
  "type": "tool_invocation_start",
  "data": {
    "invocation_id": "调用ID",
    "function": "函数名称",
    "arguments": {},
    "timestamp": "2023-05-22T09:06:00Z"
  }
}
函数名称包括read_directory, read_files和exec_code
```
**例子**

```json
{
  "type": "tool_invocation_start",
  "data": {
    "invocation_id": "inv_123",
    "function": "read_directory",
    "arguments": {
      "path":"result/"
    },
    "timestamp": "2023-05-22T09:06:00Z"
  }
}
```

```json
{
  "type": "tool_invocation_start",
  
  "invocation_id": "inv_124",
  "function": "exec_code",
  "arguments": {
  "code":"print('hello world')"
  }
   
    "timestamp": "2023-05-22T09:06:00Z"
  }

```


#### 工具调用结果通知
```json
{
  "type": "tool_invocation_result",
  "invocation_id": "调用ID",
  "function": "函数名称",
  "result": "执行结果",
  "timestamp": "2023-05-22T09:06:00Z"
  
}
result是一个json字符串。
不同函数调用结果有不同字段，对于read_directory和read_files函数，result包括status字段，值可能为success和error，对于exec_code函数，result为执行结果,包括status字段，如果代码未能执行，还会有message字段，如果代码执行还会有stdout、stderr字段。

```

#### ai助手消息
```json
{
  "type": "assistant_message",
  "data": {
    "content": "根据分析，销售额最高的产品是...",
    "timestamp": "2023-05-22T09:06:00Z",
    "conversation_id": "conv_123",
  }
}
```

#### ai助手消息流结束通知
接受到此消息后，用户可以再次发送消息。
```json
{
  "type": "done",
  "data": {
    "conversation_id": "conv_123",
    "timestamp": "2023-05-22T09:06:00Z"
  }
}
```
#### 文件系统变更通知

```json
{
  "type": "filesystem_change",
  "data": {
    "event": "created",  // 可能的值: created, modified, deleted
    "path": "D:/my_data_folder/results.csv",
    "item_type": "file",
    "timestamp": "2023-05-22T09:05:25Z"
  }
}


## 错误代码

| 代码 | 描述 |
|------|------|
| `invalid_request` | 请求格式或参数无效 |
| `unauthorized` | 未授权访问 |
| `not_found` | 资源未找到 |
| `model_error` | 大模型服务错误 |
| `filesystem_error` | 文件系统操作错误 |

## 状态码

| 状态码 | 描述 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求错误 |
| 401 | 未授权 |
| 404 | 资源未找到 |
| 500 | 服务器错误 |


```

这份 API 文档提供了前后端开发所需的接口定义，包括 HTTP REST API 和 WebSocket 实时通信接口。文档详细说明了各个接口的请求和响应格式，以及可能的错误代码和状态码，确保前后端开发人员能够协调一致地进行开发工作。