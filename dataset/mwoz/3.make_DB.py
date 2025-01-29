import json
import pdb
import os
from utils import wiki_search, serp_review
import time
from tqdm import tqdm

def is_redundant(name, items):
    for item in items:
        if item == name:
            return True
    return False


def data_cleaning(dataset):
    clean_data = {}
    for data in dataset:
        value = data['name']
        if 'category' in data:
            clean_data[value] = {'category': data}
        else:
            clean_data[value] = {}
        
    return clean_data




def add_wiki(items, save_folder, save_path):
    if os.path.exists(os.path.join(save_folder, save_path)):
        previous = json.load(open(os.path.join(save_folder, save_path)))
    else:
        previous = None
    
    for key in items:
        # sleep 1 second
        if 'online' in items[key] : continue
        if previous and key in previous:
            items[key]['online'] = previous[key]['online']
            continue
        time.sleep(1)
        name = key
        search_result = wiki_search.search_wiki(name)
    
        items[key]['online'] = search_result
        print(items[key])
        json.dump(items, open(os.path.join(save_folder, save_path), 'w'), indent=4)
    return items

def add_review(items, save_folder, save_path):
    if os.path.exists(os.path.join(save_folder, save_path)):
        previous = json.load(open(os.path.join(save_folder, save_path)))
    else:
        previous = None
                      
    for key in tqdm(items):
        
        if previous and key in previous and 'online' in previous[key]:
            items[key]['online'] = previous[key]['online']
            print("copy the previous", key)
            print("Already Have. Continue")
        else:    
            if previous and key in previous and 'name2' in previous[key]:
                print(f"If {key} is not in their, Try name2", previous[key]['name2'])
                items[key]['name2'] = previous[key]['name2']
                
            

            search_result = serp_review.get_review(key)
            if len(search_result) == 0 and 'name2' in items[key]:
                print("try", items[key]['name2'])
                search_result = serp_review.get_review(items[key]['name2'])
            items[key]['online'] = search_result
        
        json.dump(items, open(os.path.join(save_folder, save_path), 'w'), indent=4)
        
    return items



if __name__ == "__main__":
    files = ['PATH_TO_DIR/dataset/mwoz/DB/attraction_db_processed.json',
            'PATH_TO_DIR/mwoz/DB/hotel_db_processed.json',
            'PATH_TO_DIR/mwoz/DB/restaurant_db_processed.json',]

    attractions = data_cleaning(json.load(open(files[0])))
    hotels = data_cleaning(json.load(open(files[1])))
    restaurants = data_cleaning(json.load(open(files[2])))
    
    print("Attractions: ", len(attractions)) # wiki
    print("Hotels: ", len(hotels)) # serp
    print("Restaurants: ", len(restaurants)) # serp
    
    save_folder = "./DB_review"
    os.makedirs(save_folder, exist_ok=True)

    # restaurants = add_review(restaurants, save_folder, 'restaurants.json') 
    hotels = add_review(hotels, save_folder, 'hotels.json')
    # attractions = add_wiki(attractions, save_folder, 'attractions.json')  
    
    # json.dump(attractions, open(os.path.join(save_folder, 'attractions.json'), 'w'), indent=4)