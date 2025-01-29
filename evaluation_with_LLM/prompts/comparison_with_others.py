def get_prompt(dial, user_impression):
    prompt = f"""
    You are the proficient dialogue system quality assessment. You are given a two dialogue system.
    Please evaluate the following two systems based on the personalization to the user image and image description, in terms of personalized greetings, personalization to age, personalized recommendation, emotion and formal/casual context.

    **User Image Description:**
        {user_impression}    
    **dialogue**
        {dial}
        
    Your answer must be in the following format:
    (Reason : [reason for selection], Winner :[System1, Tie, System2]
    """
    

    return prompt