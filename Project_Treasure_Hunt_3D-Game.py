from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18, GLUT_BITMAP_TIMES_ROMAN_24
from OpenGL.GLU import *
import math
import random
import time
import numpy as np

# Camera-related variables
camera_pos = (0, 500, 500)
fovY = 120  # Field of view
GRID_LENGTH = 1000  # Length of grid lines

# Game state variables
CELL_SIZE = 80
MAZE_SIZE = 15
player_pos = [0, 0, 10]
player_angle = 0
player_speed = 5
diamond_pos = [0, 0, 1]
diamond_found = False
score = 0
lives = 5
cheat_mode = False
first_person = False

# Mouse control variables
mouse_x = 0
mouse_y = 0
mouse_sensitivity = 0.05

# Timer variables
game_start_time = 0
game_time = 180
game_over = False
auto_camera_switch_time = 3
enemy_start_time = 6

# Enemy variables
enemies = []  # List to hold all enemies
enemy_speed = 2
enemy_active = True
enemy_scale = 1.0
enemy_scale_direction = 0.01
enemy_started = False

# Bullet variables
bullets = []
bullet_speed = 60
bullet_radius = 1
last_shot_time = 0
shot_cooldown = 0.5

# Question variables
question_active = False
current_question = None
questions_answered = 0
MAX_QUESTIONS = 5
top_down_view = False
top_down_view_time = 0
TOP_DOWN_VIEW_DURATION = 10

# Map view variables
show_map_view = False
map_view_start_time = 0
MAP_VIEW_DURATION = 5
player_start_pos = [0, 0, 10]

# Big Ball variables
# big_ball_active = False
big_ball_pos = [0, 0, 50]
big_ball_radius = 30
big_ball_speed = 0.05
# big_ball_respawn_timer = 0
big_ball_respawn_delay = 3
# big_ball_spawned = False
big_ball_active = False
big_ball_spawned = False
big_ball_spawn_timer = 0  # NEW: Timer to track when to first spawn
big_ball_respawn_timer = 0
big_ball_spawn_delay = 5  # Delay in seconds before first spawn


questions = [
    {
        "question": "What is 2+2?",
        "options": ["3", "4"],
        "correct": 1
    },
    {
        "question": "Which is a primary color?",
        "options": ["Red", "Green"],
        "correct": 0
    },
    {
        "question": "Python is a...",
        "options": ["Snake", "Programming language"],
        "correct": 1
    },
    {
        "question": "What is the capital of France?",
        "options": ["London", "Paris"],
        "correct": 1
    },
    {
        "question": "how is anika mams teaching?",
        "options": ["good", "marvellous"],
        "correct": 1
    }
]

