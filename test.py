import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
from kivy.app import App

from kivy.uix.button import Button

from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import (ScreenManager, Screen, NoTransition,
                                    SlideTransition, CardTransition, SwapTransition,
                                    FadeTransition, WipeTransition, FallOutTransition, RiseInTransition)
from kivy.lang import Builder


path = "Images"
images = []
personalname = []
mylist = os.listdir(path)
#print(mylist)

for cu_img in mylist:
    current_Img = cv2.imread(f"{path}/{cu_img}")
    images.append(current_Img)
    personalname.append(os.path.splitext(cu_img)[0])

print(personalname)

def faceEncodings(images):
    encodelist = []
    for img in images:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodelist.append(encode)

    return encodelist

encodeListKnown = faceEncodings(images)
#print(encodeListKnown)
print("Encodings completed.")
# Marking Attendance on a CSV file
def Attendance(name):
    with open('Attendance.csv','r+') as f:
        myDatalines = f.readlines()
        namelist = []
        for line in myDatalines:
            entry = line.split(",")
            namelist.append(entry[0])

        if name not in namelist:
            time_now = datetime.now()
            tStr = time_now.strftime('%H:%M:%S')
            dStr = time_now.strftime('%d/%m/%Y')
            f.writelines(f"{name},{tStr},{dStr}\n")


# You can create your kv code in the Python file
Builder.load_string("""
<MainMenu>:
    
    GridLayout:
        cols:1
        rows:3
        Button:
            text: "About"
            background_color : 0, 0, 1, 1
            on_press:
                # You can define the duration of the change
                # and the direction of the slide
                root.manager.transition.direction = 'left'
                root.manager.transition.duration = 1
                root.manager.current = 'about'

        Button:
            text: "Check Attendance"
            background_color : 0, 0, 1, 1
            on_press:
                # You can define the duration of the change
                # and the direction of the slide
                root.manager.transition.direction = 'left'
                root.manager.transition.duration = 1
                root.manager.current = 'check'

<About>:
    BoxLayout:
        Label:
            text:"HEYYYYY!"
        FloatLayout:
        Button:
            text: "Main Menu"
            background_color : 1, 1, 0, 1
            pos_hint: {"x":0, "bottom":1}
            on_press:
                root.manager.transition.direction = 'left'
                root.manager.transition.duration = 1
                root.manager.current = 'main_menu'
                
<Check>:
    
    BoxLayout:
        Button:
            text: "Feature not available right now :("
            background_color : 0, 0, 1, 1
            on_press:
                # You can define the duration of the change
                # and the direction of the slide
                root.manager.transition.direction = 'left'
                root.manager.transition.duration = 1
                root.manager.current = 'main_menu'


""")


# Create a class for all screens in which you can include
# helpful methods specific to that screen
class MainMenu(GridLayout,Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rows = 3
        self.column = 1
        self.bt = Button(

            text="Mark Attendance",
            size_hint=(.5, .55),
            background_color=(0, 255, 0),
            color=(0, 0, 255, 1)
        )

        self.add_widget(self.bt)

        self.bt.bind(on_press=self.opencam)

    def opencam(self, event):
        # For Opening Camera
        cap = cv2.VideoCapture(1)

        while True:
            ret, frame = cap.read()
            faces = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
            faces = cv2.cvtColor(faces, cv2.COLOR_BGR2RGB)

            facesCurrrentFrame = face_recognition.face_locations(faces)
            encodeCurrentFrame = face_recognition.face_encodings(faces, facesCurrrentFrame)

            for encodeFace, faceLoc in zip(encodeCurrentFrame, facesCurrrentFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

                matchIndex = np.argmin(faceDis)

                if matches[matchIndex]:
                    name = personalname[matchIndex].upper()
                    # print(name)
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0))
                    cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), (255, 0, 0), cv2.FILLED)
                    cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2)

                    # calling Attendance Function
                    Attendance(name)

            cv2.imshow("Camera", frame)
            if cv2.waitKey(10) == 13:
                break

        cap.release()
        cv2.destroyAllWindows()


class About(Screen):
    pass

class Check(Screen):
    pass




# The ScreenManager controls moving between screens
# You can change the transitions accorsingly
screen_manager = ScreenManager(transition=RiseInTransition())

# Add the screens to the manager and then supply a name
# that is used to switch screens
screen_manager.add_widget(MainMenu(name="main_menu"))
screen_manager.add_widget(About(name="about"))
screen_manager.add_widget(Check(name="check"))


# Create the App class
class AttendanceSystem(App):
    def build(self):
        return screen_manager


# run the app

AttendanceSystem().run()