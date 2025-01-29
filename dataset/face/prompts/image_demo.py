def get_prompt():
    prompt = "This is a fake person. In your opinion, what is the gender, age, emotion and formality of this avatar?  It is okay if you cannot determine the exact age or ethnicity. "
    prompt += "gender : male, female\n"
    prompt += "age : toddler, child, teenager, adult, senior\n"
    prompt += "emotion : positive, negative, neutral\n"
    prompt += "formality: casual, formal\n"
    prompt += "These are some examples format of the attributes you can use to describe the avatar.\n "
    prompt += "gender : male, age : adult, emotion : neutral, formality : casual\n"
    prompt += "gender : female, age : teenager, emotion : positive, formality : formal\n"
    prompt +="Please provide your answer."
    
    return prompt
