# Add image to dataset
import json
import pdb
import random
from collections import Counter



def get_statics(images):
    demo_data = json.load(open('PATH_TO_DIR/dataset/face/demo.json'))
    formality = []
    emotion = []
    age = []
    
    for image in images:
        value = demo_data[image].lower()
        if 'casual' in value:
            formality.append('casual')
        elif 'formal' in value:
            formality.append('formal')
            
        if 'positive' in value:
            emotion.append('positive')
        elif 'neutral' in value:
            emotion.append('neutral')
        elif 'negative' in value:
            emotion.append('negative')
            
        # ages : toddler, child, teenager, adult, senior 
        if 'toddler' in value:
            age.append('toddler')
        elif 'child' in value:
            age.append('child')
        elif 'teenager' in value:
            age.append('teenager')
        elif 'adult' in value:
            age.append('adult')
        elif 'senior' in value:
            age.append('senior')
    result = Counter(formality), Counter(emotion), Counter(age)
    return result


if __name__ == "__main__":
    files = ['./for_testing_general/Buses_noimg.json',
            './for_testing_general/Homes_noimg.json',
            './for_testing_general/Movies_noimg.json',
            './to_change/train_noimg.json',
            './to_change/test_noimg.json',
            './to_change/dev_noimg.json']


    images = json.load(open('PATH_TO_DIR/face/emotion_split.json'))

    for file_path in files:
        data = json.load(open(file_path))
        save_path = file_path.replace('_noimg', '_nodemo')
        for item in data:
            dial_emotion = item['emotion']
            if dial_emotion == 'positive':
                pool = images['positive']
            elif dial_emotion == 'neutral':
                pool = images['neutral']
            elif dial_emotion == 'negative':
                pool = images['negative'] + images['neutral']
            else:
                print('error')
                raise ValueError
            random_image = random.choice(pool)
            item['image'] = random_image
            
                        
        # save the data to the save_path
        print('file_path', file_path)
        statics_result = get_statics([item['image'] for item in data])
        print('statics_result', statics_result)
        json.dump(data, open(save_path, 'w'), indent=4)
        print('saved to', save_path)
        
            
            


            