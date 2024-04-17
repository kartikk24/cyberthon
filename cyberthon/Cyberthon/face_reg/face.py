import numpy as np
import cv2 as cv
import os 
import imghdr
import face_recognition
import shutil
face_cascade = cv.CascadeClassifier('xmlfiles/haarcascade_frontalface_default.xml')
eye_cascade = cv.CascadeClassifier('xmlfiles/haarcascade_eye.xml')
def detect(gray,frame,count,video_file_name):
    faces = face_cascade.detectMultiScale(gray,1.3,5)
    bbox = []
    for (x,y,w,h) in faces:
        cv.rectangle(frame,(x,y),(x + w,y + h),(255,0,0),2)
        roi_gray = gray[y:y+ h,x:x+ w]
        roi_color = frame[y:y+h,x:x+w]
        # os.mkdir(video_file_name)
        cv.imwrite("detections/%s/detections%d.jpg"%(video_file_name,count), frame)
        bbox.append([x,y,w,h])
        print([x,y,w,h])

    counter = 0
    for box in bbox:
        x,y,w,h = box[0],box[1],box[2],box[3]
        roi_color = frame[y:y+h,x:x+w]
        # os.mkdir(video_file_name)
        cv.imwrite("face_frames/%s/face_frames_%d_%d.jpg"%(video_file_name,count,counter), roi_color)
        counter = counter + 1
    return frame

video_folder = "videos/"
all_files = os.listdir(video_folder)
video_files = [f for f in all_files if imghdr.what(os.path.join(video_folder, f)) is None]

for video_file in video_files:
    video_path = os.path.join(video_folder, video_file)
    video_file_name = os.path.splitext(video_file)[0]
    video = cv.VideoCapture(video_path)

    os.mkdir("detections/%s/"%video_file_name)
    os.mkdir("face_frames/%s/"%video_file_name)
    if not video.isOpened():
        print(f"Error opening video file: {video_path}")
        continue

    success = 1
    count = 0

    while success:
        success, image = video.read()
        if success == 0:
            break
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        detect(gray, image, count,video_file_name)
        count += 1

    video.release()


actual_faces_folder = "database_images/"
frame_faces_folder = "face_frames/video1/"
output_matched_folder = "outputs/"

actual_face_images = []
actual_face_encodings = []

for actual_face_file in os.listdir(actual_faces_folder):
    actual_face_path = os.path.join(actual_faces_folder, actual_face_file)
    actual_image = face_recognition.load_image_file(actual_face_path)
    actual_encoding = face_recognition.face_encodings(actual_image)[0]
    actual_face_images.append(actual_face_path)
    actual_face_encodings.append(actual_encoding)


for frame_face_file in os.listdir(frame_faces_folder):
    frame_face_path = os.path.join(frame_faces_folder, frame_face_file)
    frame_image = face_recognition.load_image_file(frame_face_path)
    frame_encoding = face_recognition.face_encodings(frame_image)
    if len(frame_encoding) == 0:
        continue
    else:
        frame_encoding = frame_encoding[0]

    
    for i, actual_encoding in enumerate(actual_face_encodings):
        result = face_recognition.compare_faces([actual_encoding], frame_encoding)
        print(result)
        if result[0] == True:  
            matched_folder = os.path.join(output_matched_folder, f"matched_{actual_face_images[i]}_{frame_face_file}")
            os.makedirs(matched_folder, exist_ok=True)

            
            shutil.copy(actual_face_images[i], matched_folder)
            shutil.copy(frame_face_path, matched_folder)





