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

    # --- Simulació a RoboDK
    robot.setSpeed(20)
    robot.MoveL(app, True)
    robot.setSpeed(10)      # més lent per fer pressió
    robot.MoveL(press, True)
    time.sleep(1.0)         # mantenir pressió 1 s
    robot.setSpeed(20)
    robot.MoveL(ret, True)
    print("Sanitizer done (simulation)")

    def pose_to_p(pose_mat):
        """Converteix una Pose() de RoboDK al format p[x,y,z,rx,ry,rz] d'URScript"""
        xyzrpw = Pose_2_UR(pose_mat)  # [x, y, z, rx, ry, rz]
        return "p[{:.6f}, {:.6f}, {:.6f}, {:.6f}, {:.6f}, {:.6f}]".format(*xyzrpw)

    # --- Enviament al robot real
    if robot_is_connected:
        send_ur_script(set_tcp)
        receive_response(0.2)
        movel_app   = f"movel({pose_to_p(app.Pose())},{accel_mss},{speed_ms},{timel},{blend_r})"
        movel_press = f"movel({pose_to_p(press.Pose())},{accel_mss},{speed_ms/2},{timel/2},{blend_r})"
        movel_ret   = f"movel({pose_to_p(ret.Pose())},{accel_mss},{speed_ms},{timel},{blend_r})"
        send_ur_script(movel_app);   receive_response(timel)
        send_ur_script(movel_press); receive_response(timel/2 + 1.0)
        send_ur_script(movel_ret);   receive_response(timel)
        print("Sanitizer (URScript) sent")

def Adjust_light():
    """Moviment per ajustar la llum cap amunt, esquerra i dreta"""
    print("Adjust light")

    app_light   = RDK.Item('app_light')
    adjust_left  = RDK.Item('adjust_left')
    adjust_right = RDK.Item('adjust_right')

    if not (app_light.Valid() and adjust_left.Valid() and adjust_right.Valid()):
        print("Adjust light targets not found!")
        return

    # --- Simulació a RoboDK
    robot.setSpeed(20)
    robot.MoveL(app_light, True)
    robot.setSpeed(15)
    robot.MoveL(adjust_left, True)
    robot.MoveL(adjust_right, True)
    robot.MoveL(app_light, True)
    print("Adjust light done (simulation)")

    def pose_to_p(pose_mat):
        """Converteix una Pose() de RoboDK al format p[x,y,z,rx,ry,rz] d'URScript"""
        xyzrpw = Pose_2_UR(pose_mat)  # [x, y, z, rx, ry, rz]
        return "p[{:.6f}, {:.6f}, {:.6f}, {:.6f}, {:.6f}, {:.6f}]".format(*xyzrpw)

    # --- Enviament al robot real
    if robot_is_connected:
        send_ur_script(set_tcp)
        receive_response(0.2)

        movel_app    = f"movel({pose_to_p(app_light.Pose())},{accel_mss},{speed_ms},{timel},{blend_r})"
        movel_left   = f"movel({pose_to_p(adjust_left.Pose())},{accel_mss},{speed_ms},{timel},{blend_r})"
        movel_right  = f"movel({pose_to_p(adjust_right.Pose())},{accel_mss},{speed_ms},{timel},{blend_r})"
        movel_return = f"movel({pose_to_p(app_light.Pose())},{accel_mss},{speed_ms},{timel},{blend_r})"

        send_ur_script(movel_app);    receive_response(timel)
        send_ur_script(movel_left);   receive_response(timel)
        send_ur_script(movel_right);  receive_response(timel)
        send_ur_script(movel_return); receive_response(timel)

        print("Adjust light (URScript) sent")

# -----------------------------
# Main
def main():
    global robot_is_connected
    robot_is_connected = check_robot_port(ROBOT_IP, ROBOT_PORT)

    Init()
    Wave()
    Press_sanitizer()
    Adjust_light() 
    if robot_is_connected:
        robot_socket.close()

# -----------------------------
if __name__ == "__main__":
    main()
