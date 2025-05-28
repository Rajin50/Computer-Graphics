from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time

player_pos = [0, 0, 0]
player_angle = 0
player_life = 5
game_score = 0
bullets_missed = 0
game_over = False
player_auto_rotate = False

camera_pos = [0, 500, 500]
camera_angle = 45
camera_height = 500
camera_distance = 500
first_person = False
fovY = 120
initial_view = True

cheat_mode = False
cheat_vision = False
cheat_rotation = 0
auto_fire_timer = 0

# Game objects
bullets = []
enemies = []
last_enemy_spawn = 0
last_bullet_fired = 0
gun_angle = 0

# Constants
GRID_LENGTH = 600
PLAYER_SPEED = 5
BULLET_SPEED = 15
ENEMY_SPEED = 0.1
BULLET_LIFETIME = 100
ENEMY_COUNT = 5
PLAYER_SIZE = 30
ENEMY_SIZE = 40
BULLET_SIZE = 10


def init_game():
    global player_pos, player_angle, player_life, game_score, bullets_missed, game_over
    global bullets, enemies, last_enemy_spawn, last_bullet_fired, gun_angle, initial_view
    global cheat_mode, cheat_vision, cheat_rotation, auto_fire_timer

    player_pos = [0, 0, 0]
    player_angle = 0
    player_life = 5
    game_score = 0
    bullets_missed = 0
    game_over = False
    initial_view = True

    bullets = []
    enemies = []
    gun_angle = 0

    cheat_mode = False
    cheat_vision = False
    cheat_rotation = 0
    auto_fire_timer = 0

    for _ in range(ENEMY_COUNT):
        spawn_enemy()

def spawn_enemy():
    angle = random.uniform(0, 2 * math.pi)
    distance = random.uniform(GRID_LENGTH * 0.6, GRID_LENGTH * 0.9)
    x = math.cos(angle) * distance
    y = math.sin(angle) * distance
    size_variation = random.uniform(0.8, 1.2)
    enemies.append({
        'pos': [x, y, 0],
        'size': ENEMY_SIZE * size_variation,
        'size_factor': size_variation,
        'growing': True,
        'speed': random.uniform(ENEMY_SPEED * 0.8, ENEMY_SPEED * 1.2)
    })

def fire_bullet():
    global last_bullet_fired

    if time.time() - last_bullet_fired < 0.1:
        return

    last_bullet_fired = time.time()

    # Calculate bullet direction based on player and gun angles
    angle_rad = math.radians(player_angle + gun_angle)
    direction = [math.sin(angle_rad), math.cos(angle_rad), 0]

    bullets.append({
        'pos': [player_pos[0], player_pos[1], PLAYER_SIZE],
        'direction': direction,
        'lifetime': BULLET_LIFETIME
    })

