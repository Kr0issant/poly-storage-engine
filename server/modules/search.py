import json

class Search():
    def __init__(self):
        self.keys :list
        with open("modules/classification.json", "r") as file:
            self.keys = json.load(file).keys()
        
    def get_keywords_from_query(self, query:str):  
        key_list = []
        for x in query.split(" "):
            lowercase = x.lower()
            if lowercase in self.keys:
                key_list.append(x)
        return key_list
    def sort_by_score(self, search_results, query_list):
        return sorted(search_results, key=lambda result: self.added_scores(result, query_list), reverse=True)
    
    def added_scores(self, element, query_list):
        sum = 0
        for x in range(0,3):
            if element["metadata"]["keywords"][x]["label"] in query_list:
                sum = element["metadata"]["keywords"][x]["score"]
        return sum


    def shorten_data(search_results, query):
        directory_list = []
        for result in search_results:
            element = {
                "title":result["filename"],
                "url":f"/search/{element["_id"]}"
            }
            directory_list.append(element)
        return {
            "title": f"Search - {query}",
            "list":directory_list
        }


    
print(Search().get_keywords_from_query(query="I need a photo of a sky and a lake"))