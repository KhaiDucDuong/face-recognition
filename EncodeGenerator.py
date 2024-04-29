import os
import pickle

import cv2
import face_recognition
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

credential = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(credential, {
    'databaseURL': "https://facialrecognitionsystem-3c1b7-default-rtdb.firebaseio.com/",
    'storageBucket': "facialrecognitionsystem-3c1b7.appspot.com"
})

# Importing student images
folderImages = 'Images'
# Get a list of all files in the 'Images' folder
pathImage = os.listdir(folderImages)
print(pathImage)
images = []
idStds = []
for link in pathImage:
    # Read image from file path and add to image list
    images.append(cv2.imread(os.path.join(folderImages, link)))
    # Get student ID from file name (remove file extension)
    idStds.append(os.path.splitext(link)[0])
    # Upload photos to Firebase Storage - Images
    photoName = f'{folderImages}/{link}'
    bucket = storage.bucket()
    blob = bucket.blob(photoName)
    blob.upload_from_filename(photoName)

print(idStds)


def findEncodings(imagesList):
    encodeList = []
    for image in imagesList:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # Find the encoding (arithmetic representation) of the face in the image
        encode = face_recognition.face_encodings(image)[0]
        encodeList.append(encode)

    return encodeList


# Encode the image list and save it to the file 'EncodeFile.p'
print("Encoding Started ...")
encodeListKnown = findEncodings(images)
encodeListKnownWithIds = [encodeListKnown, idStds]
print("Encoding Complete")
# EncodeFile.p file can be used to detect and recognize faces in images
file = open("EncodeFile.p", 'wb')
# Store the list of student face coding and the list of corresponding IDs in the file EncodeFile.p
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("File Saved")