def update_game():
    global bullets_missed, game_score, player_life, game_over, initial_view
    global cheat_rotation, auto_fire_timer, player_angle, gun_angle

    if game_over:
        return

    if cheat_mode:
        player_angle = (player_angle + 2) % 360
        gun_angle = 0

        auto_fire_timer += 1
        if auto_fire_timer >= 5:
            auto_fire_timer = 0
            if enemies:
                closest_enemy = min(enemies, key=lambda e: math.sqrt(
                    (e['pos'][0] - player_pos[0]) ** 2 +
                    (e['pos'][1] - player_pos[1]) ** 2))

                dx = closest_enemy['pos'][0] - player_pos[0]
                dy = closest_enemy['pos'][1] - player_pos[1]
                dist = math.sqrt(dx * dx + dy * dy)
                direction = [dx / dist, dy / dist, 0]

                bullets.append({
                    'pos': [player_pos[0], player_pos[1], PLAYER_SIZE],
                    'direction': direction,
                    'lifetime': BULLET_LIFETIME,
                    'cheat_bullet': True
                })

    for bullet in bullets[:]:
        if 'cheat_bullet' in bullet and bullet['cheat_bullet']:
            bullet['pos'][0] += bullet['direction'][0] * BULLET_SPEED * 2
            bullet['pos'][1] += bullet['direction'][1] * BULLET_SPEED * 2
        else:
            bullet['pos'][0] += bullet['direction'][0] * BULLET_SPEED
            bullet['pos'][1] += bullet['direction'][1] * BULLET_SPEED

        bullet['lifetime'] -= 1

        if (abs(bullet['pos'][0]) > GRID_LENGTH or
                abs(bullet['pos'][1]) > GRID_LENGTH or
                bullet['lifetime'] <= 0):
            bullets.remove(bullet)
            if 'cheat_bullet' not in bullet:
                bullets_missed += 1

    for enemy in enemies[:]:
        # Move enemy toward player
        dx = player_pos[0] - enemy['pos'][0]
        dy = player_pos[1] - enemy['pos'][1]
        dist = math.sqrt(dx * dx + dy * dy)

        if dist > 0:
            enemy['pos'][0] += (dx / dist) * enemy['speed']
            enemy['pos'][1] += (dy / dist) * enemy['speed']

        if enemy['growing']:
            enemy['size'] += 0.5
            if enemy['size'] > ENEMY_SIZE * 1.2:
                enemy['growing'] = False
        else:
            enemy['size'] -= 0.5
            if enemy['size'] < ENEMY_SIZE * 0.8:
                enemy['growing'] = True
        if dist < PLAYER_SIZE + enemy['size'] / 2:
            player_life -= 1
            enemies.remove(enemy)
            spawn_enemy()
            if player_life <= 0:
                game_over = True

    for bullet in bullets[:]:
        for enemy in enemies[:]:
            dx = bullet['pos'][0] - enemy['pos'][0]
            dy = bullet['pos'][1] - enemy['pos'][1]
            dist = math.sqrt(dx * dx + dy * dy)

            if dist < enemy['size'] / 2:
                game_score += 10
                bullets.remove(bullet)
                enemies.remove(enemy)
                spawn_enemy()
                break

    if bullets_missed >= 10:
        game_over = True

    if initial_view and (player_pos[0] != 0 or player_pos[1] != 0 or player_angle != 0):
        initial_view = False

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_player():
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    glRotatef(player_angle, 0, 0, 1)

    # Head
    glPushMatrix()
    glTranslatef(0, 0, PLAYER_SIZE * 2.0)
    glColor3f(0, 0, 0)
    glutSolidSphere(PLAYER_SIZE * 0.5, 20, 20)
    glPopMatrix()

    # Body
    glPushMatrix()
    glTranslatef(0, 0, PLAYER_SIZE * 1.2)
    glColor3f(0.0, 0.5, 0.0)
    glScalef(PLAYER_SIZE * 1.0, PLAYER_SIZE * 0.5, PLAYER_SIZE * 1.2)
    glutSolidCube(1)
    glPopMatrix()

    # Arms
    for side in [-1, 1]:
        glPushMatrix()
        glTranslatef(side * PLAYER_SIZE * 0.4, PLAYER_SIZE * 0.45, PLAYER_SIZE * 1.2)
        glRotatef(-90, 1, 0, 0)
        glColor3f(1.0, 0.8, 0.6)
        gluCylinder(gluNewQuadric(), PLAYER_SIZE * 0.15, PLAYER_SIZE * 0.15, PLAYER_SIZE * 1.0, 20, 20)
        glPopMatrix()

    # Legs
    glColor3f(0.0, 0.0, 0.8)  # Blue color
    for side in [-1, 1]:
        glPushMatrix()
        glTranslatef(side * PLAYER_SIZE * 0.35, 0, PLAYER_SIZE * 0.6)
        glRotatef(180, 1, 0, 0)
        gluCylinder(gluNewQuadric(), PLAYER_SIZE * 0.22, PLAYER_SIZE * 0.15, PLAYER_SIZE * 1.6, 20, 20)
        glPopMatrix()

    # Gun
    glPushMatrix()
    glTranslatef(0, PLAYER_SIZE * 1.0, PLAYER_SIZE * 1.2)
    glRotatef(-90, 1, 0, 0)

    glColor3f(0.2, 0.2, 0.2)
    gluCylinder(gluNewQuadric(), PLAYER_SIZE * 0.1, PLAYER_SIZE * 0.05, PLAYER_SIZE * 1.2, 10, 10)

    glPopMatrix()
    glPopMatrix()


