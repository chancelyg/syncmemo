import random
import qrcode
import base64
from io import BytesIO
from flask import jsonify


def build_verify_code(length: int, just_uppercase: False):
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


def build_qrcode(content: str, box_size: int = 4):
    """使用字符串生成二维码

    Args:
        content (str): 字符串
        box_size (int, optional): 二维码大小. Defaults to 4.

    Returns:
        str: 返回base64
    """
    qr = qrcode.QRCode(box_size=box_size)
    qr.add_data(content)
    qr.make()
    qr_code_image = qr.make_image()
    buffered = BytesIO()
    qr_code_image.save(buffered)
    return base64.b64encode(buffered.getvalue()).decode()
