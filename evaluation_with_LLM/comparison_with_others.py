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

from prompts.comparison_with_others import get_prompt

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--data_path", type=str, required=True, help="path to the inferenced dataset")
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
    # System 2 is ours!
    dial_str = ""

    for turn in dial:
        dial_str += "user : " + turn["st_user"] + "\n"
        dial_str += "system1 : " +turn['st_resp'][:-1] + "\n"
        dial_str += "system2 : " +  turn['st_resp2'] + "\n"
    return dial_str



if __name__ == "__main__":
    # Access the OpenAI API key from the environment variable
    os.environ["OPENAI_API_KEY"] = json.load(open("config.json"))["api-key"]

    dataset  =json.load(open(args.data_path))
    prefix = args.data_path.split("/")[-1].replace(".json", "")   

    
    image_dir = f"PATH_TO_DIR/dataset/face"
    save_temp = f"PATH_TO_DIR/evaluation_with_LLM/for_batch/{prefix}.jsonl"
    save_result = f"PATH_TO_DIR/evaluation_with_LLM/batch_output/{prefix}.jsonl"
        
        
    print("Will save in ", save_temp)
    print("Will save in ", save_result)
    
    # make new jsonl file
    if os.path.exists(save_temp):
        os.remove(save_temp)
        
    os.makedirs(os.path.dirname(save_temp), exist_ok=True)
    os.makedirs(os.path.dirname(save_result), exist_ok=True)

    
    dataset = dict(sorted(dataset.items()))
    
    payloads = []
    
    for dial_id, item in dataset.items():
        image_path = os.path.join(image_dir, item["image"])
        dial_str = make_dials(item['dialogue'])
        user_impression = item['FI']
        prompt = get_prompt(dial_str, user_impression)
            
        line_id = dial_id
        payload = make_line(line_id, image_path, prompt, use_img=1)
        payloads.append(payload)
        # save as jsonl
        with open(save_temp, "a") as f:
            f.write(json.dumps(payload) + "\n")

    # Do API call before batch
    
    
    
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
        
    