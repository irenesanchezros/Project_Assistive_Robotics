import os
import time
import socket
import tkinter as tk
from tkinter import messagebox
from math import radians, degrees, pi
import numpy as np
from robodk.robolink import *
from robodk.robomath import *

# Load RoboDK project from relative path
relative_path = "src/roboDK/Assistive_UR5e.rdk"
absolute_path = os.path.abspath(relative_path)
RDK = Robolink()
print("Loading RoboDK...")
time.sleep(5)
RDK.AddFile(absolute_path)
print("Loading RoboDK Project...")
time.sleep(3)

# Robot setup
robot = RDK.Item("UR5e")
base = RDK.Item("UR5e Base")
tool = RDK.Item('Hand')
Init_target = RDK.Item('Init')
App_shake_target = RDK.Item('App_shake')
Shake_target = RDK.Item('Shake')
App_give5_target = RDK.Item('App_give5')
Give5_target = RDK.Item('Give5')

robot.setPoseFrame(base)
robot.setPoseTool(tool)
robot.setSpeed(20)

# Robot Constants
ROBOT_IP = '192.168.1.5'
ROBOT_PORT = 30002
accel_mss = 1.2
speed_ms = 0.75
blend_r = 0.0
timej = 6
timel = 4

# URScript commands
set_tcp = "set_tcp(p[0.000000, 0.000000, 0.050000, 0.000000, 0.000000, 0.000000])"
movej_init = f"movej([-1.009423, -1.141297, -1.870417, 3.011723, -1.009423, 0.000000],1.20000,0.75000,{timel},0.0000)"
movel_app_shake = f"movel([-2.268404, -1.482966, -2.153143, -2.647089, -2.268404, 0.000000],{accel_mss},{speed_ms},{timel},0.000)"
movel_shake = f"movel([-2.268404, -1.663850, -2.294637, -2.324691, -2.268404, 0.000000],{accel_mss},{speed_ms},{timel/2},0.000)"
movel_app_give5 = f"movel([-2.280779, -1.556743, -2.129529, 5.257071, -1.570796, 2.280779],{accel_mss},{speed_ms},{timel},0.000)"
movel_give5 = f"movel([-2.195869, -1.642206, -2.040971, 5.253965, -1.570796, 2.195869],{accel_mss},{speed_ms},{timel/2},0.000)"

# Check robot connection
def check_robot_port(ip, port):
    global robot_socket
    try:
        robot_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        robot_socket.settimeout(1)
        robot_socket.connect((ip, port))
        return True
    except (socket.timeout, ConnectionRefusedError):
        return False
# Send URScript command
def send_ur_script(command):
    robot_socket.send((command + "\n").encode())

# Wait for robot response
def receive_response(t):
    try:
        print("Waiting time:", t)
        time.sleep(t)
    except socket.error as e:
        print(f"Error receiving data: {e}")
        exit(1)

# Movements
def Init():
    print("Init")
    robot.MoveL(Init_target, True)
    print("Init_target REACHED")
    if robot_is_connected:
        print("Init REAL UR5e")
        send_ur_script(set_tcp)
        receive_response(1)
        send_ur_script(movej_init)
        receive_response(timej)
    else:
        print("UR5e not connected. Simulation only.")

def Hand_shake():
    print("Hand Shake")
    robot.setSpeed(20)
    robot.MoveL(App_shake_target, True)
    robot.setSpeed(100)
    robot.MoveL(Shake_target, True)
    robot.MoveL(App_shake_target, True)
    print("Hand Shake FINISHED")
    if robot_is_connected:
        print("App_shake REAL UR5e")
        send_ur_script(set_tcp)
        receive_response(1)
        send_ur_script(movel_app_shake)
        receive_response(timel)
        send_ur_script(movel_shake)
        receive_response(timel)
        send_ur_script(movel_app_shake)
        receive_response(timel)

def Give_me_5():
    print("Give me 5!")
    robot.setSpeed(20)
    robot.MoveL(App_give5_target, True)
    robot.setSpeed(100)
    robot.MoveL(Give5_target, True)
    robot.MoveL(App_give5_target, True)
    print("Give me 5! FINISHED")
    if robot_is_connected:
        print("Give5 REAL UR5e")
        send_ur_script(set_tcp)
        receive_response(1)
        send_ur_script(movel_app_give5)
        receive_response(timel)
        send_ur_script(movel_give5)
        receive_response(timel)
        send_ur_script(movel_app_give5)
        receive_response(timel)

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

# Main function
def main():
    global robot_is_connected
    robot_is_connected = check_robot_port(ROBOT_IP, ROBOT_PORT)
    Init()
    Hand_shake()
    Give_me_5()
    if robot_is_connected:
        robot_socket.close()

# Run and close
if __name__ == "__main__":
    main()
    #confirm_close()
    RDK.CloseRoboDK()
