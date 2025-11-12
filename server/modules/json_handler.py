class JSONHandler():
    def __init__(self):
        pass

    def get_json_by_query(self, query):
        pass

    def get_json_storage(self, collection):
        pass
    
    def generate_schema(self, obj):
        if not isinstance(obj, dict):
            return type(obj).__name__

        schema = {}
        for key, value in obj.items():
            type_name = type(value).__name__

            if type_name == 'dict':
                schema[key] = self.generate_schema(value) 
            elif type_name == 'list':
                if value: 
                    schema[key] = [self.generate_schema(value[0])]
                else:
                    schema[key] = 'list (empty)'
            else:
                schema[key] = type_name

        
        return schema