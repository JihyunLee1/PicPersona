# Perform this after get filtering

import json
import os
import pdb
# load dataset as the one


demo_data = json.load(open('PATH_TO_DIR/dataset/face/demo.json'))

def add_meta(data):
    FI_data = json.load(open('PATH_TO_DIR/dataset/face/FI.json'))
    demo_data = json.load(open('PATH_TO_DIR/dataset/face/demo.json'))
    
    for dial_id in data:
        item = data[dial_id]
        image = item['image']
        item['FI'] = FI_data[image]
        demo = demo_data[image].lower()
        
        if 'casual' in demo:
            item['formality'] = 'casual'
        elif 'formal' in demo:
            item['formality'] = 'formal'
        else:
            item['formality'] = 'unknown'
            
        if 'positive' in demo:
            item['image_emotion'] = 'positive'
        elif 'neutral' in demo:
            item['image_emotion'] = 'neutral'
        elif 'negative' in demo:
            item['image_emotion'] = 'negative'
        else:
            item['image_emotion'] = 'unknown'
            
        # ages : toddler, child, teenager, adult, senior 
        if 'toddler' in demo:
            item['age'] = 'toddler'
        elif 'child' in demo:
            item['age'] = 'child'
        elif 'teenager' in demo:
            item['age'] = 'teenager'
        elif 'adult' in demo:
            item['age'] = 'adult'
        elif 'senior' in demo:
            item['age'] = 'senior'
        else:
            item['age'] = 'unknown'
            
            
        # gender
        if 'female' in demo:
            item['gender'] = 'female'
        else:
            item['gender'] = 'male'
    
    return data

def change_format(raw_data, data_type):
    new_data= {}
    for item in raw_data:
        dial_id = f"{item['dialogue_id']}_{data_type}"
        new_data[dial_id] = {}
        new_data[dial_id]['dialogue'] = item['dialogue']
        new_data[dial_id]['dialogue_id'] = dial_id
        new_data[dial_id]['type'] = item['type']
        new_data[dial_id]['image'] = item['image']
        new_data[dial_id]['FI'] = item['FI']
        new_data[dial_id]['image_emotion'] = item['image_emotion']
    return new_data
        
        
    
    
# load dataset as the one
def load_dataset(folder):
    # get all json files
    json_files = [f for f in os.listdir(folder) if f.endswith('.json')]
    json_files = [f for f in json_files if "task2" not in f]
    dataset = []
    for json_file in json_files:
        with open(os.path.join(folder, json_file), 'r') as f:
            dataset.extend(json.load(f))
    return dataset
            
            
def cluster_ids(data_type):
    sys_path = f"./filtered/cluster_fail/{data_type}_sys.json"
    sys_data = json.load(open(sys_path))
    s_ids = []
    for k,v in sys_data.items():
        s_ids += v
    print(f"filter from cluster, sys: {len(s_ids)}")
    
    user_path = f"./filtered/cluster_fail/{data_type}_user.json"
    user_data = json.load(open(user_path))
    u_ids = []
    for k,v in user_data.items():
        u_ids += v
    print(f"filter from cluster, user: {len(u_ids)}")
    
    return set(s_ids + u_ids)

def LLM_acc_filter(data_type):
    sys_path = f"./filtered/LLM_acc_fail/{data_type}.json"
    ids = json.load(open(sys_path))
    print(f"filter from LLM_acc, {data_type}: {len(ids)}")
    return set(ids)

def LLM_overall_fail(data_type):
    sys_path= f"./filtered/LLM_overall_fail/{data_type}.json"
    ids = json.load(open(sys_path))
    print(f"filter from LLM_overall, {data_type}: {len(ids)}")
    return set(ids)

def style_fail(data_type):
    sys_path = f"./filtered/style_fail/{data_type}_sys.json"
    sys_data = json.load(open(sys_path))
    s_ids = []
    for k,v in sys_data.items():
        s_ids += v['lower']
    print(f"filter from style strength, sys: {len(s_ids)}")
    
    user_path = f"./filtered/style_fail/{data_type}_user.json"
    user_data = json.load(open(user_path))
    u_ids = []
    for k,v in user_data.items():
        u_ids += v['lower']
    print(f"filter from style strength, user: {len(u_ids)}")
    
    return set(s_ids + u_ids)
    



        
    
    
if __name__ == "__main__":
    folders= ['PATH_TO_DIR/dataset/SGD/train',
            'PATH_TO_DIR/dataset/SGD/dev',
            'PATH_TO_DIR/dataset/SGD/test']


    for folder in folders:
        data_type = folder.split('/')[-1]
        new_data = load_dataset(folder)
        new_data = change_format(new_data, data_type)
        new_data = add_meta(new_data)
        filters = cluster_ids(data_type) | LLM_acc_filter(data_type) | LLM_overall_fail(data_type) | style_fail(data_type)
        filters = set([f"{f}_{data_type}" for f in filters])
        save_path  =folder.replace('changed_user_sys', 'final')
        
        print("Before filtering: ", len(new_data))  

        filtered_data = {k:v for k,v in new_data.items() if k not in filters}
        os.makedirs(os.path.dirname(f"{save_path}.json"), exist_ok=True)        
        json.dump(filtered_data, open(f"{save_path}.json", 'w'), indent=2)
        print("save in ", f"{save_path}.json")
        print("After filtering: ", len(filtered_data))