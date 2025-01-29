import json
import os
import argparse
from utils import parsing_batch_result, basic_cleaning
parser = argparse.ArgumentParser()
parser.add_argument('--data_type', type=str, default="test")
parser.add_argument('--split_idx', type=int)
parser.add_argument('--org_dataset', type=str, required=True)
parser.add_argument('--use_list', type=str)
args = parser.parse_args()

# python sys_pp.py --data_type train --split_idx 1 --org_dataset MWOZ
 

    
if __name__ == "__main__":
    if args.org_dataset == "MWOZ":
        org_dataset = f"PATH_TO_DIR/dataset/mwoz/{args.data_type}_split/{args.split_idx}.json"
    
    elif args.org_dataset == "SGD":
        org_dataset = f"PATH_TO_DIR/dataset/SGD/{args.data_type}/{args.split_idx}.json"
  
    batch_path= f"PATH_TO_DIR/batch_output/{args.org_dataset}/sys_{args.data_type}_split/{args.split_idx}.jsonl"
    save_path = org_dataset.replace("changed_user", "changed_user_sys")
    
    if args.use_list:
        use_list = json.load(open(args.use_list))
        post_fix = args.use_list.split("/")[-1].replace(".json", "")
        batch_path = f"PATH_TO_DIR/batch_output/{args.org_dataset}/sys_{args.data_type}_split/{args.split_idx}.jsonl"
        batch_path = batch_path.replace(".jsonl", f"_{post_fix}.jsonl")
        save_path = save_path.replace(".json", f"_{post_fix}.json")
    
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    batch_result = parsing_batch_result(batch_path)
    dataset = json.load(open(org_dataset))
    
    payloads = []
    new_data = {}
    for item in dataset:
            
        if args.org_dataset == "MWOZ":
            dial = dataset[item]['dialogue']
            item = dataset[item]
            dial_id = item['dialogue'][0]['dial_id']
        elif args.org_dataset == "SGD":
            dial = item['dialogue']
            dial_id = item['dialogue_id']
            
        if args.use_list and dial_id not in use_list: continue
            
        for turn_idx, turn in enumerate(dial):
            try:    
                custom_id = f"{turn['dial_id']}_{turn_idx}"
                styled_text = basic_cleaning(batch_result[custom_id])
                turn['st_resp'] =styled_text
            except:
                print("Error at ", custom_id)
                turn['st_resp'] = turn['resp']
        new_data[dial_id] = item
    
    # save in original dataset

    with open(save_path, "w") as f:
        json.dump(new_data, f, indent=4)
    print("Saved in ", save_path)
    
        
   