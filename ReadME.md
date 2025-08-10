# AstrBot Minecraft MOTD

![Python Versions](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-blue)
![License](https://img.shields.io/github/license/ChuranNeko/astrbot_plugin_Mirecraft_motd)
![Version](https://img.shields.io/badge/version-1.0.1-green)

## 🌟 功能简介

本插件为 **AstrBot** 提供 `/motd` 命令，可获取指定 **Minecraft Java** 或 **Bedrock** 服务器的状态信息（MOTD、在线状态、玩家人数、服务器图标等），并生成状态图片发送到聊天中。

* **支持版本**：Java 版 & 基岩版
* **自动判断**：可同时请求 Java 和 Bedrock 接口，自动选择可用版本显示
* **图片美化**：状态图支持深色背景、圆角等美化参数

---

## 📦 依赖说明

运行此插件需要以下依赖（已包含在 `requirements.txt` 中）：

```txt

httpx
validators
```

---

## 📋 使用方法

### 命令格式

```bash
/motd <server_ip>[:<port>]
```

* `server_ip`：服务器 IP 或域名
* `port`（可选）：端口号，默认 `25565`（Java 版默认端口）

### 示例

```bash
/motd play.example.com
/motd mc.example.net:19132
```

> 插件会优先探测 Java 版接口，如离线则尝试 Bedrock 接口。
> 当服务器不在线或地址无效时，会提示错误信息。

---

## 🔧 安装指南

### 1. 插件市场安装（推荐）

在 **AstrBot 插件市场** 搜索 **AstrBot\_Minecraft\_MOTD** 并一键安装。

### 2. 手动安装

```bash
cd AstrBot/data/plugins
git clone https://github.com/ChuranNeko/astrbot_plugin_Mirecraft_motd.git
cd astrbot_plugin_Mirecraft_motd
pip install -r requirements.txt
```

---

## 📜 返回效果示例

插件返回的状态图包含：

* 服务器图标
* 在线/离线状态
* 当前在线人数
* MOTD 文本

![示例图片](https://api.mcstatus.io/v2/widget/java/play.example.com?dark=true\&rounded=true\&transparent=false)

---

## 📄 许可证

本项目采用 **MIT** 许可证 - 详情请参阅 [LICENSE](LICENSE)。

---

## 🙏 致谢

* [AstrBot](https://github.com/AstrBotDevs/AstrBot) — 高性能聊天机器人框架
* [MCStatus.io](https://mcstatus.io) — Minecraft 状态 API

---
