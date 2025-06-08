# Movan Server

一个使用 Python 开发的轻量级帧同步游戏服务器（LockStep），专为多人实时在线游戏设计。

## 项目概述

Movan Server 是一个高效、轻量级的帧同步服务器框架，基于 Python 异步编程实现，主要用于需要精确状态同步的多人在线游戏，如实时策略游戏、格斗游戏和多人动作游戏等。该框架通过帧同步技术确保所有玩家在游戏中拥有一致的游戏状态和体验。

## 核心特性

- **高效的帧同步系统**：集中处理并广播所有玩家的输入操作，确保游戏状态一致性
- **多房间支持**：可同时运行多个独立的游戏房间，支持大量并发用户
- **安全通信**：内置加密通信和令牌认证，保障游戏数据安全
- **账户系统**：提供用户注册、登录和权限管理功能
- **自动重连**：网络中断时提供重连和帧数据恢复机制
- **自定义 RPC 框架**：轻量级远程过程调用实现，支持同步和异步通信

## 系统架构

Movan Server 由以下主要组件构成：

1. **同步服务器 (Sync Server)**
   - 处理实时帧同步和游戏状态维护
   - 管理玩家连接和房间分配
   - 负责游戏操作的收集、排序和广播

2. **账户服务器 (Account Server)**
   - 处理用户认证和会话管理
   - 维护用户数据和权限控制

3. **轻量级 RPC 框架 (Movan RPC)**
   - 提供服务间的通信机制
   - 支持同步和异步方法调用
   - 内置心跳检测和自动重连功能

## 帧同步模块消息包结构

帧同步是 Movan Server 的核心功能，以下是主要消息包结构：

### 1. 客户端输入操作（sync_action）

客户端向服务器发送的操作消息：

```json
{
  "uid": "用户ID",
  "token": "认证令牌",
  "extra_data": {
    "proto": "sync_action",
    "timestamp": 1234567890.123,
    "action_data": {
      "action_type": "移动/攻击/技能等",
      "parameters": {
        // 具体操作参数
      }
    }
  }
}
```

### 2. 服务器帧广播（sync_frame）

服务器向客户端广播的帧数据：

```json
{
  "proto": "sync_frame",
  "data": {
    "frame_count": 42,
    "actions": [
      {
        "uid": "用户1ID",
        "extra_data": {
          "timestamp": 1234567890.123,
          "action_data": {
            // 用户1的操作数据
          }
        }
      },
      {
        "uid": "用户2ID",
        "extra_data": {
          "timestamp": 1234567890.456,
          "action_data": {
            // 用户2的操作数据
          }
        }
      }
      // 更多用户操作...
    ]
  }
}
```

### 3. 帧数据重传请求（sync_request_reload_frames）

客户端请求重新获取帧数据：

```json
{
  "uid": "用户ID",
  "token": "认证令牌",
  "extra_data": {
    "proto": "sync_request_reload_frames",
    "data": {
      "start_frame": 30
    }
  }
}
```

### 4. 帧数据重传响应（reload_frames）

服务器响应重传请求：

```json
{
  "proto": "reload_frames",
  "data": [
    {
      "frame_count": 30,
      "actions": [/* 第30帧的所有操作 */]
    },
    {
      "frame_count": 31,
      "actions": [/* 第31帧的所有操作 */]
    }
    // 更多帧...
  ]
}
```

### 5. 房间管理消息

- **进入房间**：`room_enter`
- **离开房间**：`room_leave`
- **准备开始**：`room_prepare`

## 安装与使用

### 环境要求

- Python 3.11+
- 依赖详见 requirements.txt

### 快速开始

1. 克隆仓库

```bash
git clone https://github.com/yourusername/movan-server.git
cd movan-server
```

2. 安装依赖

```bash
pip install -r requirements.txt
```
或点击`setup_dependencies.bat`,linux下使用`setup_dependencies.sh`
3. 启动服务器

```bash
server.bat
```



### 配置文件

主要配置文件位于 `account/config.toml` 和 `sync/config.toml`，可根据需要调整参数。

## 帧同步原理简介

Movan Server 采用帧同步策略实现多人游戏的一致性：

1. **收集输入**：服务器收集所有玩家在一个固定时间段内的操作输入
2. **排序处理**：根据时间戳对操作进行排序
3. **打包广播**：将排序后的操作作为一帧数据广播给所有玩家
4. **确定性执行**：客户端按照相同的顺序执行相同的操作，实现状态一致

这种方式确保了在网络延迟条件下，所有玩家看到的游戏状态仍然保持一致。

## 扩展开发

### 添加新的游戏逻辑

可以通过扩展 Room 和 SyncCore 类来实现特定游戏的逻辑处理。

### 自定义消息处理

在 `msg_handle` 方法中添加新的消息类型处理逻辑。

## 贡献指南

欢迎提交 Issues 和 Pull Requests 来帮助改进项目！

## 许可证

[MIT License](LICENSE)