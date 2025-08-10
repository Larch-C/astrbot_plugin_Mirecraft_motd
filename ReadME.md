# AstrBot_Minecraft_MOTD

![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/ChuranNeko/astrbot_plugin_Mirecraft_motd/ci.yml?branch=main)
![Python Versions](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-blue)
![License](https://img.shields.io/github/license/ChuranNeko/astrbot_plugin_Mirecraft_motd)
![Version](https://img.shields.io/badge/version-1.0.1-green)

## 🌟 功能特点

在用户输入 `/motd <server_ip>:<port>` 命令后，插件将自动获取指定 Minecraft 服务器的 MOTD（Message of the Day）信息，并生成服务器状态图片，随后将图片发送到聊天中。
(包含状态以及服务器图标等)

## 📋 使用方法

在聊天中输入以下命令：

```bash
/motd <server_ip>:<port>
```

如果未输入"port"参数，则默认使用 25565 端口去探测

/motd 命令用于获取指定 Minecraft 服务器的 MOTD（Message of the Day）信息，并生成服务器状态图片，随后将图片发送到聊天中。

---

## 🔧 安装指南

### 推荐安装方式（本地开发）

```bash
git clone https://github.com/ChuranNeko/astrbot_plugin_Mirecraft_motd.git
cd astrbot_plugin_Mirecraft_motd
pip install -e .
```

--

## 📜 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本更新历史。

## 📄 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。

## 🙏 致谢

致谢项目 [Astrbot](https://github.com/AstrBotDevs/AstrBot)
