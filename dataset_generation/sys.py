import json
from PIL import Image
import requests
import pdb
import base64
import requests
import json
import time
import pdb
from sentence_transformers import SentenceTransformer
import numpy as np
import os
from openai import OpenAI

import os

from prompts.system_prompt import get_prompt

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--data_type', type=str, default="test")
parser.add_argument('--split_idx', type=int, required=True)
parser.add_argument('--org_dataset', type=str, default="SGD")
parser.add_argument('--use_list', type=str)
parser.add_argument('--model_name', type=str, default="gpt-4o")

args = parser.parse_args()

# python sys.py --data_type test --split_idx 1 --org_dataset MWOZ


def setting_DB(DB_path, org_dataset):
    if org_dataset == "MWOZ":
        restaurant_DB = json.load(open(os.path.join(DB_path, "restaurants.json")))
        attraction_DB = json.load(open(os.path.join(DB_path, "attractions.json")))
        hotel_DB = json.load(open(os.path.join(DB_path, "hotels.json")))
        return [restaurant_DB, attraction_DB, hotel_DB]
    
    elif org_dataset == "SGD":
        restaurant_DB = json.load(open(os.path.join(DB_path, "restaurants.json")))
        movie_DB = json.load(open(os.path.join(DB_path, "movies.json")))
        travel_DB = json.load(open(os.path.join(DB_path, "travels.json")))
        return restaurant_DB, movie_DB, travel_DB


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
    
    
def make_line(custom_id, image_path,prompt, use_img=1, model_name = "gpt-4o"):
    
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
    "model": model_name,
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
    

def act_as_dict_SGD(act):
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

def act_as_dict_MWOZ(act):
    #ds-v
    act_list = act.split(", ")
    act_dict = {}
    
    for act_ in act_list:
        act_ = act_.replace(",","")
        act_slots = '-'.join(act_.split("-")[:2])
        if act_slots not in act_dict:
            act_dict[act_slots] = [act_.split("-")[-1]]
        else:
            act_dict[act_slots].append(act_.split("-")[-1])    
    return act_dict



def get_embedding(text, embedding_model):
    sentences = [text]
    embeddings = embedding_model.encode(sentences).tolist()[0]
    return embeddings


def find_related(embedding_model, online_text, user, type='review'):
    # find most related one, by embedding with similarity
    if type == 'review' and len(online_text) < 3:
        return [review['review_text'] for review in online_text]
    if type == 'review':
        texts = [review['review_text'] for review in online_text]
    elif type == 'wiki':
        texts = online_text
    
    review_embeddings = [get_embedding(text, embedding_model) for text in texts]
    user_embedding = get_embedding(user, embedding_model)
    similarity = [np.dot(user_embedding, review_embedding) for review_embedding in review_embeddings]
    # sort by similarity
    sorted_similarity = sorted(enumerate(similarity), key=lambda x: x[1], reverse=True)
    sorted_text = [texts[idx] for idx, _ in sorted_similarity]
    return sorted_text    


def action_strategy_MWOZ(user, embedding_model, action, DBs, turn_idx):
    strategy = None
    action = act_as_dict_MWOZ(action)
    restaurant_DB, attraction_DB, hotel_DB = DBs
    if turn_idx ==0:
        return {'name' : "greeting"}
    if "general-bye" in action:
        return  {'name' : "goodbye"}

    if "Restaurant-Inform:Name" in action:
        value = action["Restaurant-Inform:Name"]
        if len(value)==1:
            if value[0].lower() in restaurant_DB:
                db_result = restaurant_DB[value[0].lower()]
                if db_result['online'] and len(db_result['online']) !=0:
                    similar_list = find_related(embedding_model, db_result['online'], user)
                    strategy = {'name':'DB', 'online': similar_list[:3], 'DB_type': 'review', 'Key': value[0]}
                    return strategy
        
        
    if "Attraction-Inform:Name" in action:
        value = action["Attraction-Inform:Name"]
        if len(value)==1:
            if value[0].lower() in attraction_DB:
                db_result = attraction_DB[value[0].lower()]
                if db_result['online'] and len(db_result['online']) !=0:
                    similar_list = find_related(embedding_model, db_result['online'], user, type = 'wiki')
                    strategy = {'name':'DB', 'online': similar_list[:3], 'DB_type': 'wiki', 'Key': value[0]}
                    return strategy
        
    if "Hotel-Inform:Name" in action:
        value = action["Hotel-Inform:Name"]
        if len(value)==1:
            if value[0].lower() in hotel_DB:
                db_result = hotel_DB[value[0].lower()]
                if db_result['online'] and len(db_result['online']) !=0:
                    similar_list = find_related(embedding_model, db_result['online'], user, type = 'review')
                    strategy = {'name':'DB', 'online': similar_list[:3], 'DB_type': 'review', 'Key': value[0]}
                    return strategy
        
    return strategy
    
