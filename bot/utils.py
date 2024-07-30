import random
import string

def generate_unique_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

report_data = {}
suggestion_data = {}
