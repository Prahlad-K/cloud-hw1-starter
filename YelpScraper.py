import requests
import json
from string import Template
cuisines = ["Indian","Chinese","Thai","Italian","Japanese","Mediterranean"]

netResult = []
restrauntId = set()
baseUrl = '''https://api.yelp.com/v3/businesses/search?term=$term&location=NY&offset=$index '''


def processResults(results,arr):
    try:
        for res in results["businesses"]:
            try:
                bid  = res["id"]
            except:
                bid = ""

            try:
                name  = res["name"]
            except:
                name = ""

            try:
                address  = res["location"]
            except:
                address = {}


            try:
                coord  = res["coordinates"]
            except:
                coord = {}

            try:
                review_count  = res["review_count"]
            except:
                review_count = 0


            try:
                rating  = res["rating"]
            except:
                rating = 0         

            entry  =  {"bid":bid,"rating":rating, "reviews":review_count,"coordinates":coord,"name":name,"address":address}
            
            if bid not in restrauntId:
                arr.append(entry)
                restrauntId.add(bid)
            else:
                continue

    except:
        return 

headers = { 'Authorization': 'Bearer o2NCvV8w1vRyxXnFHnK2YZ4uT89oObOYQLpv2-prrgZuIcuAxVzJ-kO9kwvZnD2RMy0O27z_StHJrq0cqcjrbkmSBz8EC0lIiY_2P4P5Fy6J7NcKz3Yj1MF4OWf2Y3Yx'}

for cuisine in cuisines:

    cusineResult = []
    index = 0
    prevCount = 0
    while len(cusineResult)<1000 and index<1200:
        baseURLTemplate = Template(baseUrl)
        results = requests.get(baseURLTemplate.substitute(term=cuisine+" food",index=len(cusineResult)),headers = headers)
        resultsData = results.json()    
        processResults(resultsData,cusineResult)
        print("Cuisine:",cuisine," iter:",index," Processed Items:",len(cusineResult))
        index+=1
        
    
    with open(cuisine+".json",'w') as f:
        json.dump(cusineResult,f)

    
                               
