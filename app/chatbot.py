import torch

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from app.language import LanguageProcessor
from app.retriever import WikiRetriever


# -----------------------------
# MAIN CHATBOT
# -----------------------------
class ChatBot:

    def __init__(self):

        print("Loading AI model (FLAN-T5-Large)...")

        # Load Instruction Model
        self.tokenizer = AutoTokenizer.from_pretrained(
            "google/flan-t5-large"
        )

        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            "google/flan-t5-large"
        )

        self.model.eval()

        # Initialize helpers
        self.lang = LanguageProcessor()
        self.retriever = WikiRetriever()

        print("Model loaded successfully!")


    def get_reply(self, text: str) -> str:

        # -----------------------------
        # Step 1: Detect Language
        # -----------------------------
        user_lang = self.lang.detect_lang(text)


        # -----------------------------
        # Step 2: Translate to English
        # -----------------------------
        english_text = self.lang.to_english(text, user_lang)


        # -----------------------------
        # Step 3: Retrieve Context
        # -----------------------------
        context = self.retriever.search(english_text)

        if not context:
            reply = "Sorry, I could not find reliable information."

            return self.lang.from_english(reply, user_lang)


        # -----------------------------
        # Step 4: Build Prompt
        # -----------------------------
        # Check if it's a "who is" question
        is_who_question = english_text.lower().strip().startswith(('who is', 'who are'))
        
        if is_who_question:
            prompt = f"""Using the context below, describe who this person is and what their current role or position is.

Context: {context}

Question: {english_text}

Answer:"""
        else:
            prompt = f"""Answer the question based on the context below.

Context: {context}

Question: {english_text}

Answer:"""


        # -----------------------------
        # Step 5: Tokenize
        # -----------------------------
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=1024
        )


        # -----------------------------
        # Step 6: Generate Answer
        # -----------------------------
        with torch.no_grad():

            output = self.model.generate(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                min_new_tokens=12,
                max_new_tokens=256,
                num_beams=4,
                early_stopping=True,
                no_repeat_ngram_size=3,
                length_penalty=1.5
            )


        # -----------------------------
        # Step 7: Decode
        # -----------------------------
        answer = self.tokenizer.decode(
            output[0],
            skip_special_tokens=True
        )


        # -----------------------------
        # Step 8: Translate Back
        # -----------------------------
        final_answer = self.lang.from_english(
            answer.strip(),
            user_lang
        )

        return final_answer