def action_strategy_SGD(user, embedding_model, action, turn_idx):
    strategy = None
    action = act_as_dict_SGD(action)
    if turn_idx ==0:
        strategy = {'name' : "greeting"}
        
    if '-GOODBYE' in action:
        strategy = {'name' : "goodbye"}
        
    # if 'Movies-OFFER-movie_name' in action or 'Media-OFFER-title' in action:
    
    if 'Restaurants-OFFER-restaurant_name' in action: # get three reviews
        if len(action['Restaurants-OFFER-restaurant_name'])==1:
            key = action['Restaurants-OFFER-restaurant_name'][0]
            db_result = restaurant_DB[key]
            if db_result['online'] and len(db_result['online']) !=0:
                similar_list = find_related(embedding_model, db_result['online'], user)
                strategy = {'name':'DB', 'online': similar_list[:3], 'DB_type': 'review', 'Key': key}
                
    wiki_list = ['Movies-OFFER-movie_name', 'Media-OFFER-title', 'Travel-OFFER-attraction_name']
    wiki_DBs = [movie_DB, movie_DB, travel_DB]
    for wiki_act, wiki_DB in zip(wiki_list, wiki_DBs):
        if wiki_act in action:
            if len(action[wiki_act])==1:
                key = action[wiki_act][0]
                db_result = wiki_DB[key]
                if db_result['online'] and len(db_result['online']) !=0:
                    similar_list = find_related(embedding_model, db_result['online'], user, type = 'wiki')
                    strategy = {'name':'DB', 'online': similar_list[:3], 'DB_type' : 'wiki', 'Key': key}

    return strategy    # do something
    
if __name__ == "__main__":
    # Access the OpenAI API key from the environment variable
    os.environ["OPENAI_API_KEY"] = json.load(open("config.json"))["api-key"]
    image_dir = f"PATH_TO_DIR/dataset/face"
    if args.use_list:
        use_list = json.load(open(args.use_list))
    
    if args.org_dataset == "MWOZ":
        DB_path = "PATH_TO_DIR/dataset/mwoz/DB_review"
        dataset = f"PATH_TO_DIR/dataset/mwoz/V5/changed_user/{args.data_type}_split/{args.split_idx}.json"
        
    elif args.org_dataset == "SGD":
        DB_path = "PATH_TO_DIR/dataset/SGD/DB"
        restaurant_DB, movie_DB, travel_DB = setting_DB(DB_path, 'SGD')
        dataset = f"PATH_TO_DIR/dataset/SGD/changed_user/{args.data_type}/{args.split_idx}.json"

    save_temp = f"PATH_TO_DIR/LLM/for_batch/{args.org_dataset}/sys_{args.data_type}_split/{args.split_idx}.jsonl"
    save_result = f"PATH_TO_DIR/LLM/batch_output/{args.org_dataset}/sys_{args.data_type}_split/{args.split_idx}.jsonl"

    if args.use_list:    
        post_fix = args.use_list.split("/")[-1].replace(".json", "")
        save_temp = save_temp.replace(".jsonl", f"_{post_fix}.jsonl")
        save_result = save_result.replace(".jsonl", f"_{post_fix}.jsonl")
        
        
    
    
    
    # if save_resul exists, skip
    if os.path.exists(save_result):
        print("Already exists")
        time.sleep(3)
        exit()
    embedding_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
    

        
    print("Loading dataset from ", dataset)
    print("Will save in temp", save_temp)
    print("Will save in result", save_result)
    
    # make new jsonl file
    if os.path.exists(save_temp):
        os.remove(save_temp)
    os.makedirs(os.path.dirname(save_temp), exist_ok=True)
    os.makedirs(os.path.dirname(save_result), exist_ok=True)

    
    dataset = json.load(open(dataset))
    idx =0
    

    
    payloads = []
    temp_images = []
    for item in dataset:
        if args.org_dataset == "MWOZ":
            dial = dataset[item]['dialogue']
            item = dataset[item]
            dial_id = item['dialogue'][0]['dial_id']
        elif args.org_dataset == "SGD":
            dial = item['dialogue']
            dial_id = item['dialogue_id']
            
        if use_list and dial_id not in use_list:
            continue
        
        if len(dial)<2:
            continue
        for turn_idx, turn in enumerate(dial):
            idx+=1
            image_path = os.path.join(image_dir, item["image"])
            image_impression = item["FI"]
            
            user1 = turn['st_user']
            system1 = turn['resp']
            
            if turn_idx == 0:
                dialogue_progress = "First turn"
                user2 = dial[turn_idx+1]['st_user']
            elif turn_idx == len(dial)-1:
                dialogue_progress = "Final state"
                user2 = None    
            else:
                dialogue_progress = "Middle of the dialogue"
                user2 = dial[turn_idx+1]['st_user']
            
            
            first_impression = f"Customer is {image_impression}"
            
            
            if args.org_dataset == "MWOZ":
                DBs = setting_DB(DB_path, 'MWOZ')
                strategy = action_strategy_MWOZ(user1, embedding_model, turn['act'], DBs, turn_idx)
                
            elif args.org_dataset == "SGD":
                strategy = action_strategy_SGD(user1, embedding_model, turn['act'], turn_idx)
            
            temp_images.append(image_path)
            prompt = get_prompt(user1, system1, user2, dialogue_progress, strategy, first_impression)
            line_id = f"{turn['dial_id']}_{turn_idx}"
            payload = make_line(line_id, image_path, prompt, model_name=args.model_name)
            payloads.append(payload)
            # save as jsonl
            os.makedirs(os.path.dirname(save_temp), exist_ok=True)
            with open(save_temp, "a") as f:
                f.write(json.dumps(payload) + "\n")

    # Do API call before batch
    
    print("len of payloads: ", len(payloads))
    time.sleep(3)
    for idx, payload in enumerate(payloads[:3]):
        print(temp_images[idx])
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
        
    