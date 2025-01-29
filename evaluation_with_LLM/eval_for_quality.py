import json
from PIL import Image
import requests
import pdb
import base64
import requests
import json
import time
import pdb

import os
from openai import OpenAI

import os

from prompts.eval_for_quality import get_prompt

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--use_list", type=str, default='', help="path to the list of dialogues to use") 
parser.add_argument("--dataset_path", type=str, default='', help="path to the inferenced dataset")
args = parser.parse_args()


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
    
    
def make_line( custom_id, image_path,prompt, use_img=1):
    
    base64_image = encode_image(image_path)
    text_content = {
        "type": "text",
        "text": prompt
    }
    image_content = {
        "type": "image_url",
        "image_url": {
            "url": f"data:image/jpeg;base64,{base64_image}",
            "detail": "low"
        }
    }
    if use_img ==1:
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
    


def make_dials(dial):
    org_dial, new_dial = '', ''
    for turn in dial:
        org_dial += "user : " + turn["user"] + "\n"
        org_dial += "system : " + turn["resp"] + "\n"
        new_dial += "user : " + turn["st_user"] + "\n"
        new_dial += "system : " + turn["st_resp"] + "\n"
    return org_dial, new_dial


    
if __name__ == "__main__":
    os.environ["OPENAI_API_KEY"] = json.load(open("config.json"))["api-key"]
    if args.use_list:
        use_list = json.load(open(args.use_list))

        use_list_name = args.use_list.split("/")[-1].split(".")[0]
    
    dataset_path = args.dataset_path
    dataset = json.load(open(dataset_path))
    image_dir = f"PATH_TO_DIR/dataset/face"
    
    dataset_file_name = dataset_path.split("/")[-1].replace(".json", "")
    save_temp = f"PATH_TO_DIR/eval_for_quality/for_batch/{dataset_file_name}.jsonl"
    if args.use_list:
        save_result = f"PATH_TO_DIR/eval_for_quality/batch_output/{dataset_file_name}_{use_list_name}.jsonl"
    else:
        save_result = f"PATH_TO_DIR/eval_for_quality/batch_output/{dataset_file_name}.jsonl"    
        
    print("Will save in ", save_temp)
    print("Will save in ", save_result)
    
    # make new jsonl file
    if os.path.exists(save_temp):
        os.remove(save_temp)
        
    os.makedirs(os.path.dirname(save_temp), exist_ok=True)
    os.makedirs(os.path.dirname(save_result), exist_ok=True)

    
    idx =0
    

    
    payloads = []
    for dial_id in dataset:
        image = dataset[dial_id]["image"]
        dial = dataset[dial_id]["dialogue"]
        if args.use_list and dial_id not in use_list: continue
        idx+=1
        image_path = os.path.join(image_dir, image)
        dial1, dial2 = make_dials(dial)
        user_impression = dataset[dial_id]["FI"]    
        prompt = get_prompt(dial1, dial2, user_impression)
            
        line_id = f"{dial[0]['dial_id']}"
        payload = make_line(line_id, image_path, prompt, use_img=1)
        payloads.append(payload)
        # save as jsonl
        with open(save_temp, "a") as f:
            f.write(json.dumps(payload) + "\n")

    
    
    
    print("len of payloads: ", len(payloads))
    time.sleep(3)
    for payload in payloads[:3]:
        temp_result=predict(payload['body'])
        print(payload['body']['messages'][0]['content'][0]['text'])
        print('-'*50)
        print(temp_result)
        print()
        time.sleep(10)
    
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
        
    