from openai import OpenAI
from dotenv import load_dotenv
import os


load_dotenv()

base_url = os.getenv("AI_URL")
api_key = os.getenv("AI_API_KEY")

# установка как будет вести себя AI 
system_character = "Отвечайте на вопросы прагматично и лаконично, предоставляя только необходимую информацию"
api = OpenAI(api_key=api_key, base_url=base_url)

def generate_ai_response(user_prompt):
    print('generate_ai_response')
    completion = api.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.2",
        messages=[
            {"role": "system", "content": system_character},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=256,
    )

    response = completion.choices[0].message.content

    print("User:", user_prompt)
    print("AI:", response)

    return response


# запуск скрипта (пример)
# user_prompt = "Расскажи мне о России в пару словах"

# if __name__ == "__main__":
#     generate_ai_response(user_prompt)