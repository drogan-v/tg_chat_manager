from together import Together

import dotenv
import os


class LLMClient:
    def __init__(self) -> None:
        dotenv.load_dotenv()
        self.client = Together(api_key=os.getenv('LLM_API_KEY'))

    def validate_message(self, message: str) -> str:
        response = self.client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
            messages=[
                {
                    "role": "system",
                    "content": "Твоя задача модерация введенного сообщения и его проверка на спам, ненормативную лексику,"
                               "оскорбления, религиозные риски, публичный вред, агрессию, вредоносность и политику."
                               "выводи ответ строго в этом формате:"
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
        return llm_response
