# AstrBot Minecraft MOTD

![Python Versions](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-blue)
![License](https://img.shields.io/github/license/ChuranNeko/astrbot_plugin_Mirecraft_motd)
![Version](https://img.shields.io/badge/version-1.1.0-green)
## 🌟 功能简介

本插件为 **AstrBot** 提供 `/motd` 命令，可在本地主动探测指定 **Minecraft Java** 或 **Bedrock** 服务器（无需外部 HTTP API），获取状态信息（MOTD、在线状态、玩家人数、服务器图标等），并在本地渲染状态图片发送到聊天中。

* **支持版本**：Java 版 & 基岩版
* **自动判断**：可同时请求 Java 和 Bedrock 接口，自动选择可用版本显示
* **图片美化**：状态图支持深色背景、圆角等美化参数

---

## 📦 依赖说明

运行此插件需要以下依赖（已包含在 `requirements.txt` 中）：

```txt
validators
mcstatus
Pillow
requests
```

**字体文件**：插件包含 `font/Minecraft_AE.ttf` 字体文件，确保跨平台兼容性和 Minecraft 主题一致性。

---

## 📋 使用方法

### 命令格式

```bash
/motd <server_address>[:<port>]
```

* **不带端口**：依次探测 Java(25565/TCP) → Bedrock(19132/UDP)
* **带端口**：先以 Java(TCP) 探测；若失败再以 Bedrock(UDP) 探测
* `server_address`：支持 IPv4、IPv6、域名
* `port`（可选）

### 地址格式支持

* **IPv4**：`192.168.1.1`、`mc.example.com`
* **IPv6**：`2001:db8::1`、`[::1]:25565`、`[2001:db8::1]:19132`
* **域名**：`mc.hypixel.net`、`play.example.com`

### 示例

```bash
/motd play.example.com
/motd mc.example.net:19132
```

> 插件在本地完成握手/状态查询，优先 Java，再回退 Bedrock（或按端口顺序）。当服务器不在线或地址无效时，会提示错误信息。

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

* **服务器图标**：优先显示服务器 favicon，无则显示默认 Minecraft logo
* 在线/离线状态
* 延迟、协议、客户端/服务器版本
* 当前在线人数、最大人数、玩家示例列表（若可用）
* MOTD 文本



---

## 📄 许可证

本项目采用 **MIT** 许可证 - 详情请参阅 [LICENSE](LICENSE)。

---

## 🙏 致谢

* [AstrBot](https://github.com/AstrBotDevs/AstrBot) — 高性能聊天机器人框架

---
