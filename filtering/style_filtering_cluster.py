
from collections import defaultdict

import json
import argparse
import numpy as np
import pdb
from tqdm import tqdm
import pickle
from violin_plot import draw_violin_plot_with_outliers
import os
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('--user_or_sys', type=str, default="user")
parser.add_argument('--org_dataset', type=str, required=True) # MWOZ or SGD
args = parser.parse_args()


def get_embedding(text, embedding_model):
    sentences = [text]
    embeddings = embedding_model.encode(sentences).tolist()[0]
    return embeddings
import numpy as np

def find_outliers(data, filter):

    numbers = [item['vector'] for dial_id, item in data.items() if filter in item['label']]
    dial_id = [dial_id for dial_id, item in data.items() if filter in item['label']]

    center = np.mean(numbers, axis=0)

    distance_dict = {}
    for key, value in zip(dial_id, numbers):
        distance = np.linalg.norm(center - value)
        distance_dict[key] = distance
    
    distance_values = np.array(list(distance_dict.values()))

    Q3 = np.percentile(distance_values, 75)

    Q1 = np.percentile(distance_values, 25)
    IQR = Q3 - Q1

    # Define the upper bound for outliers (no lower bound)
    upper_bound = Q3 + 4.5 * IQR

    # Find the indices of outliers above the upper bound
    outlier_indices = [key for key, value in distance_dict.items() if value > upper_bound]
        
    return outlier_indices


def make_embedding(save_path, dataset):
    try:
        embeddings = pickle.load(open(save_path, 'rb'))
        return embeddings
    except:
        use_list = ['Movies-OFFER-movie_name', 'Restaurants-OFFER-restaurant_name', 'Media-OFFER-title', 'Travel-OFFER-attraction_name']
        from sentence_transformers import SentenceTransformer
        
        embeddings = {}
        embedding_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
        # get and save embeddings, because it takes time
        for idx, item in enumerate(tqdm(dataset)):
            
            if args.org_dataset == "MWOZ":
                dial_id = item
                dial = dataset[item]['dialogue']
                item = dataset[item]
                
                
            elif args.org_dataset == "SGD":
                dial = item['dialogue']
                dial_id = item['dialogue_id']
                
                
            
            dial = item['dialogue']
            embeddings[dial_id] = {}
            embeddings[dial_id]['turns'] = {}
            
            for turn_idx, turn in enumerate(dial):
                # pass the turns with DB results
                if turn_idx ==0:continue
                if turn_idx == len(dial)-1:continue
                for use in use_list:
                    if turn['act'].count(use) ==1:
                        continue
                    
                    
                user_emb= get_embedding(turn['user'],embedding_model)
                st_user_emb = get_embedding(turn['st_user'],embedding_model)
                resp_emb = get_embedding(turn['resp'],embedding_model)
                st_resp_emb = get_embedding(turn['st_resp'],embedding_model)
                distance_user = np.linalg.norm(np.array(user_emb) - np.array(st_user_emb))
                distance_resp = np.linalg.norm(np.array(resp_emb) - np.array(st_resp_emb))
                embeddings[dial_id]['turns'][turn_idx] = {
                    'user': user_emb,
                    'st_user': st_user_emb,
                    'resp': resp_emb,
                    'st_resp': st_resp_emb,
                    'dist_user': distance_user,
                    'dist_resp': distance_resp
                }
            embeddings[dial_id]['label'] = make_label(item)
        # save as pickle
        with open(save_path, 'wb') as f:
            pickle.dump(embeddings, f, pickle.HIGHEST_PROTOCOL)
    return embeddings

def make_label(item):
    # fomality, age, emotion
    return f'{item["formality"]}_{item["age"]}_{item["image_emotion"]}'
        
