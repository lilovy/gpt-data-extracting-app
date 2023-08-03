from revChatGPT.V1 import Chatbot
from typing import Union
from ..tools.timer import timer


class MarkupGPT(object):

    __conv_id = None
    __default_prompt = ''

    def __init__(
        self, 
        access_token: str,
        proxy: str = None,
        chat_mode: bool = False,
        ) -> None:

        config = {
            "access_token": access_token,
        }
        if isinstance(proxy, str):
            config["proxy"] = proxy

        self.__session = Chatbot(
            config=config,
        )
        self.__chat_mode = chat_mode

    def set_default_prompt(self, prompt: str = "") -> None:
        self.__default_prompt = prompt + "\n"

    def enable_chat_mode(self) -> None:
        self.__chat_mode = True

    def disable_chat_mode(self) -> None:
        self.__chat_mode = False

    def new_chat(self) -> None:
        self.__session.reset_chat()

    def rollback_conversation(self, num: int = 1):
        self.__session.rollback_conversation(num)

    def __gen_title(
        self, 
        message_id: str, 
        convo_id: str | None = None,
        ) -> None:
        if not convo_id:
            convo_id = self.__conv_id
        self.__session.gen_title(
            convo_id=convo_id, 
            message_id=message_id,
            )

    def __del_conversation(self) -> None:
        self.__session.delete_conversation(convo_id=self.__conv_id)
        self.__session.reset_chat()
        self.__conv_id = None

    @timer
    def __request(
        self,
        question: str,
        conversation_id: str | None = None,
        use_prompt: bool = False,
        logs: bool = False,
        ) -> dict:

        """
        :Return dict
            {
                'message': message,
                'message_id': message_id,
                'conversation_id': conversation_id,
                'parent_id': parent_id,
                'model': model,
            }
        """

        if not conversation_id:
            conversation_id = self.__conv_id

        resp = {}
        prompt = question
        if logs:
            print(f"question: {prompt}")

        # if use_prompt:
        prompt = self.__default_prompt + prompt

        raw_response = self.__session.ask(
            prompt=prompt,
            conversation_id=conversation_id,
            )

        for data in raw_response:
            resp = data

        self.__conv_id = resp.get('conversation_id')

        if self.__chat_mode:
            self.__gen_title(resp.get('message_id'))
        else:
            self.__del_conversation()

        return resp
    
    def conversation_id(self):
        return self.__conv_id

    def ask(
        self,
        question: str,
        conversation_id: str | None = None,
        logs: bool = False,
        ) -> str:
        return self.__request(
            question, 
            conversation_id,
            logs,
            ).get('message')
