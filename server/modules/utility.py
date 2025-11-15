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