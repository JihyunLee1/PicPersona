import json
import os
import argparse
from utils import parsing_batch_result, basic_cleaning
parser = argparse.ArgumentParser()
parser.add_argument('--data_type', type=str, default="test")
parser.add_argument('--split_idx', type=int)
parser.add_argument('--org_dataset', type=str, default="SGD")

args = parser.parse_args()

# python user_pp.py --data_type train --split_idx 1
 
# python user_pp.py --data_type train --split_idx 1 --org_dataset MWOZ
    
if __name__ == "__main__":

    if args.org_dataset == "MWOZ":
        org_dataset = f"PATH_TO_DIR/dataset/mwoz/{args.data_type}_split/{args.split_idx}.json"
        save_path = org_dataset.replace("processed", "changed_user")
    elif args.org_dataset == "SGD":
        org_dataset = f"PATH_TO_DIR/dataset/SGD/{args.data_type}/{args.split_idx}.json"
        save_path = org_dataset.replace("to_change", "changed_user")
        
        
    batch_path = f"PATH_TO_DIR/batch_output/{args.org_dataset}/user_{args.data_type}_split/{args.split_idx}.jsonl"
    
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    batch_result = parsing_batch_result(batch_path)
    dataset = json.load(open(org_dataset))
    
    payloads = []
    for item in dataset:
        
        if args.org_dataset == "MWOZ":
            dial = dataset[item]['dialogue']
            item = dataset[item]
            
        elif args.org_dataset == "SGD":
            dial = item['dialogue']
            
            
        for turn_idx, turn in enumerate(dial):
            try:    
                custom_id = f"{turn['dial_id']}_{turn_idx}"
                styled_text = basic_cleaning(batch_result[custom_id])
                turn['st_user'] =styled_text
            except:
                print("Error at ", custom_id)
                turn['st_user'] = turn['user']
    
    # save in original dataset

    with open(save_path, "w") as f:
        json.dump(dataset, f, indent=4)
    print("Saved in ", save_path)
        
   