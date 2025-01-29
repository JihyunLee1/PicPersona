# Add demographic information to the dataset
import json
import pdb
import os

FI_data = json.load(open('PATH_TO_DIR/dataset/face/FI.json'))
demo_data = json.load(open('PATH_TO_DIR/dataset/face/demo.json'))


if __name__ == "__main__":
    files = ['./for_testing_general/Buses_nodemo.json',
            './for_testing_general/Homes_nodemo.json',
            './for_testing_general/Movies_nodemo.json',
            './to_change/train_nodemo.json',
            './to_change/test_nodemo.json',
            './to_change/dev_nodemo.json']

    for file_path in files:
        # split the dialogues into 100 dialogues per file
        data = json.load(open(file_path))
        for item in data:
            image = item['image']
            item['FI'] = FI_data[image]
            
            demo = demo_data[image].lower()
            if 'casual' in demo:
                item['formality'] = 'casual'
            elif 'formal' in demo:
                item['formality'] = 'formal'
            else:
                item['formality'] = 'unknown'
                
            if 'positive' in demo:
                item['image_emotion'] = 'positive'
            elif 'neutral' in demo:
                item['image_emotion'] = 'neutral'
            elif 'negative' in demo:
                item['image_emotion'] = 'negative'
            else:
                item['image_emotion'] = 'unknown'
                
            # ages : toddler, child, teenager, adult, senior 
            if 'toddler' in demo:
                item['age'] = 'toddler'
            elif 'child' in demo:
                item['age'] = 'child'
            elif 'teenager' in demo:
                item['age'] = 'teenager'
            elif 'adult' in demo:
                item['age'] = 'adult'
            elif 'senior' in demo:
                item['age'] = 'senior'
            else:
                item['age'] = 'unknown'
                
                
            # gender
            if 'female' in demo:
                item['gender'] = 'female'
            else:
                item['gender'] = 'male'


        save_path = file_path.replace('_nodemo', '')
        # save it
        json.dump(data, open(save_path, 'w'), indent=4)
        print('saved to', save_path)
            
        