# Maze generation
def generate_maze(size):
    maze = [['1'] * size for _ in range(size)]

    def carve(x, y):
        dirs = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 < nx < size and 0 < ny < size and maze[ny][nx] == '1':
                maze[ny - dy // 2][nx - dx // 2] = '0'
                maze[ny][nx] = '0'
                carve(nx, ny)

    maze[1][1] = '0'
    carve(1, 1)
    maze[0][1] = '0'
    maze[size - 1][size - 2] = '0'
    return ["".join(row) for row in maze]

maze_grid = generate_maze(MAZE_SIZE)

def grid_to_world(row, col):
    x = col * CELL_SIZE - (MAZE_SIZE * CELL_SIZE) / 2 + CELL_SIZE / 2
    y = (MAZE_SIZE - 1 - row) * CELL_SIZE - (MAZE_SIZE * CELL_SIZE) / 2 + CELL_SIZE / 2
    return x, y

def initialize_enemies():
    global enemies
    enemies = []
    
    # Generate 6 enemies at different locations
    for _ in range(6):
        while True:
            enemy_row = random.randint(MAZE_SIZE//4, MAZE_SIZE - 2)
            enemy_col = random.randint(1, MAZE_SIZE - 2)
            if maze_grid[enemy_row][enemy_col] == '0':
                x, y = grid_to_world(enemy_row, enemy_col)
                enemies.append({
                    'pos': [x, y, 20],
                    'active': True,
                    'scale': 1.0,
                    'scale_dir': 0.01,
                    'attack_range': 200,
                    'attack_angle': 45,
                    'speed': enemy_speed
                })
                break

def initialize_positions():
    global player_row, player_col, player_pos, player_start_pos, diamond_row, diamond_col, diamond_pos
    global big_ball_active, big_ball_pos, big_ball_respawn_timer
    
    player_row, player_col = 0, 1
    player_pos[0], player_pos[1] = grid_to_world(player_row, player_col)
    player_start_pos = player_pos.copy()

    diamond_row, diamond_col = MAZE_SIZE - 1, MAZE_SIZE - 2
    diamond_pos[0], diamond_pos[1] = grid_to_world(diamond_row, diamond_col)
    
    # big_ball_active = True
    big_ball_pos = [player_start_pos[0], player_start_pos[1], 50]
    big_ball_respawn_timer = 0
    
    initialize_enemies()

initialize_positions()

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

def draw_maze():
    for row_idx, row in enumerate(maze_grid):
        for col_idx, cell in enumerate(row):
            if cell == '1':
                x, y = grid_to_world(row_idx, col_idx)
                glPushMatrix()
                glTranslatef(x, y, 50)
                glScalef(CELL_SIZE, CELL_SIZE, 100)
                if (row_idx + col_idx) % 2 == 0:
                    glColor3f(0.5, 0.5, 0.5)
                else:
                    glColor3f(0.35, 0.28, 0.18)
                glutSolidCube(1)
                glPopMatrix()

def draw_player():
    if not first_person:
        glPushMatrix()
        glTranslatef(player_pos[0], player_pos[1], player_pos[2])
        glRotatef(player_angle, 0, 0, 1)

        # Body
        glPushMatrix()
        glColor3f(0.8, 0.6, 0.4)
        glScalef(0.5, 0.5, 10)
        glutSolidCube(1)
        glPopMatrix()

        # Head
        glPushMatrix()
        glTranslatef(0, 0, 10)
        glColor3f(1, 0.8, 0.6)
        glutSolidSphere(0.2, 20, 20)
        glPopMatrix()

        # Limbs
        limbs = [
            (-0.3, 0, -0.2, 0.1, 0.1, 0.3),
            (0.3, 0, -0.2, 0.1, 0.1, 0.3),
            (-0.15, 0, -0.5, 0.1, 0.2, 0.1),
            (0.15, 0, -0.5, 0.1, 0.2, 0.1)
        ]
        for px, py, pz, w, h, d in limbs:
            glPushMatrix()
            glTranslatef(px, py, pz)
            glColor3f(0.4, 0.3, 0.8)
            glScalef(w, h, d)
            glutSolidCube(1)
            glPopMatrix()

        # Nose
        glPushMatrix()
        glTranslatef(0.3, 0, 0.8)
        glColor3f(1, 0, 0)
        glRotatef(90, 0, 1, 0)
        glutSolidCone(0.05, 0.1, 10, 2)
        glPopMatrix()

        glPopMatrix()
    else:
        # Draw gun in first person view
        glPushMatrix()
        glTranslatef(0.5, -0.5, -0.5)  # Position the gun in the lower right
        glRotatef(-10, 1, 0, 0)  # Tilt the gun slightly
        
        # Gun body
        glPushMatrix()
        glColor3f(0.3, 0.3, 0.3)
        glScalef(0.5, 0.1, 0.1)
        glutSolidCube(1)
        glPopMatrix()
        
        # Gun barrel
        glPushMatrix()
        glTranslatef(0.5, 0, 0)
        glColor3f(0.2, 0.2, 0.2)
        glScalef(0.5, 0.05, 0.05)
        glutSolidCube(1)
        glPopMatrix()
        
        # Gun handle
        glPushMatrix()
        glTranslatef(0, 0, -0.1)
        glColor3f(0.4, 0.4, 0.4)
        glScalef(0.2, 0.15, 0.2)
        glutSolidCube(1)
        glPopMatrix()
        
        glPopMatrix()

def draw_enemies():
    for enemy in enemies:
        if not enemy['active']:
            continue
            
        # Update enemy scale for pulsing effect
        enemy['scale'] += enemy['scale_dir']
        if enemy['scale'] > 1.2 or enemy['scale'] < 0.8:
            enemy['scale_dir'] = -enemy['scale_dir']
        
        glPushMatrix()
        glTranslatef(enemy['pos'][0], enemy['pos'][1], enemy['pos'][2])
        
        # Body
        glPushMatrix()
        glColor3f(1.0, 0.0, 0.0)
        glScalef(enemy['scale'], enemy['scale'], enemy['scale'])
        glutSolidSphere(10, 20, 20)
        glPopMatrix()
        
        # Head
        glPushMatrix()
        glTranslatef(0, 0, 15)
        glColor3f(0.0, 0.0, 0.0)
        glScalef(enemy['scale'], enemy['scale'], enemy['scale'])
        glutSolidSphere(6, 20, 20)
        glPopMatrix()
        
        glPopMatrix()

def draw_bullets():
    current_time = time.time()
    glColor3f(0.0, 0.0, 1.0)  # Blue bullets
    
    for bullet in bullets[:]:
        # Calculate new position
        time_elapsed = current_time - bullet['time']
        distance_traveled = bullet_speed * time_elapsed
        
        # Check if bullet has exceeded max range
        if distance_traveled > 500:  # Max range of 500 units
            bullets.remove(bullet)
            continue
            
        # Calculate new position
        bullet_x = bullet['start'][0] + bullet['direction'][0] * distance_traveled
        bullet_y = bullet['start'][1] + bullet['direction'][1] * distance_traveled
        bullet_z = bullet['start'][2] + bullet['direction'][2] * distance_traveled
        
        # Update bullet position
        bullet['pos'] = [bullet_x, bullet_y, bullet_z]
        
        # Draw bullet
        glPushMatrix()
        glTranslatef(bullet_x, bullet_y, bullet_z)
        glutSolidSphere(bullet_radius, 10, 10)
        glPopMatrix()

def draw_diamond():
    if not diamond_found:
        glPushMatrix()
        glTranslatef(diamond_pos[0], diamond_pos[1], player_pos[2])
        glColor3f(0.0, 0.7, 1.0)
        glRotatef(45, 1, 0, 0)
        glRotatef(45, 0, 1, 0)
        glScalef(15, 15, 30)
        glutSolidOctahedron()
        glPopMatrix()

def draw_position_markers():
    if not show_map_view:
        return
        
    # Draw player start position (green)
    glPushMatrix()
    glTranslatef(player_start_pos[0], player_start_pos[1], 100)
    glColor3f(0, 1, 0)
    glutSolidSphere(15, 20, 20)
    glPopMatrix()
    
    # Draw current player position (blue)
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], 100)
    glColor3f(0, 0, 1)
    glutSolidSphere(15, 20, 20)
    glPopMatrix()
    
    # Draw diamond position (yellow)
    if not diamond_found:
        glPushMatrix()
        glTranslatef(diamond_pos[0], diamond_pos[1], 100)
        glColor3f(1, 1, 0)
        glutSolidSphere(15, 20, 20)
        glPopMatrix()

