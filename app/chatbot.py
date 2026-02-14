from transformers import AutoModelForCausalLM, AutoTokenizer
import torch


class ChatBot:

    def __init__(self):
        print("Loading AI model...")

        self.tokenizer = AutoTokenizer.from_pretrained(
            "microsoft/DialoGPT-small"
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            "microsoft/DialoGPT-small"
        )

        print("Model loaded successfully!")


    def get_reply(self, text):

        inputs = self.tokenizer.encode(
            text + self.tokenizer.eos_token,
            return_tensors="pt"
        )

        output = self.model.generate(
            inputs,
            max_length=100,
            pad_token_id=self.tokenizer.eos_token_id
        )

        reply = self.tokenizer.decode(
            output[0],
            skip_special_tokens=True
        )

        return reply
