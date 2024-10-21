import os

from mistralai import Mistral

api_key = os.getenv('API_KEY')
model = "mistral-large-latest"

client = Mistral(api_key=api_key)


def get_llm_mesage(message, context = ''):
    if context == '':
        chat_response = client.chat.complete(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": f"{message}",
                },
            ]
        )
        return chat_response.choices[0].message.content

    chat_response = client.chat.complete(
        model=model,
        messages=[
            {
                "role": "user",
                "content": f"Ответь на следующий вопрос:{message}\n Только если понадобится, можешь опираться на "
                           f"предыдущие сообщения, они идут после двоеточия:{context}",
            },
        ]
    )
    return chat_response.choices[0].message.content

