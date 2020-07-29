import logging
import numpy as np
import cv2
from . import asal
import json


import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    file = req.files['file']
    if 'file' not in req.files :
        return func.HttpResponse("none appeared ")
    else:
        result=chk(file)
        return func.HttpResponse(
             json.dumps(result),
             status_code=201
        )




def chk(file):
    arr = np.asarray(bytearray(file.read()), dtype=np.uint8)
    img = cv2.imdecode(arr, -1)  # 'Load it as it is'
    msg=asal.execute(img)
    return msg
    