import json
from PIL import Image
import requests
import pdb
import base64
import requests
import json
import time
import pdb
import numpy as np
import os
from openai import OpenAI
from prompts.filtering_prompt import get_acc_prompt, get_overall_prompt

import os


import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--data_type', type=str, default="test")
parser.add_argument('--split_idx', type=int, required=True)
parser.add_argument('--filter_type', type=str, default = "acc") # acc, overall
parser.add_argument('--org_dataset', type=str, required=True)
args = parser.parse_args()

# example usage
# python LLM_filter.py --data_type train --split_idx 1 --filter_type acc --org_dataset MWOZ

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
        
def predict(payload, use_img=1):
    key = os.environ["OPENAI_API_KEY"]
    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {key}"
    }
            
            
    response = requests.post("https://api.openai.com/v1/chat/completions",headers=headers, json=payload).json()
    try:
        result =  response['choices'][0]['message']['content']
    except:
        print(response)
        exit()
    return result
    
    
def make_line(custom_id, image_path, prompt, use_img=1):
    
    text_content = {
        "type": "text",
        "text": prompt
    }

    if use_img ==1:
        base64_image = encode_image(image_path)
        image_content = {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}",
                "detail": "low"
                }
            }
        content = [text_content, image_content]
    else:
        content = [text_content]
    
    
    payload = {
    "model": "gpt-4o",
    "messages": [
        {
        "role": "user",
        "content": content
        }
    ],
    "max_tokens": 300
    }
    
    overall = {
        'custom_id' : custom_id,
        'method' : 'POST',
        'url' : '/v1/chat/completions',
        'body' : payload,
    }
    return overall
    

def act_as_dict(act):
    #ds-v
    act_list = act.split(", ")
    act_dict = {}
    for act_ in act_list:
        act_slots = '-'.join(act_.split("-")[:3])
        if act_slots in act_dict:
            act_dict[act_slots].append(act_.split("-")[-1])
        else:
            act_value = act_.split("-")[-1]
            act_dict[act_slots] = [act_value]
    return act_dict


def use_db_check(act):
    if 'Movies-OFFER-movie_name' in act or 'Restaurants-OFFER-restaurant_name' in act or 'Media-OFFER-title' in act or 'Travel-OFFER-attraction_name' in act:
        return True
    
    return False
if __name__ == "__main__":
    # Access the OpenAI API key from the environment variable
    os.environ["OPENAI_API_KEY"] = json.load(open("config.json"))["api-key"]
    
    if args.org_dataset == "MWOZ":
        dataset = f"PATH_TO_DIR/changed_user_sys/{args.data_type}_split/{args.split_idx}.json"
    elif args.org_dataset == "SGD":
        dataset = f"PATH_TO_DIR/changed_user_sys/{args.data_type}/{args.split_idx}.json"
    
    
    
    save_temp = f"./batch_temp/{args.org_dataset}_filtering_{args.data_type}_split_temp/{args.filter_type}/{args.split_idx}.jsonl"
    save_result = f"./batch_result/{args.org_dataset}_filtering_{args.data_type}_split/{args.filter_type}/{args.split_idx}.jsonl"
    
    print("Dataset: ", dataset)
    print("Will save in temp", save_temp)
    print("Will save in result", save_result)
    
    # make new jsonl file
    if os.path.exists(save_temp):
        os.remove(save_temp)
    os.makedirs(os.path.dirname(save_temp), exist_ok=True)
    os.makedirs(os.path.dirname(save_result), exist_ok=True)
    
        # if save_result exists, skip
    if os.path.exists(save_result):
        print("Already exists")
        time.sleep(3)
        exit()

    
    dataset = json.load(open(dataset))
    idx =0
    
    payloads = []
    for item in dataset:
        if args.org_dataset == "MWOZ":
            dial = dataset[item]['dialogue']
            item = dataset[item]
        elif args.org_dataset == "SGD":
            dial = item['dialogue']
        
        dial = item['dialogue']
        first_impression = item["FI"]
        user, st_user, user_info, sys, st_sys, sys_info = [], [], [], [], [], []
        for turn in dial:
            user.append(turn['user'])
            st_user.append(turn['st_user'])
            user_info.append(turn['bspn'])
            sys.append(turn['resp'])
            st_sys.append(turn['st_resp'])
            sys_info.append(turn['act'])
        
        if args.filter_type == "acc":
            prompt = get_acc_prompt(user, st_user, user_info, sys, st_sys, sys_info, first_impression)
        elif args.filter_type == "overall":
            prompt = get_overall_prompt(user, st_user, sys, st_sys, first_impression)
            
                    
        
        line_id = f"{turn['dial_id']}"
        payload = make_line(line_id, None, prompt, use_img=0)
        payloads.append(payload)
        # save as jsonl
        with open(save_temp, "a") as f:
            f.write(json.dumps(payload) + "\n")

    # Do API call before batch
    
    print("len of payloads: ", len(payloads))
    time.sleep(3)
    for idx, payload in enumerate(payloads[:3]):
        temp_result=predict(payload['body'])
        print(payload['body']['messages'][0]['content'][0]['text'])
        print()
        print(temp_result)
        print()
        time.sleep(3)
    client = OpenAI()
        
    # uploading batch file
    batch_input_file = client.files.create(
        file=open(save_temp, "rb"),
        purpose="batch"
    )
    
    
    # creating batch file
    batch_input_file_id = batch_input_file.id

    obj = client.batches.create(
        input_file_id=batch_input_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={
        "description": "nightly eval job"
        }
    )
    obj_id = obj.id

    while True:
        retreived = client.batches.retrieve(obj_id)
        if retreived.status in ['completed','expired','cancelling','cancelled','failed'] :
            break
        print("status: ", retreived.status)
        if retreived.status == 'in_progress':
            print(retreived.request_counts)
        time.sleep(10)
        print("Waiting for 10 seconds")
        print()
    
    if retreived.status == 'failed':
        print("batch failed")
        print("error message: ", client.batches.retrieve(obj_id).errors.data[0].message)
    
    elif retreived.status == 'completed':
        content = client.files.content(retreived.output_file_id).content
        content =  content.decode('utf-8')
        with open(save_result, "w") as f: 
            f.write(content)
        
    