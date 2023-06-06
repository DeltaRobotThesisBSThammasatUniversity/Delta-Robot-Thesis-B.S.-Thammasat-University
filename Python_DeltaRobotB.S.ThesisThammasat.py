import customtkinter
import os
from PIL import Image
import tkinter.messagebox as mbox
import serial
import time
import numpy as np
from scipy import interpolate
import struct
import cv2
import threading
import tkinter as tk
from PIL import ImageTk, Image
import torch
import os
from matplotlib import pyplot as plt
import math
import queue
import csv

customtkinter.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"

ser = serial.Serial("COM9",250000)
# ser1 = serial.Serial("COM12",300)

# model = torch.hub.load('ultralytics/yolov5', 'custom', path='./yolov5new/runs2/train/exp/weights/best.pt')
model = torch.hub.load('ultralytics/yolov5', 'custom', path='./yolov5new/runs1/train/exp4/weights/best.pt')
# model1 = torch.hub.load('ultralytics/yolov5', 'custom', path='./yolov5nnnn/runs/train/exp4/weights/best.pt')

parameter = 400
timePlace = 0
velocity = 10



class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("DELTA ROBOT")
        self.geometry("700x450")
        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.limit_speed = 165
        # load images with light and dark mode image
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_images")
        self.icon_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "icon1.png")), 
                                                 size=(40, 40))
        self.home_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "home.png")), 
                                                 size=(30, 30))
        self.joy_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "joy.png")),
                                                 size=(30, 30))
        self.hand_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "hand.png")), 
                                                 size=(30, 30))
        self.ai_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "ai.png")), 
                                               size=(30, 30))
        self.set_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "set.png")), 
                                               size=(30, 30))
        self.ex_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "logout.png")), 
                                               size=(30, 30))
        self.dir_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "dir.png")), 
                                               size=(30, 30))
        self.ask_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "ask.png")), 
                                               size=(20, 20))
        self.comment_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "comment.png")), 
                                               size=(10, 10))
        self.setting_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "setting.png")), 
                                               size=(20, 20))
        self.delta_image = customtkinter.CTkImage(Image.open(os.path.join("delta.png")), 
                                               size=(157, 280))
        self.position_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "position.png")), 
                                               size=(30, 30))
        self.reset_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "reset.png")), 
                                               size=(30, 30))
        self.move_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "move.png")), 
                                               size=(30, 30))
        self.per_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "per.png")), 
                                               size=(20, 20))
        self.check_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "check.png")), 
                                               size=(15, 15))
        self.uncheck_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "uncheck.png")), 
                                               size=(15, 15))
        self.bDown_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "bDown.png")), 
                                               size=(70, 70))
        self.bUp_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "bUp.png")), 
                                               size=(70, 70))  
        self.bLeft_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "bLeft.png")), 
                                               size=(70, 70))
        self.bRight_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "bRight.png")), 
                                               size=(70, 70))
        self.bReset_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "bReset.png")), 
                                               size=(50, 50))
        self.bToUp_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "bToUp.png")), 
                                               size=(70, 70))
        self.bToDown_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "bToDown.png")), 
                                               size=(70, 70))    
        self.green_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "green.png")), 
                                               size=(70, 70))   
        self.blue_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "blue.png")), 
                                               size=(70, 70))
        self.red_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "red.png")), 
                                               size=(70, 70))  
        self.iconbitmap("test_images\icon1.ico") 
        # create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(7, weight=1)
        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, 
                                                             text= " DELTA ROBOT", 
                                                             image=self.icon_image,
                                                             compound="left", 
                                                             font=customtkinter.CTkFont(size=25, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=10, pady=20)
        self.home_button = customtkinter.CTkButton(self.navigation_frame, 
                                                   corner_radius=0, 
                                                   height=40, 
                                                   border_spacing=10, 
                                                   text="  Home",
                                                   fg_color="transparent", 
                                                   text_color=("gray90"), 
                                                   hover_color=("gray30"),
                                                   font=customtkinter.CTkFont(size=20),
                                                   image=self.home_image, anchor="w",
                                                   command=self.home_button_event
                                                   )
        self.home_button.grid(row=1, column=0, sticky="ew")
        self.manual_button = customtkinter.CTkButton(self.navigation_frame, 
                                                      corner_radius=0, 
                                                      height=40, 
                                                      border_spacing=10, 
                                                      text="  Manual Control",
                                                      fg_color="transparent", 
                                                      text_color=("gray90"), 
                                                      hover_color=("gray30"),
                                                      font=customtkinter.CTkFont(size=20),
                                                      image=self.joy_image, anchor="w",
                                                      command=self.manual_button_event 
                                                      )
        self.manual_button.grid(row=2, column=0, sticky="ew")
        self.hand_button = customtkinter.CTkButton(self.navigation_frame, 
                                                      corner_radius=0, 
                                                      height=40, 
                                                      border_spacing=10, 
                                                      text="  Position Hand Control",
                                                      fg_color="transparent",
                                                      text_color=("gray90"),
                                                      hover_color=("gray30"),
                                                      font=customtkinter.CTkFont(size=20),
                                                      image=self.hand_image, anchor="w",
                                                      command=self.hand_button_event 
                                                      )
        self.hand_button.grid(row=3, column=0, sticky="ew")
        self.ai_button = customtkinter.CTkButton(self.navigation_frame, 
                                                      corner_radius=0, 
                                                      height=40, 
                                                      border_spacing=10, 
                                                      text="  AI Detect Control",
                                                      fg_color="transparent",
                                                      text_color=("gray90"),
                                                      hover_color=("gray30"),
                                                      font=customtkinter.CTkFont(size=20),
                                                      image=self.ai_image, anchor="w",
                                                      command=self.ai_button_event 
                                                      )
        self.ai_button.grid(row=4, column=0, sticky="ew")       
        self.set_button = customtkinter.CTkButton(self.navigation_frame, 
                                                      corner_radius=0, 
                                                      height=40, 
                                                      border_spacing=10, 
                                                      text="  Setting",
                                                      fg_color="transparent",
                                                      text_color=("gray90"),
                                                      hover_color=("gray30"),
                                                      font=customtkinter.CTkFont(size=20),
                                                      image=self.set_image, anchor="w",
                                                      command=self.set_button_event 
                                                      )
        self.set_button.grid(row=5, column=0, sticky="ew")
        self.ex_button = customtkinter.CTkButton(self.navigation_frame, 
                                                      corner_radius=0, 
                                                      height=40, 
                                                      border_spacing=10, 
                                                      text="  Logout",
                                                      fg_color="transparent",
                                                      text_color=("gray90"),
                                                      hover_color=("gray30"),
                                                      font=customtkinter.CTkFont(size=20),
                                                      image=self.ex_image, anchor="w",
                                                      command=self.set_button_event 
                                                      )
        self.ex_button.grid(row=6, column=0, sticky="ew")
        # create home frame
        self.home_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1)
        self.home_frame_large_image_label = customtkinter.CTkLabel(self.home_frame,
                                                                   text = "WELCOME TO DELTA ROBOT PROJECT ",
                                                                   width=120,
                                                                   height=100,
                                                                   fg_color=("gray8"),
                                                                   font=customtkinter.CTkFont(size=20),
                                                                   corner_radius=20)
        self.home_frame_large_image_label.grid(row=0, column=0, padx=20, pady=30)
        self.home_frame_delta = customtkinter.CTkLabel(self.home_frame,
                                                                   text = " ",
                                                                   image=self.delta_image,)
        self.home_frame_delta.place(relx=0.05, rely=0.33)
        self.home_frame_button1 = customtkinter.CTkButton(self.home_frame, 
                                                          text="INTRODUCTION",
                                                          width=200,
                                                          height=32,
                                                          corner_radius=8,
                                                          font=customtkinter.CTkFont(size=15),
                                                          fg_color = "gray8",
                                                          image=self.dir_image,anchor="w"
                                                          )
        self.home_frame_button1.place(relx=0.47, rely=0.33)
        self.home_frame_button2 = customtkinter.CTkButton(self.home_frame, 
                                                          text="OBJECTIVE",
                                                          width=200,
                                                          height=32,
                                                          corner_radius=8,
                                                          font=customtkinter.CTkFont(size=15),
                                                          fg_color = "gray8",
                                                          image=self.dir_image,anchor="w"
                                                          )
        self.home_frame_button2.place(relx=0.47, rely=0.43)
        self.home_frame_button3 = customtkinter.CTkButton(self.home_frame, 
                                                          text="EQUATION",
                                                          width=200,
                                                          height=32,
                                                          corner_radius=8,
                                                          font=customtkinter.CTkFont(size=15),
                                                          fg_color = "gray8",
                                                          image=self.dir_image,anchor="w"
                                                          )
        self.home_frame_button3.place(relx=0.47, rely=0.53)
        self.home_frame_button4 = customtkinter.CTkButton(self.home_frame, 
                                                          text="CONTROL METHOD",
                                                          width=200,
                                                          height=32,
                                                          corner_radius=8,
                                                          font=customtkinter.CTkFont(size=15),
                                                          fg_color = "gray8",
                                                          image=self.dir_image,anchor="w"
                                                          )
        self.home_frame_button4.place(relx=0.47, rely=0.63) 
        self.home_frame_button4 = customtkinter.CTkButton(self.home_frame, 
                                                          text="PROJECT TEAM",
                                                          width=200,
                                                          height=32,
                                                          corner_radius=8,
                                                          font=customtkinter.CTkFont(size=15),
                                                          fg_color = "gray8",
                                                          image=self.dir_image,anchor="w"
                                                          )
        self.home_frame_button4.place(relx=0.47, rely=0.73)
        self.home_frame_button5 = customtkinter.CTkButton(self.home_frame, 
                                                          text="REFERENCES",
                                                          width=200,
                                                          height=32,
                                                          corner_radius=8,
                                                          font=customtkinter.CTkFont(size=15),
                                                          fg_color = "gray8",
                                                          image=self.dir_image,anchor="w"
                                                          )
        self.home_frame_button5.place(relx=0.47, rely=0.83)
        # create manual frame
        self.manual_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.manual_frame.grid_columnconfigure(0, weight=1)
        self.manual_frame_large_image_label = customtkinter.CTkLabel(self.manual_frame,
                                                                   text = "MANUAL CONTROL",
                                                                   width=400,
                                                                   height=50,
                                                                   fg_color=("gray8"),
                                                                   font=customtkinter.CTkFont(size=20),
                                                                   corner_radius=20)
        self.manual_frame_large_image_label.grid(row=0, column=0, padx=20, pady=20)
        # self.manual_monitorXY = customtkinter.CTkLabel(self.manual_frame,
        #                                                            text = "monitorXY",
        #                                                            width=300,
        #                                                            height=300,
        #                                                            fg_color=("gray8"),
        #                                                            font=customtkinter.CTkFont(size=20),
        #                                                            corner_radius=20)
        # self.manual_monitorXY.place(relx = 0.05, rely = 0.15)

        # self.manual_monitorZ = customtkinter.CTkLabel(self.manual_frame,
        #                                                            text = "monitorXZ",
        #                                                            width=300,
        #                                                            height=300,
        #                                                            fg_color=("gray8"),
        #                                                            font=customtkinter.CTkFont(size=20),
        #                                                            corner_radius=20)
        # self.manual_monitorZ.place(relx = 0.55, rely = 0.15)
        self.manual_bUp = customtkinter.CTkButton(self.manual_frame, 
                                                          text="",
                                                          width=10,
                                                          height=10,
                                                          corner_radius=5,
                                                          fg_color = "transparent",
                                                          image=self.bUp_image,
                                                          
                                                          anchor = "center",
                                                          command=self.movePY
                                                          
                                                          )
        self.manual_bUp.place(relx=0.25, rely=0.5)
        self.manual_bReset = customtkinter.CTkButton(self.manual_frame, 
                                                          text="",
                                                          width=10,
                                                          height=10,
                                                          corner_radius=5,
                                                          fg_color = "transparent",
                                                          image=self.bReset_image,
                                                          anchor = "center",
                                                          command=self.ResetManual,
                                                          
                                                          )
        self.manual_bReset.place(relx=0.275, rely=0.68)
        self.manual_bDown = customtkinter.CTkButton(self.manual_frame, 
                                                          text="",
                                                          width=10,
                                                          height=10,
                                                          corner_radius=5,
                                                          fg_color = "transparent",
                                                          image=self.bDown_image,
                                                          anchor = "center",
                                                          command=self.moveMY
                                                          
                                                          )
        self.manual_bDown.place(relx=0.25, rely=0.82)
        self.manual_bRight = customtkinter.CTkButton(self.manual_frame, 
                                                          text="",
                                                          width=10,
                                                          height=10,
                                                          corner_radius=5,
                                                          fg_color = "transparent",
                                                          image=self.bRight_image,
                                                          anchor = "center",
                                                          command=self.movePX
                                                          
                                                          )
        self.manual_bRight.place(relx=0.45, rely=0.65)
        self.manual_bLeft = customtkinter.CTkButton(self.manual_frame, 
                                                          text="",
                                                          width=10,
                                                          height=10,
                                                          corner_radius=5,
                                                          fg_color = "transparent",
                                                          image=self.bLeft_image,
                                                          anchor = "center",
                                                          command=self.moveMX
                                                          
                                                          )
        self.manual_bLeft.place(relx=0.059, rely=0.65)
        self.manual_bToUp = customtkinter.CTkButton(self.manual_frame, 
                                                          text="UP",
                                                          width=10,
                                                          height=10,
                                                          corner_radius=5,
                                                          fg_color = "transparent",
                                                          image=self.bToUp_image, 
                                                          compound = "bottom",
                                                          anchor = "center",
                                                          command=self.movePZ
                                                          
                                                          )
        self.manual_bToUp.place(relx=0.7, rely=0.54)
        self.manual_bToDown = customtkinter.CTkButton(self.manual_frame, 
                                                          text="DOWN",
                                                          width=10,
                                                          height=10,
                                                          corner_radius=5,
                                                          fg_color = "transparent",
                                                          image=self.bToDown_image,
                                                          compound = "top",
                                                          anchor = "center",
                                                          command=self.moveMZ
                                                          
                                                          )
        self.manual_bToDown.place(relx=0.7, rely=0.75)
        self.slider_2 = customtkinter.CTkSlider(self.manual_frame,
                                                width = 120,
                                                from_=0, to=100, 
                                                number_of_steps=300, 
                                                command = self.update_slider1_value)
        self.slider_2.place(relx=0.05, rely=0.2)
        self.manual_monitor1 = customtkinter.CTkLabel(self.manual_frame, 
                                                text=f"Step +X = {(self.slider_2.get()*30)/100} mm", 
                                                fg_color=("transparent"), 
                                                font=customtkinter.CTkFont(size=15))
        self.manual_monitor1.place(relx=0.4, rely=0.185)
        self.slider_3 = customtkinter.CTkSlider(self.manual_frame,
                                                width = 120, 
                                                from_=0, to=100, 
                                                number_of_steps=300, 
                                                command = self.update_slider1_value)
        self.slider_3.place(relx=0.05, rely=0.25)
        self.manual_monitor2 = customtkinter.CTkLabel(self.manual_frame, 
                                                text=f"Step -X = {-(self.slider_3.get()*30)/100} mm", 
                                                fg_color=("transparent"), 
                                                font=customtkinter.CTkFont(size=15))
        self.manual_monitor2.place(relx=0.4, rely=0.235)
        self.slider_4 = customtkinter.CTkSlider(self.manual_frame,
                                                width = 120, 
                                                from_=0, to=100, 
                                                number_of_steps=300, 
                                                command = self.update_slider1_value)
        self.slider_4.place(relx=0.05, rely=0.3)
        self.manual_monitor3 = customtkinter.CTkLabel(self.manual_frame, 
                                                text=f"Step +Y = {(self.slider_4.get()*30)/100} mm", 
                                                fg_color=("transparent"), 
                                                font=customtkinter.CTkFont(size=15))
        self.manual_monitor3.place(relx=0.4, rely=0.285)
        self.slider_5 = customtkinter.CTkSlider(self.manual_frame,
                                                width = 120, 
                                                from_=0, to=100, 
                                                number_of_steps=300, 
                                                command = self.update_slider1_value)
        self.slider_5.place(relx=0.05, rely=0.35)
        self.manual_monitor4 = customtkinter.CTkLabel(self.manual_frame, 
                                                text=f"Step -Y = {-(self.slider_5.get()*30)/100} mm", 
                                                fg_color=("transparent"), 
                                                font=customtkinter.CTkFont(size=15))
        self.manual_monitor4.place(relx=0.4, rely=0.335)
        self.slider_6 = customtkinter.CTkSlider(self.manual_frame, 
                                                width = 120,
                                                from_=0, to=100, 
                                                number_of_steps=300, 
                                                command = self.update_slider1_value)
        self.slider_6.place(relx=0.05, rely=0.4)
        self.manual_monitor5 = customtkinter.CTkLabel(self.manual_frame, 
                                                text=f"Step +Z = {(self.slider_6.get()*30)/100} mm", 
                                                fg_color=("transparent"), 
                                                font=customtkinter.CTkFont(size=15))
        self.manual_monitor5.place(relx=0.4, rely=0.385)
        self.slider_7 = customtkinter.CTkSlider(self.manual_frame, 
                                                width = 120,
                                                from_=0, to=100, 
                                                number_of_steps=300, 
                                                command = self.update_slider1_value)
        self.slider_7.place(relx=0.05, rely=0.45)
        self.manual_monitor6 = customtkinter.CTkLabel(self.manual_frame, 
                                                text=f"Step -Z = {-(self.slider_7.get()*30)/100} mm", 
                                                fg_color=("transparent"), 
                                                font=customtkinter.CTkFont(size=15))
        self.manual_monitor6.place(relx=0.4, rely=0.435)
        # create hand frame
        self.hand_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.hand_frame.grid_columnconfigure(0, weight=1)
        self.hand_frame_large_image_label = customtkinter.CTkLabel(self.hand_frame,
                                                                   text = "POSITION HAND CONTROL",
                                                                   width=400,
                                                                   height=50,
                                                                   fg_color=("gray8"),
                                                                   font=customtkinter.CTkFont(size=20),
                                                                   corner_radius=20)
        self.hand_frame_large_image_label.grid(row=0, column=0, padx=20, pady=30)
        # self.hand_camera = customtkinter.CTkSwitch(self.hand_frame, text=" CAMERA",
        #                                          command = self.CameraHand)
        # self.hand_camera.place(relx = 0.1, rely = 0.2)

        # create ai frame
        self.ai_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.ai_frame.grid_columnconfigure(0, weight=1)

        self.ai_frame_large_image_label = customtkinter.CTkLabel(self.ai_frame,
                                                                   text = "AI DETECT CONTROL",
                                                                   width=400,
                                                                   height=50,
                                                                   fg_color=("gray1"),
                                                                   font=customtkinter.CTkFont(size=20),
                                                                   corner_radius=20)
        self.ai_frame_large_image_label.grid(row=0, column=0, padx=20, pady=30)
        self.ai_camera = customtkinter.CTkSwitch(self.ai_frame, text=" CAMERA",
                                                 command = self.CameraAI)
        self.ai_camera.place(relx = 0.1, rely = 0.2)
        self.ai_position1 = customtkinter.CTkLabel(self.ai_frame,
                                                                   text = "Red box position",
                                                                   width=400,
                                                                   height=100,
                                                                   fg_color=("black"),
                                                                   font=customtkinter.CTkFont(size=20),
                                                                   corner_radius=20,
                                                                   image=self.red_image,
                                                                
                                                                compound="left")
        self.ai_position1.grid(row=1, column=0, padx=20, pady=5)
        self.ai_position2 = customtkinter.CTkLabel(self.ai_frame,
                                                                   text = "Blue box position",
                                                                   width=400,
                                                                   height=100,
                                                                   fg_color=("black"),
                                                                   font=customtkinter.CTkFont(size=20),
                                                                   corner_radius=20,image=self.blue_image,
                                                                compound="left")
        self.ai_position2.grid(row=2, column=0, padx=20, pady=5)
        self.ai_position3 = customtkinter.CTkLabel(self.ai_frame,
                                                                text = "Green box position",
                                                                width=400,
                                                                height=100,
                                                                fg_color=("black"),
                                                                font=customtkinter.CTkFont(size=20),
                                                                corner_radius=20,
                                                                image=self.green_image,
                                                                compound="left")
        self.ai_position3.grid(row=3, column=0, padx=20, pady=5)
        # create set frame
        self.set_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.set_frame.grid_columnconfigure(0, weight=1)
        self.set_frame_large_image_label = customtkinter.CTkLabel(self.set_frame,
                                                                   text = "SETTING",
                                                                   width=400,
                                                                   height=100,
                                                                   fg_color=("gray8"),
                                                                   font=customtkinter.CTkFont(size=20),
                                                                   corner_radius=20)
        self.set_frame_large_image_label.grid(row=0, column=0, padx=20, pady=30)
        self.set_setting1 = customtkinter.CTkLabel(self.set_frame, 
                                                             text= " Setting Velocity ", 
                                                             fg_color=("transparent"),
                                                             image=self.setting_image,
                                                             compound="left", 
                                                             font=customtkinter.CTkFont(size=20))
        self.set_setting1.place(relx=0.05, rely=0.3)
        self.slider_1 = customtkinter.CTkSlider(self.set_frame, from_=0, to=100, number_of_steps=100, command = self.update_slider_value)
        self.slider_1.place(relx=0.05, rely=0.38)
        self.set_monitor = customtkinter.CTkLabel(self.set_frame, 
                                                text=f" Velocity = {self.slider_1.get()}", 
                                                fg_color=("transparent"),
                                                image=self.per_image,
                                                compound="left", 
                                                font=customtkinter.CTkFont(size=20))
        self.set_monitor.place(relx=0.55, rely=0.36)
        # self.set_entry1 = customtkinter.CTkEntry(self.set_frame, placeholder_text="Time min [sec]")
        # self.set_entry1.place(relx=0.05, rely=0.38)

        # self.set_button1 = customtkinter.CTkButton(self.set_frame, 
        #                                                   text="",
        #                                                   width=10,
        #                                                   corner_radius=10,
        #                                                   fg_color = "transparent",
        #                                                   image=self.ask_image,anchor="w",
        #                                                   command=self.check_timeMin
        #                                                   )
        # self.set_button1.place(relx=0.38, rely=0.38)

        # self.set_entry2 = customtkinter.CTkEntry(self.set_frame, placeholder_text="Time max [sec]",state = "disabled")
        # self.set_entry2.place(relx=0.55, rely=0.38)

        # self.set_button2 = customtkinter.CTkButton(self.set_frame, 
        #                                                   text="",
        #                                                   width=10,
        #                                                   corner_radius=10,
        #                                                   fg_color = "transparent",
        #                                                   image=self.ask_image,anchor="w",
        #                                                   state = "disabled",
        #                                                   command=self.check_timeMax
        #                                                   )
        # self.set_button2.place(relx=0.88, rely=0.38)
        self.set_comment1 = customtkinter.CTkLabel(self.set_frame, 
                                                             text= " Set time min, time max for control velocity of delta robot", 
                                                             image=self.comment_image,
                                                             compound="left", 
                                                             font=customtkinter.CTkFont(size=10, weight="bold"))
        self.set_comment1.place(relx=0.05, rely=0.45)
        self.set_setting1 = customtkinter.CTkLabel(self.set_frame, 
                                                             text= " Setting Position Test ", 
                                                             fg_color=("transparent"),
                                                             image=self.setting_image,
                                                             compound="left", 
                                                             font=customtkinter.CTkFont(size=20))
        self.set_setting1.place(relx=0.05, rely=0.52)

        self.set_entry3 = customtkinter.CTkEntry(self.set_frame, placeholder_text="Position Pick 1",
                                                 width=100)
        self.set_entry3.place(relx=0.05, rely=0.6)

        # self.set_check1 = customtkinter.CTkLabel(self.set_frame, 
        #                                         text = "", 
        #                                         fg_color=("transparent"),
        #                                         image=self.check_image,
        #                                         compound="left", 
        #                                         font=customtkinter.CTkFont(size=20))
        # self.set_check1.place(relx=0.29, rely=0.6)

        # self.set_uncheck1 = customtkinter.CTkLabel(self.set_frame, 
        #                                         text = "", 
        #                                         fg_color=("transparent"),
        #                                         image=self.uncheck_image,
        #                                         compound="left", 
        #                                         font=customtkinter.CTkFont(size=20))
        # self.set_uncheck1.place(relx=0.34, rely=0.6)

        self.set_entry4 = customtkinter.CTkEntry(self.set_frame, placeholder_text="Position Pick 2",
                                                 width=100)
        self.set_entry4.place(relx=0.42, rely=0.6)

        # self.set_check2 = customtkinter.CTkLabel(self.set_frame, 
        #                                         text = "", 
        #                                         fg_color=("transparent"),
        #                                         image=self.check_image,
        #                                         compound="left", 
        #                                         font=customtkinter.CTkFont(size=20))
        # self.set_check2.place(relx=0.66, rely=0.6)

        # self.set_uncheck2 = customtkinter.CTkLabel(self.set_frame, 
        #                                         text = "", 
        #                                         fg_color=("transparent"),
        #                                         image=self.uncheck_image,
        #                                         compound="left", 
        #                                         font=customtkinter.CTkFont(size=20))
        # self.set_uncheck2.place(relx=0.71, rely=0.6)
    
        self.set_entry5 = customtkinter.CTkEntry(self.set_frame, placeholder_text="Position Pick 3",
                                                 width=100)
        self.set_entry5.place(relx=0.05, rely=0.7)

        # self.set_check3 = customtkinter.CTkLabel(self.set_frame, 
        #                                         text = "", 
        #                                         fg_color=("transparent"),
        #                                         image=self.check_image,
        #                                         compound="left", 
        #                                         font=customtkinter.CTkFont(size=20))
        # self.set_check3.place(relx=0.29, rely=0.7)

        # self.set_uncheck3 = customtkinter.CTkLabel(self.set_frame, 
        #                                         text = "", 
        #                                         fg_color=("transparent"),
        #                                         image=self.uncheck_image,
        #                                         compound="left", 
        #                                         font=customtkinter.CTkFont(size=20))
        # self.set_uncheck3.place(relx=0.34, rely=0.7)

        self.set_entry6 = customtkinter.CTkEntry(self.set_frame, placeholder_text="Position Place",
                                                 width=100)
        self.set_entry6.place(relx=0.42, rely=0.7)

        # self.set_check4 = customtkinter.CTkLabel(self.set_frame, 
        #                                         text = "", 
        #                                         fg_color=("transparent"),
        #                                         image=self.check_image,
        #                                         compound="left", 
        #                                         font=customtkinter.CTkFont(size=20))
        # self.set_check4.place(relx=0.66, rely=0.7)

        # self.set_uncheck4 = customtkinter.CTkLabel(self.set_frame, 
        #                                         text = "", 
        #                                         fg_color=("transparent"),
        #                                         image=self.uncheck_image,
        #                                         compound="left", 
        #                                         font=customtkinter.CTkFont(size=20))
        # self.set_uncheck4.place(relx=0.71, rely=0.7)

        self.set_comment2 = customtkinter.CTkLabel(self.set_frame, 
                                                             text= "! Set Posotion for test motion \n of delta robot",  
                                                             font=customtkinter.CTkFont(size=10, weight="bold"))
        self.set_comment2.place(relx=0.63, rely=0.53)
        self.set_button3 = customtkinter.CTkButton(self.set_frame, 
                                                          text="Verify Position",
                                                          width=10,
                                                          corner_radius=10,
                                                          fg_color = "gray40",
                                                          image=self.position_image,anchor="w",
                                                          command=self.button_verify
                                                          )
        self.set_button3.place(relx=0.05, rely=0.8)

        self.set_button4 = customtkinter.CTkButton(self.set_frame, 
                                                          text="Reset",
                                                          width=10,
                                                          corner_radius=10,
                                                          fg_color = "gray40",
                                                          image=self.reset_image,anchor="w",
                                                          command=self.button_reset
                                                          )
        self.set_button4.place(relx=0.41, rely=0.8)

        
        self.set_button5 = customtkinter.CTkButton(self.set_frame, 
                                                          text="Test Motion",
                                                          width=10,
                                                          corner_radius=10,
                                                          fg_color = "gray40",
                                                          image=self.move_image,anchor="w",
                                                          command=self.button_test,
                                                          state = "disabled"
                                                          
                                                          )
        self.set_button5.place(relx=0.65, rely=0.8)

        self.limit_Frequency = customtkinter.CTkEntry(self.set_frame, placeholder_text="Limit Frequency",
                                                      width=110)
        self.limit_Frequency.place(relx=0.05, rely=0.92)

        self.limit_Frequency_apply = customtkinter.CTkButton(self.set_frame, text=" Apply", width=10,
                                                          corner_radius=5, text_color="#001b20",
                                                          fg_color="#66FF33", anchor="w",
                                                          font=customtkinter.CTkFont(size=10),
                                                          command=self.button_apply_limit)
        self.limit_Frequency_apply.place(relx=0.33, rely=0.92)

        # select default frame
        self.select_frame_by_name("ai")

    def select_frame_by_name(self, name):
        # set button color for selected button
        self.home_button.configure(fg_color=( "gray25") if name == "home" else "transparent")
        self.manual_button.configure(fg_color=( "gray25") if name == "manual" else "transparent")
        self.hand_button.configure(fg_color=( "gray25") if name == "hand" else "transparent")
        self.ai_button.configure(fg_color=( "gray25") if name == "ai" else "transparent")
        self.set_button.configure(fg_color=( "gray25") if name == "set" else "transparent")
        

        # show selected frame
        if name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.home_frame.grid_forget()
        
        if name == "manual":
            self.manual_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.manual_frame.grid_forget()

        if name == "hand":
            self.hand_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.hand_frame.grid_forget()

        if name == "ai":
            self.ai_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.ai_frame.grid_forget()

        if name == "set":
            self.set_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.set_frame.grid_forget()


    def home_button_event(self):
        self.select_frame_by_name("home")

    def manual_button_event(self):
        self.select_frame_by_name("manual")
    
    def hand_button_event(self):
        self.select_frame_by_name("hand")
    
    def ai_button_event(self):
        self.select_frame_by_name("ai")

    def set_button_event(self):
        self.select_frame_by_name("set")

    def update_slider_value(self,event):
        velocity = self.slider_1.get()
        self.set_monitor.configure(text=f" Velocity = {velocity}")
    
    def update_slider1_value(self,event):
        XPstep = (self.slider_2.get()*30)/100
        XMstep = (self.slider_3.get()*30)/100
        YPstep = (self.slider_4.get()*30)/100
        YMstep = (self.slider_5.get()*30)/100
        ZPstep = (self.slider_6.get()*30)/100
        ZMstep = (self.slider_7.get()*30)/100
        
        self.manual_monitor1.configure(text=f"Step +X = {XPstep:.1f}")
        self.manual_monitor2.configure(text=f"Step -X = {-XMstep:.1f}")
        self.manual_monitor3.configure(text=f"Step +Y = {YPstep:.1f}")
        self.manual_monitor4.configure(text=f"Step -Y = {-YMstep:.1f}")
        self.manual_monitor5.configure(text=f"Step +Z = {ZPstep:.1f}")
        self.manual_monitor6.configure(text=f"Step -Z = {-ZMstep:.1f}")
    
    def CameraAI(self):
        value = self.ai_camera.get()
        if value == 1:
            self.start_camera()
        elif value == 0:
            self.stop_camera()

    
    # def CameraHand(self):
    #     value = self.hand_camera.get()
    #     cam = HandCamera()
    #     if value == 1:
    #         print("start")
    #         cam.start()
    #     elif value == 0:
    #          print("stop")
    #          cam.stop()

    def button_apply_limit(self):
        if  0 <= float(self.limit_Frequency.get()) <= 165:
            self.limit_speed = float(self.limit_Frequency.get())
            print(self.limit_speed)

    def button_reset(self):
        Reset()

    def button_test(self):
        test_Motion()

    def check_verify1(self, numCommand):

        self.numCommand = numCommand

        if (numCommand == 1):
            self.set_check1 = customtkinter.CTkLabel(self.set_frame, 
                                                text = "", 
                                                fg_color=("transparent"),
                                                image=self.check_image,
                                                compound="left", 
                                                font=customtkinter.CTkFont(size=20))
            self.set_check1.place(relx=0.29, rely=0.6)
        else:
            self.set_uncheck1 = customtkinter.CTkLabel(self.set_frame, 
                                                text = "", 
                                                fg_color=("transparent"),
                                                image=self.uncheck_image,
                                                compound="left", 
                                                font=customtkinter.CTkFont(size=20))
            self.set_uncheck1.place(relx=0.29, rely=0.6)

    def check_verify2(self, numCommand):

        self.numCommand = numCommand

        if (numCommand == 1):
            self.set_check2 = customtkinter.CTkLabel(self.set_frame, 
                                                text = "", 
                                                fg_color=("transparent"),
                                                image=self.check_image,
                                                compound="left", 
                                                font=customtkinter.CTkFont(size=20))
            self.set_check2.place(relx=0.66, rely=0.6)
        else:
            self.set_uncheck2 = customtkinter.CTkLabel(self.set_frame, 
                                                text = "", 
                                                fg_color=("transparent"),
                                                image=self.uncheck_image,
                                                compound="left", 
                                                font=customtkinter.CTkFont(size=20))
            self.set_uncheck2.place(relx=0.66, rely=0.6)

            
    def check_verify3(self, numCommand):

        self.numCommand = numCommand

        if (numCommand == 1):
            self.set_check3 = customtkinter.CTkLabel(self.set_frame, 
                                                text = "", 
                                                fg_color=("transparent"),
                                                image=self.check_image,
                                                compound="left", 
                                                font=customtkinter.CTkFont(size=20))
            self.set_check3.place(relx=0.29, rely=0.7)
        else:
            self.set_uncheck3 = customtkinter.CTkLabel(self.set_frame, 
                                                text = "", 
                                                fg_color=("transparent"),
                                                image=self.uncheck_image,
                                                compound="left", 
                                                font=customtkinter.CTkFont(size=20))
            self.set_uncheck3.place(relx=0.29, rely=0.7)

    def check_verify4(self, numCommand):

        self.numCommand = numCommand

        if (numCommand == 1):
            self.set_check4 = customtkinter.CTkLabel(self.set_frame, 
                                                text = "", 
                                                fg_color=("transparent"),
                                                image=self.check_image,
                                                compound="left", 
                                                font=customtkinter.CTkFont(size=20))
            self.set_check4.place(relx=0.66, rely=0.7)
        else:
            self.set_uncheck4 = customtkinter.CTkLabel(self.set_frame, 
                                                text = "", 
                                                fg_color=("transparent"),
                                                image=self.uncheck_image,
                                                compound="left", 
                                                font=customtkinter.CTkFont(size=20))
            self.set_uncheck4.place(relx=0.66, rely=0.7)
    
    def enable_test(self):
        self.set_button5.configure(state="normal")
    
    def button_verify(self):
        self.set_button5.configure(state="disabled")

    
        position1 = self.set_entry3.get()
        position2 = self.set_entry4.get()
        position3 = self.set_entry5.get()
        position4 = self.set_entry6.get()

        verify = []

        if ',' not in position1 and position2 and position3 and position4 :
            mbox.showerror("Error", "Invalid input format")
            return
        
        positionz1 = [int(x) for x in self.set_entry3.get().strip().split(",")]
        positionz2 = [int(x) for x in self.set_entry4.get().strip().split(",")]
        positionz3 = [int(x) for x in self.set_entry5.get().strip().split(",")]
        positionz4 = [int(x) for x in self.set_entry6.get().strip().split(",")]

        if positionz1[2] > 0 or positionz2[2] > 0 or positionz3[2] > 0 or positionz4[2] > 0:
            mbox.showerror("Error", "Please check position(x,y,z) at axis z is negative value ")
            return
            
        value1 = position1.split(',')
        c1 = checkPosition(float(value1[0]), float(value1[1]), float(value1[2]))
        result1 = c1.GetVerify()
        verify.append(result1[0])

        value2 = position2.split(',')
        c2 = checkPosition(float(value2[0]), float(value2[1]), float(value2[2]))
        result2 = c2.GetVerify()
        verify.append(result2[0])

        value3 = position3.split(',')
        c3 = checkPosition(float(value3[0]), float(value3[1]), float(value3[2]))
        result3 = c3.GetVerify()
        verify.append(result3[0])

        value4 = position4.split(',')
        c4 = checkPosition(float(value4[0]), float(value4[1]), float(value4[2]))
        result4 = c4.GetVerify()
        verify.append(result4[0])
        
        self.check_verify1(verify[0])
        self.check_verify2(verify[1])
        self.check_verify3(verify[2])
        self.check_verify4(verify[3])

        if all(i == 1 for i in verify):
            self.enable_test()

    positionman = [0,0,-450]

    def ResetManual(self):
        self.positionman[0] = 0
        self.positionman[1] = 0
        self.positionman[2] = -450
        ResetManual()


    def movePX(self):
        self.positionManual((float(self.slider_2.get()) * 30)/100,0,0)

    def moveMX(self):
        self.positionManual((-float(self.slider_3.get()) * 30)/100,0,0)

    def movePY(self):
        self.positionManual(0,(float(self.slider_4.get()) * 30)/100,0)

    def moveMY(self):
        self.positionManual(0,(-float(self.slider_5.get()) * 30)/100,0)
        

    def movePZ(self):
        self.positionManual(0,0,(float(self.slider_6.get()) * 30)/100)

    def moveMZ(self):
        self.positionManual(0,0,-(float(self.slider_7.get()) * 30)/100)

    
    
    
    def positionManual(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z
        self.positionman[0] = float(self.positionman[0]) + x
        self.positionman[1] = float(self.positionman[1]) + y
        self.positionman[2] = float(self.positionman[2]) + z
        print(self.positionman)
        
        manual(x = float(self.positionman[0]), y = float(self.positionman[1]), z = float(self.positionman[2]))
    
    def start_camera(self):
        self.camera = AICamera()
        self.camera.start()
        self.update_video()

    def stop_camera(self):
        self.camera.stop()
        del self.camera
        cv2.destroyAllWindows()

    def update_video(self):
        if self.camera is not None:
            frame = self.camera.frame_2
            if frame is not None:
                cv2.imshow("Camera", frame)
                if self.camera.predict == "RED":
                    self.ai_position1.configure(text = f"{self.camera.predict} box position\n({self.camera.position[0]},{self.camera.position[1]})")
                if self.camera.predict == "BLUE":
                    self.ai_position2.configure(text = f"{self.camera.predict} box position\n({self.camera.position[0]},{self.camera.position[1]})")
                if self.camera.predict == "GREEN":
                    self.ai_position3.configure(text = f"{self.camera.predict} box position\n({self.camera.position[0]},{self.camera.position[1]})")
        self.after(5, self.update_video) # Delay ประมาณ 10 - 15 กำลังดี

class AICamera():
    def __init__(self):
        # self.cap = cv2.VideoCapture("detect/video/video1.mp4")
        self.cap = cv2.VideoCapture(0)
        
        self.thread = None
        self.frame = None
        self.stopped = False
        self.frame_2 = None
        self.predict = None
        self.position = None
        self.app = app

    def start(self):
        if self.thread is None:
            self.thread = threading.Thread(target=self.update, args=())
            self.stopped = False
            self.thread.start()

    def showPosition(self,predict,position = [0,0]):
        self.predict = predict
        self.position = position
        
   

    def update(self):
        while not self.stopped:
            ret, self.frame = self.cap.read()
            self.frame = cv2.flip(self.frame, -1)
            
            ratio = parameter/self.frame.shape[0]
            data = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            results = model(data)
            img = np.squeeze(results.render())
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

            self.frame = cv2.line(self.frame, (640,55), (0,425), (75, 0, 130), 4)
            self.frame = cv2.line(self.frame, (459,480), (182,0), (75, 0, 130), 4)
            self.frame = cv2.putText(self.frame, "DELTA ROBOT AXIS", (480,32),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (75, 0, 130), 2)
            self.frame = cv2.putText(self.frame, "-X", (570,72),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (75, 0, 130), 2)
            self.frame = cv2.putText(self.frame, "-Y", (150,20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (75, 0, 130), 2)
            self.frame_2 = self.frame
            table = results.pandas().xyxy[0]
            if results.pandas().xyxy[0].empty is not True:
                table = results.pandas().xyxy[0]
                for re in zip(table.xmin, table.ymin, table.xmax, table.ymax, table.confidence, table.name):
                    xcCap = (re[0] + re[2])/2
                    ycCap = (re[1] + re[3])/2
                    xc = (re[0] + re[2])/2 - self.frame.shape[1]/2 
                    yc = -1*((re[1] + re[3])/2 - self.frame.shape[0]/2) 

                    # mikex = ((xcCap - 320 + 11 ) / 640 ) * 533.33
                    # mikey = ((ycCap - 240 - 21 ) / 480) * 400

                    # XcDelta = (mikex * np.cos(np.deg2rad(150)) - mikey * np.sin(np.deg2rad(150)))
                    # YcDelta = (mikex * np.sin(np.deg2rad(150)) + mikey * np.cos(np.deg2rad(150))) 
                
                    XcDelta = (xc * np.cos(np.deg2rad(150)) - yc * np.sin(np.deg2rad(150))) * ratio - 27
                    YcDelta = (xc * np.sin(np.deg2rad(150)) + yc * np.cos(np.deg2rad(150))) * ratio - 18 + 4

                    # if re[4] > 0.4 and xcCap <= 450 and xcCap >= 190 and ycCap >= 0 and ycCap <= 165:
                    if re[4] > 0.7:
                        self.frame_2 = self.frame
                        start_time = time.time()
                        if re[5] == "RED":
                            self.frame = cv2.circle(self.frame, (int(xcCap), int(ycCap)), 5, (0, 0, 255), -1)
                            self.frame = cv2.putText(self.frame, f"{XcDelta:.0f}, {YcDelta:.0f}", (int(xcCap) - 15,int(ycCap) + 20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                            self.frame = cv2.putText(self.frame,re[5], (int(re[0]) ,int(re[1]) - 10),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                            self.frame = cv2.rectangle(self.frame, (int(re[0]),int(re[1])), (int(re[2]), int(re[3])), (0,0,255), 3)
                            self.showPosition(re[5],position = [int(XcDelta),-1*(int(YcDelta))])
                        elif re[5] == "GREEN":
                            self.frame = cv2.circle(self.frame, (int(xcCap), int(ycCap)), 5, (0, 255, 0), -1)
                            self.frame = cv2.putText(self.frame, f"{XcDelta:.0f}, {YcDelta:.0f}", (int(xcCap) - 15,int(ycCap) + 20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                            self.frame = cv2.putText(self.frame,re[5], (int(re[0]) ,int(re[1]) - 10),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                            self.frame = cv2.rectangle(self.frame, (int(re[0]),int(re[1])), (int(re[2]), int(re[3])), (0, 255, 0), 3)  
                            self.showPosition(re[5],position = [int(XcDelta),-1*(int(YcDelta))])
                        elif re[5] == "BLUE":
                            self.frame = cv2.circle(self.frame, (int(xcCap), int(ycCap)), 5, (255, 0, 0), -1)
                            self.frame = cv2.putText(self.frame, f"{XcDelta:.0f}, {YcDelta:.0f}", (int(xcCap) - 15,int(ycCap) + 20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                            self.frame = cv2.putText(self.frame,re[5], (int(re[0]) ,int(re[1]) - 10),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                            self.frame = cv2.rectangle(self.frame, (int(re[0]),int(re[1])), (int(re[2]), int(re[3])), (255, 0, 0), 3)
                            self.showPosition(re[5],position = [int(XcDelta),-1*(int(YcDelta))])
                with open('data.csv', mode='w', newline='') as file:
                    writer = csv.writer(file)
                    sorted_data = sorted([(xmin, ymin, xmax, ymax, confidence, name) for xmin, ymin, xmax, ymax, confidence, name in zip(table.xmin, table.ymin, table.xmax, table.ymax, table.confidence, table.name) if confidence > 0.7], key=lambda x: x[0])
                    for count, (x_min, y_min, x_max, y_max, confidence, name) in enumerate(sorted_data, start=1):
                        # mikex = ((xcCap - 320 + 11 ) / 640 ) * 533.33
                        # mikey = ((ycCap - 240 - 21 ) / 480) * 400

                        # XcDelta = (mikex * np.cos(np.deg2rad(150)) - mikey * np.sin(np.deg2rad(150))) 
                        # YcDelta = (mikex * np.sin(np.deg2rad(150)) + mikey * np.cos(np.deg2rad(150))) 
                        
                        xc = (x_min + x_max)/2 - self.frame.shape[1]/2 
                        yc = -1*((y_min + y_max)/2 - self.frame.shape[0]/2) 

                        XcDelta = (xc * np.cos(np.deg2rad(150)) - yc * np.sin(np.deg2rad(150))) * ratio - 27 + 5
                        YcDelta = (xc * np.sin(np.deg2rad(150)) + yc * np.cos(np.deg2rad(150))) * ratio - 20
                        writer.writerow([count, start_time, XcDelta, YcDelta, name])
                
                with open('data.csv', mode='r') as file:
                    csv_reader = csv.reader(file)
                    data = [row for row in csv_reader]

                positionPlace = [[180, -60, -550], [180,-60,-490] ,[180,-60, -430]]
                
                for i in range(len(data)):
                    speed = self.app.slider_1.get()
                    ser.write(str(777).encode())

                    start_time = data[i][1]
                    XcDelta = data[i][2]
                    YcDelta = data[i][3]
                    name = data[i][4]

                    line1 = ser.readline().decode()
                    line1split = line1.split(",")

                    countCurrent = [float(line1split[0]), float(line1split[1]), float(line1split[2])]

                    posmpi = InverseKinematics(float(XcDelta),float(YcDelta),-450)
                    cal = CalCount(countCurrent, posmpi, speedUse = speed)
                    frequencympi, countmpi, timempi, dirmpi = cal.GetValue()

                    posdpi = InverseKinematics(float(XcDelta),float(YcDelta),-545)
                    cal = CompareCount(posmpi, posdpi, speedUse = speed)
                    frequencydpi, countdpi, timedpi, dirdpi = cal.GetValue()

                    posupi = InverseKinematics(float(XcDelta),float(YcDelta),-450)
                    cal = CompareCount(posdpi, posupi, speedUse = speed)
                    frequencyupi, countupi, timeupi, dirupi = cal.GetValue()

                    if name == "RED":
                        posmpl = InverseKinematics(int(positionPlace[0][0]), int(positionPlace[0][1]), -420)
                        cal = CompareCount(posupi, posmpl, speedUse = speed)
                        frequencympl, countmpl, timempl, dirmpl = cal.GetValue()

                        posdpl = InverseKinematics(int(positionPlace[0][0]), int(positionPlace[0][1]), -545)
                        cal = CompareCount(posmpl, posdpl, speedUse = speed)
                        frequencydpl, countdpl, timedpl, dirdpl = cal.GetValue()

                        posupl = InverseKinematics(int(positionPlace[0][0]), int(positionPlace[0][1]), -420)
                        cal = CompareCount(posdpl, posupl, speedUse = speed)
                        frequencyupl, countupl, timeupl, dirupl = cal.GetValue()

                    elif name == "GREEN":
                        posmpl = InverseKinematics(int(positionPlace[1][0]), int(positionPlace[1][1]), -500)
                        cal = CompareCount(posupi, posmpl, speedUse = speed)
                        frequencympl, countmpl, timempl, dirmpl = cal.GetValue()

                        posdpl = InverseKinematics(int(positionPlace[1][0]), int(positionPlace[1][1]), -545)
                        cal = CompareCount(posmpl, posdpl, speedUse = speed)
                        frequencydpl, countdpl, timedpl, dirdpl = cal.GetValue()

                        posupl = InverseKinematics(int(positionPlace[1][0]), int(positionPlace[1][1]), -545)
                        cal = CompareCount(posdpl, posupl, speedUse = speed)
                        frequencyupl, countupl, timeupl, dirupl = cal.GetValue()
                    
                    elif name == "BLUE":
                        posmpl = InverseKinematics(int(positionPlace[2][0]), int(positionPlace[2][1]), -500)
                        cal = CompareCount(posupi, posmpl, speedUse = speed)
                        frequencympl, countmpl, timempl, dirmpl = cal.GetValue()

                        posdpl = InverseKinematics(int(positionPlace[2][0]), int(positionPlace[2][1]), -545)
                        cal = CompareCount(posmpl, posdpl, speedUse = speed)
                        frequencydpl, countdpl, timedpl, dirdpl = cal.GetValue()

                        posupl = InverseKinematics(int(positionPlace[2][0]), int(positionPlace[2][1]), -400)
                        cal = CompareCount(posdpl, posupl, speedUse = speed)
                        frequencyupl, countupl, timeupl, dirupl = cal.GetValue()




                    if int(line1split[3]) == 777:
                        datampi = [frequencympi[0], frequencympi[1], frequencympi[2],countmpi[0], countmpi[1], countmpi[2], timempi, dirmpi[0], dirmpi[1], dirmpi[2]]
                        datampi = struct.pack('{}f'.format(len(datampi)), *datampi)
                        print(f"{frequencympi[0]}\n{frequencympi[1]}\n{frequencympi[2]}")
                        

                        datadpi = [frequencydpi[0], frequencydpi[1], frequencydpi[2],countdpi[0], countdpi[1], countdpi[2], timedpi, dirdpi[0], dirdpi[1], dirdpi[2]]
                        datadpi = struct.pack('{}f'.format(len(datadpi)), *datadpi)
                        

                        dataupi = [frequencyupi[0], frequencyupi[1], frequencyupi[2],countupi[0], countupi[1], countupi[2], timeupi, dirupi[0], dirupi[1], dirupi[2]]
                        dataupi = struct.pack('{}f'.format(len(dataupi)), *dataupi)
                        

                        datampl = [frequencympl[0], frequencympl[1], frequencympl[2],countmpl[0], countmpl[1], countmpl[2], timempl, dirmpl[0], dirmpl[1], dirmpl[2]]
                        datampl = struct.pack('{}f'.format(len(datampl)), *datampl)
                        

                        datadpl = [frequencydpl[0], frequencydpl[1], frequencydpl[2],countdpl[0], countdpl[1], countdpl[2], timedpl, dirdpl[0], dirdpl[1], dirdpl[2]]
                        datadpl = struct.pack('{}f'.format(len(datadpl)), *datadpl)
                        

                        dataupl = [frequencyupl[0], frequencyupl[1], frequencyupl[2],countupl[0], countupl[1], countupl[2], timeupl, dirupl[0], dirupl[1], dirupl[2]]
                        dataupl = struct.pack('{}f'.format(len(dataupl)), *dataupl)
                        
                        ser.write(datampi)
                        ser.write(datadpi)
                        ser.write(dataupi)
                        while True:
                            a = ser.readline().decode()
                            if int(a) == 77:
                                break
                        ser.write(datampl)
                        ser.write(datadpl)
                        ser.write(dataupl)

                        

                        while True:                     
                            line1 = ser.readline().decode()
                            line1split = line1.split(",")
                            print(f'Count test = {line1split[0]}, {line1split[1]}, {line1split[2]}')
                            if int(line1split[3]) == 700:
                                print(f"END Pick {i + 1}")
                                break 

            self.frame_2 = self.frame
    
    def stop(self):
        self.stopped = True
        self.thread.join()

    def __del__(self):
        self.stop()  

    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()
# class HandCamera():
class CompareCount:
    def __init__(self, posB, posA, speedUse = 100.0):

        thetaPB,thetaMB = posB.GetValue()
        thetaPA,thetaMA = posA.GetValue()

        countB = []
        for i in range(0,3):
            countB.append(thetaMB[i]*584)
    #   
        countA = []
        for i in range(0,3):
            countA.append(thetaMA[i]*584)

        countUse = []
        dirUse= []
        for i in range(0,3):
            countUse.append(abs(countA[i] - countB[i]))
    #         print((countPick[i] - countCurrent[i]))
    #         print("------------------------------------------------------------------------------------------")
            if (countA[i] - countB[i]) >= 0:
                dirUse.append(1)
            else:
                dirUse.append(0)

        predictor = Predictor()
        timeUse, frequencyUse = predictor.predict(countUse, speed = speedUse) 

        self.frequencyUse = frequencyUse 
        self.countUse = countUse
        self.timeUse = timeUse
        self.dirUse = dirUse
    def GetValue(self):
        return self.frequencyUse, self.countUse, self.timeUse, self.dirUse
    
class checkPosition():
    def __init__ (self, xp, yp, zp):
        R = 118 #รัศมีของแผ่น plate ด้านบน [mm]
        r = 112 #รัศมีของแผ่น plate ด้านล่าง [mm]
        L1 = 237 #ความยาวของขาด้านบน [mm]
        L2 = 500 #ความยาวของขาด้านล่าง [mm]
        R1 = R - r

        alpha = [np.pi/6, 5*np.pi/6, 3*np.pi/2] #องศาติดตั้งแขนแต่ละแขน [rad] เขียนเป็น column matrix
        
        self.xp = xp #ตำแหน่งที่ปลายแขนที่ต้องการ พิกัด X
        self.yp = yp #ตำแหน่งที่ปลายแขนที่ต้องการ พิกัด Y
        self.zp = zp #ตำแหน่งที่ปลายแขนที่ต้องการ พิกัด Z
        Q = [] #สร้าง List เปล่าๆไว้ใช้สำหรับใส่ค่าที่ได้จากการคำนวณ
        S = []
        Check = []
        TanThetaPlus = []
        TanThetaMinus = []
        thetaP = []
        thetaM = []

        for m in range(0,3): #คำนวณค่าต่างๆ
            Q.append((2*xp*np.cos(alpha[m])) + 2*yp*np.sin(alpha[m]))
            S.append(((xp**2) + (yp**2) + (zp**2) - (L2**2) + (L1**2) + (R1**2) )/ (-L1))
            Check.append(4*(zp**2) + 4*(R1**2) - (S[m]**2) + ((Q[m]**2) * (1-((R1/L1)**2))) - (Q[m]*((2*R1*S[m]/L1)+4*R1))) # สมการที่มีไว้เช็คตำแหน่ง
        verify = []
        all_value = all(x > 0 for x in Check)
        if all_value:
            verify.append(1)
        else:
            verify.append(0)
        self.verify = verify

    def GetVerify(self):
        return(self.verify)
    
class InverseKinematics:
    def __init__ (self, xp, yp, zp):
        import math
        #import numpy as np

        R = 118 #รัศมีของแผ่น plate ด้านบน [mm]
        r = 112 #รัศมีของแผ่น plate ด้านล่าง [mm]
        L1 = 237 #ความยาวของขาด้านบน [mm]
        L2 = 500 #ความยาวของขาด้านล่าง [mm]
        R1 = R - r

        alpha = [math.pi/6, 5*math.pi/6, 3*math.pi/2] #องศาติดตั้งแขนแต่ละแขน [rad] เขียนเป็น column matrix
        
        self.xp = xp #ตำแหน่งที่ปลายแขนที่ต้องการ พิกัด X
        self.yp = yp #ตำแหน่งที่ปลายแขนที่ต้องการ พิกัด Y
        self.zp = zp #ตำแหน่งที่ปลายแขนที่ต้องการ พิกัด Z
        Q = [] #สร้าง List เปล่าๆไว้ใช้สำหรับใส่ค่าที่ได้จากการคำนวณ
        S = []
        Check = []
        TanThetaPlus = []
        TanThetaMinus = []
        thetaP = []
        thetaM = []
        
        for m in range(0,3): #คำนวณค่าต่างๆ
            Q.append((2*xp*math.cos(alpha[m])) + 2*yp*math.sin(alpha[m]))
            S.append(((xp**2) + (yp**2) + (zp**2) - (L2**2) + (L1**2) + (R1**2) )/ (-L1))
            Check.append(4*(zp**2) + 4*(R1**2) - (S[m]**2) + ((Q[m]**2) * (1-((R1/L1)**2))) - (Q[m]*((2*R1*S[m]/L1)+4*R1))) # สมการที่มีไว้เช็คตำแหน่ง

        for n in Check:
            if n < 0:
                print('This position is impossible')
                break
        else:
            print(f'Position {xp},{yp},{zp}')
    
            for c in range(0,3):
                TanThetaPlus.append((-2*zp + math.sqrt(4*(zp**2) + 4*(R1**2) - (S[c]**2) + ((Q[c]**2) * (1-((R1/L1)**2))) - (Q[c]*((2*R1*S[c]/L1)+4*R1))))/(-2*R1 -Q[c]*((R1/L1)-1)-S[c]))
                TanThetaMinus.append((-2*zp - math.sqrt(4*(zp**2) + 4*(R1**2) - (S[c]**2) + ((Q[c]**2) * (1-((R1/L1)**2))) - (Q[c]*((2*R1*S[c]/L1)+4*R1))))/(-2*R1 -Q[c]*((R1/L1)-1)-S[c]))
    
                thetaP.append(((2*math.atan(TanThetaPlus[c]))*180)/math.pi)
                thetaM.append(((2*math.atan(TanThetaMinus[c]))*180)/math.pi)
        self.thetaP = thetaP
        self.thetaM = thetaM
        
    def GetValue(self): #เพื่อใช้ในการนำค่าไปใช้ข้างนอก class ต่อได้
        return self.thetaP,self.thetaM

class Predictor:
    def __init__(self):
        self.time = np.arange(0.0, 4.0, 0.5)
        self.frequency = [0, 20, 60, 100, 140, 180, 220, 260]
        self.count = np.array([[0,0,0,0,0,0,0,0],
                               [0,10063,20024,30259,40144,50028,59911,70151],
                               [0,30253,60194,90933,120613,150293,179973,210713],
                               [0,50448,100369,151640,201144,252279,300153,351425],
                               [0,70619,140486,212261,281560,350861,420162,491936],
                               [0,90931,180898,273295,362501,451710,540918,633313],
                               [0,111516,221853,335188,444612,554035,663460,776792],
                               [0,131593,261793,395540,524677,653813,782950,916697]])

    def predict(self, count_values, speed=100.0):
        percent_speed = speed
        set_speed = 2.5 * ((100 - percent_speed) / 100)
        time_min = set_speed + 0.2
        time_max = set_speed + 0.3
        f = interpolate.interp2d(self.time, self.frequency, self.count, kind='cubic')

        predicted_time = np.arange(time_min, time_max, 0.05)
        predicted_frequency = np.arange(0.0, 260, 0.01)  # extended range to include 0

        def find_min_error_index(predicted_count):
            errors = np.abs(predicted_count - count_value)
            return np.argmin(errors)

        time_indices = []
        frequency_indices = []
        for count_value in count_values:
            predicted_count = f(predicted_time, predicted_frequency)
            min_error_index = find_min_error_index(predicted_count)
            time_index = min_error_index % predicted_time.size
            frequency_index = min_error_index // predicted_time.size
            time_indices.append(time_index)
            frequency_indices.append(frequency_index)

        time_max = predicted_time[max(time_indices)]
        predicted_count = f(time_max, predicted_frequency)

        frequency_values = []
        while True:
            for count_value in count_values:
                min_error_index = find_min_error_index(predicted_count)
                frequency_value = predicted_frequency[min_error_index]

                # Limit frequency value to 250
                if frequency_value > app.limit_speed:
                    time_max = round(time_max + 0.01, 3)
                    predicted_count = f(time_max, predicted_frequency)
                    min_error_index = find_min_error_index(predicted_count)
                    frequency_value = predicted_frequency[min_error_index]

                frequency_values.append(frequency_value)

            if max(frequency_values) <= app.limit_speed:
                break

            time_max = round(time_max + 0.01, 3)
            predicted_count = f(time_max, predicted_frequency)
            frequency_values = []

        return time_max, frequency_values
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class CalCount:
    def __init__(self, countCurrent, pos, speedUse = 100.0):
        thetaP,thetaM = pos.GetValue()
        count = []
        for i in range(0,3):
            count.append(thetaM[i]*584)
    #         print(countPick)
    #         print("------------------------------------------------------------------------------------------")
        countUse = []
        dirUse= []
        for i in range(0,3):
            countUse.append(abs(count[i] - countCurrent[i]))
    #         print((countPick[i] - countCurrent[i]))
    #         print("------------------------------------------------------------------------------------------")
            if (count[i] - countCurrent[i]) >= 0:
                dirUse.append(1)
            else:
                dirUse.append(0)
        predictor = Predictor()
        timeUse, frequencyUse = predictor.predict(countUse, speed = speedUse) 

        self.frequencyUse = frequencyUse 
        self.countUse = countUse
        self.timeUse = timeUse
        self.dirUse = dirUse
    def GetValue(self):
        return self.frequencyUse, self.countUse, self.timeUse, self.dirUse

class Reset():
    def __init__(self):
        thread2 = threading.Thread(target= self.thReset)
        thread2.start()
    def thReset(self):
        ser.write(str(999).encode())
        while True:
            print("Function Reset")
            rs = ser.readline().decode()
            rs = int(rs)
            if rs == 900:
                print("---------------------------------------------------------")
                break

class test_Motion():
    def __init__(self):
        thread3 = threading.Thread(target= self.thTest)
        thread3.start()
        self.app = app
    def thTest(self):
        print("Function Test Motion")
        speed = self.app.slider_1.get()
        print(speed)

        positionPI1 = self.app.set_entry3.get()
        positionPI1 = [int(x) for x in positionPI1.strip().split(",")]
        

        positionPI2 = self.app.set_entry4.get()
        positionPI2 = [int(x) for x in positionPI2.strip().split(",")]
        

        positionPI3 = self.app.set_entry5.get()
        positionPI3 = [int(x) for x in positionPI3.strip().split(",")]

        
        positionPI4 = [0, -120, -528]
        

        positionPL = self.app.set_entry6.get()
        positionPL = [int(x) for x in positionPL.strip().split(",")]

        # positionPlace1 = [0,150,-542]
        # positionPlace2 = [0,150,-487]
        # positionPlace3= [0,150,-420]

        pos1 = [120,0,-528]
        pos2 = [-120,0,-528]
        pos3 = [0,120,-528]
        pos4 = [0,-120,-528]
        pos5 = [60,60,-528]
        pos6 = [-80,100,-528]
        pos7 = [100,-120,-528]
        pos8 = [-120,-120,-528]


        # positionPlace = [positionPlace1, positionPlace2, positionPlace3]
        

        operate = [pos1,pos1,pos1,pos1,pos1]

        for i in range(len(operate)):
            
            
            ser.write(str(888).encode()) 
            

            x = operate[i][0]
            y = operate[i][1]
            z = operate[i][2]

            line1 = ser.readline().decode()
            line1split = line1.split(",")
            countCurrent = [0,0,0]

            countCurrent = [float(line1split[0]), float(line1split[1]), float(line1split[2])]
            posUse = InverseKinematics(float(x),float(y),float(z))

            cal = CalCount(countCurrent, posUse, speedUse = speed)
            frequencyUse, countUse, timeUse, dirUse = cal.GetValue()

            if int(line1split[3]) == 888:

                print(f'CountCurrent [kHz] = {countCurrent}')
                # print(f'frequencyUse [kHz] =3 {frequencyUse}')
                # print(f'CountPink = {countUse}')
                # print(f'DirectionPick [0 = CW | 1 = CCW] = {dirUse}')
                # print(f'Time [sec] = {timeUse}')

                dataUse = [frequencyUse[0], frequencyUse[1], frequencyUse[2],countUse[0], countUse[1], countUse[2], timeUse, dirUse[0], dirUse[1], dirUse[2]]
                dataUse = struct.pack('{}f'.format(len(dataUse)), *dataUse)
    
                ser.write(dataUse) 

                print("------------------------------------------------------------")
                while True:                     
                    line1 = ser.readline().decode()
                    line1split = line1.split(",")
                    print(f'Count test = {line1split[0]}, {line1split[1]}, {line1split[2]}')

                    if int(line1split[3]) == 800:
                        print(f"END Pick {i + 1}")
                        time.sleep(1)
                        
                        break
            #--------------------------------------------------------------
            
            ser.write(str(888).encode()) 
            

            x = positionPL[0]
            y = positionPL[1]
            z = positionPL[2]

            line1 = ser.readline().decode()
            line1split = line1.split(",")
            countCurrent = [0,0,0]

            countCurrent = [float(line1split[0]), float(line1split[1]), float(line1split[2])]
            posUse = InverseKinematics(float(x),float(y),float(z))

            cal = CalCount(countCurrent, posUse, speedUse = speed)
            frequencyUse, countUse, timeUse, dirUse = cal.GetValue()

            if int(line1split[3]) == 888:

                print(f'CountCurrent [kHz] = {countCurrent}')
                # print(f'frequencyUse [kHz] =3 {frequencyUse}')
                # print(f'CountPink = {countUse}')
                # print(f'DirectionPick [0 = CW | 1 = CCW] = {dirUse}')
                # print(f'Time [sec] = {timeUse}')

                dataUse = [frequencyUse[0], frequencyUse[1], frequencyUse[2],countUse[0], countUse[1], countUse[2], timeUse, dirUse[0], dirUse[1], dirUse[2]]
                dataUse = struct.pack('{}f'.format(len(dataUse)), *dataUse)
    
                ser.write(dataUse) 

                print("------------------------------------------------------------")
                while True:                     
                    line1 = ser.readline().decode()
                    line1split = line1.split(",")
                    print(f'Count test = {line1split[0]}, {line1split[1]}, {line1split[2]}')

                    if int(line1split[3]) == 800:
                        print(f"END UP place {i + 1}")
                        time.sleep(0.5)
                        
                        break



# #----------------------------------------------------------------------------------------------------
#             ser.write(str(888).encode()) 
#             speed = self.app.slider_1.get()
#             print(speed)

#             x = positionPlace[i][0]
#             y = positionPlace[i][1]
#             z = positionPlace[i][2]
            
#             # x = positionPL[0]
#             # y = positionPL[1]
#             # z = positionPL[2]

#             line1 = ser.readline().decode()
#             line1split = line1.split(",")
#             # countCurrent = [0,0,0]

#             countCurrent = [float(line1split[0]), float(line1split[1]), float(line1split[2])]
#             posUse = InverseKinematics(float(x),float(y),float(z))

#             cal = CalCount(countCurrent, posUse, speedUse = speed)
#             frequencyUse, countUse, timeUse, dirUse = cal.GetValue()
            
        

#             if int(line1split[3]) == 888:

#                 print(f'CountCurrent [kHz] = {countCurrent}')
#                 # print(f'frequencyUse [kHz] =3 {frequencyUse}')
#                 # print(f'CountPink = {countUse}')
#                 # print(f'DirectionPick [0 = CW | 1 = CCW] = {dirUse}')
#                 # print(f'Time [sec] = {timeUse}')

#                 dataUse = [frequencyUse[0], frequencyUse[1], frequencyUse[2],countUse[0], countUse[1], countUse[2], timeUse, dirUse[0], dirUse[1], dirUse[2]]
#                 dataUse = struct.pack('{}f'.format(len(dataUse)), *dataUse)
    
#                 ser.write(dataUse) 

#                 print("------------------------------------------------------------")
#                 while True:                     
#                     line1 = ser.readline().decode()
#                     line1split = line1.split(",")
#                     print(f'Count test = {line1split[0]}, {line1split[1]}, {line1split[2]}')

#                     if int(line1split[3]) == 800:
#                         print(f"END Place {i + 1}")
#                         time.sleep(0.5)
#                         break
#         #--------------------------------------------------------
#             ser.write(str(888).encode()) 
#             speed = self.app.slider_1.get()
#             print(speed)

#             x = positionPlace[i][0]
#             y = positionPlace[i][1]
#             z = positionPlace[i][2]
            
#             # x = positionPL[0]
#             # y = positionPL[1]
#             # z = positionPL[2]

#             line1 = ser.readline().decode()
#             line1split = line1.split(",")
#             # countCurrent = [0,0,0]

#             countCurrent = [float(line1split[0]), float(line1split[1]), float(line1split[2])]
#             posUse = InverseKinematics(float(x),float(y),float(z)+120)

#             cal = CalCount(countCurrent, posUse, speedUse = speed)
#             frequencyUse, countUse, timeUse, dirUse = cal.GetValue()
            
        

#             if int(line1split[3]) == 888:

#                 print(f'CountCurrent [kHz] = {countCurrent}')
#                 # print(f'frequencyUse [kHz] =3 {frequencyUse}')
#                 # print(f'CountPink = {countUse}')
#                 # print(f'DirectionPick [0 = CW | 1 = CCW] = {dirUse}')
#                 # print(f'Time [sec] = {timeUse}')

#                 dataUse = [frequencyUse[0], frequencyUse[1], frequencyUse[2],countUse[0], countUse[1], countUse[2], timeUse, dirUse[0], dirUse[1], dirUse[2]]
#                 dataUse = struct.pack('{}f'.format(len(dataUse)), *dataUse)
    
#                 ser.write(dataUse) 

#                 print("------------------------------------------------------------")
#                 while True:                     
#                     line1 = ser.readline().decode()
#                     line1split = line1.split(",")
#                     print(f'Count test = {line1split[0]}, {line1split[1]}, {line1split[2]}')

#                     if int(line1split[3]) == 800:
#                         print(f"END UP Place {i + 1}")
#                         break

class ResetManual():
    def __init__(self):
        thread4 = threading.Thread(target= self.thRemanual)
        thread4.start()
        self.app = app
    def thRemanual(self):
        ser.write(str(999).encode())
        while True:
            print("Function Reset")
            rs = ser.readline().decode()
            rs = int(rs)
            if rs == 900:
                print("---------------------------------------------------------")
                break
        
        print("Reset manual Motion")
        ser.write(str(888).encode()) 
            

        x = 0
        y = 0
        z = -450

        line1 = ser.readline().decode()
        line1split = line1.split(",")

        speed = self.app.slider_1.get()

        countCurrent = [float(line1split[0]), float(line1split[1]), float(line1split[2])]
        # countCurrent = [0,0,0]

        posUse = InverseKinematics(float(x),float(y),float(z))

        cal = CalCount(countCurrent, posUse, speedUse = speed)
        frequencyUse, countUse, timeUse, dirUse = cal.GetValue()

        if int(line1split[3]) == 888:

            
                # print(f'frequencyUse [kHz] =3 {frequencyUse}')
                # print(f'CountPink = {countUse}')
                # print(f'DirectionPick [0 = CW | 1 = CCW] = {dirUse}')
                # print(f'Time [sec] = {timeUse}')

            dataUse = [frequencyUse[0], frequencyUse[1], frequencyUse[2],countUse[0], countUse[1], countUse[2], timeUse, dirUse[0], dirUse[1], dirUse[2]]
            dataUse = struct.pack('{}f'.format(len(dataUse)), *dataUse)
    
            ser.write(dataUse) 

            print("------------------------------------------------------------")
            while True:                     
                line1 = ser.readline().decode()
                line1split = line1.split(",")
                print(f'Count test = {line1split[0]}, {line1split[1]}, {line1split[2]}')

                if int(line1split[3]) == 800:
                    print("END round")
                    break

                    #  r = ser.readline().decode()
                    #  if int(r) == 800:
                    #       print("END round")
                    #       break
        with open("positionM.txt", mode="w") as f:
            f.write(f"{0},{0},{-450}\n") # เขียนข้อความว่างเปล่าเพื่อล้างไฟล์

class manual():
    def __init__(self, x = 0, y = 0, z = -450):
        self.x = x
        self.y = y
        self.z = z
        thread4 = threading.Thread(target= self.thmanual,args = [x,y,z] )
        thread4.start()
        self.app = app
    def thmanual(self,x,y,z):
        print(f"Function manual Motion {x},{y},{z}")
        speed = self.app.slider_1.get()
        print(speed)
        ser.write(str(888).encode()) 
        line1 = ser.readline().decode()
        line1split = line1.split(",")

    
        countCurrent = [float(line1split[0]), float(line1split[1]), float(line1split[2])]
        # countCurrent = [0,0,0]
        posUse = InverseKinematics(float(x),float(y),float(z))

        cal = CalCount(countCurrent, posUse, speedUse = speed)
        frequencyUse, countUse, timeUse, dirUse = cal.GetValue()


        if int(line1split[3]) == 888:

            
                # print(f'frequencyUse [kHz] =3 {frequencyUse}')
                # print(f'CountPink = {countUse}')
                # print(f'DirectionPick [0 = CW | 1 = CCW] = {dirUse}')
                # print(f'Time [sec] = {timeUse}')

            dataUse = [frequencyUse[0], frequencyUse[1], frequencyUse[2],countUse[0], countUse[1], countUse[2], timeUse, dirUse[0], dirUse[1], dirUse[2]]
            dataUse = struct.pack('{}f'.format(len(dataUse)), *dataUse)
    
            ser.write(dataUse) 

            print("------------------------------------------------------------")
            while True:                     
                line1 = ser.readline().decode()
                line1split = line1.split(",")
                print(f'Count test = {line1split[0]}, {line1split[1]}, {line1split[2]}')

                if int(line1split[3]) == 800:
                    print("END round")
                    break

                    #  r = ser.readline().decode()
                    #  if int(r) == 800:
                    #       print("END round")
                    #       break

if __name__ == "__main__":
    app = App()
    app.mainloop()
