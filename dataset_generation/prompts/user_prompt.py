def get_prompt(user, previous_system):
    
    prompt = f"""
    **Objective:**
    Adjust the tone, age, gender, emotion, and formality of the user's utterance to match the style of the user depicted in the provided image. 
    Rephrase the utterance as if the user originally spoke in that style, while preserving the original meaning. 
    Answer naturally, and Do not add any greetings, closing remarks, or expressions of thanks unless they were part of the original utterance.
    """
    
    if previous_system:
        prompt += f"""
        Ensure the revised utterance flows naturally as a response to the following system message:
        Previous system message: {previous_system}
        """
    
    prompt += f"""    
    Original user utterance: {user}
    Rephrased user utterance:
    """
    return prompt