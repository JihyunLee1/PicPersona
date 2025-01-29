# Split the file, for generalization testing in sec 6.2
import json
import pdb
from collections import Counter
import os
dataset = ['train','dev','test']

for_general_testing = ['Homes', 'Buses', 'Movies']


### Don't care original train, dev, test split
for gt in for_general_testing:
    new_data = []
    for data_type in dataset:
        data = json.load(open(f'raw_emotion_Mwoz/{data_type}.json', 'r'))
        for item in data:
            if len(item['domains']) == 1 and item['domains'][0] == gt:
                new_data.append(item)
    
    # save it to new file
    file_path = f'for_testing_general/{gt}_noimg.json'
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    
    with open(file_path, 'w') as f:
        json.dump(new_data, f, indent=2)


# dataset to change
for data_type in dataset:
    new_dataset = []
    data = json.load(open(f'raw_emotion_Mwoz/{data_type}.json', 'r'))
    for item in data:
        continue_flag = False
        
        domain = sorted(item['domains'])
        for d in domain:
            if d in for_general_testing:
                continue_flag = True
                break
        if continue_flag: continue
        new_dataset.append(item)
    file_path = f'to_change/{data_type}_noimg.json'
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        if data_type != 'train':
            new_dataset = new_dataset[:1100]
        json.dump(new_dataset, f, indent=2)
    print(len(new_dataset))
    
    
