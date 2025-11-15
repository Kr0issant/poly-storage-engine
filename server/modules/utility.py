import string, random
def random_id_generator(length: int = 8):
    characters = string.ascii_letters + string.digits
    return "".join(random.choices(characters, k=length))