import jsonlines
import pdb

def parsing_batch_result(file_path):
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
    return data

def basic_cleaning(text):
    text = text.replace("\n", " ")
    text = text.replace("\t", " ")
    text = text.replace("\r", " ")
    text = text.replace("  ", " ")
    text = text.strip()
    return text