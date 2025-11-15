import random, string

def random_id_generator(length: int = 8):
    characters = string.ascii_letters + string.digits
    return "".join(random.choices(characters, k=length))

def avg_predictions(predictions):
    category_scores = dict()
    size = len(predictions)
    for i in range(len(predictions)):
        for j in predictions[i]:
            label = j["label"]
            score = j["score"]
            
            category_scores[label] = category_scores.get(label, 0.0) + score

    avg_p = []
    for label, total_score in category_scores.items():
        average_score = total_score / size
        avg_p.append({"label": label, "score": average_score})

    avg_p = sorted(
        avg_p, 
        key=lambda d: d["score"], 
        reverse=True
    )
    return avg_p[:3]

def get_unduplicated_name(options: list, file_name: str, separate_extension: bool = False):
    if separate_extension:
        file_name = "".join(file_name.split(".")[:-1])
        
    duplicate_names = 0
    
    while True:
        name = file_name + (f"_{duplicate_names}" * (0 if duplicate_names == 0 else 1))

        if name in options:
            duplicate_names += 1
        else:
            break

    return name

def clean_list_to_str(keys: list):
    return ", ".join([f'"{keys}"' for key in keys])
    
def clean_vales_to_str(data: dict, keys: list):
    values = ""
    for key in keys:
        value = data[key]
        if isinstance(value, str):
            value = f'"{value}"'
        values.append(f"{data[key]}")
    
    return ", ".join(values)