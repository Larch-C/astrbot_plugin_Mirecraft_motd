from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
import astrbot.api.message_components as Comp
from astrbot.api import logger

import asyncio
import re
import base64
from io import BytesIO
from typing import Optional, List, Tuple
import os
import tempfile

import validators
from mcstatus import JavaServer, BedrockServer
from PIL import Image, ImageDraw, ImageFont


@register("astrbot_minecraft_motd", "ChuranNeko", "Minecraft 服务器 MOTD 状态图", "1.1.0")
class MinecraftMOTDPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.command("motd")
    async def handle_motd(self, event: AstrMessageEvent):
        '''获取 Minecraft 服务器 MOTD 状态信息'''
        
        # 从消息内容中解析服务器地址
        message_str = event.message_str.strip()
        logger.info(f"原始消息: '{message_str}'")
        
        if message_str == "motd":
            address = None
        else:
            # 提取 motd 后面的内容作为地址
            address = message_str.replace("motd", "").strip()
            if not address:
                address = None
        
        logger.info(f"解析后的地址: '{address}'")

        if not address:
            usage = (
                "用法:\n"
                "/motd <server_ip>[:<port>]\n"
                "示例:\n"
                "/motd play.example.com\n"
                "/motd play.example.com:19132\n"
                "不带端口时将依次探测 Java(25565/TCP) 与 基岩版(19132/UDP)\n"
                "若指定端口：先以 Java(TCP) 探测，失败后再以 基岩版(UDP) 探测"
            )
            yield event.plain_result(usage)
            return

        logger.info(f"尝试匹配地址: '{address}'")
        # 支持 IPv4、IPv6、域名的正则表达式
        ipv6_pattern = r"^\[?([0-9a-fA-F:]+)\]?(?::(\d+))?$"
        ipv4_domain_pattern = r"^([a-zA-Z0-9\.\-_]+)(?::(\d+))?$"
        
        # 先尝试 IPv6 格式（方括号包围）
        match = re.match(ipv6_pattern, address)
        if not match:
            # 再尝试 IPv4 或域名格式
            match = re.match(ipv4_domain_pattern, address)
        logger.info(f"正则匹配结果: {match}")
        if not match:
            yield event.plain_result("参数格式错误，请使用 /motd <server_ip>[:<port>]")
            return

        ip = match.group(1)
        port = int(match.group(2)) if match.group(2) else None

        # 对输入的ip做预检查
        if (not validators.ip_address.ipv4(ip, cidr=False) and
                not validators.ip_address.ipv6(ip, cidr=False) and
                not validators.domain(ip, consider_tld=False)):
            logger.info(f"预检查{ip}无效")
            yield event.plain_result("服务器地址无效")
            return

        # 探测逻辑
        status_info = None
        if port is None:
            # 未指定端口：先探测 Java 默认 25565，再探测 Bedrock 默认 19132
            status_info = await self._probe_java(ip, 25565)
            if status_info is None:
                status_info = await self._probe_bedrock(ip, 19132)
        else:
            # 指定端口：先以 Java(TCP) 探测，失败再以 Bedrock(UDP) 探测
            status_info = await self._probe_java(ip, port)
            if status_info is None:
                status_info = await self._probe_bedrock(ip, port)

        if status_info is None:
            yield event.plain_result("当前服务器不在线，或者当前服务器信息输入错误，请检查服务器与端口后重试")
            return

        # 渲染图片，保存临时文件并返回本地路径（兼容 AstrBot 期望本地文件路径的行为）
        img_bytes, status_text = self._render_status_card(status_info)
        file_path = self._save_temp_image(img_bytes)

        logger.info(f"发送 Minecraft MOTD 本地渲染图片: {file_path}")

        # 异步清理临时文件，延后删除以保证发送完成
        try:
            asyncio.create_task(self._cleanup_file(file_path))
        except Exception:
            pass

        yield event.chain_result([Comp.Image(file_path)])
        yield event.plain_result(status_text)
        return

    async def initialize(self):
        logger.info("MinecraftMOTDPlugin 已初始化")

    async def terminate(self):
        logger.info("MinecraftMOTDPlugin 已停止")

    async def _probe_java(self, host: str, port: int, timeout_sec: float = 5.0) -> Optional[dict]:
        try:
            server = JavaServer.lookup(f"{host}:{port}")
            status = await asyncio.wait_for(server.async_status(), timeout=timeout_sec)
            # 解析 Java 返回
            version_name = getattr(status.version, "name", "")
            protocol = getattr(status.version, "protocol", None)
            players_online = getattr(status.players, "online", 0)
            players_max = getattr(status.players, "max", 0)
            sample_names: List[str] = []
            sample = getattr(status.players, "sample", None)
            if sample:
                try:
                    sample_names = [getattr(p, "name", "") for p in sample if getattr(p, "name", None)]
                except Exception:
                    sample_names = []

            # MOTD 兼容处理
            motd_text = None
            desc = getattr(status, "description", None)
            if isinstance(desc, str):
                motd_text = desc
            else:
                # mcstatus 可能返回 Description 对象或 dict
                try:
                    motd_text = getattr(desc, "clean", None) or str(desc)
                except Exception:
                    motd_text = str(desc) if desc is not None else ""

            favicon_data_uri = getattr(status, "favicon", None)

            return {
                "edition": "Java",
                "host": host,
                "port": port,
                "online": True,
                "latency_ms": round(getattr(status, "latency", 0)),
                "protocol": protocol,
                "version_name": version_name,
                "players_online": players_online,
                "players_max": players_max,
                "player_names": sample_names,
                "motd": motd_text or "",
                "favicon_data_uri": favicon_data_uri,
            }
        except Exception as e:
            logger.info(f"Java 探测失败 {host}:{port} - {e}")
            return None

    async def _probe_bedrock(self, host: str, port: int, timeout_sec: float = 5.0) -> Optional[dict]:
        try:
            server = BedrockServer.lookup(f"{host}:{port}")
            status = await asyncio.wait_for(server.async_status(), timeout=timeout_sec)

            # Bedrock 字段兼容
            version_name = getattr(status, "version", None) or getattr(status, "version_brand", "")
            players_online = getattr(status, "players_online", 0)
            players_max = getattr(status, "players_max", 0)
            motd_text = getattr(status, "motd", "")

            return {
                "edition": "BE基岩版",
                "host": host,
                "port": port,
                "online": True,
                "latency_ms": round(getattr(status, "latency", 0)),
                "protocol": getattr(status, "protocol", None),
                "version_name": version_name or "",
                "players_online": players_online,
                "players_max": players_max,
                "player_names": [],
                "motd": motd_text or "",
                "favicon_data_uri": None,
            }
        except Exception as e:
            logger.info(f"Bedrock 探测失败 {host}:{port} - {e}")
            return None

    def _render_status_card(self, info: dict) -> Tuple[bytes, str]:
        # 准备画布
        width, height = 900, 300
        bg_color = (28, 30, 34)
        fg_primary = (235, 235, 235)
        fg_secondary = (170, 170, 170)
        accent = (88, 166, 255)

        image = Image.new("RGBA", (width, height), bg_color)
        draw = ImageDraw.Draw(image)

        # 字体
        def load_font(size: int):
            # 优先使用插件自带的 Minecraft 字体
            plugin_dir = os.path.dirname(os.path.abspath(__file__))
            minecraft_font = os.path.join(plugin_dir, "font", "Minecraft_AE.ttf")
            
            try:
                if os.path.exists(minecraft_font):
                    return ImageFont.truetype(minecraft_font, size)
            except Exception as e:
                logger.info(f"加载 Minecraft 字体失败: {e}")
            
            # 备选方案：尝试加载系统中文字体
            font_paths = [
                "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
                "C:/Windows/Fonts/simsun.ttc",  # 宋体
                "C:/Windows/Fonts/arial.ttf",  # Arial
                "/System/Library/Fonts/PingFang.ttc",  # macOS 苹方
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
            ]
            
            for font_path in font_paths:
                try:
                    if os.path.exists(font_path):
                        return ImageFont.truetype(font_path, size)
                except Exception:
                    continue
            
            # 最后的备选方案：使用默认字体
            try:
                return ImageFont.load_default()
            except Exception:
                return ImageFont.load_default()

        font_title = load_font(28)
        font_body = load_font(20)
        font_small = load_font(16)

        padding = 20
        x = padding
        y = padding

        # 服务器图标处理
        icon_loaded = False
        if info.get("favicon_data_uri"):
            try:
                prefix = "data:image/png;base64,"
                data_uri: str = info["favicon_data_uri"]
                if data_uri.startswith("data:"):
                    b64 = data_uri.split(",", 1)[1]
                else:
                    b64 = data_uri
                icon = Image.open(BytesIO(base64.b64decode(b64))).convert("RGBA")
                icon = icon.resize((96, 96))
                image.paste(icon, (x, y), icon)
                x_text = x + 96 + 16
                icon_loaded = True
            except Exception as e:
                logger.info(f"加载服务器 favicon 失败: {e}")
                icon_loaded = False
        
        # 如果没有 favicon，尝试加载默认 Minecraft logo
        if not icon_loaded:
            try:
                # 尝试从网络加载默认 logo
                import requests
                from io import BytesIO
                
                default_logo_url = "https://patchwiki.biligame.com/images/mc/5/53/smk9nesqj6bkd5qyd718xxhocic6et0.png"
                response = requests.get(default_logo_url, timeout=10)
                if response.status_code == 200:
                    default_icon = Image.open(BytesIO(response.content)).convert("RGBA")
                    default_icon = default_icon.resize((96, 96))
                    image.paste(default_icon, (x, y), default_icon)
                    x_text = x + 96 + 16
                    icon_loaded = True
                    logger.info("使用默认 Minecraft logo")
            except Exception as e:
                logger.info(f"加载默认 logo 失败: {e}")
        
        # 如果都没有加载成功，不显示图标
        if not icon_loaded:
            x_text = x

        # 标题行：host:port 与 Edition 徽标
        title = f"{info['host']}:{info['port']}"
        draw.text((x_text, y), title, font=font_title, fill=fg_primary)

        edition_badge = f"{info['edition']}"
        badge_w, badge_h = draw.textbbox((0, 0), edition_badge, font=font_small)[2:]
        badge_x = x_text
        badge_y = y + 34
        # 徽标背景
        draw.rounded_rectangle([badge_x, badge_y, badge_x + badge_w + 12, badge_y + badge_h + 8], radius=6, fill=accent)
        draw.text((badge_x + 6, badge_y + 4), edition_badge, font=font_small, fill=(255, 255, 255))

        # 第二行：延迟 / 协议 / 版本
        y_info = badge_y + badge_h + 20
        line2 = f"延迟: {info['latency_ms']} ms    协议: {info.get('protocol', '-') or '-'}    版本: {info.get('version_name', '-') or '-'}"
        draw.text((x_text, y_info), line2, font=font_body, fill=fg_secondary)

        # 第三行：在线人数
        y_players = y_info + 28
        players_line = f"在线: {info['players_online']} / {info['players_max']}"
        draw.text((x_text, y_players), players_line, font=font_body, fill=fg_secondary)

        # 玩家示例列表（Java 有 sample）
        if info.get("player_names"):
            sample_text = ", ".join(info["player_names"][:10])
            draw.text((x_text, y_players + 26), f"在线玩家: {sample_text}", font=font_small, fill=fg_secondary)

        # MOTD 描述（多行，先清洗颜色码与换行）
        motd = self._clean_motd_text(info.get("motd", "") or "")
        y_motd = y_players + 60
        max_width = width - x_text - padding
        for line in self._wrap_text(draw, motd, font_body, max_width):
            draw.text((x_text, y_motd), line, font=font_body, fill=fg_primary)
            y_motd += 26

        # 导出字节
        buf = BytesIO()
        image.save(buf, format="PNG", optimize=True)
        img_bytes = buf.getvalue()

        # 文本摘要
        status_text = (
            f"{info['edition']} | {info['host']}:{info['port']}\n"
            f"在线: {info['players_online']}/{info['players_max']}  延迟: {info['latency_ms']}ms\n"
            f"版本: {info.get('version_name', '-') or '-'}  协议: {info.get('protocol', '-') or '-'}\n"
            f"MOTD: {motd}"
        )

        return img_bytes, status_text

    def _wrap_text(self, draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> List[str]:
        if not text:
            return []
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        result_lines: List[str] = []
        for paragraph in text.split("\n"):
            if paragraph == "":
                # 保留空行
                result_lines.append("")
                continue
            current_line = ""
            for ch in paragraph:
                test_line = current_line + ch
                # 仅测量单行文本宽度，避免包含换行符
                if draw.textlength(test_line, font=font) <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        result_lines.append(current_line)
                    current_line = ch
            if current_line:
                result_lines.append(current_line)
        return result_lines

    def _clean_motd_text(self, text: str) -> str:
        if not text:
            return ""
        # 统一换行
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # 去除 Minecraft 颜色码（例如 §a、§l、§x§R§R§G§G§B§B 等，按配对清理）
        try:
            return re.sub(r"§.", "", text)
        except Exception:
            return text

    def _save_temp_image(self, img_bytes: bytes) -> str:
        tmp = tempfile.NamedTemporaryFile(prefix="motd_", suffix=".png", delete=False)
        try:
            tmp.write(img_bytes)
            tmp.flush()
            return tmp.name
        finally:
            tmp.close()

    async def _cleanup_file(self, path: str, delay_sec: float = 180.0):
        try:
            await asyncio.sleep(delay_sec)
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            logger.info(f"临时文件清理失败 {path}: {e}")
