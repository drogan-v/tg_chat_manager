from together import Together

import dotenv
import os


class LLMClient:
    def __init__(self):
        dotenv.load_dotenv()
        self.client = Together(api_key=os.getenv('LLM_API_KEY'))

    def validate_message(self, message):
        print("Проверяем сообщение")
        response = self.client.chat.completions.create(
            model="lgai/exaone-3-5-32b-instruct",
            messages=[
                {
                    "role": "system",
                    "content": "Твоя задача модерация введенного сообщения и его проверка на спам, ненормативную лексику, вредоносность и политику."
                               "выводи ответ строго в этом формате:"
                               "если прошло модерацию:Safe"
                               "Если не прошло: Unsafe <Reason>, внутри скобок поясни причину."
                },
                {
                    "role": "user",
                    "content": f"{message}"
                }
            ],
        )
        print("Проверка прошла")
        return response.choices[0].message.content
