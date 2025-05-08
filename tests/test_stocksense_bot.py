import pytest
import requests
import allure
import json
import re
import csv
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

# Load environment variables from .env file
load_dotenv(".env")

# API setup from environment variables
BOT_URL = os.environ.get("BOT_URL", "https://stocksense-backend.onrender.com/api/prompt/")
JWT_TOKEN = os.environ.get("JWT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

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

            with allure.step("Judge bot response using llama3-8b-8192"):
                evaluation = self.judge_response_with_groq(prompt, cleaned_response)
                allure.attach(evaluation, name="llama3-8b-8192 LLM Judgment", attachment_type=allure.attachment_type.TEXT)

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
    def judge_response_with_groq(prompt: str, cleaned_response: str) -> str:
        # Initialize Groq LLM via LangChain
        llm = ChatGroq(
            model="llama3-8b-8192",  # You can change to another available model
            groq_api_key=GROQ_API_KEY
        )
        
        system_prompt = """You are a friendly financial expert reviewing answers given by a financial chatbot named StockSense. Your job is to give helpful feedback that will guide the chatbot to improve over time.

Please evaluate each response using the three categories below:

1. ACCURACY (0–3 points):
   - Is the information generally correct?
   - Does it explain financial concepts reasonably well?

2. CLARITY (0–3 points):
   - Is the explanation clear and easy to follow?
   - Are financial terms explained simply if needed?

3. HELPFULNESS (0–4 points):
   - Does the response make an effort to answer the question?
   - Is it useful, relevant, or educational in a basic way?

📌 **Important Instruction**:  
Start your evaluation with this line, using the same format and asterisks:  
**TOTAL SCORE: your_score/10**

Then include:
- A short breakdown of how you gave points in each category
- 1–2 examples from the chatbot's response that show what worked well or what needs improvement
- A quick explanation of why you gave that score

Be encouraging and constructive. This feedback is helping a young AI get better at its job!
"""
        
        judge_prompt = f"""
User prompt: "{prompt}"
Bot response: "{cleaned_response}"

Give a score from 1 to 10 with a brief explanation.
"""

        # Create message objects for LangChain
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=judge_prompt)
        ]
        
        # Get response from Groq via LangChain
        response = llm.invoke(messages)
        return response.content

    @staticmethod
    def extract_score(text: str) -> int:
        match = re.search(r"\bTOTAL SCORE[:\s]*([1-9]|10)/10\b", text, re.IGNORECASE)
        return int(match.group(1)) if match else 0