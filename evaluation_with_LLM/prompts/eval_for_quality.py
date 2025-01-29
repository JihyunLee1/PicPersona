def get_prompt(dial1, dial2, user_impression):
    prompt = f"""
    You are the proficient dialogue quality assessment. You are given a two dialogue a user and a system.
    First one is the original dialogue and the second one is the paraphrased dialogue, to match the style described in the user image description.
    
    Please check the dialogue in five perspectives.
    1) Dose the paraphrase user utterance is well matched to user description?
    2) Dose the user paraphrased user utterance is semantically equivalent to the original user utterance ?
    3) Dose the paraphrase system utterance is well personalized (style, tone, formality) to user description?
        - 1: Not at all (The sentence paraphrased system utterance is not personalized with specific words, phrases, or style to user description)
        - 2: A little (changes formality or tone for according to user description (Please tell your plan -> Could I know your plan?, Not specifically for user in description)
        - 3: Somewhat (changes style, tone, formality, greeting words, etc. to user description, ex, Nice red hat! or Your smile is beautiful!)
        - 4: A lot (The paraphrase system utterance is well personalized with specific words, phrases, or style to user description)
    4) Dose the system paraphrased system utterance is semantically equivalent to the original system utterance?
    5) Does the system’s utterance enhance the overall user experience, compared to system_reference?
    
    assess the dataset in four scales.
    1) 1: Not at all
    2) 2: A little
    3) 3: Somewhat
    4) 4: A lot

    
    **Original Dialogue**
        {dial1}
    **User Image Description:**
        {user_impression}
        
    **Changed Dialogue:**
        {dial2}
        
    Your answer must be in the following format/. Below is just an example, not the actual answer.:
    Score : (Q1:3, Q2:4, Q3:2, Q4:4, Q5:3)
    Score : (Q1:3, Q2:3, Q3:4, Q4:2, Q5:4)
    Score : (Q1:2, Q2:4, Q3:3, Q4:2, Q5:2)
    Now your turn to make your own answer with brief reason.
    """
    

    return prompt