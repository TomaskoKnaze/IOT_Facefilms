import os
import vlc
import math
import cv2
import numpy as np
import time

from keras.models import load_model
from time import sleep
from keras.preprocessing.image import img_to_array
from keras.preprocessing import image

import pymongo
from pymongo import MongoClient


from functions import *




face_classifier = cv2.CascadeClassifier('C:/Users/knaze/Python/pyproj/iot2/Code/haarcascade_frontalface_default.xml')
classifier =load_model('C:/Users/knaze/Python/pyproj/iot2/Code/Emotion_weights.h5')
class_labels = ['Angry','Happy','Neutral','Sad','Surprise','None']

cluster = MongoClient("mongodb+srv://Client:1234@cluster0.big8l.mongodb.net/Filmy?retryWrites=true&w=majority")
db = cluster["Filmy"]

immediate_emotion_list = []
Immediate_movement_list = []

emotions_seconds_list = []
movement_seconds_list = []
text_seconds_list = []
playback_seconds_list = []

sec = 0
t_end = time.time() + 1

face_presence_test = []
t_end_facetest = time.time() + 3
face_presence_test_bool = False

continuing = False
continuing2 = False
continuing3 = False
continuing4 = False
playing = False

current_position = []
old_position = [200,170]
position_difference = []
movement_average = 0

cap = cv2.VideoCapture(0)


#-------------------------------------Inital Film Choice - Question 1 ---------------------------
desktop = os.path.expanduser('~/Desktop')
os.chdir(desktop)
print('\n')
print("Please store all your movies and subtitles in a single directory on the Desktop.")


reply = str(input("Type READY to continue "))

while continuing == False:
    if reply in ["Ready", "ready", "READY"]:
        continuing = True
    else:
        reply = str(input("Type READY to continue ")) 

film_dir = str(input("What is your movie directory called? "))

while continuing2 == False:
    try:
        film_dir_path = os.path.abspath(film_dir)
        os.chdir(film_dir_path)
        print(film_dir_path)
        print('\n')
        print("Thesea are your movies")
        continuing2 = True
    except FileNotFoundError:
        film_dir = str(input("A folder with the name you have provided does not exist. What is your movie directory called? "))

for files in os.listdir(film_dir_path):
    print(files)


#-------------------------------------  Question 2 ------------------------------------------
film_choice = str(input("Which one would you like to watch? "))

while continuing3 == False:
    if os.path.exists(film_choice):
        media_player = vlc.MediaPlayer()
        film = vlc.Media(film_choice)
        media_player.set_media(film)
        print('Choice Successful! You have chosen {}'.format(film_choice))

        film_name = film_choice[:film_choice.rfind(".")]
        collection = db[film_name]
        print(film_name)

        continuing3 = True  
    else:
        film_choice = str(input("A film with the name you provided does not exist. Which one would you like to watch? "))


#-------------------------------------  Question 3 ------------------------------------------
for files in os.listdir(film_dir_path):
    print(files)
subtitle_choice = str(input("Please choose the subtitle file for the film {}? ".format(film_choice)))
while continuing4 == False:
    if os.path.exists(subtitle_choice):
        print('Subtitles Loaded!')
        dlzka = math.ceil(media_player.get_length()/1000)
        print(dlzka)
        continuing4 = True  
    else:
        film_choice = str(input("A film with the name you provided does not exist. Which one would you like to watch? "))

#-------------------------------------  Face Presence Check ------------------------------------------
print('Face Presence Check Will be carried out, please move your face in front of the webcam')
time.sleep(2)

