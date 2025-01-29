# Generate related DB for the dataset
import json
import pdb
import os
from utils import wiki_search, serp_review
import time
from tqdm import tqdm
# add SERP results to the dataset


def is_redundant(name, items):
    for item in items:
        if item == name:
            return True
    return False

def add_to_restaurants(act_dict, value):
    
    city = act_dict['Restaurants-OFFER-city'][0] if 'Restaurants-OFFER-city' in act_dict else None
    item = {'name': value,
            'city': city}
    return item


def add_to_travel(act_dict, value):
    category = act_dict['Travel-OFFER-category'] if 'Travel-OFFER-category' in act_dict else None
    item = {'name': value,
            'category': category[0]}
    return item

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

    
def examine_total(files, use_list):
    movies = {}
    restaurants = {}
    travels = {}
    for file_path in files:
        data = json.load(open(file_path))
        for item in data:
            for turn in item['dialogue']:
                act_dict = act_as_dict(turn['act']) # remove redundant here
                for use in use_list:
                    if use in act_dict:
                        values = act_dict[use]
                        for value in values:
                            if use == 'Movies-OFFER-movie_name' or use == 'Media-OFFER-title':
                                if is_redundant(value, movies):
                                    continue
                                movies[value] = {}
                            elif use == 'Restaurants-OFFER-restaurant_name':
                                if is_redundant(value, restaurants):
                                    continue
                                restaurants[value] = {'city': act_dict['Restaurants-OFFER-city'][0] if 'Restaurants-OFFER-city' in act_dict else None}
                            elif use == 'Travel-OFFER-attraction_name':
                                if is_redundant(value, travels):
                                    continue
                                travels[value] = {'category': act_dict['Travel-OFFER-category'][0] if 'Travel-OFFER-category' in act_dict else None}
    return movies, restaurants, travels



def add_wiki(items, save_folder, save_path):
    previous = json.load(open(os.path.join(save_folder, save_path.replace('.json', '_v1_dict.json'))))
    
    for key in items:
        # sleep 1 second
        if 'online' in items[key] : continue
        if key in previous:
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
        items = json.load(open(os.path.join(save_folder, save_path)))
    previous = json.load(open(os.path.join(save_folder, save_path.replace('.json', '_v1_dict.json'))))
                      
    for key in tqdm(items):
        if 'online' in  items[key] : continue
        if key in previous:
            items[key]['online'] = previous[key]
            continue
        
        name = key
        search_result = serp_review.get_review(name)
        items[key]['online'] = search_result
        print(items[key])
        
        json.dump(items, open(os.path.join(save_folder, save_path), 'w'), indent=4)
        
    return items



if __name__ == "__main__":
    files = ['./for_testing_general/Buses.json',
            './for_testing_general/Homes.json',
            './for_testing_general/Movies.json',
            './to_change/train.json',
            './to_change/test.json',
            './to_change/dev.json']

    use_list = ['Movies-OFFER-movie_name', 'Restaurants-OFFER-restaurant_name', 'Media-OFFER-title', 'Travel-OFFER-attraction_name']
    movies, restaurants, travels = examine_total(files, use_list)
    print('movies:', len(movies))
    print('restaurants:', len(restaurants))
    print('travels:', len(travels))
    save_folder = "./DB"
    os.makedirs(save_folder, exist_ok=True)