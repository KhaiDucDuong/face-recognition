import os
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import numpy as np
from PIL import Image
import requests
from io import BytesIO
from datetime import datetime

credential = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(credential, {
    'databaseURL': "https://facialrecognitionsystem-3c1b7-default-rtdb.firebaseio.com/",
    'storageBucket': "facialrecognitionsystem-3c1b7.appspot.com"
})
bucket = storage.bucket()
# Creating an instance of video capture for capturing video
# cap = cv2.VideoCapture(1) # DroidCam
# cap = cv2.VideoCapture(0)  # Camera Laptop
# cap.set(3, 640)
# cap.set(4, 480)
background = cv2.imread('Resources/background.png')
# Importing the mode images into a list
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))
# Load the encoding file
print("Loading Encode File ...")
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
# print(studentIds)
print("Encode File Loaded")
modeType = 0
counter = 0
id = -1
imgStd = []

while True:

    # Read ESP32 Camera
    response = requests.get("http://10.0.30.224/cam-hi.jpg")
    image = np.array(Image.open(BytesIO(response.content)))
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    #Read laptop camera
    # success, image = cap.read()

    imageSize = cv2.resize(image, (0, 0), None, 0.25, 0.25)  # Resize image
    imageSize = cv2.cvtColor(imageSize, cv2.COLOR_BGR2RGB)  # Converting image to RGB format
    faceCurFrame = face_recognition.face_locations(imageSize)
    encodeCurFrame = face_recognition.face_encodings(imageSize, faceCurFrame)
    background[162:162 + 480, 55:55 + 640] = image
    background[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)  # Comparing the encoded face
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)  # Getting the distances
            print("matches", matches)
            print("faceDis", faceDis)
            matchIndex = np.argmin(faceDis)  # Finding the closest match
            # print("Match Index", matchIndex)
            if matches[matchIndex]: # If matched, update the information
                # print("Known Face Detected")
                # print(studentIds[matchIndex])
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                background = cvzone.cornerRect(background, bbox, rt=0)
                id = studentIds[matchIndex]
                if counter == 0:
                    cvzone.putTextRect(background, "Loading", (275, 400))
                    # cv2.imshow("Face Attendance", background)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1

        if counter != 0:
            if counter == 1:
                # Get the Data
                stdInfo = db.reference(f'Students/{id}').get()
                print(stdInfo)
                # Get the Images from the storage
                blob = bucket.get_blob(f'Images/{id}.png')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStd = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                # Update data of attendance
                datetimeObject = datetime.strptime(stdInfo['last_opening_door_time'], "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                print(secondsElapsed)
                if secondsElapsed > 20:  #30
                    ref = db.reference(f'Students/{id}')
                    stdInfo['total_open_door'] += 1
                    ref.child('total_open_door').set(stdInfo['total_open_door'])
                    ref.child('last_opening_door_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    background[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
            if modeType != 3:
                if 10 < counter < 20:
                    modeType = 2
                background[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
                if counter <= 10:
                    cv2.putText(background, str(stdInfo['total_open_door']), (861, 125), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                    cv2.putText(background, str(stdInfo['family_role']), (1006, 550), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(background, str(id), (1006, 493), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(background, str(stdInfo['age']), (1025, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(background, str(stdInfo['job_status']), (1125, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    (w, h), _ = cv2.getTextSize(stdInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414 - w) // 2
                    cv2.putText(background, str(stdInfo['name']), (808 + offset, 445), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)
                    background[175:175 + 216, 909:909 + 216] = imgStd
                counter += 1
                if counter >= 20:
                    counter = 0
                    modeType = 0
                    stdInfo = []
                    imgStd = []
                    background[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0
    cv2.imshow("Face Recognition", background)
    cv2.waitKey(100)
