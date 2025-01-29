# Add emotion to the raw data using sentiment analysis model
from transformers import pipeline
import json
import pdb
from tqdm import tqdm
import os
model_path  ="cardiffnlp/twitter-roberta-base-sentiment-latest"




sentiment_task = pipeline("sentiment-analysis", model=model_path, tokenizer=model_path, device=2)
# print(sentiment_task("Covid cases are increasing fast!"))



def raw_with_emotion(file_path):
    data = json.load(open(file_path, 'r'))
    for dialog in tqdm(data):
        for turn_id, turn in enumerate(dialog['turns']):
            if turn_id %2 ==0:
                turn['emotion'] = sentiment_task(turn['utterance'])[0]['label']
    return data


if __name__ == '__main__':
    for i in range(1,35 ):
        file_path = f"PATH_TO_DIR/SGD/raw/test/dialogues_{str(i).zfill(3)}.json"
        save_path = file_path.replace("raw", "raw_emotion")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        result = raw_with_emotion(file_path)
        json.dump(result, open(save_path, 'w'), indent=2)
        print("saved", save_path)
        
        
        