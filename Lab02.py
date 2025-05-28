# Name: RAJIN IBNA RAJUANUR RAHMAN
# Student ID: 22101717
# CSE423 Lab Section: 01
# Lab No: 02

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
W_Width,W_Height=400,500
speed= 0.5
create_new=False
game_over = False

class point:
    def __init__(self):
        self.x=0
        self.y=0
        self.z=0

def crossProduct(a, b):
    result=point()
    result.x = a.y * b.z - a.z * b.y
    result.y = a.z * b.x - a.x * b.z
    result.z = a.x * b.y - a.y * b.x
    return result

def convert_coordinate(x,y):
    global W_Width, W_Height
    a = x - (W_Width/2)
    b = (W_Height/2) - y
    return a,b

def draw_points(x, y, s):
    glPointSize(s) #pixel size. by default 1 thake
    glBegin(GL_POINTS)
    glVertex2f(x,y) #jekhane show korbe pixel
    glEnd()

def specialKeyListener(key, x, y):
    global c_p1, c_p2, c_p3, c_p4, game_over
    if key == 'w':
        print(1)
    s = 20
    catcher_left_edge = min(c_p1[0], c_p2[0], c_p3[0], c_p4[0])
    catcher_right_edge = max(c_p1[2], c_p2[2], c_p3[2], c_p4[2])
    screen_left = -250
    screen_right = 250

    if not pause and not game_over:
        if key == GLUT_KEY_LEFT:
            if catcher_left_edge - s >= screen_left:
                for cp in [c_p1, c_p2, c_p3, c_p4]:
                    cp[0] -= s
                    cp[2] -= s

        if key == GLUT_KEY_RIGHT:
            if catcher_right_edge + s <= screen_right:
                for cp in [c_p1, c_p2, c_p3, c_p4]:
                    cp[0] += s
                    cp[2] += s

    glutPostRedisplay()

def mouseListener(button, state, x, y): # x, y is the x-y of the screen (2D)
    global create_new, y_start, gamepoint, pause, cat_color
    global speed, game_over, d_color
    global c_p1, c_p2, c_p3, c_p4, ran_x1  # Also reset catcher position!

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        # Exit button
        if x >= 360 and x <= 390 and y >= 15 and y <= 45:
            print("Goodbye!")
            glutLeaveMainLoop()

        # Pause/Resume button
        elif x >= 170 and x <= 220 and y >= 10 and y <= 45:
            pause = not pause

        # Restart button (left arrow)
        elif x >= 6 and x <= 50 and y >= 10 and y <= 45:
            print("Starting Over!")
            # Reset game state
            y_start = 210
            ran_x1 = random.randint(-250, 230)
            gamepoint = 0
            speed = 1
            pause = False
            game_over = False
            cat_color = [1, 1, 1]
            d_color = [random.random(), random.random(), random.random()]

            # Reset catcher position
            c_p1 = [-70, -235, 70, -235]
            c_p2 = [-50, -250, 50, -250]
            c_p3 = [-50, -250, -70, -235]
            c_p4 = [50, -250, 70, -235]

    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        create_new = convert_coordinate(x, y)

    glutPostRedisplay()

def MidPointLine(x1, y1, x2, y2):
    points = []
    dx = x2 - x1
    dy = y2 - y1
    d = 2*dy - dx
    incE = 2*dy
    incNE = 2*dy - 2*dx
    x = x1
    y = y1
    for i in range(int(x), int(x2)+1):
        points += [[i, y]]
        if d > 0:
            d += incNE
            y += 1
        else:
            d += incE
    return points

