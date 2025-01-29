# Code for image first impression
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

from prompts.image_FI import get_prompt

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--data_index', type=str)
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
    result =  response['choices'][0]['message']['content']
    
    return result
    
    
def make_line(custom_id, image_path,prompt, use_img=1):
    
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
    



    
if __name__ == "__main__":
    # Access the OpenAI API key from the environment variable
    os.environ["OPENAI_API_KEY"] = json.load(open("config.json"))["api-key"]
    
    image_dir = f"PATH_TO_DIR/face/{args.data_index}"
    save_temp = f"PATH_TO_DIR/for_batch/FI/{args.data_index}.jsonl"
    save_result = f"PATH_TO_DIR/batch_output/FI/{args.data_index}.jsonl"
    os.makedirs(os.path.dirname(save_temp), exist_ok=True)
    os.makedirs(os.path.dirname(save_result), exist_ok=True)
    
    image_list = os.listdir(image_dir)
    image_list = [i for i in image_list if i.endswith(".png")]
    # make new jsonl file
    if os.path.exists(save_temp):
        os.remove(save_temp)
    
    idx =0
    payloads = []
    for turn_idx, image in enumerate(image_list):
        image_path = os.path.join(image_dir, image)
        prompt = get_prompt()
        line_id = f"{image.replace('/','-')}"
        payload = make_line(line_id, image_path, prompt)
        payloads.append(payload)

        with open(save_temp, "a") as f:
            f.write(json.dumps(payload) + "\n")

    # Do API call before batch
    
    for payload in payloads[:3]:
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
        
    