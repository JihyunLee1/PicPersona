import jsonlines

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
parser.add_argument("--data_path", type=str, required=True, help = "path to LLM output")
args = parser.parse_args()



def parsing_batch_result1(file_path):
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
    result = []
    cnt1, cnt2, cnt3 = 0, 0, 0
    for key in data.keys():
        data_ = data[key].lower().replace(" ","").replace("*","")
        if 'winner:system1' in data_:
            result.append([1,0,0])
            cnt1 += 1
        elif 'winner:system2' in data_:
            result.append([0,0,1])
            cnt3 += 1
        else:
            result.append([0,1,0])
            cnt2 += 1
    print("System1: ", cnt1)
    print("Draw: ", cnt2)
    print("System2: ", cnt3)
    
    return result


def parsing_batch_result2(file_path, org_dataset):
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
    result = []

    types = {
        'age':['senior', 'adult', 'child'],
        'image_emotion':['positive', 'negative', 'neutral'],
        'formality':['casual', 'formal'],
    }
    
    for class_type in types.keys():
        for class_ in types[class_type]:
            cnt1, cnt2, cnt3 = 0, 0, 0
            for key in data.keys():
                dataset = org_dataset[key]
                if dataset[class_type] == class_ or (dataset[class_type]=='teenager' and class_ == 'child'):
                    data_ = data[key].lower().replace(" ","").replace("*","")
                    if 'winner:system1' in data_:
                        cnt1 +=1
                    elif 'winner:system2' in data_:
                        cnt3+=1
                    else:
                        cnt2+=1
            case_sum = cnt1+cnt2+cnt3
        
            print(class_type, class_)
            if case_sum == 0:
                print("No data")
            else:
                print("number of data: ", case_sum)
                print("sys1, tie, sys2: ", 
                        round(cnt1*100/case_sum,2), round(cnt2*100/case_sum,2),
                        round(cnt3*100/case_sum,2)
                        )
            
    return result
    
    
    

if __name__ == "__main__":
    args = parser.parse_args()
    dataset = json.load(open(args.data_path))
    prefix = args.data_path.split("/")[-1].replace(".json", "")     

    llm_result_path = f"PATH_TO_DIR/evaluation_with_LLM/batch_output/{prefix}.jsonl"
    llm_result1 = parsing_batch_result1(llm_result_path)
    llm_result2 = parsing_batch_result2(llm_result_path, dataset)
    
    save_path1 = "./parsed_result/Task2_"+prefix+".json"
    save_path2 = "./parsed_result/Task2_"+prefix+"_2.json"
    
    
    # save the result
    with open(save_path1, "w") as f:
        json.dump(llm_result1, f)
    print("Saved the result at ", save_path1)
    
    
    with open(save_path2, "w") as f:
        json.dump(llm_result2, f)
    print("Saved the result at ", save_path2)
    # for item in llm_result:
    #     print(item)
    