def findZone(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if dx>0 and dy>=0:
        if abs(dx) > abs(dy):
            return 0
        else:
            return 1
    elif dx<=0 and dy>=0:
        if abs(dx) > abs(dy):
            return 3
        else:
            return 2
    elif dx < 0 and dy < 0:
        if abs(dx) > abs(dy):
            return 4
        else:
            return 5
    elif dx >= 0 and dy < 0:
        if abs(dx) > abs(dy):
            return 7
        else:
            return 6

def convertToZone0(zone, x1, y1, x2, y2):
    if zone == 1:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
    elif zone == 2:
        x1, y1 = y1, -x1
        x2, y2 = y2, -x2
    elif zone == 3:
        x1, y1 = -x1, y1
        x2, y2 = -x2, y2
    elif zone == 4:
        x1, y1 = -x1, -y1
        x2, y2 = -x2, -y2
    elif zone == 5:
        x1, y1 = -y1, -x1
        x2, y2 = -y2, -x2
    elif zone == 6:
        x1, y1 = -y1, x1
        x2, y2 = -y2, x2
    elif zone == 7:
        x1, y1 = x1, -y1
        x2, y2 = x2, -y2
    return x1, y1, x2, y2

def convertToZoneM(color, zone, points):
    s = 2
    glColor3f(color[0], color[1], color[2])
    if zone ==0:
        for x, y in points:
            draw_points(x, y, s)
    elif zone == 1:
        for x, y in points:
            draw_points(y, x, s)
    elif zone == 2:
        for x, y in points:
            draw_points(-y, x, s)
    elif zone == 3:
        for x, y in points:
            draw_points(-x, y, s)
    elif zone == 4:
        for x, y in points:
            draw_points(-x, -y, s)
    elif zone == 5:
        for x, y in points:
            draw_points(-y, -x, s)
    elif zone == 6:
        for x, y in points:
            draw_points(y, -x, s)
    elif zone == 7:
        for x, y in points:
            draw_points(x, -y, s)

def drawLines(color, x1, y1, x2, y2):
    zone = findZone(x1, y1, x2, y2)
    x1, y1, x2, y2 = convertToZone0(zone, x1, y1, x2, y2)
    points = MidPointLine(x1, y1, x2, y2)
    convertToZoneM(color, zone, points)

import random
ran_x1 = 50
y_start = 210
c_p1 = [-70, -235, 70, -235]
c_p2 = [-50, -250, 50, -250]
c_p3 = [-50, -250, -70, -235]
c_p4 = [ 50, -250, 70, -235]
pause = False
cat_color = [1, 1, 1]

d_color = [random.random(), random.random(), random.random()]
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(0,0,0,0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0,0,200, 0,0,0, 0,1,0)
    glMatrixMode(GL_MODELVIEW)

    global c_p1, c_p2, c_p3, c_p4, cat_color, d_color, game_over
    drawLines(cat_color, c_p1[0], c_p1[1], c_p1[2], c_p1[3])
    drawLines(cat_color, c_p2[0], c_p2[1], c_p2[2], c_p2[3])
    drawLines(cat_color, c_p3[0], c_p3[1], c_p3[2], c_p3[3])
    drawLines(cat_color, c_p4[0], c_p4[1], c_p4[2], c_p4[3])

    # Drawing exit
    color = [1,0,0]
    drawLines(color, 240, 240, 210, 210)
    drawLines(color, 240, 210, 210, 240)

    #Drawing pause
    color = [1, 0.984, 0]
    if pause == False:
        drawLines(color, 5, 210, 5, 240)
        drawLines(color, -5, 210, -5, 240)
    else:
        drawLines(color, -15, 210, -15, 240)
        drawLines(color, -15, 240, 20, 225)
        drawLines(color, -15, 210, 20, 225)

    # Drawing restart
    color = [0,0,1]
    drawLines(color, -200, 225, -240, 225)
    drawLines(color, -218, 240, -240, 225)
    drawLines(color, -218, 210, -240, 225)

    if not game_over:
        # Drawing diamond
        color = [0, 0, 0]
        a = 20
        b = 26
        global ran_x1, y_start
        drawLines(color, ran_x1, y_start, ran_x1 + a, y_start)
        drawLines(color, ran_x1, y_start - b, ran_x1 + a, y_start - b)
        drawLines(color, ran_x1, y_start - b, ran_x1, y_start)
        drawLines(color, ran_x1 + a, y_start - b, ran_x1 + a, y_start)
        d_p1 = [int((ran_x1 + ran_x1 + a) / 2), y_start]
        d_p2 = [ran_x1 + a, int((y_start + y_start - b) / 2)]
        d_p3 = [d_p1[0], y_start - b]
        d_p4 = [ran_x1, d_p2[1]]
        color = [0.941, 0.922, 0.541]
        drawLines(d_color, d_p1[0], d_p1[1], d_p2[0], d_p2[1])
        drawLines(d_color, d_p2[0], d_p2[1], d_p3[0], d_p3[1])
        drawLines(d_color, d_p3[0], d_p3[1], d_p4[0], d_p4[1])
        drawLines(d_color, d_p4[0], d_p4[1], d_p1[0], d_p1[1])

    glutSwapBuffers()

gamepoint = 0
def animate():
    global ran_x1, y_start, c_p1, gamepoint, pause, cat_color, d_color, speed, game_over

    if pause or game_over:
        glutPostRedisplay()
        return

    if y_start <= -214:
        if c_p1[0] < ran_x1 + 20 and c_p1[2] > ran_x1:
            # Caught!
            y_start = 210
            ran_x1 = random.randint(-250, 230)
            gamepoint += 1
            speed = min(speed + 0.05, 5)  # max speed = 5
            d_color = [random.random(), random.random(), random.random()]
            print(f'Score: {gamepoint}')
        else:
            game_over = True
            cat_color = [1, 0, 0]
            print(f"Game Over! Score: {gamepoint}")
    else:
        y_start -= speed

    glutPostRedisplay()


def init():
    glClearColor(0, 0, 0, 0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(104, 1, 1, 1000.0)

glutInit()
glutInitWindowSize(W_Width, W_Height)
glutInitWindowPosition(500, 0)
glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGB)
wind = glutCreateWindow(b"Catch the Diamonds Game")
init()
glutDisplayFunc(display)
glutIdleFunc(animate)
glutSpecialFunc(specialKeyListener)
glutMouseFunc(mouseListener)
glutMainLoop()





