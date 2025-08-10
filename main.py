from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api.message_components import Image, Plain
import re
from astrbot.api import logger

@register("astrbot_minecraft_motd", "初然", "Minecraft 服务器 MOTD 状态图", "1.0.1")
class MinecraftMOTDPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.command("motd")
    async def motd_command(self, event: AstrMessageEvent, *args, **kwargs):
        msg = event.message_str.strip()
        parts = msg.split()

        if len(parts) == 1:
            usage = (
                "用法:\n"
                "/motd <server_ip>[:<port>]\n"
                "示例:\n"
                "/motd play.example.com:25565\n"
                "port 可省略，默认 25565（Java 版）"
            )
            yield event.plain_result(usage)
            return

        address = parts[1]
        match = re.match(r"^([\w\.-]+)(?::(\d+))?$", address)
        if not match:
            yield event.plain_result("参数格式错误，请使用 /motd <server_ip>[:<port>]")
            return

        ip = match.group(1)
        port = int(match.group(2)) if match.group(2) else 25565

        is_java = (port == 25565)
        base_url = "https://api.mcstatus.io/v2/widget/java/" if is_java else "https://api.mcstatus.io/v2/widget/bedrock/"

        # 组装图片 URL
        # dark=true, rounded=true, transparent=false, timeout=5 默认参数
        img_url = f"{base_url}{ip}:{port}?dark=true&rounded=true&transparent=false&timeout=5"

        logger.info(f"发送 Minecraft MOTD 图片: {img_url}")

        img_component = Image(img_url)
        yield event.result([img_component])

    async def initialize(self):
        logger.info("MinecraftMOTDPlugin 已初始化")

    async def terminate(self):
        logger.info("MinecraftMOTDPlugin 已停止")
