import secrets
import string

def shortcode_generator():
    characters = string.ascii_letters + string.digits
    random_string = ''.join(secrets.choice(characters) for _ in range(7))
    return random_string