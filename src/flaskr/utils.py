import random
import qrcode
import base64
from random import choice
from io import BytesIO
from flask import jsonify


def BuildRandomString(length: int):
    """Build random string

    Args:
        length (int): string length

    Returns:
        _type_: str
    """    
    verify_code = ''
    while length > 0:
        num = random.randint(0, 9)
        s = str(random.choice([num, chr(random.randint(65, 90))]))
        if s in ['0','O','I','1']:
            continue
        verify_code += s
        length -= 1
    return verify_code


def APIResponse(success: bool = True, data: dict = {}, message: str = None):
    """Http data response

    Args:
        success (bool, optional): request result. Defaults to True.
        data (dict, optional): request data. Defaults to {}.
        message (str, optional): request message. Defaults to None.

    Returns:
        _type_: str
    """    
    
    return jsonify({'data': data, 'success': success, 'message': message})


def BuildContentQRCode(content: str, box_size: int = 4):
    """Build qrcode by text

    Args:
        content (str): qrcode content
        box_size (int, optional): box size. Defaults to 4.

    Returns:
        _type_: bytes
    """
    qr = qrcode.QRCode(box_size=box_size)
    qr.add_data(content)
    qr.make()
    qr_code_image = qr.make_image()
    buffered = BytesIO()
    qr_code_image.save(buffered)
    return base64.b64encode(buffered.getvalue()).decode()
