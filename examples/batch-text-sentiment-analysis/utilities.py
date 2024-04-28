from typing import Any, Dict, List


def print_emotions(emotions: List[Dict[str, Any]]) -> None:
    emotion_map = {e["name"]: e["score"] for e in emotions}
    
    # Iterate over the entire emotion_map and print each emotion and its score
    for emotion, score in emotion_map.items():
        print(f"- {emotion}: {score:4f}")


def print_sentiment(sentiment: List[Dict[str, Any]]) -> None:
    sentiment_map = {e["name"]: e["score"] for e in sentiment}
    for rating in range(1, 10):
        print(f"- Sentiment {rating}: {sentiment_map[str(rating)]:4f}")
def print_toxicity(toxicity: List[Dict[str, Any]]) -> None:
    toxicity_map = {e["name"]: e["score"] for e in toxicity}
    for label in ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]:
        print(f"- {label}: {toxicity_map[label]:4f}")
