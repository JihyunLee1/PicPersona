import pdb
from convokit import PolitenessStrategies, Corpus, Utterance, Speaker, TextParser
import json
# Define the speakers
speaker_a = Speaker(id="A")
from tqdm import tqdm


politeness_analyzer = PolitenessStrategies()

def is_polite(politeness_strategies):
    # Sum the values of the politeness features
    politeness_score = sum(politeness_strategies.values())
    # Define a simple threshold for politeness
    return  politeness_score/len(politeness_strategies)



def is_in_class(item, key_words):
    if key_words == 'all':
        return True
    else:
        c1,c2 = key_words.split('-')
        if item[c1] == c2:
            return True
    return False


if __name__ == "__main__":
    dial_path = "PATH_TO_DIR/friendly/dataset/mwoz_sgd/train.json"
    dial_data = json.load(open(dial_path))
    
    all_document, greeting_document, goodbye_document = "", "", ""
    all_word_level, greeting_word_level, goodbye_word_level = 0, 0, 0
    all_cnt, greeting_cnt, goodbye_cnt = 0, 0, 0
    

    
    classes =['all', 'age-senior', 'age-child', 'formality-formal','formality-casual']
    
    for class_type in classes:
        polite =0 
        in_class_cnt = 0
        utterances = []
        for  dial_id in dial_data:
            item = dial_data[dial_id]
            if is_in_class(item, class_type):
                in_class_cnt +=1
                if in_class_cnt>3000:
                    break
                dial = dial_data[dial_id]['dialogue']
                for turn in dial:
                    # ID should be uniq
                    utterances.append(Utterance(id=str(in_class_cnt), speaker=speaker_a, text=turn['st_resp']))
        
        print("class : ", class_type)
        print("in class cnt : ", in_class_cnt)
        corpus = Corpus(utterances=utterances)
                
        # Load the SpaCy-based TextParser
        parser = TextParser()
        corpus = parser.transform(corpus)
        corpus = politeness_analyzer.transform(corpus)
        
        for utt in corpus.iter_utterances():
            polite += is_polite(utt.meta['politeness_strategies'])
        
        print("polite score : ",  round(polite*100/in_class_cnt, 2))
        print()

                    