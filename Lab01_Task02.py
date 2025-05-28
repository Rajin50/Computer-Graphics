from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random

# Global variables
points = []  # Stores (x, y, dx, dy, r, g, b) for each point
speed = 1  # Speed factor
blinking = False
frozen = False
blink_state = True

def generate_point(x, y):
    # Generates a new point with random direction and color.
    dx = random.choice([-1, 1]) * speed
    dy = random.choice([-1, 1]) * speed
    r, g, b = random.random(), random.random(), random.random()
    points.append([x, y, dx, dy, r, g, b])

def draw_points():
    # Draws all the moving points.
    global blink_state
    glPointSize(5)
    glBegin(GL_POINTS)
    for p in points:
        x, y, dx, dy, r, g, b = p
        if blinking:
            glColor3f(r * blink_state, g * blink_state, b * blink_state)
        else:
            glColor3f(r, g, b)
        glVertex2f(x, y)
    glEnd()

def update_points(value):
    # Updates points' positions, making them bounce from walls.
    global points
    if not frozen:
        for i in range(len(points)):
            x, y, dx, dy, r, g, b = points[i]
            x += dx
            y += dy
            # Bounce from walls
            if x <= 0 or x >= 500:
                dx *= -1
            if y <= 0 or y >= 500:
                dy *= -1
            points[i] = [x, y, dx, dy, r, g, b]
    glutPostRedisplay()
    glutTimerFunc(10, update_points, 0)

def toggle_blinking(value):
    # Toggles blinking state.
    global blink_state
    if blinking:
        blink_state = not blink_state
        glutPostRedisplay()
        glutTimerFunc(500, toggle_blinking, 0)

def mouse_listener(button, state, x, y):
    # Handles mouse clicks to generate points and toggle blinking.
    global blinking
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        generate_point(x, 500 - y)  # Convert from OpenGL coordinates
    elif button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        blinking = not blinking
        if blinking:
            toggle_blinking(0)

def keyboard_listener(key, x, y):
    # Handles keyboard inputs for freezing and adjusting speed.
    global frozen, blinking
    key = key.decode("utf-8")
    if key == ' ':
        frozen = not frozen
        if frozen:
            blinking = False
        else:
            glutTimerFunc(500, toggle_blinking, 0)

def special_keys(key, x, y):
    # Handles special keys for speed adjustment.
    global speed
    if key == GLUT_KEY_UP:
        speed += 1
    elif key == GLUT_KEY_DOWN and speed > 1:
        speed -= 1
    # Update all points' speed
    for i in range(len(points)):
        x, y, dx, dy, r, g, b = points[i]
        dx = speed if dx > 0 else -speed
        dy = speed if dy > 0 else -speed
        points[i] = [x, y, dx, dy, r, g, b]

def iterate():
    glViewport(0, 0, 500, 500)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, 500, 0.0, 500, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    iterate()
    draw_points()
    glutSwapBuffers()

# Initialize OpenGL
glutInit()
glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
glutInitWindowSize(500, 500)
glutInitWindowPosition(0, 0)
wind = glutCreateWindow(b"Amazing Box")
glutDisplayFunc(showScreen)
glutMouseFunc(mouse_listener)
glutKeyboardFunc(keyboard_listener)
glutSpecialFunc(special_keys)
glutTimerFunc(10, update_points, 0)
glutMainLoop()