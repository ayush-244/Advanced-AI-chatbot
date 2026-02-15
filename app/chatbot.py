import torch

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from app.language import LanguageProcessor
from app.retriever import WikiRetriever
from app.memory import ChatMemory


class ChatBot:

    def __init__(self):

        print("Loading AI model...")

        self.tokenizer = AutoTokenizer.from_pretrained(
            "google/flan-t5-large"
        )

        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            "google/flan-t5-large"
        )

        self.model.eval()

        self.lang = LanguageProcessor()
        self.retriever = WikiRetriever()
        self.memory = ChatMemory()

        print("Model loaded successfully.")


    def get_reply(self, text: str) -> str:

        user_lang = self.lang.detect_lang(text)

        english_text = self.lang.to_english(text, user_lang)

        history = self.memory.get_last_messages()

        last_topic = ""

        if history:
            last_user, _ = history[-1]
            last_topic = last_user


        # Improve retrieval
        search_query = english_text

        if english_text.lower().startswith(
            ("where", "when", "how", "why", "he", "she", "they")
        ):
            if last_topic:
                search_query = last_topic + " " + english_text


        context = self.retriever.search(search_query)

        if not context:

            reply = "Sorry, I could not find reliable information."

            final_reply = self.lang.from_english(reply, user_lang)

            self.memory.save(text, final_reply)

            return final_reply


        # Build history
        history_text = ""

        for user_msg, bot_msg in history:
            history_text += f"User: {user_msg}\n"
            history_text += f"Bot: {bot_msg}\n"


        is_who_question = english_text.lower().strip().startswith(
            ("who is", "who are")
        )


        if is_who_question:

            prompt = f"""
You are a helpful AI assistant.

Answer strictly using only the context.
If the answer is not in context, say "I don't know".

Previous conversation:
{history_text}

Context:
{context}

Question:
{english_text}

Answer:
"""

        else:

            prompt = f"""
You are a helpful AI assistant.

Answer strictly using only the context.
If the answer is not in context, say "I don't know".

Previous conversation:
{history_text}

Context:
{context}

Question:
{english_text}

Answer:
"""


        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=1024
        )


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


        answer = self.tokenizer.decode(
            output[0],
            skip_special_tokens=True
        )


        # Remove "Bot:" if present
        if answer.lower().startswith("bot:"):
            answer = answer[4:].strip()


        final_answer = self.lang.from_english(
            answer.strip(),
            user_lang
        )


        self.memory.save(text, final_answer)

        return final_answer
