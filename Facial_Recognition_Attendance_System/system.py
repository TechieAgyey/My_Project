############################################# IMPORTING ################################################
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mess
import tkinter.simpledialog as tsd
import cv2,os
import csv
import numpy as np
from PIL import Image
import pandas as pd
import datetime
import time
import mediapipe as mp
from tensorflow.keras.models import model_from_json

############################################# FUNCTIONS ################################################

def assure_path_exists(path):
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)

##################################################################################

def tick():
    time_string = time.strftime('%H:%M:%S')
    clock.config(text=time_string)
    clock.after(200,tick)

###################################################################################

def contact():
    mess._show(title='Contact us', message="Please contact us on : 's.btiwari.manas@gmail.com' ")

###################################################################################

def check_haarcascadefile():
    exists = os.path.isfile("haarcascade_frontalface_default.xml")
    if exists:
        pass
    else:
        mess._show(title='Some file missing', message='Please contact us for help')
        window.destroy()

###################################################################################

def save_pass():
    assure_path_exists("TrainingImageLabel/")
    exists1 = os.path.isfile("TrainingImageLabel\psd.txt")
    if exists1:
        tf = open("TrainingImageLabel\psd.txt", "r")
        key = tf.read()
    else:
        master.destroy()
        new_pas = tsd.askstring('Old Password not found', 'Please enter a new password below', show='*')
        if new_pas == None:
            mess._show(title='No Password Entered', message='Password not set!! Please try again')
        else:
            tf = open("TrainingImageLabel\psd.txt", "w")
            tf.write(new_pas)
            mess._show(title='Password Registered', message='New password was registered successfully!!')
            return
    op = (old.get())
    newp= (new.get())
    nnewp = (nnew.get())
    if (op == key):
        if(newp == nnewp):
            txf = open("TrainingImageLabel\psd.txt", "w")
            txf.write(newp)
        else:
            mess._show(title='Error', message='Confirm new password again!!!')
            return
    else:
        mess._show(title='Wrong Password', message='Please enter correct old password.')
        return
    mess._show(title='Password Changed', message='Password changed successfully!!')
    master.destroy()

###################################################################################

def change_pass():
    global master
    master = tk.Tk()
    master.geometry("400x160")
    master.resizable(False,False)
    master.title("Change Password")
    master.configure(background="white")
    lbl4 = tk.Label(master,text='    Enter Old Password',bg='white',font=('times', 12, ' bold '))
    lbl4.place(x=10,y=10)
    global old
    old=tk.Entry(master,width=25 ,fg="black",relief='solid',font=('times', 12, ' bold '),show='*')
    old.place(x=180,y=10)
    lbl5 = tk.Label(master, text='   Enter New Password', bg='white', font=('times', 12, ' bold '))
    lbl5.place(x=10, y=45)
    global new
    new = tk.Entry(master, width=25, fg="black",relief='solid', font=('times', 12, ' bold '),show='*')
    new.place(x=180, y=45)
    lbl6 = tk.Label(master, text='Confirm New Password', bg='white', font=('times', 12, ' bold '))
    lbl6.place(x=10, y=80)
    global nnew
    nnew = tk.Entry(master, width=25, fg="black", relief='solid',font=('times', 12, ' bold '),show='*')
    nnew.place(x=180, y=80)
    cancel=tk.Button(master,text="Cancel", command=master.destroy ,fg="black"  ,bg="red" ,height=1,width=25 , activebackground = "white" ,font=('times', 10, ' bold '))
    cancel.place(x=200, y=120)
    save1 = tk.Button(master, text="Save", command=save_pass, fg="black", bg="#3ece48", height = 1,width=25, activebackground="white", font=('times', 10, ' bold '))
    save1.place(x=10, y=120)
    master.mainloop()

#####################################################################################

def psw():
    assure_path_exists("TrainingImageLabel/")
    exists1 = os.path.isfile("TrainingImageLabel\psd.txt")
    if exists1:
        tf = open("TrainingImageLabel\psd.txt", "r")
        key = tf.read()
    else:
        new_pas = tsd.askstring('Old Password not found', 'Please enter a new password below', show='*')
        if new_pas == None:
            mess._show(title='No Password Entered', message='Password not set!! Please try again')
        else:
            tf = open("TrainingImageLabel\psd.txt", "w")
            tf.write(new_pas)
            mess._show(title='Password Registered', message='New password was registered successfully!!')
            return
    password = tsd.askstring('Password', 'Enter Password', show='*')
    if (password == key):
        TrainImages()
    elif (password == None):
        pass
    else:
        mess._show(title='Wrong Password', message='You have entered wrong password')