def draw_dead_player():
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], PLAYER_SIZE * 0.8)

    glRotatef(90, 1, 0, 0)

    glPushMatrix()
    glTranslatef(0, 0, PLAYER_SIZE * 2.0)
    glColor3f(0, 0, 0)
    glutSolidSphere(PLAYER_SIZE * 0.5, 20, 20)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0, 0, PLAYER_SIZE * 1.2)
    glColor3f(0.0, 0.5, 0.0)
    glScalef(PLAYER_SIZE * 1.0, PLAYER_SIZE * 0.5, PLAYER_SIZE * 1.2)
    glutSolidCube(1)
    glPopMatrix()

    for side in [-1, 1]:
        glPushMatrix()
        glTranslatef(side * PLAYER_SIZE * 0.4, PLAYER_SIZE * 0.45, PLAYER_SIZE * 1.2)
        glRotatef(-90, 1, 0, 0)
        glColor3f(1.0, 0.8, 0.6)
        gluCylinder(gluNewQuadric(), PLAYER_SIZE * 0.15, PLAYER_SIZE * 0.15, PLAYER_SIZE * 1.0, 20, 20)
        glPopMatrix()

    glColor3f(0.0, 0.0, 0.8)  # Blue color
    for side in [-1, 1]:
        glPushMatrix()
        glTranslatef(side * PLAYER_SIZE * 0.35, 0, PLAYER_SIZE * 0.6)
        glRotatef(180, 1, 0, 0)
        gluCylinder(gluNewQuadric(), PLAYER_SIZE * 0.22, PLAYER_SIZE * 0.15, PLAYER_SIZE * 1.6, 20, 20)
        glPopMatrix()

    glPushMatrix()
    glTranslatef(0, PLAYER_SIZE * 1.0, PLAYER_SIZE * 1.2)
    glRotatef(-90, 1, 0, 0)

    glColor3f(0.2, 0.2, 0.2)
    gluCylinder(gluNewQuadric(), PLAYER_SIZE * 0.1, PLAYER_SIZE * 0.05, PLAYER_SIZE * 1.2, 10, 10)

    glPopMatrix()
    glPopMatrix()

def draw_enemies():
    for enemy in enemies:
        glPushMatrix()

        glTranslatef(enemy['pos'][0], enemy['pos'][1], enemy['size'])

        glColor3f(1.0, 0.0, 0.0)
        glutSolidSphere(enemy['size'], 15, 15)

        glTranslatef(0, 0, enemy['size'] * 1.3)
        glColor3f(0.0, 0.0, 0.0)
        glutSolidSphere(enemy['size'] * 0.5, 20, 20)

        glPopMatrix()


def draw_bullets():
    for bullet in bullets:
        glPushMatrix()
        glTranslatef(bullet['pos'][0], bullet['pos'][1], bullet['pos'][2])
        glColor3f(1, 1, 0)
        glutSolidCube(BULLET_SIZE)
        glPopMatrix()

