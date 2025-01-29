import json
import pdb
import os

# 
if __name__ == "__main__":
    files = ['./for_testing_general/Buses.json',
            './for_testing_general/Homes.json',
            './for_testing_general/Movies.json',
            './to_change/train.json',
            './to_change/test.json',
            './to_change/dev.json']

    for file_path in files:
        # split the dialogues into 100 dialogues per file
        data = json.load(open(file_path))
        save_dir = file_path.replace('.json', '')
        os.makedirs(save_dir, exist_ok=True)
        
        for i in range(0, len(data), 100):
            save_path = os.path.join(save_dir, f'{int(i/100)+1}.json')
            with open(save_path, 'w') as f:
                json.dump(data[i:i+100], f, indent=4)
            print('saved to', save_path)
        