import pytest
import requests
import allure
import json
import re
import csv
import os

# API setup
BOT_URL = "https://stocksense-backend.onrender.com/api/prompt/"
OLLAMA_URL = "http://localhost:11434/api/chat"
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ0NzMyMjk5LCJpYXQiOjE3NDQ2NDU4OTksImp0aSI6Ijk0YzZkZDY0YWMwMzQ3ZjU4NTUwMzliNDJjM2M4OTE4IiwidXNlcl9pZCI6M30.fyqHscBxC87mzfNdfSYWZ0QP15ROYRNO-_bpmozyO_Q"  # 🔐 Replace with actual JWT

def load_prompts_from_csv(csv_path):
    prompts = []
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            prompts.append(row['prompt'])
    return prompts

# Get the test data directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'test_prompts')

# Load prompts from CSV files
TUTOR_PROMPTS = load_prompts_from_csv(os.path.join(DATA_DIR, 'stock_tutor_prompts.csv'))
LIVE_DATA_PROMPTS = load_prompts_from_csv(os.path.join(DATA_DIR, 'live_data_prompts.csv'))
BASIC_PROMPTS = load_prompts_from_csv(os.path.join(DATA_DIR, 'basic_conversation_prompts.csv'))
# Add the comparison prompts
COMPARISON_PROMPTS = load_prompts_from_csv(os.path.join(DATA_DIR, 'comparison_prompts.csv'))

@allure.epic("StockSense Bot Testing")
class TestStockSenseBot:

    @allure.feature("Stock Tutor Prompts")
    @pytest.mark.parametrize("prompt", TUTOR_PROMPTS)
    def test_stock_tutor_prompts(self, prompt):
        self._run_test(prompt, "Stock Tutor")

    @allure.feature("Live Data Prompts")
    @pytest.mark.parametrize("prompt", LIVE_DATA_PROMPTS)
    def test_live_data_prompts(self, prompt):
        self._run_test(prompt, "Live Data")

    @allure.feature("Basic Conversation Prompts")
    @pytest.mark.parametrize("prompt", BASIC_PROMPTS)
    def test_basic_conversation_prompts(self, prompt):
        self._run_test(prompt, "Basic Conversation")
        
    # Add the new test for comparison prompts
    @allure.feature("Comparison Prompts")
    @pytest.mark.bot  # Custom marker for bot tests
    @pytest.mark.parametrize("prompt", COMPARISON_PROMPTS)
    def test_comparison_prompts(self, prompt):
        with allure.step(f"Testing comparison prompt: '{prompt}'"):
            self._run_test(prompt, "Comparison", min_score=7)

    def _run_test(self, prompt, category, min_score=6):
        with allure.step(f"Test {category} Prompt: '{prompt}'"):
            allure.attach(prompt, name="Prompt", attachment_type=allure.attachment_type.TEXT)
            
            with allure.step("Send prompt to StockSense bot"):
                raw_response = self.stream_response_from_bot(prompt)
                allure.attach(raw_response, name="Bot Response (Raw)", attachment_type=allure.attachment_type.TEXT)

            with allure.step("Clean Markdown from bot response"):
                cleaned_response = self.clean_markdown(raw_response)
                allure.attach(cleaned_response, name="Bot Response (Cleaned)", attachment_type=allure.attachment_type.TEXT)

            with allure.step("Judge bot response using Mistral (Ollama)"):
                evaluation = self.judge_response_with_ollama(prompt, cleaned_response)
                allure.attach(evaluation, name="Mistral Judgment", attachment_type=allure.attachment_type.TEXT)

                score = self.extract_score(evaluation)
                assert score >= min_score, f"{category} response quality below threshold: {score}/{min_score}"

    @staticmethod
    def stream_response_from_bot(prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {JWT_TOKEN}",
            "Content-Type": "application/json"
        }

        response = requests.post(BOT_URL, headers=headers, json={"prompt": prompt}, stream=True)
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
    def clean_markdown(text: str) -> str:
        # Remove markdown: bold, italics, inline code, headers, etc.
        text = re.sub(r"[*_`#~>-]", "", text)
        text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)  # [text](url) → text
        return text.strip()

    @staticmethod
    def judge_response_with_ollama(prompt: str, cleaned_response: str) -> str:
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

        response = requests.post(OLLAMA_URL, json=payload)
        return response.json()["message"]["content"]

    @staticmethod
    def extract_score(text: str) -> int:
        match = re.search(r"\b([1-9]|10)\b", text)
        return int(match.group(1)) if match else 0