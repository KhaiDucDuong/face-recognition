import os
import pickle
import threading
import time
import numpy as np
import cv2
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
<<<<<<< HEAD
=======
import numpy as np
from PIL import Image
import requests
from io import BytesIO
>>>>>>> 96f73dd503dc0b48ecf571daa21e6a722f16727d
from datetime import datetime
import requests
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from io import BytesIO
from PIL import Image

<<<<<<< HEAD

class FaceRecognitionSystem:
    def __init__(self):
        # Initialize Firebase
        credential = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(credential, {
            'databaseURL': "https://facialrecognitionsystem-3c1b7-default-rtdb.firebaseio.com/",
            'storageBucket': "facialrecognitionsystem-3c1b7.appspot.com"
        })
        self.bucket = storage.bucket()
        
        # Initialize Video Capture labtop
        self.cap = cv2.VideoCapture(0)  # Camera Laptop
        self.cap.set(3, 640)
        self.cap.set(4, 480)

        # camaraIOT Read ESP32 Camera
        self.response = None
        self.image_camara = None
        self.image = None
        
        # Load background image
        self.background = cv2.imread('Resources/background.png')
        self.background_recognize = cv2.imread('Resources/background.png')
        
        # Load mode images into a list
        folderModePath = 'Resources/Modes'
        modePathList = os.listdir(folderModePath)
        self.imgModeList = [cv2.imread(os.path.join(folderModePath, path)) for path in modePathList]
        
        # Load the encoding file
        print("Loading Encode File ...")
        with open('EncodeFile.p', 'rb') as file:
            encodeListKnownWithIds = pickle.load(file)
        self.encodeListKnown, self.studentIds = encodeListKnownWithIds
        print("Encode File Loaded")
        
        # Initialize modeType and counter
        self.modeType = 0
        self.counter = 9
        self.id = -1
        self.imgStd = []
        
        self.success = False
        self.imgdetect = None
        # Case 
        self.detect_face_status = False
        self.recognize_safeface_status = False
        self.waring = 0
        self.face_detected_on_cammara = False
        self.face_same_person = True
        self.before_id = -1
        self.warning_email_sent = False
        self.warning_image_path = "warning_image.jpg"
        self.email = ""
        self.password = ""
        self.fromMail = ""
        self.toMail = ""
    
    def config(self):
        with open('config.json') as file:
            config = json.load(file)
        self.email = config['email']
        self.password = config['password']
        self.fromMail = config['from']
        self.toMail = config['to']

    def warring_notice(self):
        if self.waring > 10 and not self.warning_email_sent:
            # Save the detected image
            self.config()
            cv2.imwrite(self.warning_image_path, self.imgdetect)
            self.send_mail(self.warning_image_path)
            self.warning_email_sent = True
            print("Warning and sent message to user")

    def send_mail(self, image_path):
        # Set up the SMTP server
        s = smtplib.SMTP(host='smtp.gmail.com', port=587)
        s.starttls()
        s.login(self.email, self.password)

        # Create the email
        msg = MIMEMultipart()
        msg['From'] = self.fromMail
        msg['To'] = self.toMail
        msg['Subject'] = "Warning Notice"
        message = "Unknown person try to unlock the door."
        msg.attach(MIMEText(message, 'plain'))

        with open(image_path, 'rb') as f:
            image_data = f.read()
        image = MIMEImage(image_data, name=os.path.basename(image_path))
        msg.attach(image)
        # Send the email
        s.send_message(msg)
        del msg

        # Close the SMTP server connection
        s.quit()
    
    def img_process(self): 
        if self.imgdetect is not None:
            img = self.imgdetect.copy()
            # img_path = "D:/UTE/Year 3 Hk 2/Digital Image Processing/0 Facial Recognition Security System/IoT-based-Facial-Recognition-Security-System/Images/test.jpg"
            # img = cv2.imread(img_path)
            # img = cv2.resize(img, (640, 480))
            
            # Kiểm tra độ sáng của ảnh
            brightness = np.mean(img)

            # Nếu ảnh quá tối (độ sáng < 50), tăng độ sáng
            if brightness < 50:
                alpha = 2.0  # Tăng giá trị alpha để tăng độ sáng
                beta = 0     # Không điều chỉnh beta vì chỉ muốn tăng độ sáng
            # Nếu ảnh quá sáng (độ sáng > 200), giảm độ sáng
            elif brightness > 200:
                alpha = 0.5  # Giảm giá trị alpha để giảm độ sáng
                beta = 50    # Điều chỉnh giá trị beta để điều chỉnh mức độ tối mong muốn
            # Nếu ảnh có độ sáng trong khoảng từ 50 đến 200, không cần điều chỉnh
            else:
                alpha = 1.0  # Không thay đổi độ sáng
                beta = 0     # Không thay đổi độ sáng

            # Thực hiện điều chỉnh độ sáng của ảnh
            img_adjusted = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
            
            self.imgdetect = img_adjusted
            # cv2.imshow("Image", self.imgdetect)
        
    
    def recognize_safeface(self):
        stdInfo = db.reference(f'Students/{self.id}').get()
        print(stdInfo)
    
        blob = self.bucket.get_blob(f'Images/{self.id}.png')
        if blob is not None:
            array = np.frombuffer(blob.download_as_string(), np.uint8)
            self.imgStd = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
            
            datetimeObject = datetime.strptime(stdInfo['last_opening_door_time'], "%Y-%m-%d %H:%M:%S")
            secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
            print(secondsElapsed)
            
            if secondsElapsed > 60:  
                ref = db.reference(f'Students/{id}')
                stdInfo['total_open_door'] += 1
                ref.child('total_open_door').set(stdInfo['total_open_door'])
                ref.child('last_opening_door_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
            if self.recognize_safeface_status == True:
                    self.background_recognize = cv2.imread('Resources/background.png')
                    cv2.putText(self.background_recognize, str(stdInfo['total_open_door']), (861, 125), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                    cv2.putText(self.background_recognize, str(stdInfo['family_role']), (1006, 550), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(self.background_recognize, str(id), (1006, 493), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(self.background_recognize, str(stdInfo['age']), (1025, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(self.background_recognize, str(stdInfo['job_status']), (1125, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
=======
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
>>>>>>> 96f73dd503dc0b48ecf571daa21e6a722f16727d
                    (w, h), _ = cv2.getTextSize(stdInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414 - w) // 2
                    cv2.putText(self.background_recognize, str(stdInfo['name']), (808 + offset, 445), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)
                    self.background_recognize[175:175 + 216, 909:909 + 216] = self.imgStd
                    self.face_same_person == True
                    self.counter = 0
                    cv2.imshow("Recognition Background", self.background_recognize)
            if self.recognize_safeface_status == False:
                    stdInfo = []
<<<<<<< HEAD
                    self.imgStd = []
                    self.background_recognize[44:44 + 633, 808:808 + 414] = self.imgModeList[self.modeType]   

    def detect_face(self):    
        if self.success:
            self.detect_face_status = True
            imageSize = cv2.resize(self.imgdetect, (0, 0), None, 0.25, 0.25)
            imageSize = cv2.cvtColor(imageSize, cv2.COLOR_BGR2RGB)
            faceCurFrame = face_recognition.face_locations(imageSize)
            encodeCurFrame = face_recognition.face_encodings(imageSize, faceCurFrame)
            self.background[162:162 + 480, 55:55 + 640] = self.imgdetect
            self.background[44:44 + 633, 808:808 + 414] = self.imgModeList[self.modeType]
            if faceCurFrame:
                self.face_detected_on_cammara = True
                for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
                    matches = face_recognition.compare_faces(self.encodeListKnown, encodeFace)
                    faceDis = face_recognition.face_distance(self.encodeListKnown, encodeFace)
                    print("matches", matches)
                    print("faceDis", faceDis)
                    matchIndex = np.argmin(faceDis)
                    print("faceDis Match",faceDis[matchIndex])
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                    self.background = cvzone.cornerRect(self.background, bbox, rt=0)
                    time_detect = datetime.now()
                    closest_distance = faceDis[matchIndex]
                    if matches[matchIndex] and closest_distance < 0.38:                       
                        self.id = self.studentIds[matchIndex]
                        self.recognize_safeface_status = True
                        self.counter += 1
                        print("Counter" + str(self.counter))
                        
                    Timewarring = (datetime.now() - time_detect).total_seconds()
                    print("closest_distance", closest_distance)
                    print("Timewarring", Timewarring)
                    if closest_distance > 0.5 and Timewarring > 5:
                        self.waring += 1
                        print("Warring" + str(self.waring))
            else:
                self.face_detected_on_cammara = False
                if self.before_id != self.id:
                            self.face_same_person = False
                            self.before_id = self.id
                
    def warring_notice(self):
        if self.waring > 10:
            print("Warring and send message to user")
    
    def read_camera_data(self):
        while True:
            # #labtop camara8
            self.success, self.imgdetect = self.cap.read() 
            
            # ESP32Camera   
            # self.response = requests.get("http://192.168.1.10/cam-hi.jpg")
            # self.imgdetect = np.array(Image.open(BytesIO(self.response.content)))
            # self.imgdetect = cv2.cvtColor(self.imgdetect, cv2.COLOR_RGB2BGR)
            # self.success = True
            
            self.img_process()
            self.detect_face()   
            time.sleep(0.1)  # Add a small delay to avoid consuming too much CPU

    def process_face_recognition(self):
        while True:
            if self.success:
                # self.detect_face()
                if self.counter == 20 and self.recognize_safeface_status == True and self.face_detected_on_cammara == True:
                    self.recognize_safeface()
                self.warring_notice() 
                cv2.imshow("Face Recognition", self.background)
                cv2.waitKey(100)# Adjust the delay time as needed
             
                

    def run(self):
        while True:
        #     self.success, self.imgdetect = self.cap.read() 
        #     self.detect_face()
        #     if self.counter == 20 and self.recognize_safeface_status == True and self.face_detected_on_cammara == True:
        #         self.recognize_safeface()
        
        #     self.warring_notice() 
        #     cv2.imshow("Face Recognition", self.background)
        #     cv2.waitKey(100)
            
            # Start two threads for reading camera data and processing face recognition
            camera_thread = threading.Thread(target=self.read_camera_data)
            recognition_thread = threading.Thread(target=self.process_face_recognition)
            
            # Start both threads
            camera_thread.start()
            recognition_thread.start()
            
            # Wait for both threads to finish
            camera_thread.join()
            recognition_thread.join()

            # Release the camera and close OpenCV windows after threads finish
            self.cap.release()
            cv2.destroyAllWindows()
            # self.img_process()
            # cv2.waitKey()
            # Check if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


if __name__ == "__main__":
    face_recognition_system = FaceRecognitionSystem()
    face_recognition_system.run()

=======
                    imgStd = []
                    background[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0
    cv2.imshow("Face Recognition", background)
    cv2.waitKey(100)
>>>>>>> 96f73dd503dc0b48ecf571daa21e6a722f16727d
