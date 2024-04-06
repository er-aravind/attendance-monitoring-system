import face_recognition
import imutils
import pickle
import time
import cv2
import os

from datetime import datetime
from tkinter import messagebox

import sqlite3

db = sqlite3.connect('db.sqlite3')#
print("Successfully Connected to SQLite")

now = datetime.now() 
dte=now.strftime("%m/%d/%Y")
#print("date :",dte)	
time = now.strftime("%H:%M:%S")
#print("time:", time)


sqlnew="select * from smartatt_app_subject_table where Department='CSE'and Semester='S2'"
#print(sqlnew)
cursor2=db.cursor()
cursor2.execute(sqlnew)
res1=cursor2.fetchall()
#print(res1)
subval=""
for i in res1:
    # print("\n\n")
    # print(i)
    # print('***************')
    dnow=datetime.now()
    #print(dnow)
    stime=datetime.strptime(i[4],'%H:%M')
    etime=datetime.strptime(i[5],'%H:%M')
    # print("^^^^^")
    # print(stime)
    # print(etime)
    # print("^^^^^")

    if((dnow.time() > stime.time()) and (dnow.time() < etime.time()) ):
        print("Subject-->",i[3])
        subval=i[3]


print("Subval : ",subval)



faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_alt2.xml")
# load the known faces and embeddings saved in last file
data = pickle.loads(open('encodings_face', "rb").read())
countuk=0
video_capture = cv2.VideoCapture(0)

def punch_attendance(usname):
    cursor2=db.cursor()


    sql2="select * from smartatt_app_attendance_table where Usernm='%s'and Date='%s' and Subject='%s'"%(usname,dte,subval)
    #print(sql2)
    cursor2.execute(sql2)
    res1=cursor2.fetchall()
    #print(len(res1))
    if(len(res1)==0):
        cursor=db.cursor()
        sql="""insert into smartatt_app_attendance_table(Usernm,Date,Punchin,Punchout,Subject)values('%s','%s','%s','%s','%s')"""%(usname,dte,time,"0",subval)
        #print (sql)
        try:
            cursor.execute(sql)
            db.commit()
            print ("Inserted to Table")
        except Exception as e:
            db.rollback()
            print ("error",e)
    


# lmes from the video file stream
while True:
    # grab the frame from the threaded video stream
    ret, frame = video_capture.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray,
                                         scaleFactor=1.1,
                                         minNeighbors=5,
                                         minSize=(60, 60),
                                         flags=cv2.CASCADE_SCALE_IMAGE)
 
    # convert the input frame from BGR to RGB 
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # the facial embeddings for face in input
    encodings = face_recognition.face_encodings(rgb)
    names = []
    # loop over the facial embeddings incase
    # we have multiple embeddings for multiple fcaes
    for encoding in encodings:
       #Compare encodings with encodings in data["encodings"]
       #Matches contain array with boolean values and True for the embeddings it matches closely
       #and False for rest
        matches = face_recognition.compare_faces(data["encodings"],
         encoding)
        #set name =inknown if no encoding matches
        name = "Unknown"
        # check to see if we have found a match
        if True in matches:
            #Find positions at which we get True and store them
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}
            # loop over the matched indexes and maintain a count for
            # each recognized face face
            for i in matchedIdxs:
                #Check the names at respective indexes we stored in matchedIdxs
                name = data["names"][i]
                #increase count for the name we got
                counts[name] = counts.get(name, 0) + 1
            #set name which has highest count
            name = max(counts, key=counts.get)
 
 
        # update the list of names
        names.append(name)
        # loop over the recognized faces
        for ((x, y, w, h), name) in zip(faces, names):
            # rescale the face coordinates
            # draw the predicted face name on the image
            if(name=='unknown' or name=="Unknown" or subval==""):
                print("unknown or no subject")
            else:
                punch_attendance(name)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # cv2.putText(frame, name, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
            #  0.75, (0, 255, 0), 2)
    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
video_capture.release()
cv2.destroyAllWindows()