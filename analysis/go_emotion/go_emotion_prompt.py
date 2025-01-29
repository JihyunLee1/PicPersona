emotion_labels = [
    "admiration", "amusement", "anger", "annoyance", "approval", "caring", "confusion", 
    "curiosity", "desire", "disappointment", "disapproval", "disgust", "embarrassment", 
    "excitement", "fear", "gratitude", "grief", "joy", "love", "nervousness", "neutral", 
    "optimism", "pride", "realization", "relief", "remorse", "sadness", "surprise"
]


def get_prompt(user_utterance, system_utterance):
    prompt = f"""
    Please analyze the following conversation and determine the emotion expressed in the system's response. 
    The possible emotions are: {", ".join(emotion_labels)}.

    User: {user_utterance}

    System: {system_utterance}

    Based on the system's response, what emotion is being expressed by the system? The answer should be one word.
    """
    return prompt