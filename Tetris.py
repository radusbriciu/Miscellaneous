import pygame
import sys
import random

# Constants
WIDTH, HEIGHT = 10, 20
BLOCK_SIZE = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 30
MOVE_DELAY = 500  # Milliseconds between automatic downward movement

# Initialize Pygame
pygame.init()
pygame.font.init()  # Initialize the font module
# Add extra space for the preview area to the right of the game board
extra_preview_width = 5 * BLOCK_SIZE  # Adjust as needed for the size of the preview area
screen = pygame.display.set_mode((WIDTH * BLOCK_SIZE + extra_preview_width, HEIGHT * BLOCK_SIZE))

clock = pygame.time.Clock()

# Game board
board = [[0] * WIDTH for _ in range(HEIGHT)]

# Tetrominoes
tetrominoes = [
    # I in vertical orientation
    [[1], [1], [1], [1]],

    # T with the long part vertical, single block on top
    [[1, 0], [1, 1], [1, 0]],

    # L with the long part vertical, "L" shape pointing to the right
    [[1, 0], [1, 0], [1, 1]],

    # J with the long part vertical, "J" shape pointing to the left
    [[0, 1], [0, 1], [1, 1]],

    # S, adjusted for a more vertical orientation
    [[0, 1, 1], [1, 1, 0]],

    # Z, adjusted for a more vertical orientation
    [[1, 1, 0], [0, 1, 1]],

    # O, orientation does not matter
    [[1, 1], [1, 1]]
]

# Function to generate a random sequence of tetrominoes
def generate_tetromino_queue():
    queue = tetrominoes.copy()
    random.shuffle(queue)
    return queue

