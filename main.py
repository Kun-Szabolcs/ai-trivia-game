import os
from dotenv import load_dotenv
import json
import requests

# Loading variables from .venv
load_dotenv()

api_key:str = os.getenv("API_KEY")
base_url:str = os.getenv("BASE_URL")
model:str = os.getenv("MODEL")
number_of_questions:int = int(os.getenv("NUMBER_OF_QUESTIONS", "5"))

#connecting to AI API and requesting question/answer pairs in JSON format
def get_trivia_questions(topic, difficulty):

    headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    }
    
    prompt = [
        {
            "role": "system", 
            "content": "You are a trivia generator. "
                "CRITICAL RULES:\n"
                "1. Respond ONLY with a raw JSON array of objects.\n"
                "2. Each object must have 'question' and 'answer' keys.\n"
                "3. Each 'question' MUST be designed so that it can be answered with a single word.\n"
                "4. Do not use markdown blocks (```json)."
                "5. If the topic is not a topic then default to the topic: birds"
                "6. If the difficulty is not a difficulty then default to the difficulty: Normal"
        },
        {
            "role": "user", 
            "content": f'The difficulty is set to: {difficulty}, Create {number_of_questions} trivia pairs with the topic: "{topic}".'
        }
    ]

    data = {
        "model": model,
        "messages": prompt,
        "stream": False,
        "temperature": 0.2
    }
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=data,
            stream=False
        )

        response.raise_for_status()
        
        content:str = response.json()['choices'][0]['message']['content']
   
        content = content.replace("```json", "").replace("```", "").strip()
        
        return json.loads(content)
        
    except (requests.RequestException, json.JSONDecodeError, KeyError) as e:
        print(f"Failed to fetch trivia: {e}")
        return []

if not base_url or not api_key:
    raise Exception("")

difficulty = input("Set the difficulty (max 10 char):\n")[:10].lower().strip()
user_topic = input("What should the topic of the trivia game be? (max 10 char):\n")[:10].lower().strip()
questions = get_trivia_questions(user_topic, difficulty)

score = 0

if questions:
    for item in questions:
        print(f"{item["question"]}")
        
        user_answer = input("Answer: ").lower().strip()
        
        if user_answer == item["answer"].lower().strip():
            score += 1
        else:
            print(f"WRONG! The correct answer is: {item["answer"]}")

print(f"Game Over! Your score: {score}")
        
