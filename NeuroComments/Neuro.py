from g4f.client import Client

gpt_client = Client()


async def get_neuro_comment(message_text):
    response = gpt_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user",
                   "content": f"Напиши короткий комментарий по этому тексту от первого лица, в разговорном стиле, как будто говоришь с другом. текст:{message_text}"}]
    )
    return response.choices[0].message.content
