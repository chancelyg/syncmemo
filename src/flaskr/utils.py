import random
from flask import jsonify

def build_verify_code(length: int,just_uppercase:False):
    verify_code = ""
    while length > 0:
        num = random.randint(0, 9)
        if just_uppercase:
            s = str(random.choice([num, chr(random.randint(65, 90))]))
        if not just_uppercase:
            s = str(random.choice([num, chr(random.randint(65, 90)), chr(random.randint(97, 122))]))
        verify_code += s
        length -= 1
    return verify_code

def api_response(success: bool = True, data: dict = {}, message: str = None):
    """ 返回的API Response 包装"""
    return jsonify({'data': data, 'success': success, 'message': message})
