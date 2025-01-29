import textstat
from tqdm import tqdm
import json


def how_many_years(text):
    return textstat.gunning_fog(text)

def is_in_class(item, key_words):
    if key_words == 'all':
        return True
    else:
        c1,c2 = key_words.split('-')
        if item[c1] == c2:
            return True
    return False


if __name__ == "__main__":
    dial_path = "PATH_TO_DIR/dataset/mwoz_sgd/train.json"
    dial_data = json.load(open(dial_path))
    
    
    classes =['all', 'age-senior', 'age-child', 'formality-formal','formality-casual']
    
    for class_type in classes:
        polite =0 
        in_class_cnt = 0
        years = []
        for  dial_id in dial_data:
            item = dial_data[dial_id]
            if is_in_class(item, class_type):
                in_class_cnt +=1
                if in_class_cnt>3000:
                    break
                dial = dial_data[dial_id]['dialogue']
                for turn in dial:
                    # ID should be uniq
                    years.append(how_many_years(turn['st_resp']))
        
        print("class : ", class_type)
        print("in class cnt : ", in_class_cnt)
        print("Number of years: ", round(sum(years)/len(years),2))


                    