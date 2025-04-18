# tests/utils/bot_helpers.py
import csv
import requests
import json
import re
import os

class BotTestHelper:
    """Helper class for bot-related tests"""
    
    BOT_URL = "https://stocksense-backend.onrender.com/api/prompt/"
    OLLAMA_URL = "http://localhost:11434/api/chat"
    JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ0NzMyMjk5LCJpYXQiOjE3NDQ2NDU4OTksImp0aSI6Ijk0YzZkZDY0YWMwMzQ3ZjU4NTUwMzliNDJjM2M4OTE4IiwidXNlcl9pZCI6M30.fyqHscBxC87mzfNdfSYWZ0QP15ROYRNO-_bpmozyO_Q"
    
    @staticmethod
    def load_prompts_from_csv(csv_path):
        prompts = []
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                prompts.append(row['prompt'])
        return prompts
    
    def run_prompt_test(self, prompt):
        """Run a complete prompt test and return results"""
        raw_response = self.stream_response_from_bot(prompt)
        cleaned_response = self.clean_markdown(raw_response)
        evaluation = self.judge_response_with_ollama(prompt, cleaned_response)
        score = self.extract_score(evaluation)
        
        return {
            "prompt": prompt,
            "raw_response": raw_response,
            "cleaned_response": cleaned_response,
            "evaluation": evaluation,
            "score": score
        }
    
    def stream_response_from_bot(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.JWT_TOKEN}",
            "Content-Type": "application/json"
        }

        response = requests.post(self.BOT_URL, headers=headers, json={"prompt": prompt}, stream=True)
        accumulated = ""

        for line in response.iter_lines():
            if line:
                try:
                    event = json.loads(line.decode("utf-8"))
                    if event.get("event") == "chat_streaming":
                        accumulated += event["data"].get("chunk", "")
                except Exception as e:
                    print(f"Streaming parse error: {e}")
        return accumulated.strip()
    
    @staticmethod
    def clean_markdown(text):
        # Remove markdown formatting
        text = re.sub(r"[*_`#~>-]", "", text)
        text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)
        return text.strip()
    
    def judge_response_with_ollama(self, prompt, cleaned_response):
        system_prompt = "You're a finance tutor. Score this chatbot reply on accuracy, clarity, and helpfulness."
        
        judge_prompt = f"""
User prompt: "{prompt}"
Bot response: "{cleaned_response}"

Give a score from 1 to 10 with a brief explanation.
"""
        
        payload = {
            "model": "mistral",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": judge_prompt}
            ],
            "stream": False,
        }
        
        response = requests.post(self.OLLAMA_URL, json=payload)
        return response.json()["message"]["content"]
    
    @staticmethod
    def extract_score(text):
        match = re.search(r"\b([1-9]|10)\b", text)
        return int(match.group(1)) if match else 0