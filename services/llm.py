from together import Together

import logging
import dotenv
import os

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self) -> None:
        try:
            dotenv.load_dotenv()
            self.client = Together(api_key=os.getenv('LLM_API_KEY'))
            logger.info("LLM initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LLm: {e}")
            raise

    def validate_message(self, message: str) -> (str, str):
        logger.info(f"НАЧАЛИ")
        response = self.client.chat.completions.create(
            model="lgai/exaone-3-5-32b-instruct",
            messages=[
                {
                    "role": "system",
                    "content": "Представь, что ты модератор канала."
                               "Твоя задача модерация введенного сообщения и его проверка на спам, ненормативную лексику,"
                               "оскорбления, религиозные риски, публичный вред, агрессию, вредоносность и политику."
                               "Сообщения, содержащие восхваление стран, одобряющие нацизм, неонацизм, агрессию на рассовой почве "
                               "НЕ ДОЛЖНЫ пройти модерацию."
                               "Например: слава + <страна/политический деятель> НЕ ДОЛЖНО ПРОХОДИТЬ МОДЕРАЦИЮ"
                               "Все, кроме вышеперечисленного, явялется безопасным и должно проходить модерацию."
                               "Не превышай свои полномочия. Модерацию не должен проходить ИСКЛЮЧИТЕЛЬНО вредоносный контент."
                               "Если по контексту сообщения не понятно, является ли содержимое вредоносным контентом, то "
                               "это сообщение БЕЗОПАСНО и ДОЛЖНО проходить модерацию."
                               "выводи ответ СТРОГО в этом формате:"
                               "если прошло модерацию: safe"
                               "Если не прошло: unsafe Reason, вместо Reason напиши что именно не прошло модерацию."
                },
                {
                    "role": "user",
                    "content": f"{message}"
                }
            ],
        )
        llm_response = response.choices[0].message.content
        logger.info(f"LLM response: {llm_response}")
        parsed_response = llm_response.split()
        status, reason = parsed_response[0], ' '.join(parsed_response[1:])
        logger.info(f"ЗАКОНЧИЛИ")
        return status, reason
