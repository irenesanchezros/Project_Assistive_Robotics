import os
import time
import socket
import math
from robodk.robolink import *   # API RoboDK
from robodk.robomath import *   # Funcions útils

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

# Targets 
Init_target = RDK.Item('Init')
Pick_drug_target = RDK.Item('Pick_drug')
Move_drug_target = RDK.Item('Move_drug')
Drop_drug_target = RDK.Item('Drop_drug')
Mix_solution_target = RDK.Item('Mix_solution')

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
# Moviments bàsics
def Init():
    print("Init")
    if Init_target.Valid():
        robot.MoveL(Init_target, True)
    else:
        print("Init target not found!")
    if robot_is_connected:
        send_ur_script(set_tcp)
        receive_response(1)
        send_ur_script(movej_init)
        receive_response(timej)


#comments on github

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

def Press_sanitizer():
    """Moviment per prémer el dosificador i deixar caure el gel a la mà."""
    print("Press sanitizer")

    app  = RDK.Item('App_sanitizer')
    press = RDK.Item('Press_sanitizer')
    ret   = RDK.Item('Ret_sanitizer')

    if not (app.Valid() and press.Valid() and ret.Valid()):
        print("Sanitizer targets not found!")
        return

    robot.setSpeed(20)
    robot.MoveL(app, True)
    robot.setSpeed(10)
    robot.MoveL(press, True)
    time.sleep(1.0)
    robot.setSpeed(20)
    robot.MoveL(ret, True)
    print("Sanitizer done (simulation)")

def Adjust_light():
    """Moviment per ajustar la llum cap amunt, esquerra i dreta"""
    print("Adjust light")

    app_light   = RDK.Item('App_light')
    adjust_left  = RDK.Item('Adjust_left')
    adjust_right = RDK.Item('Adjust_right')

    if not (app_light.Valid() and adjust_left.Valid() and adjust_right.Valid()):
        print("Adjust light targets not found!")
        return

    robot.setSpeed(20)
    robot.MoveL(app_light, True)
    robot.setSpeed(15)
    robot.MoveL(adjust_left, True)
    robot.MoveL(adjust_right, True)
    robot.MoveL(app_light, True)
    print("Adjust light done (simulation)")

# -----------------------------
# Nous moviments
def Pick_drug():
    print("Pick drug")
    if Pick_drug_target.Valid():
        robot.MoveL(Pick_drug_target, True)
    else:
        print("Pick_drug target not found!")

def Move_drug():
    print("Move drug")
    if Move_drug_target.Valid():
        robot.MoveL(Move_drug_target, True)
    else:
        print("Move_drug target not found!")

def Drop_drug():
    print("Drop drug")
    if Drop_drug_target.Valid():
        robot.MoveL(Drop_drug_target, True)
    else:
        print("Drop_drug target not found!")

def Mix_solution():
    """
    Stirring movement: circular motion in X-Z plane (Y fixed).
    """
    print("Mix solution")
    if not Mix_solution_target.Valid():
        print("Mix_solution target not found!")
        return

    center_pose = Mix_solution_target.Pose()
    print("Center pose found. Starting X-Z stirring...")

    # Parameters
    radius_mm = 30.0      # radius in mm
    x_offset = 0 #X fixed
    turns = 3             # number of turns
    steps = 60            # points per turn
    total_points = turns * steps

    # Faster speed for stirring
    robot.setSpeed(1000)
    delay_per_move = 0.00001

    try:
        # approach from above
        approach = center_pose * transl(0, 0, 50)
        robot.MoveL(approach, True)
        robot.MoveL(center_pose, True)

        # perform X-Z circular motion
        for i in range(total_points):
            angle = 2.0 * math.pi * (i / steps)
            y= radius_mm * math.sin(angle)
            z = radius_mm * math.cos(angle)
            new_pose = center_pose * transl(x_offset, y, z)
            robot.MoveL(new_pose, True)
            time.sleep(delay_per_move)

        # return to center and move up
        robot.MoveL(center_pose, True)
        robot.MoveL(approach, True)
        print("Mix solution done (X-Z plane)")

    except Exception as e:
        print("Error during Mix_solution():", e)


# -----------------------------
# Main
def main():
    global robot_is_connected
    robot_is_connected = check_robot_port(ROBOT_IP, ROBOT_PORT)

    Init()
    Wave()
    Press_sanitizer()
    Adjust_light()

    # Seqüència nova
    Pick_drug()
    Move_drug()
    Drop_drug()
    Mix_solution()

    if robot_is_connected:
        robot_socket.close()

# -----------------------------
if __name__ == "__main__":
    main()
