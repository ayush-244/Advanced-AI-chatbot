from transformers import AutoModelForCausalLM, AutoTokenizer
import torch


class ChatBot:

    def __init__(self):
        print("Loading AI model...")

        self.tokenizer = AutoTokenizer.from_pretrained(
            "microsoft/DialoGPT-small"
        )
        self.tokenizer.pad_token = self.tokenizer.eos_token

        self.model = AutoModelForCausalLM.from_pretrained(
            "microsoft/DialoGPT-small"
        )

        print("Model loaded successfully!")


    def get_reply(self, text):

        inputs = self.tokenizer(
            text + self.tokenizer.eos_token,
            return_tensors="pt",
            padding=True,
            truncation=True
        )

        output = self.model.generate(
            inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_length=150,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            temperature=0.7,
            pad_token_id=self.tokenizer.eos_token_id,
            no_repeat_ngram_size=2
        )

        reply = self.tokenizer.decode(
            output[0],
            skip_special_tokens=True
        )

        if reply.lower().startswith(text.lower()):
            reply = reply[len(text):].strip()

        return reply
