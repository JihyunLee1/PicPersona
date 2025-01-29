# Format SGD to Mwoz
import json
import pdb
import os
from collections import Counter

# Set the emotion of dialgoue, and change the format SGD to Mwoz. File will saved in raw_emotion_Mwoz
def set_emotion(turns):
    emotions = []
    for idx, turn in enumerate(turns):
        if idx %2 == 0:
            emotions.append(turn['emotion'])
    if 'negative' in emotions:
        return 'negative'
    elif emotions.count('neutral')*0.5>emotions.count('positive'):
        return 'neutral'
    else:
        return 'positive'
    
    
def make_dst(turn, previous, domain):
    dst = {}
    bspn = ""
    # pass
    
    # print(turn['utterance'])
    for f in turn['frames']:
        if domain not in dst and len(f['state']['slot_values'])!=0 : dst[domain] = {}
        for s in f['state']['slot_values']:
            v = f['state']['slot_values'][s][0]
            dst[domain][s] = v
        
    for d in dst:
        previous[d] = dst[d]
        
    for pd in previous:
        bspn += f"[{pd}] "
        for s in previous[pd]:
            bspn += f"{s} '{previous[pd][s]}' "

    return dst, bspn
    
def make_action(turn, domain):
    #  Taxi-Request:Leave-?, Taxi-Request:Arrive-?,
    #  Restaurant-Inform:Food-Indian, Restaurant-Inform:Area-centre, Restaurant-Inform:Choice-nine, 
    if len(turn['frames'])!=1:
        pdb.set_trace()
    actions = ""
    exception = ['GOODBYE', 'NOTIFY_FAILURE', 'NOTIFY_SUCCESS', ]
    for act in turn['frames'][0]['actions']:
        act_name = act['act']
        if len(act['canonical_values'])==0:
            if act_name in exception: 
                actions += f"{domain}-{act_name}, "
            else:
                actions += f"{domain}-{act_name}-{act['slot']}-?, "
        else:
            for val in act['canonical_values']:
                actions += f"{domain}-{act_name}-{act['slot']}-{val}, "
            
    actions = actions[:-2]
    return actions
    
def SGD_to_Mwoz(file_path):
    emotions = []
    data = json.load(open(file_path, 'r'))
    result = []
    prev = {}
    for dialog in data:
        overall_dial = {}
        dial_new = []
        domains = []
        for turn_id, turn in enumerate(dialog['turns']):
            if turn_id %2 !=0:
                domain = dialog['turns'][turn_id]['frames'][0]['service'].replace('_1','').replace('_2','').replace('_3','').replace('_4','')
                
                dst,bspn = make_dst(dialog['turns'][turn_id-1], prev, domain)
                prev = dst
                action = make_action(dialog['turns'][turn_id], domain)
                domains.append(domain)
                new_turn={
                    'dial_id': dialog['dialogue_id'],
                    'domain' : domain,
                    'turn_num': turn_id//2,
                    'user': dialog['turns'][turn_id-1]['utterance'],
                    'resp': dialog['turns'][turn_id]['utterance'],
                    'bspn': bspn,
                    'act': action
                }
              
                dial_new.append(new_turn)
        overall_dial['dialogue_id'] = dialog['dialogue_id']
        overall_dial['dialogue'] = dial_new
        overall_dial['domains'] = list(set(domains))
        overall_dial['type'] = 'SGD'
        overall_dial['emotion'] = set_emotion(dialog['turns'])
        emotions.append(overall_dial['emotion'])
                
        result.append(overall_dial)
    counter = Counter(emotions) 
    return result

    
    
if __name__ == '__main__':
    types = ['train','dev','test']
    numbers = [127,20,34]
    
    for data_type, number in zip(types, numbers):
        new_dataset = []
        
        for i in range(1,number+1):
            file_path = f"PATH_TO_DIR/SGD/raw_emotion/{data_type}/dialogues_{str(i).zfill(3)}.json"
            result = SGD_to_Mwoz(file_path)
            new_dataset+=result
            
            
        save_path = f"PATH_TO_DIR/SGD/raw_emotion_Mwoz/{data_type}.json"
        json.dump(new_dataset, open(save_path, 'w'), indent=2)
        print(len(new_dataset))
        print("save in", save_path)
    
    