def get_style_vector(embeddings, key1, key2):
    style_vector_dict={}
    for dial_id in embeddings.keys():
        dial = embeddings[dial_id]['turns']
        for idx, turn in enumerate(dial.values()):
            diff_vector = np.array(turn[key1]) - np.array(turn[key2])
            if np.isnan(diff_vector).sum()>0:
                pdb.set_trace()
            if idx == 0:
                style_vector = diff_vector
            else:
                style_vector += diff_vector
        if len(dial) == 0:continue
        # make mean of the style distance
        style_vector_dict[dial_id] = {'vector' : style_vector/len(dial), 'label' : embeddings[dial_id]['label']}
    return style_vector_dict

def as_different_fomrt(data):
    new_data = {}
    for dial in data:
        dial_id = dial['dialogue_id']
        new_data[dial_id] = dial
    return new_data
def load_dataset(data_folder, org_data):
    # load *.json files in the data_folder. need os
    import os
    jsons = [f for f in os.listdir(data_folder) if f.endswith('.json')]
    jsons = [f for f in jsons if "task2" not in f]
    if org_data == "MWOZ":
        data = {}
    elif org_data == "SGD":
        data = []
    for json_file in jsons:
        with open(f"{data_folder}/{json_file}", 'r') as f:
            new_data = json.load(f)
            if org_data == "MWOZ":
                data = {**data, **new_data}
            elif org_data == "SGD":
                data= data + new_data
    return data

if __name__ == '__main__':
    if args.org_dataset == "MWOZ":
        data_folders= [
            "PATH_TO_DIR/changed_user_sys/test_split",
            "PATH_TO_DIR/changed_user_sys/valid_split",
            "PATH_TO_DIR/changed_user_sys/train_split",
        ]
    elif args.org_dataset == "SGD":
        data_folders = [
            "PATH_TO_DIR/changed_user_sys/train",
            "PATH_TO_DIR/changed_user_sys/dev",
            "PATH_TO_DIR/changed_user_sys/test",
        ]

    
    
    
    filters = ['positive', 'negative', 'neutral', 'casual', 'formal', 'child', 'teenager', 'adult']
    
    
    for data_folder in data_folders:
        data_type = data_folder.split('/')[-1].replace('_split', '')    
        data = load_dataset(data_folder, args.org_dataset)
        
        
        pickle_path = f"./pickle_{args.org_dataset}/{data_type}_{args.user_or_sys}"
        os.makedirs('/'.join(pickle_path.split('/')[:-1]), exist_ok=True)
        data = load_dataset(data_folder, args.org_dataset)
        embeddings = make_embedding(f"{pickle_path}.pickle", data)
        
        if args.user_or_sys == "sys":
            st_vector = get_style_vector(embeddings, 'resp', 'st_resp')
        elif args.user_or_sys == "user":
            st_vector = get_style_vector(embeddings, 'user', 'st_user')

        outliers= {}
        style_dict = defaultdict(list)
        dials = defaultdict(list)
        if args.org_dataset == "SGD":
            sgd_data = as_different_fomrt(data)
        for filter in filters:
            outliers[filter] = find_outliers(st_vector, filter)
            for dial_id in outliers[filter]:
                if args.org_dataset == "MWOZ":
                    dials[filter].append(data[dial_id]['dialogue'])
                else:
                    dials[filter].append(sgd_data[dial_id]['dialogue'])
                
                
                
        
                        
        if args.org_dataset == "MWOZ":
            save_path = f"PATH_TO_DIR/cluster_fail/{data_type}_{args.user_or_sys}.json"
        elif args.org_dataset == "SGD":
            save_path = f"PATH_TO_DIR/cluster_fail/{data_type}_{args.user_or_sys}.json"
            
            
        
        # save the outlier dials
        
        
       
                
        os.makedirs('/'.join(save_path.split('/')[:-1]), exist_ok=True)
        json.dump(outliers, open(save_path, 'w'), indent=4)
        print(f"save the outliers in {save_path}")
        
        dial_save_path = save_path.replace(".json", "_dials.json")
        json.dump(dials, open(dial_save_path, 'w'), indent=4)
        print(f"save the dials in {dial_save_path}")
        