def draw_grid():
    grid_size = GRID_LENGTH
    step = (2 * GRID_LENGTH) // 13

    glBegin(GL_QUADS)
    for i in range(-grid_size, grid_size, step):
        for j in range(-grid_size, grid_size, step):
            if (i // step + j // step) % 2 == 0:
                glColor3f(1, 1, 1)
            else:
                glColor3f(0.7, 0.5, 0.95)

            glVertex3f(i, j, 0)
            glVertex3f(i + step, j, 0)
            glVertex3f(i + step, j + step, 0)
            glVertex3f(i, j + step, 0)
    glEnd()

    wall_height = grid_size // 4

    glBegin(GL_QUADS)
    glColor3f(0, 1, 0)
    glVertex3f(-grid_size, -grid_size, 0)
    glVertex3f(-grid_size, grid_size, 0)
    glVertex3f(-grid_size, grid_size, wall_height)
    glVertex3f(-grid_size, -grid_size, wall_height)
    glEnd()

    glBegin(GL_QUADS)
    glColor3f(0, 0, 1)
    glVertex3f(grid_size, -grid_size, 0)
    glVertex3f(grid_size, grid_size, 0)
    glVertex3f(grid_size, grid_size, wall_height)
    glVertex3f(grid_size, -grid_size, wall_height)
    glEnd()

    glBegin(GL_QUADS)
    glColor3f(0.3, 0.9, 1)
    glVertex3f(-grid_size, -grid_size, 0)
    glVertex3f(grid_size, -grid_size, 0)
    glVertex3f(grid_size, -grid_size, wall_height)
    glVertex3f(-grid_size, -grid_size, wall_height)
    glEnd()

    if not initial_view:
        glBegin(GL_QUADS)
        glColor3f(1, 1, 1)
        glVertex3f(-grid_size, grid_size, 0)
        glVertex3f(grid_size, grid_size, 0)
        glVertex3f(grid_size, grid_size, wall_height)
        glVertex3f(-grid_size, grid_size, wall_height)
        glEnd()


def keyboardListener(key, x, y):
    global player_pos, player_angle, gun_angle, cheat_mode, cheat_vision, initial_view

    key = key.decode('utf-8').lower()

    if game_over and key == 'r':
        init_game()
        return

    if game_over:
        return

    if key == 'w':
        angle_rad = math.radians(player_angle)
        player_pos[0] += math.sin(angle_rad) * PLAYER_SPEED
        player_pos[1] += math.cos(angle_rad) * PLAYER_SPEED
        initial_view = False
    elif key == 's':
        angle_rad = math.radians(player_angle)
        player_pos[0] -= math.sin(angle_rad) * PLAYER_SPEED
        player_pos[1] -= math.cos(angle_rad) * PLAYER_SPEED
        initial_view = False

    if not cheat_mode:
        if key == 'a':
            player_angle += 5
            initial_view = False
        elif key == 'd':
            player_angle -= 5
            initial_view = False
    player_angle %= 360

    # Cheat modes
    if key == 'c':
        cheat_mode = not cheat_mode
    elif key == 'v' and cheat_mode:
        cheat_vision = not cheat_vision

    player_pos[0] = max(-GRID_LENGTH + PLAYER_SIZE, min(GRID_LENGTH - PLAYER_SIZE, player_pos[0]))
    player_pos[1] = max(-GRID_LENGTH + PLAYER_SIZE, min(GRID_LENGTH - PLAYER_SIZE, player_pos[1]))

def specialKeyListener(key, x, y):
    global camera_angle, camera_height, initial_view

    if key == GLUT_KEY_UP:
        camera_height += 10
        initial_view = False
    elif key == GLUT_KEY_DOWN:
        camera_height -= 10
        initial_view = False
    elif key == GLUT_KEY_LEFT:
        camera_angle += 5
        initial_view = False
    elif key == GLUT_KEY_RIGHT:
        camera_angle -= 5
        initial_view = False

    camera_height = max(100, min(1000, camera_height))


def mouseListener(button, state, x, y):
    global first_person, initial_view

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN and not game_over:
        fire_bullet()
    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        first_person = not first_person
        initial_view = False


def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if initial_view:
        gluLookAt(0, 400, 500,
                  0, 0, 0,
                  0, 0, 1)
    elif first_person:
        eye_x = player_pos[0]
        eye_y = player_pos[1]
        eye_z = PLAYER_SIZE * 0.8

        if cheat_mode and cheat_vision:
            angle_rad = math.radians(player_angle + gun_angle)
            look_x = eye_x + math.sin(angle_rad) * 100
            look_y = eye_y + math.cos(angle_rad) * 100
            look_z = eye_z

            gluLookAt(eye_x, eye_y, eye_z + 20,
                      look_x, look_y, look_z + 10,
                      0, 0, 1)

            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluPerspective(150, 1.25, 0.1, 1500)
            glMatrixMode(GL_MODELVIEW)
        else:
            angle_rad = math.radians(player_angle + gun_angle)
            look_x = eye_x + math.sin(angle_rad) * 100
            look_y = eye_y + math.cos(angle_rad) * 100
            look_z = eye_z

            gluLookAt(eye_x, eye_y, eye_z,
                      look_x, look_y, look_z,
                      0, 0, 1)
    else:
        angle_rad = math.radians(camera_angle)
        eye_x = player_pos[0] + math.sin(angle_rad) * camera_distance
        eye_y = player_pos[1] + math.cos(angle_rad) * camera_distance
        eye_z = camera_height

        gluLookAt(eye_x, eye_y, eye_z,
                  player_pos[0], player_pos[1], PLAYER_SIZE * 0.5,
                  0, 0, 1)

def idle():
    update_game()
    glutPostRedisplay()


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)

    setupCamera()
    glEnable(GL_DEPTH_TEST)

    draw_grid()

    if game_over:
        draw_dead_player()
    else:
        draw_player()

    draw_enemies()
    draw_bullets()

    draw_text(10, 770, f"Player Life Remaining: {player_life}")
    draw_text(10, 740, f"Game Score: {game_score}")
    draw_text(10, 710, f"Player Bullet Missed: {bullets_missed}")

    if cheat_mode:
        draw_text(10, 680, "CHEAT MODE: ON", GLUT_BITMAP_HELVETICA_12)

    if game_over:
        draw_text(400, 400, "GAME OVER! Press R to restart", GLUT_BITMAP_TIMES_ROMAN_24)

    glutSwapBuffers()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Bullet Frenzy - 3D Game")

    glClearColor(0.1, 0.1, 0.2, 1.0)

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    init_game()
    glutMainLoop()

if __name__ == "__main__":
    main()