import requests
import json
import pdb


def get_review(restaurant_name = 'Roaming Buffalo Bar-B-Que'):
    
    ### Get the place_id of the restaurant
    try:
        params1 = {
        'api_key': '',
        'search_type': 'places',
        'q': restaurant_name,
        }
        
        api_result = requests.get('https://api.scaleserp.com/search', params1).json()
        place_cid = api_result['places_results'][0]['data_cid'] #0x876c7e3a0ba4ad01:0x2b4cae2da597326a
        
        params2 = {
        'api_key': '',
        'search_type': 'place_details',
        'data_cid': place_cid
        }
        
        api_result = requests.get('https://api.scaleserp.com/search', params2).json()
        place_id = api_result['place_details']['data_id']

        # Get the reviews of the restaurant
        params3 = {
        'api_key': '',
        'search_type': 'place_reviews',
        'data_id': place_id,
        }

        # make the http GET request to Scale SERP
        reviews = []
        api_result = requests.get('https://api.scaleserp.com/search', params3).json()
        for review_raw in api_result['place_reviews_results'][:10]:
            review_text = review_raw['body']
            review_rating = review_raw['rating']
            if int(review_rating) >= 3:
                reviews.append({'review_text': review_text, 'review_rating': review_rating})
    except Exception as e:
        print("ERROR", e)
        reviews = []
    return reviews

if __name__ == '__main__':
    print(get_review())
