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
from datetime import datetime

credential = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(credential, {
    'databaseURL': "https://facialrecognitionsystem-3c1b7-default-rtdb.firebaseio.com/",
    'storageBucket': "facialrecognitionsystem-3c1b7.appspot.com"
})
bucket = storage.bucket()

# Creating an instance of video capture for capturing video
# cap = cv2.VideoCapture(1) # DroidCam
cap = cv2.VideoCapture(0)  # Camera Laptop
cap.set(3, 640)
cap.set(4, 480)
# take background image
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

def image_process(img):
    # Resize the input image to 216x216 shape
    img_resized = cv2.resize(img, (216, 216))
    
    # Chuyển đổi ảnh sang không gian màu HSV
    hsv = cv2.cvtColor(img_resized, cv2.COLOR_BGR2HSV)
    
    # Tăng độ sáng của kênh Value (V)
    brightness_factor = 1.2
    hsv[:,:,2] = np.clip(hsv[:,:,2] * brightness_factor, 0, 255)
    
    # Chuyển đổi ảnh từ không gian màu HSV trở lại BGR
    img_brightness_adjusted = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    # Làm đậm ảnh sử dụng kỹ thuật histogram equalization
    img_darkened = cv2.cvtColor(img_brightness_adjusted, cv2.COLOR_BGR2GRAY)
    img_darkened = cv2.equalizeHist(img_darkened)
    
    # Áp dụng Gaussian Blur để loại bỏ nhiễu
    img_blurred = cv2.GaussianBlur(img_darkened, (5, 5), 0)
    
    # Convert the image back to the BGR color space
    img_rgb = cv2.cvtColor(img_blurred, cv2.COLOR_GRAY2RGB)
    # cv2.imshow("Processed Image", img_rgb)
    return img_rgb



while True:
    success, image = cap.read()
    imageSize = cv2.resize(image, (0, 0), None, 0.25, 0.25)  # # Resize frame of video to 1/4 size for faster face detection processing
    
    # cv2.imshow("Resized Image", imageSize)
    # # Lấy kích thước của hình ảnh sau khi đã thay đổi kích thước
    # height, width, channels = imageSize.shape
    # print("Kích thước của hình ảnh sau khi đã thu nhỏ: {}x{}".format(width, height))
    
    imageSize = cv2.cvtColor(imageSize, cv2.COLOR_BGR2RGB)  # Converting image to RGB format từ BGR sang RGB.
    #  trả về một danh sách các tuple, mỗi tuple chứa 4 giá trị đại diện cho vị trí của một khuôn mặt trong hình ảnh. 
    #  Cụ thể, các giá trị này thường là (top, right, bottom, left),
    #  nghĩa là tọa độ của góc trên bên trái và góc dưới bên phải của hộp giới hạn khuôn mặt.
    faceCurFrame = face_recognition.face_locations(imageSize)
    encodeCurFrame = face_recognition.face_encodings(imageSize, faceCurFrame)
    # Edit
    imageEncode = image_process(imageSize)
    faceCurFrameEdit = face_recognition.face_locations(imageEncode)
    # encodeCurFrame = face_recognition.face_encodings(imageEncode, faceCurFrameEdit)
    background[162:162 + 480, 55:55 + 640] = image
    background[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            #encodeListKnown read from Encode file .p
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)  # Comparing the encoded face
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)  # Getting the distances
            print("matches", matches)
            print("faceDis", faceDis)
            matchIndex = np.argmin(faceDis)  # Finding the closest match
            print("faceDis Match",faceDis[matchIndex])
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
            background = cvzone.cornerRect(background, bbox, rt=0)
            # print("Match Index", matchIndex)
            print(matches[matchIndex])
            # if matches[matchIndex] and faceDis[matchIndex] > 0.4: # If matched, update the information
            if matches[matchIndex]:
                # print("Known Face Detected")
                # print(studentIds[matchIndex])
                # y1, x2, y2, x1 = faceLoc
                # y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                # bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                # background = cvzone.cornerRect(background, bbox, rt=0)
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
                if secondsElapsed > 20:  
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
