# make as json file

import jsonlines
import pdb
import json
import pdb
import json
import pdb

import os

import argparse


parser = argparse.ArgumentParser()
parser.add_argument('--data_index', type=str)
args = parser.parse_args()

def parsing_batch_result(file_path):
    # read jsonl file
    data = {}
    lines = []
    # read jsonl file
    with jsonlines.open(file_path) as reader:
        for obj in reader:
            lines.append(obj)
        
    for line in lines:
        try:
            custom_id = line["custom_id"]
            response = line['response']['body']['choices'][0]['message']['content']
            data[custom_id] = response
        except:
            pdb.set_trace()
    return data




if __name__ == "__main__":
    save_result = f"PATH_TO_DIR/batch_output/neg_neu_pos/{args.data_index}.jsonl"
    save_path = f"PATH_TO_DIR/face/{args.data_index}.json"

    data = parsing_batch_result(save_result)

    new_data = {}
    for key, value in data.items():
        new_data[key] = value.replace("\n", " ")
    
    with open(save_path, 'w') as f:
        json.dump(new_data, f, indent=4)
    print(f"Saved to {save_path}")
    
    
    