def draw_big_ball():
    if not big_ball_active:
        return
        
    glPushMatrix()
    glTranslatef(big_ball_pos[0], big_ball_pos[1], big_ball_pos[2])
    glColor3f(1.0, 0.5, 0.0)  # Orange color
    glutSolidSphere(big_ball_radius, 30, 30)
    glPopMatrix()

def is_collision(x, y):
    radius = 7
    for dx in [-radius, 0, radius]:
        for dy in [-radius, 0, radius]:
            cx = x + dx
            cy = y + dy
            col = int((cx + (MAZE_SIZE * CELL_SIZE) / 2) // CELL_SIZE)
            row = int((MAZE_SIZE - 1 - ((cy + (MAZE_SIZE * CELL_SIZE) / 2) // CELL_SIZE)))
            if 0 <= row < MAZE_SIZE and 0 <= col < MAZE_SIZE:
                if maze_grid[row][col] == '1':
                    return True
            else:
                return True
    return False

def can_see_player(enemy):
    # Check if player is within attack range
    px, py, pz = player_pos
    ex, ey, ez = enemy['pos']
    distance = math.sqrt((px - ex)**2 + (py - ey)**2)
    
    if distance > enemy['attack_range']:
        return False
        
    # Check if player is within attack angle (field of view)
    angle_to_player = math.degrees(math.atan2(py - ey, px - ex))
    enemy_angle = math.degrees(math.atan2(ey - py, ex - px))  # Angle from enemy to player
    
    # Calculate angle difference (simplified)
    angle_diff = abs((enemy_angle - angle_to_player + 180) % 360 - 180)
    
    if angle_diff > enemy['attack_angle'] / 2:
        return False
        
    # Check if there's a clear line of sight (simplified)
    # In a real game, you'd want to implement proper raycasting
    steps = 20
    for i in range(1, steps + 1):
        t = i / steps
        check_x = ex + t * (px - ex)
        check_y = ey + t * (py - ey)
        if is_collision(check_x, check_y):
            return False
            
    return True

def update_big_ball():
    global big_ball_active, big_ball_spawned, big_ball_pos
    global big_ball_spawn_timer, big_ball_respawn_timer
    global lives, player_pos, game_over

    current_time = time.time()

    # Spawn after initial delay
    if not big_ball_spawned:
        if current_time - game_start_time >= big_ball_spawn_delay:
            big_ball_spawned = True
            big_ball_active = True
            big_ball_pos = [player_start_pos[0], player_start_pos[1], 50]
        return

    # Handle respawn after hit
    if not big_ball_active:
        if current_time - big_ball_respawn_timer >= big_ball_respawn_delay:
            big_ball_active = True
            # Spawn near player but not too close
            angle = random.uniform(0, 2*math.pi)
            distance = random.uniform(100, 200)
            big_ball_pos = [
                player_pos[0] + distance * math.cos(angle),
                player_pos[1] + distance * math.sin(angle),
                50
            ]
        return

    # Movement logic - REMOVED WALL COLLISION CHECK
    px, py, _ = player_pos
    bx, by, _ = big_ball_pos
    dx = px - bx
    dy = py - by
    distance = math.sqrt(dx * dx + dy * dy)

    if distance > 0:
        dx = dx / distance * big_ball_speed
        dy = dy / distance * big_ball_speed
        # Simply update position without collision check
        big_ball_pos[0] += dx
        big_ball_pos[1] += dy

    # Collision with player
    if distance < big_ball_radius + 15:
        lives -= 1
        big_ball_active = False
        big_ball_respawn_timer = current_time

        if lives <= 0:
            game_over = True
        else:
            angle = math.atan2(py - by, px - bx)
            player_pos[0] = bx + (big_ball_radius + 20) * math.cos(angle)
            player_pos[1] = by + (big_ball_radius + 20) * math.sin(angle)

def show_question():
    global question_active, current_question, questions_answered
    
    if questions_answered >= MAX_QUESTIONS:
        return
        
    available_questions = [q for q in questions if "asked" not in q]
    if not available_questions:
        return
        
    current_question = random.choice(available_questions)
    current_question["asked"] = True
    question_active = True
    questions_answered += 1

def draw_question():
    if not question_active or not current_question:
        return

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)

    glBegin(GL_POINTS)
    glVertex2f(0, 0)
    glEnd()

    # Question box
    glColor3f(0.2, 0.2, 0.5)
    glBegin(GL_QUADS)
    glVertex2f(200, 300)
    glVertex2f(800, 300)
    glVertex2f(800, 500)
    glVertex2f(200, 500)
    glEnd()

    # Question text
    glColor3f(1, 1, 1)
    question_x = 250
    question_y = 450
    glRasterPos2f(question_x, question_y)
    for ch in current_question["question"]:
        glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(ch))

    # Options
    option_y = 400
    for i, option in enumerate(current_question["options"]):
        glRasterPos2f(300, option_y - i * 50)
        option_text = f"{i + 1}. {option}"
        for ch in option_text:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(ch))

    glEnable(GL_DEPTH_TEST)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def handle_answer(answer):
    global question_active, show_map_view, map_view_start_time
    
    if not question_active or not current_question:
        return
        
    question_active = False
    
    if answer == current_question["correct"]:
        show_map_view = True
        map_view_start_time = time.time()

def check_diamond_collision():
    global diamond_found, game_over
    if not diamond_found:
        px, py, pz = player_pos
        dx, dy, dz = diamond_pos
        distance = math.sqrt((px - dx) ** 2 + (py - dy) ** 2)
        if distance < 20:
            diamond_found = True
            game_over = True

def check_enemy_collision():
    global lives, game_over
    
    px, py, pz = player_pos
    
    for enemy in enemies:
        if not enemy['active']:
            continue
            
        ex, ey, ez = enemy['pos']
        distance = math.sqrt((px - ex) ** 2 + (py - ey) ** 2)
        
        if distance < 20:
            lives -= 1
            angle = math.atan2(ey - py, ex - px)
            enemy['pos'][0] = px + 50 * math.cos(angle)
            enemy['pos'][1] = py + 50 * math.sin(angle)
            
            if lives <= 0:
                game_over = True
            break

def check_bullet_collisions():
    for bullet in bullets[:]:
        for enemy in enemies[:]:
            if not enemy['active']:
                continue
                
            bx, by, bz = bullet['pos']
            ex, ey, ez = enemy['pos']
            distance = math.sqrt((bx - ex) ** 2 + (by - ey) ** 2 + (bz - ez) ** 2)
            
            if distance < 15:  # Bullet hit enemy
                enemy['active'] = False
                if bullet in bullets:
                    bullets.remove(bullet)
                break

def update_enemy_positions():
    if game_over:
        return
        
    for enemy in enemies:
        if not enemy['active']:
            continue
            
        # If enemy can see player, move toward player
        if can_see_player(enemy):
            px, py, pz = player_pos
            ex, ey, ez = enemy['pos']
            
            dx = px - ex
            dy = py - ey
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0:
                dx = dx / distance * enemy['speed']
                dy = dy / distance * enemy['speed']
                
                new_x = ex + dx
                new_y = ey + dy
                
                if not is_collision(new_x, new_y):
                    enemy['pos'][0] = new_x
                    enemy['pos'][1] = new_y

def update_bullets():
    current_time = time.time()
    
    # Remove bullets that have traveled too far
    for bullet in bullets[:]:
        time_elapsed = current_time - bullet['time']
        if time_elapsed * bullet_speed > 500:  # Max range
            bullets.remove(bullet)

def shoot_bullet():
    global last_shot_time
    
    current_time = time.time()
    if current_time - last_shot_time < shot_cooldown:
        return
        
    last_shot_time = current_time
    
    # Calculate bullet direction based on player angle
    angle_rad = math.radians(player_angle)
    direction = (
        math.cos(angle_rad),
        math.sin(angle_rad),
        0  # Flat trajectory
    )
    
    # Start bullet slightly in front of player
    start_pos = (
        player_pos[0] + direction[0] * 10,
        player_pos[1] + direction[1] * 10,
        player_pos[2] + 5  # Gun height
    )
    
    bullets.append({
        'start': start_pos,
        'pos': list(start_pos),
        'direction': direction,
        'time': current_time
    })

def update_game_time():
    global game_time, game_over, first_person
    
    elapsed = time.time() - game_start_time
    remaining = max(0, 180 - int(elapsed))
    game_time = remaining
    
    if game_time <= 0:
        game_over = True
    
    if not first_person and elapsed >= auto_camera_switch_time:
        first_person = True

def keyboardListener(key, x, y):
    global player_pos, player_angle, cheat_mode, first_person, question_active

    if game_over:
        return

    key = key.decode('utf-8').lower()
    if question_active:
        if key == '1':
            handle_answer(0)
        elif key == '2':
            handle_answer(1)
        glutPostRedisplay()
        return
    
    dx, dy = 0, 0
    rotate = 0
    if key == 'w':
        dx = player_speed * math.cos(math.radians(player_angle))
        dy = player_speed * math.sin(math.radians(player_angle))
    elif key == 's':
        dx = -player_speed * math.cos(math.radians(player_angle))
        dy = -player_speed * math.sin(math.radians(player_angle))
    elif key == 'a':
        rotate = 5
    elif key == 'd':
        rotate = -5
    elif key == 'c':
        cheat_mode = not cheat_mode
    elif key == 'v':
        first_person = not first_person
        if first_person:
            center_x = glutGet(GLUT_WINDOW_WIDTH) // 2
            center_y = glutGet(GLUT_WINDOW_HEIGHT) // 2
            glutWarpPointer(center_x, center_y)
            global mouse_x, mouse_y
            mouse_x = center_x
            mouse_y = center_y
            glutSetCursor(GLUT_CURSOR_NONE)
        else:
            glutSetCursor(GLUT_CURSOR_INHERIT)
    elif key == ' ' and first_person:  # Space to shoot
        shoot_bullet()

    if rotate != 0:
        player_angle = (player_angle + rotate) % 360
    else:
        new_x = player_pos[0] + dx
        new_y = player_pos[1] + dy
        if not is_collision(new_x, new_y) or cheat_mode:
            player_pos[0] = new_x
            player_pos[1] = new_y
            check_diamond_collision()

    glutPostRedisplay()

def mouseMotionListener(x, y):
    global mouse_x, mouse_y, player_angle
    
    if first_person:
        dx = x - mouse_x
        dy = y - mouse_y
        
        player_angle -= dx * mouse_sensitivity
        player_angle %= 360
        
        mouse_x = x
        mouse_y = y
        
        if glutGet(GLUT_WINDOW_WIDTH) > 0 and glutGet(GLUT_WINDOW_HEIGHT) > 0:
            center_x = glutGet(GLUT_WINDOW_WIDTH) // 2
            center_y = glutGet(GLUT_WINDOW_HEIGHT) // 2
            glutWarpPointer(center_x, center_y)
            mouse_x = center_x
            mouse_y = center_y
        
        glutPostRedisplay()

def enterMouseListener(state):
    if state == GLUT_ENTERED and first_person:
        center_x = glutGet(GLUT_WINDOW_WIDTH) // 2
        center_y = glutGet(GLUT_WINDOW_HEIGHT) // 2
        glutWarpPointer(center_x, center_y)
        global mouse_x, mouse_y
        mouse_x = center_x
        mouse_y = center_y

def specialKeyListener(key, x, y):
    global camera_pos
    
    if game_over:
        return
        
    x, y, z = camera_pos

    if key == GLUT_KEY_UP:
        y += 10
    elif key == GLUT_KEY_DOWN:
        y -= 10
    elif key == GLUT_KEY_LEFT:
        x -= 10
    elif key == GLUT_KEY_RIGHT:
        x += 10

    camera_pos = (x, y, z)
    glutPostRedisplay()

def mouseListener(button, state_btn, x, y):
    global first_person, mouse_x, mouse_y, question_active
    
    if game_over:
        return
        
    if button == GLUT_RIGHT_BUTTON and state_btn == GLUT_DOWN:
        if not question_active and questions_answered < MAX_QUESTIONS and not top_down_view:
            show_question()
        else:
            first_person = not first_person
            if first_person:
                center_x = glutGet(GLUT_WINDOW_WIDTH) // 2
                center_y = glutGet(GLUT_WINDOW_HEIGHT) // 2
                glutWarpPointer(center_x, center_y)
                mouse_x = center_x
                mouse_y = center_y
                glutSetCursor(GLUT_CURSOR_NONE)
            else:
                glutSetCursor(GLUT_CURSOR_INHERIT)
    elif button == GLUT_LEFT_BUTTON and state_btn == GLUT_DOWN and first_person:
        shoot_bullet()
        
    glutPostRedisplay()

def update():
    global top_down_view, top_down_view_time, show_map_view, map_view_start_time
    
    if not game_over:
        update_game_time()
        update_enemy_positions()
        update_bullets()
        update_big_ball()
        check_enemy_collision()
        check_bullet_collisions()
        check_diamond_collision()
            
    if top_down_view and time.time() - top_down_view_time > TOP_DOWN_VIEW_DURATION:
        top_down_view = False
        
    if show_map_view and time.time() - map_view_start_time > MAP_VIEW_DURATION:
        show_map_view = False
        
    glutPostRedisplay()

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    
    if show_map_view or top_down_view:
        glOrtho(-GRID_LENGTH/2, GRID_LENGTH/2, -GRID_LENGTH/2, GRID_LENGTH/2, -1000, 1000)
    elif first_person:
        gluPerspective(90, 1.25, 0.1, 1500)
    else:
        gluPerspective(fovY, 1.25, 0.1, 1500)
        
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if show_map_view or top_down_view:
        gluLookAt(0, 0, 1000, 0, 0, 0, 0, 1, 0)
    elif first_person:
        x, y, z = player_pos
        forward_x = math.cos(math.radians(player_angle))
        forward_y = math.sin(math.radians(player_angle))
        gluLookAt(x, y, z + 5, x + forward_x, y + forward_y, z + 5, 0, 0, 1)
    else:
        x, y, z = camera_pos
        gluLookAt(x, y, z, 0, 0, 0, 0, 0, 1)

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)

    setupCamera()

    # Draw floor
    glBegin(GL_QUADS)
    glColor3f(0.2, 0.5, 0.2)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glEnd()

    draw_maze()
    draw_diamond()
    draw_player()
    draw_enemies()
    draw_bullets()
    draw_big_ball()
    draw_position_markers()

    # HUD
    draw_text(10, 770, f"Time Remaining: {game_time} sec")
    draw_text(10, 740, f"Lives: {lives}")
    draw_text(10, 710, f"Questions left: {MAX_QUESTIONS - questions_answered}")
    draw_text(10, 680, f"Enemies left: {sum(1 for e in enemies if e['active'])}")
    draw_text(10, 650, f"Big Ball: {'Active' if big_ball_active else f'Respawning in {max(0, big_ball_respawn_delay - (time.time() - big_ball_respawn_timer)):.1f}s'}")
    
    if show_map_view:
        remaining = max(0, MAP_VIEW_DURATION - (time.time() - map_view_start_time))
        draw_text(10, 620, f"Map view: {int(remaining)}s remaining")
    
    if game_over:
        if diamond_found:
            draw_text(400, 400, "CONGRATULATIONS! YOU WON!", GLUT_BITMAP_TIMES_ROMAN_24)
        elif lives <= 0:
            draw_text(400, 400, "GAME OVER! YOU LOST!", GLUT_BITMAP_TIMES_ROMAN_24)
        else:
            draw_text(400, 400, "TIME'S UP! GAME OVER!", GLUT_BITMAP_TIMES_ROMAN_24)
    
    if cheat_mode:
        draw_text(10, 590, "CHEAT MODE: ON")
    
    draw_question()

    glutSwapBuffers()

def main():
    global game_start_time, mouse_x, mouse_y
    
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Maze Diamond Hunter")

    glEnable(GL_DEPTH_TEST)

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutMotionFunc(mouseMotionListener)
    glutPassiveMotionFunc(mouseMotionListener)
    glutEntryFunc(enterMouseListener)
    glutIdleFunc(update)
    
    mouse_x = glutGet(GLUT_WINDOW_WIDTH) // 2
    mouse_y = glutGet(GLUT_WINDOW_HEIGHT) // 2
    
    game_start_time = time.time()

    glutMainLoop()

if __name__ == "__main__":
    main()