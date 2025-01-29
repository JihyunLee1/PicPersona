import jsonlines
from collections import Counter
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


import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--llm_result", type=str, default='', help="path to the LLM output")
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
    result = {}
    result2 = []
    for key in data.keys():
        temp = []
        item = data[key]
        item = item.replace(" ","")
        for q in ['Q1', 'Q2', 'Q3', 'Q4', 'Q5']:
            for score in [1,2,3,4]:
                if q+":"+str(score) in item:
                    result2.append(score)
                    temp.append(score)
        if len(temp) != 5:
            temp = [3,3,3,3,3]
        result[key] = temp
    
    
    return result, result2
    
    
def get_average(data):
    concat = []
    for key in data.keys():
        concat += data[key]
    for i in range(5):
        print("Average of Q{}: {}".format(i+1, sum([x[i] for x in data.values()])/len(data.values())))
        print(Counter([x[i] for x in data.values()]))
        

        
if __name__ == "__main__":
    args = parser.parse_args()

    llm_result = args.llm_result
    llm_result1, llm_result2 = parsing_batch_result(llm_result)
    
    
    # save the result
    data_name = llm_result.split("/")[-1].replace(".jsonl", "")
    
    save_path1 = f"parsed_result/{data_name}.json"
    save_path2 = f"parsed_result/{data_name}_diff_format.json"

    
    with open(save_path1, "w") as f:
        json.dump(llm_result1, f, indent=4)
    print("Save in ", save_path1)
    get_average(llm_result1)
    
    
    with open(save_path2, "w") as f:
        json.dump(llm_result2, f, indent=4)
    print("Save in ", save_path2)
    
