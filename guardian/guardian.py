from transformers import BertTokenizer, BertForSequenceClassification
import torch
import os


class FineTunedBERT:
    def __init__(self, model_path: str):
        self.model = BertForSequenceClassification.from_pretrained(model_path, num_labels=2)
        self.tokenizer = BertTokenizer.from_pretrained(model_path)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self.model.to(self.device)

    def predict(self, text):
        # Tokenize the input text
        inputs = self.tokenizer(text, padding=True, truncation=True, max_length=128, return_tensors='pt')
        input_ids = inputs['input_ids'].to(self.device)
        attention_mask = inputs['attention_mask'].to(self.device)

        # Get the model's prediction
        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            predicted_class = torch.argmax(logits, dim=1).item()
        return predicted_class

    def is_approved(self, prompt: str):
        return self.predict(prompt)


# TODO: поместить путь к модели в конфиг
anti_fraud = FineTunedBERT(r"C:\Users\mrlel\PycharmProjects\Text-2-SQL\guardian\ruBERT_1.0acc")
