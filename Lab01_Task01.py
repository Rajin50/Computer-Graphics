#TASK- 01

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random

# Rain properties
rain_drops = []

for i in range(100):
    x = random.randint(0, 500)
    y = random.randint(300, 500)
    rain_drops.append((x, y))
rain_direction = 0

# Background color (0 = night, 1 = day)
background_brightness = 0.0

def draw_house():
    # House body (using two triangles)
    glColor3f(0.678, 0.847, 0.902)
    glBegin(GL_TRIANGLES)
    glVertex2f(200, 100)
    glVertex2f(200, 250)
    glVertex2f(350, 250)
    glEnd()

    glBegin(GL_TRIANGLES)
    glVertex2f(200, 100)
    glVertex2f(350, 250)
    glVertex2f(350, 100)
    glEnd()

    # Roof
    glColor3f(0.5, 0.5, 0.5)
    glBegin(GL_TRIANGLES)
    glVertex2f(175, 250)
    glVertex2f(375, 250)
    glVertex2f(275, 350)
    glEnd()

    # Door
    glColor3f(0.5, 0.5, 0.5)
    glBegin(GL_TRIANGLES)
    glVertex2f(260, 100)
    glVertex2f(260, 180)
    glVertex2f(290, 180)
    glEnd()

    glBegin(GL_TRIANGLES)
    glVertex2f(260, 100)
    glVertex2f(290, 180)
    glVertex2f(290, 100)
    glEnd()

    # Windows (Left Window)
    glBegin(GL_TRIANGLES)
    glVertex2f(220, 180)
    glVertex2f(220, 220)
    glVertex2f(250, 220)
    glEnd()

    glBegin(GL_TRIANGLES)
    glVertex2f(220, 180)
    glVertex2f(250, 220)
    glVertex2f(250, 180)
    glEnd()

    # Windows (Right Window)
    glBegin(GL_TRIANGLES)
    glVertex2f(300, 180)
    glVertex2f(300, 220)
    glVertex2f(330, 220)
    glEnd()

    glBegin(GL_TRIANGLES)
    glVertex2f(300, 180)
    glVertex2f(330, 220)
    glVertex2f(330, 180)
    glEnd()


def draw_rain():
    glColor3f(0.6, 0.6, 1.0)
    glBegin(GL_LINES)
    for i in range(len(rain_drops)):
        x, y = rain_drops[i]
        glVertex2f(x, y)
        glVertex2f(x + rain_direction, y - 10)
    glEnd()


def update_rain(value):
    global rain_drops
    for i in range(len(rain_drops)):
        x, y = rain_drops[i]
        y -= 10
        x += rain_direction
        if y < 0:
            y = random.randint(300, 500)
            x = random.randint(0, 500)
        rain_drops[i] = (x, y)
    glutPostRedisplay()
    glutTimerFunc(50, update_rain, 0)


def change_background_light(increase):
    global background_brightness
    if increase:
        background_brightness = min(1.0, background_brightness + 0.05)
    else:
        background_brightness = max(0.0, background_brightness - 0.05)


def keyboard_listener(key, x, y):
    global rain_direction, background_brightness
    key = key.decode("utf-8")
    if key == 'a':  # Dark to Light (Night to Day)
        change_background_light(True)
    elif key == 'd':  # Light to Dark (Day to Night)
        change_background_light(False)


def special_keys(key, x, y):
    global rain_direction
    if key == GLUT_KEY_LEFT:
        rain_direction -= 1
    elif key == GLUT_KEY_RIGHT:
        rain_direction += 1


def iterate():
    glViewport(0, 0, 500, 500)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, 500, 0.0, 500, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def showScreen():
    glClearColor(background_brightness, background_brightness, background_brightness, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    iterate()
    draw_house()
    draw_rain()
    glutSwapBuffers()


glutInit()
glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
glutInitWindowSize(500, 500)
glutInitWindowPosition(0, 0)
wind = glutCreateWindow(b"OpenGL House in Rain")
glutDisplayFunc(showScreen)
glutTimerFunc(50, update_rain, 0)
glutKeyboardFunc(keyboard_listener)
glutSpecialFunc(special_keys)
glutMainLoop()