while face_presence_test_bool == False:
    ret, frame = cap.read()
    labels = []
    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray,1.3,5)
    
    if isinstance(faces, np.ndarray):
        cv2.putText(frame,'Face Found!',(20,60),cv2.FONT_HERSHEY_SIMPLEX,2,(177,73,250),3)

        for (x,y,w,h) in faces:
            cv2.rectangle(frame,(x,y),(x+w,y+h),(9,254,158),2)

            if time.time() < t_end_facetest:
                    face_presence_test.append(1)
            else:
                try:
                    test_frequent = most_frequent(face_presence_test)
                    if test_frequent == 1:
                        print("Face Presence Check Done!")
                        face_presence_test_bool = True
                    else:
                        t_end_facetest = time.time() + 3
                except IndexError:
                    face_presence_test.append(0)
    else:
        
        face_presence_test.append(0)
        cv2.putText(frame,'No Face Found',(20,60),cv2.FONT_HERSHEY_SIMPLEX,2,(255,0,103),3)
    
    cv2.imshow('Emotion Detector',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
        

#-------------------------------------  Initiate the playback ------------------------------------------
media_player.audio_set_mute(True)
media_player.play()
time.sleep(1)
media_player.pause()

media_player.audio_set_mute(False)
dlzka = math.ceil(media_player.get_length()/1000)
print("Dlzka je {}".format(dlzka))
subtitle_text_list = subtitle_parse(subtitle_choice,dlzka)


print('The film will begin shortly, enjoy!')
print ('5')
time.sleep(1)
print ('4')
time.sleep(1)
print ('3')
time.sleep(1)
print ('2')
time.sleep(1)
print ('1')
time.sleep(1)

media_player.toggle_fullscreen() 
media_player.play()
time.sleep(0.5)

playing = media_player.is_playing()

emotions_minute_list = []
movement_minute_list = []
text_minute_list = []
playback_minute_list = []
sekunda_prehravania = 0
post_id = 0



#-------------------------------------Playing-----------------------------------------------------------

while playing == 1:
    playing = media_player.is_playing()

    # Grab a single frame of video
    ret, frame = cap.read()
    labels = []
    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray,1.3,5)

    if isinstance(faces, np.ndarray):
        for (x,y,w,h) in faces:
            cv2.rectangle(frame,(x,y),(x+w,y+h),(9,254,158),2)
            roi_gray = gray[y:y+h,x:x+w]
            roi_gray = cv2.resize(roi_gray,(48,48),interpolation=cv2.INTER_AREA)

            if np.sum([roi_gray])!=0:
                roi = roi_gray.astype('float')/255.0
                roi = img_to_array(roi)
                roi = np.expand_dims(roi,axis=0)

                # make a prediction on the ROI, then lookup the class

                preds = classifier.predict(roi)[0]
                label=class_labels[preds.argmax()]
                label_position = (x,y)
                cv2.putText(frame,label,label_position,cv2.FONT_HERSHEY_SIMPLEX,2,(177,73,250),3)
                
                # Determine Dominant Emotion
                predicted_coefficient = preds
                dominant_emotion_index = np.where(predicted_coefficient == np.amax(predicted_coefficient))
                dominant_emotion_index = dominant_emotion_index[0][0]

                
                if time.time() < t_end:
                    immediate_emotion_list.append(dominant_emotion_index)

                    #Calculate face movement
                    current_position = [x,y]
                    position_difference = [old_position[0]-current_position[0], old_position[1]-current_position[1]] 
                    Immediate_movement_list.append(math.sqrt(position_difference[0]**2 + position_difference[1]**2))
                    old_position = current_position
                else:
                    sekunda_prehravania += 1
                    print('Second {}'.format(sekunda_prehravania))
                    try:
                        #After 1 second has passed, find the most frequent emotion and calculate average movement during that sceond
                        frequent = most_frequent(immediate_emotion_list)
                        emotions_seconds_list.append(frequent)
                        immediate_emotion_list = []
                        dominant_emotion = class_labels[frequent]

                        movement_average = round(sum(Immediate_movement_list)/len(Immediate_movement_list), 2)
                        movement_seconds_list.append(movement_average)
                        Immediate_movement_list = []

                        # Get the current Playback time from VLC, find the corresponding script lines and append to respective lists
                        playback_time = math.floor((media_player.get_time())/1000)
                        text_seconds_list.append(subtitle_text_list[playback_time-1])
                        playback_seconds_list.append(playback_time)

                        if sec > 58:
                            #After 1 minute has passed
                            #First resete the minute lists
                            emotions_minute_list = []
                            movement_minute_list = []
                            text_minute_list = []
                            playback_minute_list = []


                            sec = 0
                            t_end = time.time() + 1

                            #Mongo cannot take value formats other than Unicode, make sure that all values can be transferred
                            for entry in emotions_seconds_list:
                                emotions_minute_list.append(int(entry))

                            for entry in movement_seconds_list:
                                movement_minute_list.append(float(entry))

                            for entry in text_seconds_list:
                                try:
                                    text_minute_list.append(int(entry))
                                except ValueError:
                                    text_minute_list.append(str(entry))

                            for entry in playback_seconds_list:
                                playback_minute_list.append(int(entry))

                            #Prepare and submit the dictiionary of minute values to MongoDB Server
                            post = {"_id": int(post_id), 
                                    "name": film_name, 
                                    "emotions": emotions_minute_list,
                                    "movement" : movement_minute_list,
                                    "text" : text_minute_list,
                                    "timestamp" : playback_minute_list,
                                    }
                            collection.insert_one(post)

                            #Reset the second lists
                            emotions_seconds_list = []
                            movement_seconds_list = []
                            text_seconds_list = []
                            playback_seconds_list = []

                            post_id +=1

                        else:
                            t_end = time.time() + 1
                            sec += 1

                    except (IndexError, ZeroDivisionError):
                        
                        frequent = 5
                        emotions_seconds_list.append(frequent)
                        immediate_emotion_list = []
                        dominant_emotion = class_labels[frequent]

                        movement_seconds_list.append(2)
                        Immediate_movement_list = []

                        playback_time = math.floor((media_player.get_time())/1000)
                        text_seconds_list.append(subtitle_text_list[playback_time-1])
                        playback_seconds_list.append(playback_time)

                        
                        if sec > 58:
                            emotions_minute_list = []
                            movement_minute_list = []
                            text_minute_list = []
                            playback_minute_list = []


                            sec = 0
                            t_end = time.time() + 1

                            for entry in emotions_seconds_list:
                                emotions_minute_list.append(int(entry))

                            for entry in movement_seconds_list:
                                movement_minute_list.append(float(entry))

                            for entry in text_seconds_list:
                                try:
                                    text_minute_list.append(int(entry))
                                except ValueError:
                                    text_minute_list.append(str(entry))

                            for entry in playback_seconds_list:
                                playback_minute_list.append(int(entry))


                            post = {"_id": int(post_id), 
                                    "name": film_name, 
                                    "emotions": emotions_minute_list,
                                    "movement" : movement_minute_list,
                                    "text" : text_minute_list,
                                    "timestamp" : playback_minute_list,
                                    }
                            collection.insert_one(post)


                            emotions_seconds_list = []
                            movement_seconds_list = []
                            text_seconds_list = []
                            playback_seconds_list = []

                            post_id +=1

                        else:
                            t_end = time.time() + 1
                            sec += 1

            else:
                cv2.putText(frame,'No Face Found',(20,60),cv2.FONT_HERSHEY_SIMPLEX,2,(0,255,0),3)
    else:
        cv2.putText(frame,'No Face Found',(20,60),cv2.FONT_HERSHEY_SIMPLEX,2,(0,255,0),3)

        if time.time() < t_end:
            #If no face is found, Append EMotion = None, Standard movement Value of 3
            immediate_emotion_list.append(5)
            Immediate_movement_list.append(2)
        else:
            sekunda_prehravania += 1
            print('Second {}'.format(sekunda_prehravania))
            try:
                frequent = most_frequent(immediate_emotion_list)
                emotions_seconds_list.append(frequent)
                immediate_emotion_list = []
                dominant_emotion = class_labels[frequent]

                movement_average = round(sum(Immediate_movement_list)/len(Immediate_movement_list), 2)
                movement_seconds_list.append(movement_average)
                Immediate_movement_list = []

                playback_time = math.floor((media_player.get_time())/1000)
                text_seconds_list.append(subtitle_text_list[playback_time-1])
                playback_seconds_list.append(playback_time)

                if sec > 58:
                    emotions_minute_list = []
                    movement_minute_list = []
                    text_minute_list = []
                    playback_minute_list = []


                    sec = 0
                    t_end = time.time() + 1

                    for entry in emotions_seconds_list:
                        emotions_minute_list.append(int(entry))

                    for entry in movement_seconds_list:
                        movement_minute_list.append(float(entry))

                    for entry in text_seconds_list:
                        try:
                            text_minute_list.append(int(entry))
                        except ValueError:
                            text_minute_list.append(str(entry))

                    for entry in playback_seconds_list:
                        playback_minute_list.append(int(entry))

                    post = {"_id": int(post_id), 
                            "name": film_name, 
                            "emotions": emotions_minute_list,
                            "movement" : movement_minute_list,
                            "text" : text_minute_list,
                            "timestamp" : playback_minute_list,
                            }
                    collection.insert_one(post)


                    emotions_seconds_list = []
                    movement_seconds_list = []
                    text_seconds_list = []
                    playback_seconds_list = []

                    post_id +=1

                else:
                    t_end = time.time() + 1
                    sec += 1
            except IndexError:
                frequent = 5
                emotions_seconds_list.append(frequent)
                immediate_emotion_list = []
                dominant_emotion = class_labels[frequent]

                movement_seconds_list.append(2)
                Immediate_movement_list = []

                playback_time = math.floor((media_player.get_time())/1000)
                text_seconds_list.append(subtitle_text_list[playback_time-1])
                playback_seconds_list.append(playback_time)
                
                if sec > 58:
                    emotions_minute_list = []
                    movement_minute_list = []
                    text_minute_list = []
                    playback_minute_list = []


                    sec = 0
                    t_end = time.time() + 1

                    for entry in emotions_seconds_list:
                        emotions_minute_list.append(int(entry))

                    for entry in movement_seconds_list:
                        movement_minute_list.append(float(entry))

                    for entry in text_seconds_list:
                        try:
                            text_minute_list.append(int(entry))
                        except ValueError:
                            text_minute_list.append(str(entry))

                    for entry in playback_seconds_list:
                        playback_minute_list.append(int(entry))

                    post = {"_id": int(post_id), 
                            "name": film_name, 
                            "emotions": emotions_minute_list,
                            "movement" : movement_minute_list,
                            "text" : text_minute_list,
                            "timestamp" : playback_minute_list,
                            }
                    collection.insert_one(post)


                    emotions_seconds_list = []
                    movement_seconds_list = []
                    text_seconds_list = []
                    playback_seconds_list = []

                    post_id +=1

                else:
                    t_end = time.time() + 1
                    sec += 1


    cv2.imshow('Emotion Detector',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

