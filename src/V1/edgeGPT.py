from EdgeGPT import Chatbot, ConversationStyle
from ..tools.timer import async_timer


class BingGPT:
    def __init__(self, cookies: dict | list[dict], proxy: str = None):
        self.cookies = cookies
        self.proxy = proxy
        self.__bot = Chatbot(cookies=self.cookies, proxy=self.proxy)
    
    @async_timer
    async def ask(self, prompt: str, debag: bool = False):
        request = await self.__bot.ask(
            prompt=prompt,
            conversation_style=ConversationStyle.creative,
            wss_link="wss://sydney.bing.com/sydney/ChatHub",
        )
        await self.__bot.close()
        if debag:
            return request
        return request["item"]["messages"][1]['text']
