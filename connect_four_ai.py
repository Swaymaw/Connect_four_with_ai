# To increase depth further:
# todo: Make a better winning move looking function by iterating over directions from the last made move

import numpy as np
import pygame
import sys
import math
import random
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

ROW_COUNTS = 6
COL_COUNTS = 7

SQUARESIZE = 100

PLAYER = 0
AI = 1

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

WINDOW_LENGTH = 4

width = COL_COUNTS * SQUARESIZE
height = (ROW_COUNTS + 1) * SQUARESIZE
size = (width, height)


def create_board():
    board = np.zeros((ROW_COUNTS, COL_COUNTS))
    return board


def drop_piece(board, row, col, piece):
    board[row][col] = piece


def is_valid_location(board, col):
    return board[ROW_COUNTS-1][col] == 0


def get_next_open_row(board, col):
    for r in range(ROW_COUNTS):
        if board[r][col] == 0:
            return r


def print_board(board):
    print(np.flip(board, 0))


def winning_move(board, piece):
    # Check all horizontal locations for win
    for c in range(COL_COUNTS - 3):
        for r in range(ROW_COUNTS):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True

    # Check all vertical locations for win
    for c in range(COL_COUNTS):
        for r in range(ROW_COUNTS - 3):
            if board[r][c] == piece and board[r + 1][c] == piece and board[r + 2][c] == piece and board[r + 3][c] == piece:
                return True

    # Check positively sloped diagnols
    for c in range(COL_COUNTS - 3):
        for r in range(ROW_COUNTS - 3):
            if board[r][c] == piece and board[r + 1][c + 1] == piece and \
               board[r + 2][c + 2] == piece and board[r + 3][c + 3] == piece:
                return True
    # Check negatively sloped diagnols
    for c in range(COL_COUNTS - 3):
        for r in range(3, ROW_COUNTS):
            if board[r][c] == piece and board[r - 1][c + 1] == piece and \
               board[r - 2][c + 2] == piece and board[r - 3][c + 3] == piece:
                return True

def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opp_piece = AI_PIECE

    if window.count(piece) == 4:
        score += 1000
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 30
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 15

    if window.count(opp_piece) == 2 and window.count(EMPTY) == 2:
        score -= 12

    return score


def score_position(board, piece):
    ## Score Horizontal
    score = 0
    # Adding more preference for the center pieces
    center_array = [int(i) for i in list(board[:, COL_COUNTS//2])]
    center_count = center_array.count(piece)
    score += center_count * 3
    for r in range(ROW_COUNTS):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COL_COUNTS - 3):
            window = row_array[c:c+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    ## Score Vertical
    for c in range(COL_COUNTS):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROW_COUNTS - 3):
            window = col_array[r:r+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    ## Score positively sloped diagnols
    for r in range(ROW_COUNTS - 3):
        for c in range(COL_COUNTS - 3):
            window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    ## Score negatively sloped diagnols
    for r in range(ROW_COUNTS - 3):
        for c in range(COL_COUNTS - 3):
            window = [board[r + 3 - i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score


def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0


def minimax(board, depth, alpha, beta, maximizing_player):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return (None, 10000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -10000)
            else:
                return (None, 0)
        else:
            return (None, score_position(board, AI_PIECE))

    if maximizing_player:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            _, new_score = minimax(b_copy, depth - 1, alpha, beta, False)
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else:    # Minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            _, new_score = minimax(b_copy, depth-1, alpha, beta, True)
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value


def get_valid_locations(board):
    valid_locations = []
    for col in range(COL_COUNTS):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations


def pick_best_move(board, piece):
    valid_locations = get_valid_locations()
    best_score = -100000
    best_col = random.choice(valid_locations)
    for col in valid_locations:
        row = get_next_open_row(board, col)
        temp_board = board.copy()
        drop_piece(temp_board, row, col, piece)
        score = score_position(temp_board, piece)
        if score > best_score:
            best_score = score
            best_col = col

    return best_col


def draw_board(board):
    for c in range(COL_COUNTS):
        for r in range(ROW_COUNTS):
            pygame.draw.rect(screen, BLUE, (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK,
                               (int(c * SQUARESIZE + SQUARESIZE / 2),
                                int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)),
                               RADIUS)

    for c in range(COL_COUNTS):
        for r in range(ROW_COUNTS):
            if board[r][c] == PLAYER_PIECE:
                pygame.draw.circle(screen, RED,
                                   (int(c * SQUARESIZE + SQUARESIZE / 2),
                                    height - int(r * SQUARESIZE + SQUARESIZE / 2)),
                                   RADIUS)
            elif board[r][c] == AI_PIECE:
                pygame.draw.circle(screen, YELLOW,
                                   (int(c * SQUARESIZE + SQUARESIZE / 2),
                                    height - int(r * SQUARESIZE + SQUARESIZE / 2)),
                                   RADIUS)
    pygame.display.update()


board = create_board()
print_board(board)
game_over = False

pygame.init()


RADIUS = int(SQUARESIZE/2 - 7)

screen = pygame.display.set_mode(size)
draw_board(board)
pygame.display.update()

myfont = pygame.font.SysFont('monospace', 75)

turn = random.randint(PLAYER, AI)

while not game_over:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
            pos_x = event.pos[0]
            if turn == PLAYER:
                pygame.draw.circle(screen, RED, (pos_x, int(SQUARESIZE/2)), RADIUS)
            # else:
            #    pygame.draw.circle(screen, YELLOW, (pos_x, int(SQUARESIZE / 2)), RADIUS)
        pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
            # Ask for Player 1 input
            if turn == PLAYER:
                pos_x = event.pos[0]
                col = int(math.floor(pos_x/SQUARESIZE))

                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, PLAYER_PIECE)

                    if winning_move(board, PLAYER_PIECE):
                        label = myfont.render("PLAYER 1 Wins!!!", True, RED)
                        screen.blit(label, (20, 10))
                        game_over = True
                    turn += 1
                    turn = turn % 2

                    print_board(board)
                    draw_board(board)

    # Ask for Player 2 input
    if turn == AI and not game_over:

        # col = random.randint(0, COL_COUNTS-1)
        # col = pick_best_move(board, AI_PIECE)
        col, minimax_score = minimax(board, 6, -math.inf, math.inf, True)

        if is_valid_location(board, col):
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, AI_PIECE)

            if winning_move(board, AI_PIECE):
                label = myfont.render("PLAYER 2 Wins!!!", True, YELLOW)
                screen.blit(label, (20, 10))
                game_over = True

            print_board(board)
            draw_board(board)

            turn += 1
            turn = turn % 2

    if game_over:
        pygame.time.wait(3000)