######################################################################################

def clear():
    txt.delete(0, 'end')
    res = "1)Take Images  >>>  2)Save Profile"
    message1.configure(text=res)


def clear2():
    txt2.delete(0, 'end')
    res = "1)Take Images  >>>  2)Save Profile"
    message1.configure(text=res)

#######################################################################################

def TakeImages():
    columns = ['SERIAL NO.', '', 'ID', '', 'NAME']
    assure_path_exists("StudentDetails/")
    assure_path_exists("TrainingImage/")
    
    # Check if the person is already registered
    Id = txt.get()  # Make sure txt and txt2 are defined elsewhere in your code
    name = txt2.get()

    # Check if the person is already registered and images exist
    if person_already_registered(Id, name) and person_images_exist(Id, name):
        res = "Id is registered."
        message1.configure(text=res, fg="white")  # Update message1 with the new message and white text color
        return

    # Check if the person is already registered and images are less than 120
    if person_already_registered(Id, name) and total_images < 120:
        delete_record(Id, name)
        delete_images(Id, name)
        reset_total_images()
    
    serial = 0
    exists = os.path.isfile("StudentDetails\StudentDetails.csv")
    if exists:
        with open("StudentDetails\StudentDetails.csv", 'r') as csvFile1:
            reader1 = csv.reader(csvFile1)
            for l in reader1:
                serial = serial + 1
        serial = (serial // 2)
    else:
        with open("StudentDetails\StudentDetails.csv", 'a+') as csvFile1:
            writer = csv.writer(csvFile1)
            writer.writerow(columns)
            serial = 1

    # Counter to track the total number of images captured
    total_images = 0

    mp_face_detection = mp.solutions.face_detection
    mp_drawing = mp.solutions.drawing_utils
    
    # Initialize MediaPipe face detection
    face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)

    cam = cv2.VideoCapture(0)

    # Load existing images for comparison
    existing_images = []
    for root, dirs, files in os.walk("TrainingImage/"):
        for file in files:
            existing_images.append(file)

    detected_name = None
    frame_count = 0
    while True:
        ret, img = cam.read()
        if not ret:
            print("Failed to read from webcam.")
            break

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = face_detection.process(img_rgb)

        if results.detections:
            for detection in results.detections:
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, _ = img.shape
                bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                    int(bboxC.width * iw), int(bboxC.height * ih)

                # Draw rectangle with yellow color and thickness 3
                cv2.rectangle(img, bbox, (0, 255, 255), 3)

                # Capture images only if the person is already detected and no other person is detected
                if detected_name == name:
                    if total_images < 120:
                        cropped_img = img[bbox[1]:bbox[1]+bbox[3], bbox[0]:bbox[0]+bbox[2]]
                        if cropped_img.size != 0:
                            # Validate the captured image against existing images
                            if not person_already_exists(cropped_img, existing_images):
                                cv2.imwrite(f"TrainingImage/{name}.{serial}.{Id}.{total_images}.jpg", cropped_img)
                                total_images += 1
                else:
                    # Increment frame count if the detected name is not the desired one
                    frame_count += 1

                    # If the same name is detected for 5 consecutive frames, consider it as a valid detection
                    if frame_count >= 5:
                        detected_name = name
                        frame_count = 0

                    # If images already exist for this person, display ID and name around the rectangle
                    if person_images_exist(Id, name):
                        cv2.putText(img, f'ID: {Id}', (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 127), 2)
                        cv2.putText(img, f'Name: {name}', (bbox[0], bbox[1] - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 127), 2)
                    
        # Check if the total count of images is increasing and the total count in the live webcam is zero
        if total_images == 0:
            if person_registered_with_different_name(Id, name):
                text = "Id is registered with another name."
            else:
                text = "Images already exist for this person."
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
            cv2.rectangle(img, (0, 0), (text_size[0] + 20, text_size[1] + 20), (0, 0, 0), -1)
            cv2.putText(img, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        else:
            # Display take images at left corner
            cv2.putText(img, f'Total Images: {total_images}', (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

        cv2.imshow('Taking Images', img)
        if cv2.waitKey(100) & 0xFF == ord('q') or total_images >= 120:
            break

    cam.release()
    cv2.destroyAllWindows()

    # Only update the CSV file if 120 images are captured
    if total_images == 120:
        res = f"Images Taken for ID: {Id}"
        row = [serial, '', Id, '', name]
        with open('StudentDetails\StudentDetails.csv', 'a+') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(row)
        message1.configure(text=res)

# Function to check if images already exist for the person
def person_images_exist(Id, name):
    for root, dirs, files in os.walk("TrainingImage/"):
        for file in files:
            if f"{name}.{Id}." in file:
                return True
    return False

# Function to delete the record in student details and attendance details
def delete_record(Id, name):
    # Delete record from StudentDetails.csv
    with open("StudentDetails/StudentDetails.csv", 'r') as csvFile:
        reader = csv.reader(csvFile)
        rows = list(reader)

    with open("StudentDetails/StudentDetails.csv", 'w', newline='') as csvFile:
        writer = csv.writer(csvFile)
        for row in rows:
            if row[2] != Id and row[4] != name:
                writer.writerow(row)

    # Delete record from AttendanceDetails.csv (if needed)
    # Add your code to delete records from AttendanceDetails.csv here (if required)

# Function to delete all images associated with the person
def delete_images(Id, name):
    for root, dirs, files in os.walk("TrainingImage/"):
        for file in files:
            if f"{name}.{Id}." in file:
                os.remove(os.path.join(root, file))

# Function to reset the total images count
def reset_total_images():
    global total_images
    total_images = 0

# Function to check if the person is already registered with a different name
def person_registered_with_different_name(Id, name):
    with open("StudentDetails/StudentDetails.csv", 'r') as csvFile:
        reader = csv.reader(csvFile)
        for row in reader:
            if len(row) >= 5 and row[2] == Id and row[4] != name:
                return True
    return False

# Function to check if the person is already registered
def person_already_registered(Id, name):
    exists = os.path.isfile("StudentDetails\StudentDetails.csv")
    if exists:
        with open("StudentDetails\StudentDetails.csv", 'r') as csvFile:
            reader = csv.reader(csvFile)
            for row in reader:
                if len(row) >= 5 and (row[2] == Id or row[4] == name):
                    return True
    return False

# Function to check if the person already exists in the existing images
def person_already_exists(cropped_img, existing_images):
    # Convert the image to grayscale
    gray_cropped_img = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
    
    # Loop through existing images to compare
    for image_path in existing_images:
        existing_image = cv2.imread(os.path.join("TrainingImage/", image_path))
        gray_existing_image = cv2.cvtColor(existing_image, cv2.COLOR_BGR2GRAY)
        
        # Compare images using a suitable method (e.g., histogram comparison, feature matching)
        # Here, we'll use the histogram comparison
        similarity = cv2.compareHist(cv2.calcHist([gray_cropped_img], [0], None, [256], [0, 256]),
                                     cv2.calcHist([gray_existing_image], [0], None, [256], [0, 256]),
                                     cv2.HISTCMP_CORREL)
        
        # If the similarity is above a certain threshold, consider the person already exists
        if similarity > 0.9:  # You may need to adjust this threshold based on your application
            return True
    
    return False

########################################################################################

def TrainImages():
    check_haarcascadefile()
    assure_path_exists("TrainingImageLabel/")
    recognizer = cv2.face_LBPHFaceRecognizer.create()
    harcascadePath = "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(harcascadePath)
    faces, ID = getImagesAndLabels("TrainingImage")
    try:
        recognizer.train(faces, np.array(ID))
    except:
        mess._show(title='No Registrations', message='Please Register someone first!!!')
        return
    recognizer.save("TrainingImageLabel\Trainner.yml")
    res = "Profile Saved Successfully"
    message1.configure(text=res)
    message.configure(text='Total Registrations till now  : ' + str(ID[0]))

############################################################################################3

def getImagesAndLabels(path):
    # get the path of all the files in the folder
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    # create empth face list
    faces = []
    # create empty ID list
    Ids = []
    # now looping through all the image paths and loading the Ids and the images
    for imagePath in imagePaths:
        # loading the image and converting it to gray scale
        pilImage = Image.open(imagePath).convert('L')
        # Now we are converting the PIL image into numpy array
        imageNp = np.array(pilImage, 'uint8')
        # getting the Id from the image
        ID = int(os.path.split(imagePath)[-1].split(".")[1])
        # extract the face from the training image sample
        faces.append(imageNp)
        Ids.append(ID)
    return faces, Ids

###########################################################################################

def TrackImages():
    col_names = ['ID', 'Name', 'Date', 'Time']
    assure_path_exists("Attendance/")
    assure_path_exists("StudentDetails/")
    
    # Clear the treeview
    for k in tv.get_children():
        tv.delete(k)
        
    msg = ''
    i = 0
    j = 0
    
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    exists3 = os.path.isfile("TrainingImageLabel\Trainner.yml")
    if exists3:
        recognizer.read("TrainingImageLabel\Trainner.yml")
    else:
        mess._show(title='Data Missing', message='Please click on Save Profile to reset data!!')
        return
    
    # Initialize MediaPipe face detection
    mp_face_detection = mp.solutions.face_detection
    mp_drawing = mp.solutions.drawing_utils
    
    # Load the anti-spoofing model
    json_file = open('antispoofing_models/antispoofing_model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    model = model_from_json(loaded_model_json)
    model.load_weights('antispoofing_models/antispoofing_model.h5')
    print("Models loaded from disk")
    
    cam = cv2.VideoCapture(0)  # Initialize the camera
    
    # Define df here or retrieve it from wherever it's supposed to be defined
    df = pd.read_csv("StudentDetails\StudentDetails.csv")  # Example of how to retrieve df
    
    all_faces_genuine = True  # Flag to track if all detected faces are genuine
    
    while True:
        ret, im = cam.read()
        if not ret:
            print("Failed to read from webcam.")
            break
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        
        # Initialize name variable
        name = 'Unknown'
        
        # Use MediaPipe for face detection
        with mp_face_detection.FaceDetection(min_detection_confidence=0.5) as face_detection:
            img_rgb = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
            results = face_detection.process(img_rgb)
    
            if results.detections:
                for detection in results.detections:
                    bboxC = detection.location_data.relative_bounding_box
                    ih, iw, _ = im.shape
                    bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                        int(bboxC.width * iw), int(bboxC.height * ih)
                    
                    # Ensure the bounding box coordinates are within the image dimensions
                    if bbox[1] >= 0 and bbox[0] >= 0 and bbox[1] + bbox[3] < gray.shape[0] and bbox[0] + bbox[2] < gray.shape[1]:
                        # Extract the region of interest (ROI) from the grayscale image
                        roi_gray = gray[bbox[1]:bbox[1]+bbox[3], bbox[0]:bbox[0]+bbox[2]]
                        
                        # Convert grayscale ROI to RGB
                        roi_rgb = cv2.cvtColor(roi_gray, cv2.COLOR_GRAY2RGB)
                        
                        # Resize ROI for anti-spoofing model
                        resized_roi = cv2.resize(roi_rgb, (160, 160))
                        resized_roi = resized_roi.astype("float") / 255.0
                        resized_roi = np.expand_dims(resized_roi, axis=0)
                        
                        # Predict whether the face is genuine or fake
                        preds = model.predict(resized_roi)[0]
                        
                        # Display whether the face is genuine or fake
                        if preds > 0.5:  # Fake face
                            cv2.putText(im, 'Fake', (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                            name = 'Fake'
                            all_faces_genuine = False  # Update flag if any face is fake
                        else:  # Genuine face
                            id_, conf = recognizer.predict(roi_gray)
                            if conf < 50:
                                ts = time.time()
                                date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
                                timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                                name = df.loc[df['SERIAL NO.'] == id_]['NAME'].values
                                ID = df.loc[df['SERIAL NO.'] == id_]['ID'].values
                                ID = str(ID)[1:-1]
                                name = str(name)[2:-2]
                                attendance = [ID, '', name, '', date, '', timeStamp]
                            else:
                                name = 'Unknown'
                                all_faces_genuine = False  # Update flag if any face is unknown
                        
                        # Draw bounding box around the face
                        thickness = 3
                        cv2.rectangle(im, bbox, (0, 255, 0), thickness)
                        
                        # Display name below the rectangle
                        cv2.putText(im, str(name), (bbox[0], bbox[1] + bbox[3] + 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    else:
                        name = 'Unknown'
                        # Display "Unknown" label outside the loop
                        cv2.putText(im, str(name), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        cv2.imshow('Taking Attendance', im)
        if cv2.waitKey(1) == ord('q'):
            break
    
    # Only save attendance if all faces were genuine
    if all_faces_genuine:
        ts = time.time()
        date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
        exists = os.path.isfile("Attendance\Attendance_" + date + ".csv")
        if exists:
            with open("Attendance\Attendance_" + date + ".csv", 'a+') as csvFile1:
                writer = csv.writer(csvFile1)
                writer.writerow(attendance)
            csvFile1.close()
        else:
            with open("Attendance\Attendance_" + date + ".csv", 'a+') as csvFile1:
                writer = csv.writer(csvFile1)
                writer.writerow(col_names)
                writer.writerow(attendance)
            csvFile1.close()
        
        # Update the tree view
        with open("Attendance\Attendance_" + date + ".csv", 'r') as csvFile1:
            reader1 = csv.reader(csvFile1)
            for lines in reader1:
                i = i + 1
                if i > 1:
                    if i % 2 != 0:
                        iidd = str(lines[0]) + '  '
                        tv.insert('', 0, text=iidd, values=(str(lines[2]), str(lines[4]), str(lines[6])))
        csvFile1.close()
    
    cam.release()
    cv2.destroyAllWindows()

######################################## USED STUFFS ############################################
    
global key
key = ''

ts = time.time()
date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
day,month,year=date.split("-")

mont={'01':'January',
      '02':'February',
      '03':'March',
      '04':'April',
      '05':'May',
      '06':'June',
      '07':'July',
      '08':'August',
      '09':'September',
      '10':'October',
      '11':'November',
      '12':'December'
      }

######################################## GUI FRONT-END ###########################################

window = tk.Tk()
window.geometry("1280x720")
window.resizable(True,False)
window.title("Attendance System")
window.configure(background='#262523')

frame1 = tk.Frame(window, bg="#00aeff")
frame1.place(relx=0.11, rely=0.17, relwidth=0.39, relheight=0.80)

frame2 = tk.Frame(window, bg="#00aeff")
frame2.place(relx=0.51, rely=0.17, relwidth=0.38, relheight=0.80)

message3 = tk.Label(window, text="Face Recognition Based Attendance System" ,fg="white",bg="#262523" ,width=55 ,height=1,font=('times', 29, ' bold '))
message3.place(x=10, y=10)

frame3 = tk.Frame(window, bg="#c4c6ce")
frame3.place(relx=0.52, rely=0.09, relwidth=0.09, relheight=0.07)

frame4 = tk.Frame(window, bg="#c4c6ce")
frame4.place(relx=0.36, rely=0.09, relwidth=0.16, relheight=0.07)

datef = tk.Label(frame4, text = day+"-"+mont[month]+"-"+year+"  |  ", fg="orange",bg="#262523" ,width=55 ,height=1,font=('times', 22, ' bold '))
datef.pack(fill='both',expand=1)

clock = tk.Label(frame3,fg="orange",bg="#262523" ,width=55 ,height=1,font=('times', 22, ' bold '))
clock.pack(fill='both',expand=1)
tick()

head2 = tk.Label(frame2, text="                       For New Registrations                       ", fg="black",bg="#3ece48" ,font=('times', 17, ' bold ') )
head2.grid(row=0,column=0)

head1 = tk.Label(frame1, text="                       For Already Registered                       ", fg="black",bg="#3ece48" ,font=('times', 17, ' bold ') )
head1.place(x=0,y=0)

lbl = tk.Label(frame2, text="Enter ID",width=20  ,height=1  ,fg="black"  ,bg="#00aeff" ,font=('times', 17, ' bold ') )
lbl.place(x=80, y=55)

txt = tk.Entry(frame2,width=32 ,fg="black",font=('times', 15, ' bold '))
txt.place(x=30, y=88)

lbl2 = tk.Label(frame2, text="Enter Name",width=20  ,fg="black"  ,bg="#00aeff" ,font=('times', 17, ' bold '))
lbl2.place(x=80, y=140)

txt2 = tk.Entry(frame2,width=32 ,fg="black",font=('times', 15, ' bold ')  )
txt2.place(x=30, y=173)

message1 = tk.Label(frame2, text="1)Take Images  >>>  2)Save Profile" ,bg="#00aeff" ,fg="black"  ,width=39 ,height=1, activebackground = "yellow" ,font=('times', 15, ' bold '))
message1.place(x=7, y=230)

message = tk.Label(frame2, text="" ,bg="#00aeff" ,fg="black"  ,width=39,height=1, activebackground = "yellow" ,font=('times', 16, ' bold '))
message.place(x=7, y=450)

lbl3 = tk.Label(frame1, text="Attendance",width=20  ,fg="black"  ,bg="#00aeff"  ,height=1 ,font=('times', 17, ' bold '))
lbl3.place(x=100, y=115)

res=0
exists = os.path.isfile("StudentDetails\StudentDetails.csv")
if exists:
    with open("StudentDetails\StudentDetails.csv", 'r') as csvFile1:
        reader1 = csv.reader(csvFile1)
        for l in reader1:
            res = res + 1
    res = (res // 2) - 1
    csvFile1.close()
else:
    res = 0
message.configure(text='Total Registrations till now  : '+str(res))

##################### MENUBAR #################################

menubar = tk.Menu(window,relief='ridge')
filemenu = tk.Menu(menubar,tearoff=0)
filemenu.add_command(label='Change Password', command = change_pass)
filemenu.add_command(label='Contact Us', command = contact)
filemenu.add_command(label='Exit',command = window.destroy)
menubar.add_cascade(label='Help',font=('times', 29, ' bold '),menu=filemenu)

################## TREEVIEW ATTENDANCE TABLE ####################

tv= ttk.Treeview(frame1,height =13,columns = ('name','date','time'))
tv.column('#0',width=82)
tv.column('name',width=130)
tv.column('date',width=133)
tv.column('time',width=133)
tv.grid(row=2,column=0,padx=(0,0),pady=(150,0),columnspan=4)
tv.heading('#0',text ='ID')
tv.heading('name',text ='NAME')
tv.heading('date',text ='DATE')
tv.heading('time',text ='TIME')

###################### SCROLLBAR ################################

scroll=ttk.Scrollbar(frame1,orient='vertical',command=tv.yview)
scroll.grid(row=2,column=4,padx=(0,100),pady=(150,0),sticky='ns')
tv.configure(yscrollcommand=scroll.set)

###################### BUTTONS ##################################

clearButton = tk.Button(frame2, text="Clear", command=clear  ,fg="black"  ,bg="#ea2a2a"  ,width=11 ,activebackground = "white" ,font=('times', 11, ' bold '))
clearButton.place(x=335, y=86)
clearButton2 = tk.Button(frame2, text="Clear", command=clear2  ,fg="black"  ,bg="#ea2a2a"  ,width=11 , activebackground = "white" ,font=('times', 11, ' bold '))
clearButton2.place(x=335, y=172)    
takeImg = tk.Button(frame2, text="Take Images", command=TakeImages  ,fg="white"  ,bg="blue"  ,width=34  ,height=1, activebackground = "white" ,font=('times', 15, ' bold '))
takeImg.place(x=30, y=300)
trainImg = tk.Button(frame2, text="Save Profile", command=psw ,fg="white"  ,bg="blue"  ,width=34  ,height=1, activebackground = "white" ,font=('times', 15, ' bold '))
trainImg.place(x=30, y=380)
trackImg = tk.Button(frame1, text="Take Attendance", command=TrackImages  ,fg="black"  ,bg="yellow"  ,width=35  ,height=1, activebackground = "white" ,font=('times', 15, ' bold '))
trackImg.place(x=30,y=50)
quitWindow = tk.Button(frame1, text="Quit", command=window.destroy  ,fg="black"  ,bg="red"  ,width=35 ,height=1, activebackground = "white" ,font=('times', 15, ' bold '))
quitWindow.place(x=30, y=450)

##################### END ######################################

window.configure(menu=menubar)
window.mainloop()

####################################################################################################
