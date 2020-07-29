





from azure.cognitiveservices.vision.computervision.models import TextOperationStatusCodes

import requests

import os
import time
import enchant
import numpy as np
import cv2

scriptpath=os.path.abspath(__file__)
scriptdir=os.path.dirname(scriptpath)

# Add your Computer Vision subscription key and endpoint to your environment variables.
# if 'COMPUTER_VISION_SUBSCRIPTION_KEY' in os.environ:
subscription_key = 'Your subscription key'
# else:
    # print("\nSet the COMPUTER_VISION_SUBSCRIPTION_KEY environment variable.\n**Restart your shell or IDE for changes to take effect.**")
    # sys.exit()

# if 'COMPUTER_VISION_ENDPOINT' in os.environ:
def remove_values_from_list(the_list, val):
        return [value for value in the_list if value != val]
def execute(img):
    List1 = []
   
    List2 = []
    


    endpoint = 'https://handwrittingrecognition.cognitiveservices.azure.com/'

    text_recognition_url = endpoint + "vision/v2.1/read/core/asyncBatchAnalyze"

    # Set image_path to the local path of an image that you want to analyze.

    # image = img

    # img2 = image.copy()
    # # detecting red color
    # image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # lower = np.array([155, 25, 0])
    # upper = np.array([179, 255, 255])
    # mask = cv2.inRange(image, lower, upper)

    # thresh = cv2.threshold(mask, 0, 255, cv2.THRESH_BINARY)[1]

    # # apply canny edge detection
    # edges = cv2.Canny(thresh, 100, 200)

    # # get hough line segments
    # threshold = 100
    # minLineLength = 50
    # maxLineGap = 20
    # lines = cv2.HoughLinesP(thresh, 1, np.pi / 360, threshold, minLineLength, maxLineGap)

    # # draw lines
    # linear = np.zeros_like(thresh)
    # for [line] in lines:
    #     # print(line)
    #     x1 = line[0]
    #     y1 = line[1]
    #     x2 = line[2]
    #     y2 = line[3]
    #     cv2.line(linear, (x1, y1), (x2, y2), (255), 1)

    # # get bounds of white pixels
    # white = np.where(linear == 255)
    # xmin, ymin, xmax, ymax = np.min(white[1]), np.min(white[0]), np.max(white[1]), np.max(white[0])

    # # draw bounding box on input
    # bounds = img2.copy()
    # cv2.rectangle(bounds, (xmin, ymin), (xmax, ymax), (0, 0, 255))

    # crop the image at the bounds
    #crop = img2[ymin:ymax, xmin:xmax]
    crop=img
    shp=img.shape

    # cv2.imwrite("crop.jpg", crop)
    #mp = ((xmax - xmin) / 1.714, (ymax - ymin) / 2)
    mp=(shp[0]/1.714,shp[1]/2)   
    # image_path = "crop.jpg"
    # # Read the image into a byte array
    # image_data = open(image_path, "rb").read()
    # print(image_data)
    # crop = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
    # image_data=Image.fromarray(crop)

    
    is_success, im_buf_arr = cv2.imencode(".jpg", crop)
    image_data = im_buf_arr.tobytes()


    # image_data=crop

    headers = {'Ocp-Apim-Subscription-Key': subscription_key,
               'Content-Type': 'application/octet-stream'}

    response = requests.post(
        text_recognition_url, headers=headers, data=image_data)
    response.raise_for_status()

    # Extracting text requires two API calls: One call to submit the
    # image for processing, the other to retrieve the text found in the image.

    # Holds the URI used to retrieve the recognized text.
    operation_url = response.headers["Operation-Location"]

    # The recognized text isn't immediately available, so poll to wait for completion.
    analysis = {}
    poll = True
    notes_text = ""
    specialization = ""
    medicine_text = ""
    m=0
    l=0
    lab_text = ""
    while (poll):
        response_final = requests.get(
            response.headers["Operation-Location"], headers=headers)
        analysis = response_final.json()
        # print(analysis)
        # Print the detected text, line by line
        if analysis["status"] == TextOperationStatusCodes.succeeded:
            for text_result in analysis["recognitionResults"]:
                for line in text_result["lines"]:
                    if ("Specialization" in line["text"]):
                        specialization = line["text"][17:]
                    elif ("Dr. Name" not in line["text"]):
                        for word in line["words"]:
                            if (word["boundingBox"][0] + word["boundingBox"][2]) / 2 > mp[1]:
                                if (word["boundingBox"][1] + word["boundingBox"][7]) / 2 < mp[0]:

                                    medicine_text = medicine_text + word["text"] + " "
                                    m=1

                                else:

                                    lab_text = lab_text + word["text"] + " "
                                    l=1
                            else:

                                notes_text = notes_text + word["text"] + " "
                        if(m==1):
                            medicine_text=medicine_text+","
                        if(l==1):
                            lab_text=lab_text+","
        time.sleep(1)
        if ("recognitionResults" in analysis):
            poll = False
        if ("status" in analysis and analysis['status'] == 'Failed'):
            poll = False
    # Word Suggestions
    

    # #print(os.path.curdir, "medicine/", specialization, ".txt")
    
    medicine_lines=medicine_text.split(',')
    medicine_dict = enchant.PyPWL(os.path.join(scriptdir,specialization+".txt"))
    for medicine_line in medicine_lines:
        words = medicine_line.split()
        # print(words)


        value=" "
        for input_medicine_name in words:
            suggestions = medicine_dict.suggest(input_medicine_name)
            if(len(suggestions)!=0):

            #print(suggestions[0])
                value=value+suggestions[0]+" "
            else:
                value=value+input_medicine_name
        if(List1!=' '):
            List1.append(value)


        #print('line end')



    test_lines = lab_text.split(',')
    test_dict = enchant.PyPWL(os.path.join(scriptdir, "tests.txt"))
    for test_line in test_lines:
        words=test_line.split()

        value=" "
        for input_test_name in words:
            suggestions = test_dict.suggest(input_test_name)
            if(len(suggestions)!=0):
            #print(suggestions[0])

                value=value+suggestions[0]+" "
            else:
                value=value+input_test_name
        if(value!=' '):
            List2.append(value)

        #print('test end')

    # print(words)
    
   
    # List1.rstrip()
    # List2.rstrip()
    
    List1 = remove_values_from_list(List1, ' ')
    List2 = remove_values_from_list(List2, ' ')

    dictionary={"name":"Hamza",
                "medicine":List1,
                "tests":List2,
                "notes":notes_text}
    print(dictionary)
    return dictionary


