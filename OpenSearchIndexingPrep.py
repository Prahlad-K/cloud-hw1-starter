import json
cusineType = ["Indian","Chinese","Italian","Japanese","Thai","Mediterranean"]

base = {"index": {"_index": "restaurant","_id": 1}}
index = 1
with open("IndexedData.json",'a') as f:

    for cusine in cusineType:
        with open(cusine+'.json') as file:
            file_contents = json.load(file)
        
        for entry in file_contents:
            base['index']['_id'] = index
            index+=1
            json.dump(base,f)
            #print(entry)
            f.write('\n')
            json.dump({"RestaurantID":entry["bid"],"Cuisine":cusine},f)
            f.write('\n')


MASTER_NODE =  "master"
MASTER_PASSWORD = "Random#123"
DOMAIN_ENDPOINT = "https://search-opensearch-bm76vifk5cwboacjwiduj6p6bm.us-east-1.es.amazonaws.com/"
JSON_FILENAME = "IndexedData.json"

!curl -XPOST -u [MASTER_NAME]:[MASTER_PASSWORD] [DOMAIN_ENDPOINT]/_bulk --data-binary @[JSON_FILENAME] -H 'Content-Type: application/json'