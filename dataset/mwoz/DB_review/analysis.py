
import pdb
import json


files = ['attractions.json', 'hotels.json', 'restaurants.json']

for file_name in files:
    data = json.load(open(file_name))
    num_reviews = 0
    item_nums = 0
    for key in data:
        if data[key]['online']:
            num_reviews += len(data[key]['online'])
            item_nums += 1
    print(f'{file_name}: {num_reviews}')
    print(f"Item nums: {item_nums}")