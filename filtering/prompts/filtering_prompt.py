def get_acc_prompt(user, st_user, user_info, sys, st_sys, sys_info, first_impression):
    prompt = "You are the proficient dialogue quality evaluator. Please evaluate the dialogue quality of the following dialogue. "
    prompt += "You will be given a two dialogue sets. The first one in original dialogue and the second one is dialogue style transferred version. "
    prompt += f"In the restyled version, the user's utterance is modified to reflect how they would say it based on their first impression: {first_impression}."
    prompt += "System utterance is changed to give personalized response to user, in terms of user's first impression"
    prompt += "You will also be given the dialogue actions for both user and system, which is the direction user and system should follow."
    prompt += "In the original dialogue, user and systems followed the action well."
    
    prompt +="This is the original dialogue: \n"
    for i in range(len(user)):
        prompt += f"Turn {i+1}\n"
        prompt += f"User: {user[i]}, UserAction {user_info[i]}\n"
        prompt += f"System: {sys[i]}, SystemAction {sys_info[i]}\n"
        
        
    prompt +="This is the dialogue style transferred version."
    for i in range(len(st_user)):
        prompt += f"Turn {i+1}\n"
        prompt += f"Transferred User: {st_user[i]}, UserAction {user_info[i]}\n"
        prompt += f"Transferred System: {st_sys[i]}, SystemAction {sys_info[i]}\n"
        
    prompt +="Please evaluate the dialogue quality in two aspects: "
    prompt +="1. User's dialogue quality : Does the transferred user dialogue follow the action well?"
    prompt +="2. System's dialogue quality : Does the transferred system dialogue follow the action well?"
    
    prompt += 'Additionally, transferred systems sometimes provide personalized recommendation using the DB results. Don not consider the DB results in the evaluation.'
    prompt += "Additionally, changes the booking time, such as 5:45 PM to 5:30 PM or 6PM should not be considered as a failure."
    
    
    
    prompt += "If there is any issue in the dialogue, please report it."
    prompt += "Format of the report: \n"
    prompt += "User's dialogue quality: <pass/fail>, System's dialogue quality: <pass/fail>,Reason: <reason>"
    prompt += "for example, User's dialogue quality: fail, System's dialogue quality: pass, Reason: User's dialogue is not following the action"
    prompt += "or User's dialogue quality: pass, System's dialogue quality: fail, Reason: System's dialogue is not following the action" 
    prompt += "or User's dialogue quality: pass, System's dialogue quality: pass,  Reason: transferred dialogue contains all information as in original dialogue"
    prompt += "Now, please evaluate the dialogue quality of the transferred dialogue."
        
    return prompt



    
    
    
def get_overall_prompt(user, st_user,  sys, st_sys,  first_impression):
    prompt = "You are the proficient dialogue quality evaluator. Please evaluate the dialogue quality of the following dialogue. "
    prompt += "You will be given a synthesized dialogue sets."
    prompt += f"In this dialogue, the user's utterance is synthesized to reflect how they would say it based on their first impression: {first_impression}."
    prompt += "System utterance is synthesized to give personalized response to user, in terms of user's first impression \n"
        
    for i in range(len(st_user)):
        prompt += f"Turn {i+1}\n"
        prompt += f"User: {st_user[i]}\n"
        prompt += f"System: {st_sys[i]}\n"
        
    prompt +="Please evaluate the quality of the dialogue's in two criteria\n"
    prompt += "1. Flow: Does the  dialogue flow as smoothly? Does it sound natural?"
    prompt += "2. Logical: Does the  dialogue and system response make sense in the context of the conversation?"
    
    prompt += 'Additionally, greetings and ending words can be some what overly sentimental over personalized. However do not consider the greetings in the evaluation. It is intended to make the dialogue more personalized.'
    prompt += "Additionally, changes the booking time slightly, such as 5:45 PM to 5:30 PM or 6PM should not be considered as a failure."
    
    prompt += "If there is any issue in the dialogue, please report it."
    prompt += "Format of the report: \n"

    prompt += "Flow: <pass/fail>, Logical: <pass/fail> Reason: <reason>"
    prompt += "for example, Flow: fail, Logical: pass, Reason: System's dialogue is too rude for the user, in terms of user's first impression"
    prompt += "for example, Flow: fail, Logical: pass, Reason: System's dialogue is too verbose and gives too much information which makes the dialogue unnatural"
    prompt += "for example, Flow: pass, Logical: fail, Reason: System's response is not logical or coherent, as the answer is not related to the user's query"
    prompt += "for example, Flow: pass, Logical: pass, Reason: Transferred dialogue contains all information as in original dialogue, and flows naturally"
    prompt += "Now, please evaluate the dialogue quality of the transferred dialogue."
        
    return prompt


