import os
import time
import socket
from robodk.robolink import *   # API RoboDK
from robodk.robomath import *   # Fonctions utiles

# -----------------------------
# Load RoboDK project
relative_path = "src/roboDK/Assistive_UR5e.rdk"
absolute_path = os.path.abspath(relative_path)
RDK = Robolink()
RDK.AddFile(absolute_path)

# -----------------------------
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

# -----------------------------
# Robot Constants
ROBOT_IP = '192.168.1.5'
ROBOT_PORT = 30002
accel_mss = 1.2
speed_ms = 0.75
blend_r = 0.0
timej = 6
timel = 4

# -----------------------------
# URScript commands
set_tcp = "set_tcp(p[0.000000, 0.000000, 0.050000, 0.000000, 0.000000, 0.000000])"
movej_init = f"movej([-1.009423, -1.141297, -1.870417, 3.011723, -1.009423, 0.000000],1.20000,0.75000,{timel},0.0000)"
movel_app_shake = f"movel([-2.268404, -1.482966, -2.153143, -2.647089, -2.268404, 0.000000],{accel_mss},{speed_ms},{timel},0.000)"
movel_shake = f"movel([-2.268404, -1.663850, -2.294637, -2.324691, -2.268404, 0.000000],{accel_mss},{speed_ms},{timel/2},0.000)"
movel_app_give5 = f"movel([-2.280779, -1.556743, -2.129529, 5.257071, -1.570796, 2.280779],{accel_mss},{speed_ms},{timel},0.000)"
movel_give5 = f"movel([-2.195869, -1.642206, -2.040971, 5.253965, -1.570796, 2.195869],{accel_mss},{speed_ms},{timel/2},0.000)"

# -----------------------------
# Socket connection
def check_robot_port(ip, port):
    global robot_socket
    try:
        robot_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        robot_socket.settimeout(1)
        robot_socket.connect((ip, port))
        return True
    except (socket.timeout, ConnectionRefusedError):
        return False

def send_ur_script(command):
    robot_socket.send((command + "\n").encode())

def receive_response(t):
    time.sleep(t)

# -----------------------------
# Movements
def Init():
    print("Init")
    robot.MoveL(Init_target, True)
    if robot_is_connected:
        send_ur_script(set_tcp)
        receive_response(1)
        send_ur_script(movej_init)
        receive_response(timej)

def Hand_shake():
    print("Hand Shake")
    robot.setSpeed(20)
    robot.MoveL(App_shake_target, True)
    robot.setSpeed(100)
    robot.MoveL(Shake_target, True)
    robot.MoveL(App_shake_target, True)
    if robot_is_connected:
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
    if robot_is_connected:
        send_ur_script(set_tcp)
        receive_response(1)
        send_ur_script(movel_app_give5)
        receive_response(timel)
        send_ur_script(movel_give5)
        receive_response(timel)
        send_ur_script(movel_app_give5)
        receive_response(timel)

def Wave():
    print("Wave")
    wave_start = RDK.Item('Wave_start')
    wave_left = RDK.Item('Wave_left')
    wave_right = RDK.Item('Wave_right')

    if wave_start.Valid() and wave_left.Valid() and wave_right.Valid():
        robot.MoveJ(wave_start)
        for i in range(3):
            robot.MoveL(wave_left)
            robot.MoveL(wave_right)
        robot.MoveJ(wave_start)
        print("Wave FINISHED")
    else:
        print("Wave targets are not found!")

# -----------------------------
# Main
def main():
    global robot_is_connected
    robot_is_connected = check_robot_port(ROBOT_IP, ROBOT_PORT)

    Init()
    Hand_shake()
    Give_me_5()
    Wave()

    if robot_is_connected:
        robot_socket.close()

# -----------------------------
if __name__ == "__main__":
    main()
