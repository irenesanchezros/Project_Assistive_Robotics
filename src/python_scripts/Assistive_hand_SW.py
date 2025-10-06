import os
import time
import tkinter as tk
from tkinter import messagebox
from robodk.robolink import *
from robodk.robomath import *

# Define relative path to the .rdk file
relative_path = "src/roboDK/Assistive_UR5e.rdk"
absolute_path = os.path.abspath(relative_path)

# Start RoboDK with the project file
RDK = Robolink()
print("Loading RoboDK...")
time.sleep(5)
RDK.AddFile(absolute_path)
print("Loading RoboDK Project...")
time.sleep(3)

# Retrieve items from the RoboDK station
robot = RDK.Item("UR5e")
base = RDK.Item("UR5e Base")
tool = RDK.Item("Hand")
Init_target = RDK.Item("Init")
App_shake_target = RDK.Item("App_shake")
Shake_target = RDK.Item("Shake")
App_give5_target = RDK.Item("App_give5")
Give5_target = RDK.Item("Give5")

# Set robot frame, tool and speed
robot.setPoseFrame(base)
robot.setPoseTool(tool)
robot.setSpeed(20)

# Move to initial position
def move_to_init():
    print("Init")
    robot.MoveL(Init_target, True)
    print("Init_target REACHED")

# Perform handshake sequence
def hand_shake():
    print("Hand Shake")
    robot.MoveL(App_shake_target, True)
    robot.MoveL(Shake_target, True)
    robot.MoveL(App_shake_target, True)
    print("Hand Shake FINISHED")

# Perform "Give me 5" sequence
def give_me_5():
    print("Give me 5!")
    robot.MoveL(App_give5_target, True)
    robot.MoveL(Give5_target, True)
    robot.MoveL(App_give5_target, True)
    print("Give me 5! FINISHED")

# Main sequence
def main():
    move_to_init()
    hand_shake()
    give_me_5()
    move_to_init()

# Confirmation dialog to close RoboDK
def confirm_close():
    root = tk.Tk()
    root.withdraw()
    response = messagebox.askquestion(
        "Close RoboDK",
        "Do you want to save changes before closing RoboDK?",
        icon='question'
    )
    if response == 'yes':
        RDK.Save()
        RDK.CloseRoboDK()
        print("RoboDK saved and closed.")
    else:
        RDK.CloseRoboDK()
        print("RoboDK closed without saving.")

# Run main and handle closing
if __name__ == "__main__":
    main()
    #confirm_close()
