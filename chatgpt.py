import os
from dotenv import load_dotenv
load_dotenv()
OpenAI_Key = os.getenv('OpenAI_Key')

import openai
openai.api_key = OpenAI_Key
def send_to_chatGPT(messages, model="gpt-3.5-turbo"):

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    )

    message = response.choices[0].message.content
    messages.append(response.choices[0].message)
    return message