# Functions
def draw_board():
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if board[y][x] == 1:
                pygame.draw.rect(screen, WHITE, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
            else:
                pygame.draw.rect(screen, BLACK, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

def draw_tetromino(tetromino, pos):
    for y, row in enumerate(tetromino):
        for x, value in enumerate(row):
            if value == 1:
                pygame.draw.rect(screen, WHITE, ((pos[0] + x) * BLOCK_SIZE, (pos[1] + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

def move_tetromino(tetromino, pos, dx, dy):
    new_pos = [pos[0] + dx, pos[1] + dy]
    if not check_collision(tetromino, new_pos):
        return new_pos
    return pos

def check_collision(tetromino, pos):
    for y, row in enumerate(tetromino):
        for x, value in enumerate(row):
            if value == 1:
                if pos[1] + y >= HEIGHT or pos[0] + x < 0 or pos[0] + x >= WIDTH or board[pos[1] + y][pos[0] + x] == 1:
                    return True
    return False

def rotate_tetromino(tetromino, pos):
    rotated_tetromino = [list(row) for row in zip(*reversed(tetromino))]
    rotated_width = len(rotated_tetromino[0])
    rotated_height = len(rotated_tetromino)
    
    # Calculate the bounds of the rotated tetromino
    min_x = pos[0]
    max_x = pos[0] + rotated_width - 1
    min_y = pos[1]
    max_y = pos[1] + rotated_height - 1
    
    # Adjust position if the rotated tetromino goes out of bounds
    if min_x < 0:
        pos[0] -= min_x
    elif max_x >= WIDTH:
        pos[0] -= max_x - WIDTH + 1
    
    if min_y < 0:
        pos[1] -= min_y
    elif max_y >= HEIGHT:
        pos[1] -= max_y - HEIGHT + 1
    
    # Return the rotated tetromino and adjusted position
    return rotated_tetromino, pos

def drop_tetromino(tetromino, pos):
    # Start from the current position and move down until a collision is detected
    while not check_collision(tetromino, [pos[0], pos[1] + 1]):
        pos[1] += 1  # Move down by one row
    return pos

def draw_tetromino_preview(current_tetromino, next_tetromino, screen, block_size, offset):
    # Draw the current tetromino preview
    preview_offset_x = offset[0]
    preview_offset_y = offset[1]
    
    for y, row in enumerate(current_tetromino):
        for x, value in enumerate(row):
            if value == 1:
                pygame.draw.rect(screen, WHITE, (preview_offset_x + x * block_size, preview_offset_y + y * block_size, block_size, block_size))
    
    # Adjust the Y offset for the next tetromino to draw it below the current one with some spacing
    preview_offset_y += 5 * block_size  # Adjust this value based on your preference for spacing

    for y, row in enumerate(next_tetromino):
        for x, value in enumerate(row):
            if value == 1:
                pygame.draw.rect(screen, WHITE, (preview_offset_x + x * block_size, preview_offset_y + y * block_size, block_size, block_size))

def show_game_over_screen(screen):
    screen.fill(BLACK)  # Clear the screen
    font = pygame.font.SysFont("Arial", 48)
    text_surface = font.render("Game Over", True, WHITE)
    text_rect = text_surface.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2))
    screen.blit(text_surface, text_rect)
    pygame.display.flip()
    # Wait for the user to acknowledge the game over
    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    waiting_for_input = False

# Define the preview offset from the top right corner of the game window
preview_offset = (WIDTH * BLOCK_SIZE + 10, 10)

def main():
    # Define the preview offset from the top right corner of the game window
    preview_offset = (WIDTH * BLOCK_SIZE + 10, 10)
    falling_tetromino_queue = generate_tetromino_queue()
    falling_tetromino_index = 0
    falling_tetromino = falling_tetromino_queue[falling_tetromino_index]
    tetromino_pos = [4, 0]  # Initial position of the falling tetromino
    last_move_time = pygame.time.get_ticks()
    has_changed = False  # Track if the current block has been changed
    game_over = False  # Track the game over state

    while True:
        if game_over:
            show_game_over_screen(screen)
            break  # Exit the game loop

        current_time = pygame.time.get_ticks()
        if current_time - last_move_time > MOVE_DELAY:
            last_move_time = current_time
            new_pos = move_tetromino(falling_tetromino, tetromino_pos, 0, 1)
            if new_pos == tetromino_pos:  # Tetromino reached bottom or collided
                for y, row in enumerate(falling_tetromino):
                    for x, value in enumerate(row):
                        if value == 1:
                            board[tetromino_pos[1] + y][tetromino_pos[0] + x] = 1
                for y in range(HEIGHT):
                    if all(board[y]):
                        del board[y]
                        board.insert(0, [0] * WIDTH)

                falling_tetromino_index = (falling_tetromino_index + 1) % len(falling_tetromino_queue)
                falling_tetromino = falling_tetromino_queue[falling_tetromino_index]
                tetromino_pos = [4, 0]  # Reset position for new tetromino
                has_changed = False  # Reset change tracker for the new block

                # Check for game over condition after placing the tetromino
                if check_collision(falling_tetromino, tetromino_pos):
                    game_over = True  # Set the game over flag

            else:
                tetromino_pos = new_pos

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    tetromino_pos = move_tetromino(falling_tetromino, tetromino_pos, -1, 0)
                elif event.key == pygame.K_RIGHT:
                    tetromino_pos = move_tetromino(falling_tetromino, tetromino_pos, 1, 0)
                elif event.key == pygame.K_DOWN:
                    tetromino_pos = move_tetromino(falling_tetromino, tetromino_pos, 0, 1)
                elif event.key == pygame.K_UP:
                    # Pass the current position to rotate_tetromino
                    falling_tetromino, tetromino_pos = rotate_tetromino(falling_tetromino, tetromino_pos)
                elif event.key == pygame.K_z:
                    if not has_changed:  # Change block if not already changed
                        falling_tetromino_index = (falling_tetromino_index + 1) % len(falling_tetromino_queue)
                        falling_tetromino = falling_tetromino_queue[falling_tetromino_index]
                        has_changed = True
                elif event.key == pygame.K_SPACE:
                    tetromino_pos = drop_tetromino(falling_tetromino, tetromino_pos)
                    for y, row in enumerate(falling_tetromino):
                        for x, value in enumerate(row):
                            if value == 1:
                                board[tetromino_pos[1] + y][tetromino_pos[0] + x] = 1
                    for y in range(HEIGHT):
                        if all(board[y]):
                            del board[y]
                            board.insert(0, [0] * WIDTH)
                    falling_tetromino_index = (falling_tetromino_index + 1) % len(falling_tetromino_queue)
                    falling_tetromino = falling_tetromino_queue[falling_tetromino_index]
                    tetromino_pos = [4, 0]  # Reset position for new tetromino
                    has_changed = False  # Reset the change flag for the new tetromino

        # Calculate next tetromino for preview
        next_tetromino_index = (falling_tetromino_index + 1) % len(falling_tetromino_queue)
        next_tetromino = falling_tetromino_queue[next_tetromino_index]

        screen.fill(BLACK)
        draw_board()
        draw_tetromino(falling_tetromino, tetromino_pos)
        draw_tetromino_preview(falling_tetromino, next_tetromino, screen, BLOCK_SIZE, preview_offset)
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
