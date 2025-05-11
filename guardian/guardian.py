from transformers import BertTokenizer, BertForSequenceClassification
import torch


class FineTunedBERT:
    def __init__(self, model_path: str):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = BertTokenizer.from_pretrained(model_path)
        self.model = BertForSequenceClassification.from_pretrained(
            model_path, num_labels=2
        ).to(self.device)

    def predict(self, text: str) -> int:
        inputs = self.tokenizer(
            text, padding=True, truncation=True, max_length=128, return_tensors="pt"
        )
        input_ids = inputs["input_ids"].to(self.device)
        attention_mask = inputs["attention_mask"].to(self.device)

        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            predicted_class = torch.argmax(logits, dim=1).item()
        return predicted_class  # 1 == not fraud class, 0 == fraud class


class DummyBERT:
    def predict(self, text):
        return 1
