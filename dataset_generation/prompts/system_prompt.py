def get_prompt(user1, system1, user2, dialogue_progress, strategy, first_impression):
    prompt = f"""
    You are given a dialogue between a user and a system, consisting of the latest user utterance, the current system utterance, and the next user utterance. 
    Your task is to modify the tone, formality, and wording of the current system utterance to give a personalized response to the user. The response should match the provided image and description.
    This is user image description : {first_impression}
    Below is the information you have:
    
     **Latest User Utterance (user1):**
        {user1}

     **Current System Utterance (system1):**
        {system1}
    """
    if user2 is not None:
        prompt += f"""
            **And this is the next user answer (user2):**
                {user2}
            As this is future information, do not use it in your response, just keep it in mind.
        
            """
    if strategy != None:
        if strategy['name'] == 'greeting':
            prompt += '''As this is the first turn in the conversation, make the greetings reflect the user's image or highlight something extraordinary about their appearance, like "Nice hat!" or "Congratulations on your graduation!"'''
            prompt +="""However, if the user doesn't looks like in a good mood, or it is formal setting, you can just say "Hello" or "Hi" or Hello sir, madam, etc. Dont' say appearance related things."""
        if strategy['name'] == 'goodbye':
            prompt += '''As this is the final turn in the conversation, make the ending statement. If needed, reflect the user\'s image or "Enjoy your vacation!". You can just say "Goodbye" things if no other information is available.'''
        if strategy['name'] == 'DB':
            prompt += '''The user is providing information from internet soruces. \n'''
            prompt +=f'This is online {strategy["DB_type"]} information for {strategy["Key"]}. \n'
            prompt += '\n'.join(strategy['online'])
            prompt += '''\nIf this relates to the user's age, emotion, gender, formality and their style, make a personalized response using that context. \
                Mention why you recommend this, connecting it to something specific about their age, emotion, gender, formality and events. \
                For instance, you might say, 'This could perfectly match your cool mood,' or 'Given your artistic taste, this seems ideal,' \
                or even 'It's a great fit for an academic setting with children—you might really enjoy it.' \
                You could also highlight occasions like celebrations, with phrases like 'This spot would be perfect for celebration.'\
                If no connection exists, simply omit this step.\n''' 


    prompt += f"""
        **Dialogue progress:**
            {dialogue_progress}
        """
    if dialogue_progress == "Middle of the dialogue":
        prompt += "Don't say celebration, thank you, or goodbye. In the middle of the conversation, it is not natural."
        
    prompt += """
    

        **Objective:**

        Modify the current system utterance (system1) so that it matches the style described in the user image description. 
        Don't use 'craving' 'kindly' 'certainly', 'sure thing', 'hey there', 'hey and 'vibe' It is not natural.
        Keep in the information center staff role.
        Your Answer (no description needed):
    """
    return prompt
