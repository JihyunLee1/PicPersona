
from collections import defaultdict

from sentence_transformers import SentenceTransformer
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

# python style_filtering_strength.py --org_dataset MWOZ --user_or_sys user


def get_embedding(text, embedding_model):
    sentences = [text]
    embeddings = embedding_model.encode(sentences).tolist()[0]
    return embeddings
import numpy as np

def find_outlier(data, filter):
    """
    Identify the indices of outliers in a list of numbers using the IQR method.
    
    Parameters:
    - data: list or numpy array of numbers
    
    Returns:
    - outlier_indices: list of indices where outliers are found
    """
    # Convert data to numpy array for easier computation
    
    numbers = [item['value'] for dial_id, item in data.items() if filter in item['label']]
    dial_id = [dial_id for dial_id, item in data.items() if filter in item['label']]
    
    numbers = pd.Series(numbers)
    
    # Calculate Q1 (25th percentile) and Q3 (75th percentile)
    Q1 = numbers.quantile(0.25)
    Q3 = numbers.quantile(0.75)
    IQR = Q3 - Q1
    # Define the bounds for outliers
    lower_bound = Q1 - 2.5 * IQR
    upper_bound = Q3 + 2.5 * IQR

    # Define the bounds for detecting outliers
    lower_bound = Q1 - 2.5 * IQR
    upper_bound = Q3 + 2.5 * IQR
    
    # Identify outlier indices
    
    lower_class_outliers = numbers[(numbers < lower_bound)].index
    upper_class_outliers = numbers[(numbers > upper_bound)].index
    lower_outlier_ids = [dial_id[i] for i in lower_class_outliers]
    upper_outlier_ids = [dial_id[i] for i in upper_class_outliers]
    
    return lower_outlier_ids, upper_outlier_ids


def make_embedding(save_path, dataset):
    # if exist, load embeddings
    try:
        print(f"load embeddings from {save_path}")
        embeddings = pickle.load(open(save_path, 'rb'))
        return embeddings
    except:
        print("Embedding not in", save_path)
        use_list = ['Movies-OFFER-movie_name', 'Restaurants-OFFER-restaurant_name', 'Media-OFFER-title', 'Travel-OFFER-attraction_name']
        
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
    return f'{item["formality"]}_{item["age"]}_{item["image_emotion"]}'
        
def get_style_vector(embeddings, key):
    style_vector_dict={}
    for dial_id in embeddings.keys():
        style_distance = [turn[key] for turn_id, turn in embeddings[dial_id]['turns'].items()]
        # make mean of the style distance
        style_vector_dict[dial_id] = {'value' : np.mean(style_distance, axis=0), 'label' : embeddings[dial_id]['label']}
    return style_vector_dict


def load_dataset(data_folder, org_dataset):
    # load *.json files in the data_folder. need os
    import os
    jsons = [f for f in os.listdir(data_folder) if f.endswith('.json')]
    jsons = [f for f in jsons if "task2" not in f]
    if org_dataset == "MWOZ":
        data = {}
    elif org_dataset == "SGD":
        data = []
    for json_file in jsons:
        with open(f"{data_folder}/{json_file}", 'r') as f:
            new_data = json.load(f)
            if org_dataset == "MWOZ":
                data = {**data, **new_data}
            elif org_dataset == "SGD":
                data= data + new_data
    return data

if __name__ == '__main__':
    if args.org_dataset == "MWOZ":
        data_folders= [
            "PATH_TO_DIR/changed_user_sys/test_split",
            "PATH_TO_DIR/changed_user_sys/valid_split",
            "/PATH_TO_DIR/changed_user_sys/train_split",
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
        
        pickle_path = f"./pickle_{args.org_dataset}/{data_type}_{args.user_or_sys}"
        os.makedirs('/'.join(pickle_path.split('/')[:-1]), exist_ok=True)
        data = load_dataset(data_folder, args.org_dataset)
        embeddings = make_embedding(f"{pickle_path}.pickle", data)
        
        if args.user_or_sys == "sys":
            st_vector = get_style_vector(embeddings, 'dist_resp')
        elif args.user_or_sys == "user":
            st_vector = get_style_vector(embeddings, 'dist_user')

        outliers= {}
        style_dict = defaultdict(list)
        for filter in filters:
            lowers, uppers = find_outlier(st_vector, filter)
            outliers[filter] = {
            
                'lower' : lowers,
                'upper' : uppers
            }
            for key, value in st_vector.items():
                if filter in value['label']:
                    style_dict[filter].append(value['value'])       
                    
                         
        # save the outliers
        if args.org_dataset == "MWOZ":
            save_path = f"PATH_TO_DIR/filtered/style_fail/{data_type}_{args.user_or_sys}.json"
        elif args.org_dataset == "SGD":
            save_path = f"PATH_TO_DIR/filtered/style_fail/{data_type}_{args.user_or_sys}.json"
                
                
        os.makedirs('/'.join(save_path.split('/')[:-1]), exist_ok=True)
        json.dump(outliers, open(save_path, 'w'), indent=4)
        print(f"save the outliers in {save_path}")

