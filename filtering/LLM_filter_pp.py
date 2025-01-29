import json
import os
import argparse
from utils import parsing_batch_result, basic_cleaning
parser = argparse.ArgumentParser()
parser.add_argument('--data_type', type=str, default="test")
parser.add_argument('--filter_type', type=str, default = "acc")
parser.add_argument('--original_data', type=str, default = "SGD")

args = parser.parse_args()

# python LLM_filter_pp.py --data_type train --split_idx 1
 


def load_results(dir):
    # load path jsonl files in the directory
    files = os.listdir(dir) 
    files = [f for f in files if f.endswith(".jsonl")]
    print(f"Load {len(files)} files from {dir}")
    return files
    
        
if __name__ == "__main__":
    # Not use split, use all
    if args.original_data == "SGD":
        save_path = "PATH_TO_DIR/filtered"
        fail_save_path = f"{save_path}/LLM_{args.filter_type}_fail/{args.data_type}.json"
    elif args.original_data == "MWOZ":
        save_path = "PATH_TO_DIR/filtered"
        fail_save_path = f"{save_path}/LLM_{args.filter_type}_fail/{args.data_type}.json"
        
        
    batch_dir = f"PATH_TO_DIR/batch_result/{args.original_data}_filtering_{args.data_type}_split/{args.filter_type}"
    batch_files = load_results(batch_dir)
    os.makedirs(os.path.dirname(fail_save_path), exist_ok=True)
    
    
    fail_dial = []
    for batch_file in batch_files:
        batch_result_ = parsing_batch_result(f"{batch_dir}/{batch_file}")
        for key in batch_result_:
            line_result = batch_result_[key]
            if ': fail' in line_result:
                fail_dial.append(key)

    # save fail_dial
    
    with open(fail_save_path, 'w') as f:
        json.dump(fail_dial, f, indent=4)
        
    print(f"Fail dial saved at {fail_save_path}")
    print(f"Fail dial count: {len(fail_dial)}")