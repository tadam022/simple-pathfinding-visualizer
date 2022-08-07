import pygame
import sys
from queue import PriorityQueue
import time
import pygameButton
import random

# COLORS

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
PURPLE = (155, 0, 255)
GREY = (84, 82, 82)
DARK_GREY = (50, 45, 50)
DARK_ORANGE = (202, 103, 1)
BROWN = (100, 65, 25)
TEAL = (0, 170, 255)

GREEN = (130, 255, 130)
DARKER_GREEN = (0, 180, 0)
DARKEST_GREEN = (13, 77, 0)

GREENS = [GREEN, DARKER_GREEN, DARKEST_GREEN]

YELLOW = (255, 190, 0)
DARKER_YELLOW = (205, 205, 0)
DARKEST_YELLOW = (150, 130, 0)
YELLOWS = [YELLOW, DARKER_YELLOW, DARKEST_YELLOW]

RED = (255, 0, 0)
DARKER_RED = (150, 0, 0)
DARKEST_RED = (102, 0, 0)
REDS = [RED, DARKER_RED, DARKEST_RED]

# Other Constants

ROWS = 50
COLUMNS = 50

SQUARE_SIDE_LENGTH = 10
LINE_THICKNESS = 2

GUI_HEIGHT = 200

SCREEN_HEIGHT = ((SQUARE_SIDE_LENGTH + LINE_THICKNESS) * COLUMNS) + GUI_HEIGHT
SCREEN_WIDTH = ((SQUARE_SIDE_LENGTH + LINE_THICKNESS) * ROWS) + LINE_THICKNESS

SLOW = 0.05
FAST = 0.01
FASTEST = 0

# Initialization

pygame.init()
clock = pygame.time.Clock()
screen_display = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygame Pathfinding Visualizer")
screen_display.fill(BLACK)


class Node:
    def __init__(self, position, passable, color=WHITE, previous=None, distance=0, weight=1):
        self.previous = previous  # keeps track of shortest path in reverse
        self.position = position
        self.color = color
        self.passable = passable
        self.x = position[0]
        self.y = position[1]
        self.weight = weight
        self.distance = distance
        self.weight_color = color

    def get_x_val(self):
        return self.position[0]

    def get_y_val(self):
        return self.position[1]

    def __eq__(self, other):
        return self.position == other.position

    def __hash__(self):
        return hash(self.position)  # since we define nodes with the same position to be the same node, they will have
        # the same hash value

    def __lt__(self,
               other):  # Overrides < operator, in this case its for
        # comparing nodes in _put in heappush(self.queue, item)
        return False


font = pygame.font.SysFont('Sans', 16, True, False)  # Font name, size, bold, italics
buttons = []


def initialize_board():
    new_board = [[Node((row, column), True, WHITE) for row in range(COLUMNS)] for column in range(ROWS)]
    return new_board


def draw_board(board):
    for row in range(ROWS):
        for column in range(COLUMNS):
            pygame.draw.rect(screen_display, board[row][column].color, [
                (LINE_THICKNESS + SQUARE_SIDE_LENGTH) * column + LINE_THICKNESS,
                (LINE_THICKNESS + SQUARE_SIDE_LENGTH) * row + LINE_THICKNESS,
                SQUARE_SIDE_LENGTH,
                SQUARE_SIDE_LENGTH])


def make_buttons():
    x = 40
    y = SCREEN_HEIGHT - GUI_HEIGHT + 20

    # Diagonal button
    diagonal_text = " Diagonals: OFF "
    diagonal_button = pygameButton.Button("Diagonals_option", x, y, diagonal_text, YELLOW,
                                          GREY, font)

    buttons.append(diagonal_button)

    # Algorithm selection button
    algorithm_selection_text = center_text("A* Algorithm")
    x2 = diagonal_button.x + diagonal_button.size[0] + 40
    algorithm_selection_button = pygameButton.Button("Algorithm_selection", x2, y, algorithm_selection_text,
                                                     YELLOW, GREY, font)

    buttons.append(algorithm_selection_button)

    # Speed selection button
    speed_select_text = center_text(" Speed: Slow ")
    x3 = algorithm_selection_button.x + algorithm_selection_button.size[0] + 40
    speed_select_button = pygameButton.Button("Speed_select", x3, y, speed_select_text, YELLOW, GREY, font)

    buttons.append(speed_select_button)

    y = SCREEN_HEIGHT - GUI_HEIGHT + 60

    # View Instructions button
    instructions_text = "   See Controls   "
    instructions_button = pygameButton.Button("Controls", x-20, y, instructions_text, YELLOW, GREY, font)
    buttons.append(instructions_button)

    x2 -= 50
    # View Legend button
    legend_button = pygameButton.Button("Show_legend", x2, y, "   Board Legend   ", YELLOW, GREY, font)
    buttons.append(legend_button)

    # Generate Maze button
    maze_button = pygameButton.Button("Maze", x2+120, y, "   Generate Maze   ", YELLOW, GREY, font)
    buttons.append(maze_button)

    # View Detailed Colors button
    show_colors = pygameButton.Button("ShowColors", x3, y, "   Show Detailed Colors   ", YELLOW, GREY, font)
    buttons.append(show_colors)


def draw_GUI(show_instructions=False, show_legend=False):
    # GUI box
    pygame.draw.rect(screen_display, DARK_GREY, [
        0,
        SCREEN_HEIGHT + LINE_THICKNESS - GUI_HEIGHT,
        SCREEN_WIDTH,
        GUI_HEIGHT])

    for button in buttons:
        pygame.draw.rect(screen_display, button.button_color, button.rect)
        screen_display.blit(button.text, button.text_rect)
    if show_instructions:
        x = (LINE_THICKNESS + SQUARE_SIDE_LENGTH) * 10
        x += LINE_THICKNESS
        y = x

        instructions_text = " Use LMB to place walls" \
                            " Use RMB to clear tiles \n" \
                            " Press S with LMB to place start node\n" \
                            " Press E  with LMB to place end node\n" \
                            " Press T with LMB to place nodes with weight 2" \
                            " Press R with LMB to place nodes with weight 5" \
                            " Press space bar to start selected algorithm\n" \
                            " Press C to clear board\n" \
                            " Press V to clear and keep walls\n" \
                            " Press B to clear and keep start, end and walls\n" \
                            " Press N to clear, but keep all placed tiles\n" \
                            " Click Anywhere to minimize this window\n"

        text_box(screen_display, instructions_text, x, y, YELLOW)

    if show_legend:
        legend_popup(screen_display, 100, 50)


def text_box(surface, text, pos_x, pos_y, text_color):
    font2 = pygame.font.SysFont('Sans', 20, True, False)  # Font name, size, bold, italics
    split = text.splitlines()
    longest_line = str(max(split, key=len))
    rect_width = font2.render(longest_line, True, text_color).get_size()[0] + 10
    words_in_row = [word.split(" ") for word in split]
    space_xsize = font2.size(" ")[0]  # x value, width of each space
    max_w = surface.get_size()[0]
    x, y = pos_x, pos_y

    for row in words_in_row:
        total = 0
        x = pos_x
        for i in range(len(row)):

            word_surface = font2.render(row[i], True, text_color)
            word_width, word_height = word_surface.get_size()


            if x + word_width >= max_w:
                x = pos_x
                total = 0
                y += word_height
            rect = word_surface.get_rect()
            if i == len(row) - 1:  # if on last word
                inc = (rect_width - total)

            else:
                inc = rect.w + space_xsize

            pygame.draw.rect(surface, DARK_GREY, [x, y, inc + space_xsize, rect.h])
            surface.blit(word_surface, (x, y))
            x += word_width + space_xsize
            total += word_width + space_xsize

            if i == len(row) - 1:  # move y to next line
                y += word_height

    # Drawing borders around window
    pygame.draw.rect(surface, GREY, [pos_x - 5, pos_y, 5, y - pos_y])
    pygame.draw.rect(surface, GREY, [pos_x + rect_width, pos_y, 5, y - pos_y])
    pygame.draw.rect(surface, GREY, [pos_x - 5, y, rect_width + 10, 5])
    pygame.draw.rect(surface, GREY, [pos_x - 5, pos_y - 5, rect_width + 10, 5])


def legend_popup(surface, pos_x, pos_y):
    colors = [BLUE, TEAL, GREY, WHITE, PURPLE, BROWN, GREEN, YELLOW, RED, None, None, None,
              GREEN, DARKER_GREEN, DARKEST_GREEN,
              YELLOW, DARKER_YELLOW, DARKEST_YELLOW,
              RED, DARKER_RED, DARKEST_RED]
    legend_text = " Start node\n" \
                  " End node\n" \
                  " Wall \n" \
                  " Default tile with weight  1 \n" \
                  " Weighted tile with weight 2 \n" \
                  " Weighted tile with weight 5 \n" \
                  " Found path \n" \
                  " Visited Node \n" \
                  " Closed Node \n" \
                  " \n" \
                  " With detailed colors: \n" \
                  " \n" \
                  " Found path over default tile (White Tile): \n" \
                  " Found path over tile with weight 2 (Purple Tile): \n" \
                  " Found path over tile with weight 5 (Brown Tile): \n" \
                  " Visited default tile (White Tile): \n" \
                  " Visited weighted tile with weight 2 (Purple Tile): \n" \
                  " Visited weighted tile with weight 5 (Brown Tile): \n" \
                  " Closed default tile (White Tile): \n" \
                  " Closed weighted tile with weight 2 (Purple Tile): \n" \
                  " Closed weighted tile with weight 5  (Brown Tile): \n"

    font2 = pygame.font.SysFont('Sans', 20, True, False)  # Font name, size, bold, italics
    split = legend_text.splitlines()
    longest_line = max(split, key=len)
    rect_width = font2.render(longest_line, True, YELLOW).get_size()[0] + 50
    words_in_row = [word.split(" ") for word in split]
    space_xsize = font2.size(" ")[0]  # x value, width of each space
    max_w = surface.get_size()[0]
    x, y = pos_x, pos_y

    square_space = 20

    counter = 0
    for row in words_in_row:

        total = 0
        x = pos_x + square_space

        pygame.draw.rect(surface, DARK_GREY, [pos_x, y, square_space, square_space + 6])
        if colors[counter] is not None:
            pygame.draw.rect(surface, colors[counter], [pos_x + 5, y + 6, SQUARE_SIDE_LENGTH, SQUARE_SIDE_LENGTH])
        for i in range(len(row)):

            word_surface = font2.render(row[i], True, YELLOW)
            word_width, word_height = word_surface.get_size()

            if x + word_width >= max_w:
                x = pos_x
                total = 0
                y += word_height
            rect = word_surface.get_rect()
            if i == len(row) - 1:  # if on last word
                inc = (rect_width - total)

            else:
                inc = rect.w + space_xsize

            pygame.draw.rect(surface, DARK_GREY, [x, y, inc + space_xsize, rect.h])
            surface.blit(word_surface, (x, y))

            x += word_width + space_xsize
            total += word_width + space_xsize

            if i == len(row) - 1:  # move y to next line
                y += word_height

        counter += 1

        # pygame.draw.rect(surface, DARK_GREY, [pos_x + 5, y - rect.h, square_space, rect.h])

    #  Drawing borders around window
    pygame.draw.rect(surface, GREY, [pos_x - 5, pos_y, 5, y - pos_y])  # Left
    pygame.draw.rect(surface, GREY, [pos_x + rect_width + square_space, pos_y, 5, y - pos_y])  # Right

    pygame.draw.rect(surface, GREY, [pos_x - 5, pos_y - 5, rect_width + 10 + square_space, 5])  # Top
    pygame.draw.rect(surface, GREY, [pos_x - 5, y, rect_width + 10 + square_space, 5])  # Bottom


def check_if_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


def draw_console(console_message):
    pos_x = 50
    pos_y = SCREEN_HEIGHT + LINE_THICKNESS - GUI_HEIGHT + 100
    console_rect = pygame.Rect([pos_x, pos_y, SCREEN_WIDTH - 100, 80])

    pygame.draw.rect(screen_display, GREY, console_rect)

    x, y = pos_x + 5, pos_y
    space_xsize = font.size(" ")[0]  # x value, width of each space
    words = console_message.split(" ")

    for word in words:
        if check_if_number(word) or word.lower() == "unweighted":
            word_surface = font.render(word, True, RED)
        else:
            word_surface = font.render(word, True, YELLOW)
        word_width, word_height = word_surface.get_size()

        if x + word_width > console_rect.w - 10:
            x = pos_x + 5
            y += word_height + 5
        screen_display.blit(word_surface, (x, y))
        x += word_width + space_xsize


def on_click_diagonals(button, can_move_diagonally):
    if can_move_diagonally:
        can_move_diagonally = False
        button.change_text(" Diagonals: OFF ")
    else:
        can_move_diagonally = True
        button.change_text(" Diagonals: ON ")
    return can_move_diagonally


def center_text(new_text):
    if len(new_text) < 30:
        remainder = 30 - len(new_text)
        spacing = remainder // 2
        new_text = " " * spacing + new_text + " " * spacing
    return new_text


def on_click_algorithm_select(button, algorithms_dict, reverse=False):
    # maybe storing function calls in a dict is better

    if not reverse:
        if button.counter + 1 >= len(algorithms_dict):
            button.counter = 0
        else:
            button.counter += 1
    else:
        if button.counter == 0:
            button.counter = len(algorithms_dict) - 1
        else:
            button.counter -= 1

    new_text = center_text(algorithms_dict[button.counter])

    button.change_text(new_text)
    algorithm_index_selection = button.counter
    return algorithm_index_selection


def on_click_speed_select(button, speeds_index, speeds):
    if speeds_index + 1 >= len(speeds):
        speeds_index = 0
    else:
        speeds_index += 1
    new_text = center_text(speeds[speeds_index][0])
    button.change_text(new_text)
    return speeds_index


def on_click_show_colors(button, showing):
    if not showing:
        button.change_text("   Hide Detailed Colors   ")
        return True
    else:
        button.change_text("   Show Detailed Colors   ")
        return False


def clicked_in_GUI():
    mouse_position = pygame.mouse.get_pos()
    if 0 <= mouse_position[0] <= SCREEN_WIDTH:
        if SCREEN_HEIGHT - GUI_HEIGHT <= mouse_position[1] <= SCREEN_HEIGHT:
            return True
    return False


def get_mouse_coordinates_to_grid_row_and_column():
    mouse_position = pygame.mouse.get_pos()
    mouse_column = mouse_position[0] // (SQUARE_SIDE_LENGTH + LINE_THICKNESS)
    mouse_row = mouse_position[1] // (SQUARE_SIDE_LENGTH + LINE_THICKNESS)
    return mouse_row, mouse_column


def color_square(board, color, is_passable, start, end, start_placed, end_placed):
    mouse_coords = get_mouse_coordinates_to_grid_row_and_column()
    mouse_row = mouse_coords[0]
    mouse_column = mouse_coords[1]

    if color == BROWN:
        weight = 5
    elif color == PURPLE:
        weight = 2
    else:
        weight = 1

    try:
        if board[mouse_row][mouse_column].color == BLUE:
            start_placed = False
            start = (999, 999)

        elif board[mouse_row][mouse_column].color == TEAL:
            end_placed = False
            end = (999, 999)

        if color == BLUE:
            start = (mouse_column, mouse_row)
            start_placed = True
        elif color == TEAL:
            end = (mouse_column, mouse_row)
            end_placed = True

        board[mouse_row][mouse_column].weight = weight
        board[mouse_row][mouse_column].color = color
        board[mouse_row][mouse_column].weight_color = color
        board[mouse_row][mouse_column].passable = is_passable

        return start, end, start_placed, end_placed  # Mutability, no need to return the board
    except IndexError:  # User clicks outside grid (onto buttons)
        return


def color_visited(board, position, show_detailed_colors):
    if show_detailed_colors:
        if board[position[1]][position[0]].weight == 2:
            board[position[1]][position[0]].color = DARKER_YELLOW
        elif board[position[1]][position[0]].weight == 5:
            board[position[1]][position[0]].color = DARKEST_YELLOW
        else:
            board[position[1]][position[0]].color = YELLOW
    else:
        board[position[1]][position[0]].color = YELLOW


def color_closed(board, position, show_detailed_colors):
    if show_detailed_colors:
        if board[position[1]][position[0]].weight == 2:  # PURPLE TILES
            board[position[1]][position[0]].color = DARKER_RED
        elif board[position[1]][position[0]].weight == 5:  # BROWN TILES
            board[position[1]][position[0]].color = DARKEST_RED
        else:  # WHITE TILES
            board[position[1]][position[0]].color = RED
    else:
        board[position[1]][position[0]].color = RED


def check_if_weighted_tiles(board):
    for row in range(len(board)):
        for column in range(len(board[0])):
            if board[row][column].color == BROWN or board[row][column].color == PURPLE:
                return True
    return False


def breadth_first_search(board, start_pos, end_pos, diagonals_on, speed, increments, show_detailed_colors):
    if check_if_weighted_tiles(board):
        msg = "Breadth first search only works on unweighted graphs. Remove all weighted tiles " \
              "(the Purple and Brown tiles) with B key, or press/hold RMB on them"
        return None, msg

    return dijkstras_algorithm(board, start_pos, end_pos, diagonals_on, speed, increments, show_detailed_colors)


def dijkstras_algorithm(board, start_pos, end_pos, diagonals_on, speed, increments, show_detailed_colors):
    return a_star_algorithm(board, start_pos, end_pos, diagonals_on, speed, increments, show_detailed_colors, False)


def get_return_path(end_node):

    return_path = []
    current = end_node
    while current is not None:
        return_path.append(current.position)
        current = current.previous

    return return_path[::-1]  # Return reversed path to get path going from start to end


def a_star_algorithm(board, start_pos, end_pos, diagonals_on, speed, increments, show_detailed_colors,
                     use_heuristic=True):
    open_vertices = PriorityQueue()

    move_set = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    if diagonals_on:
        move_set.extend([(-1, -1), (-1, 1), (1, -1), (1, 1)])

    count = 0  # tie breaker for better/smoother looking visualization
    start_node = Node(start_pos, True)
    end_node = Node(end_pos, True)
    current_cost = {start_node: 0} # node: cost
    open_vertices.put((0, count, start_node))
    # Compares TUPLES lexographically, first compares the first tuple item of each priority,
    # if they are equal it then compares the next.

    while not open_vertices.empty():

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c or event.key == pygame.K_x:
                    clear_board(board, start_pos, end_pos, keep_weights=True, keep_start_and_end=True,
                                clear_walls=False)
                    # No need to have start_placed and end_placed passed, as those are kept when algorithm is stopped
                    # mid way.

                    msg = "Board reset."

                    return (None, 0), msg

        current_node = open_vertices.get()[2]

        if current_node == end_node:
            return_path = get_return_path(current_node)
            return (return_path, current_node.distance), None

        for index, move in enumerate(move_set):  # Possible neighbors to current node

            new_node_position = (current_node.position[0] + move[0], current_node.position[1] + move[1])

            if not (new_node_position[0] > (len(board) - 1) or new_node_position[0] < 0 or new_node_position[1] > (
                    len(board[len(board) - 1]) - 1) or new_node_position[1] < 0):

                if board[new_node_position[1]][new_node_position[0]].passable:
                    node_weight = board[new_node_position[1]][new_node_position[0]].weight
                    new_node = Node(new_node_position, True, previous=current_node, distance=current_node.distance,
                                    weight=node_weight)
                    # Use default color for new node as color doesn't matter

                    if index > 3:  # diagonals
                        increment = increments[new_node.weight]
                    else:
                        increment = new_node.weight

                    new_node.distance += increment

                    new_cost = current_cost[current_node] + increment # not necessarily equal to current_node.distance

                    if new_node not in current_cost or new_cost < current_cost[new_node]:
                        count += increment # could be incremented by some other amount
                        current_cost[new_node] = new_cost
                        priority = new_cost

                        if use_heuristic:
                            priority += heuristic(new_node.position, end_node.position)
                        open_vertices.put((priority, count, new_node))  # TIE BREAKER. SMOOTHER FOR NO DIAGONALS
                        if new_node != end_node:
                            color_visited(board, new_node.position, show_detailed_colors)

        if speed != FASTEST:
            if speed != FAST:
                time.sleep(speed)
            draw_board(board)
            pygame.display.update()

        if current_node != start_node:
            color_closed(board, current_node.position, show_detailed_colors)

    msg = "No possible path found."
    return (None, 0), msg


def heuristic(point1, point2):
    return abs(point1[0] - point2[0]) + abs(point1[1] - point2[1])


def best_first_search(board, start_pos, end_pos, diagonals_on, speed, increments, show_detailed_colors):
    open_vertices = PriorityQueue()

    move_set = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    if diagonals_on:
        move_set.extend([(-1, -1), (-1, 1), (1, -1), (1, 1)])

    count = 0  # tie breaker for better/smoother visualization
    start_node = Node(start_pos, True)
    end_node = Node(end_pos, True)
    open_vertices.put((0, start_node))
    previous = {start_node: None}

    while not open_vertices.empty():

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c or event.key == pygame.K_x:
                    clear_board(board, start_pos, end_pos, keep_weights=True, keep_start_and_end=True,
                                clear_walls=False)  # Don't need to assign returned values here
                    msg = "Board Reset."

                    return (None, 0), msg

        current_node = open_vertices.get()[1]

        if current_node == end_node:
            return_path = []
            current = current_node
            distance = current.distance
            while current in previous:
                if current:
                    return_path.append(current.position)
                current = previous[current]
            return (return_path[::-1], distance), None  # Return reversed path

        for index, move in enumerate(move_set):  # Possible neighbors to current node

            new_node_position = (current_node.position[0] + move[0], current_node.position[1] + move[1])

            if not (new_node_position[0] > (len(board) - 1) or new_node_position[0] < 0 or new_node_position[1] > (
                    len(board[len(board) - 1]) - 1) or new_node_position[1] < 0):

                if board[new_node_position[1]][new_node_position[0]].passable:
                    node_weight = board[new_node_position[1]][new_node_position[0]].weight
                    new_node = Node(new_node_position, True, previous=current_node, distance=current_node.distance,
                                    weight=node_weight)
                    # Use default color for new node as color doesn't matter

                    if index > 3:  # diagonals
                        increment = increments[new_node.weight]
                    else:
                        increment = new_node.weight

                    new_node.distance += increment

                    if new_node not in previous:

                        count += increment
                        priority = heuristic(new_node.position, end_node.position)
                        open_vertices.put((priority, new_node))
                        previous[new_node] = current_node
                        if new_node != end_node:
                            color_visited(board, new_node.position, show_detailed_colors)
        if speed != FASTEST:
            if speed != FAST:
                time.sleep(speed)
            draw_board(board)
            pygame.display.update()

        if current_node != start_node:
            color_closed(board, current_node.position, show_detailed_colors)

    msg = "No possible path found with Best First Search."
    return (None, 0), msg


def depth_first_search(board, start_pos, end_pos, diagonals_on, speed, increments, show_detailed_colors):
    if check_if_weighted_tiles(board):
        msg = "Depth first search only works on unweighted graphs. Remove all weighted tiles " \
              "(the Purple and Brown tiles) with B key, or press/hold RMB on them"
        return None, msg

    start_node = Node(start_pos, True)
    end_node = Node(end_pos, True)
    stack = [start_node]
    visited_nodes = set()
    visited_nodes.add(start_node)

    move_set = [(-1, 0), (1, 0), (0, -1), (0, 1), ]
    if diagonals_on:
        move_set.extend([(-1, -1), (-1, 1), (1, -1), (1, 1)])

    while stack:  # Not empty

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c or event.key == pygame.K_x:
                    clear_board(board, start_pos, end_pos, keep_weights=True, keep_start_and_end=True,
                                clear_walls=False)
                    msg = "Board Reset."

                    return (None, 0), msg

        current_node = stack.pop()
        if current_node == end_node:

            return_path = get_return_path(current_node)
            return (return_path, current_node.distance), None

        for index, move in enumerate(move_set):

            new_node_position = (current_node.position[0] + move[0], current_node.position[1] + move[1])

            if not (new_node_position[0] > (len(board) - 1) or new_node_position[0] < 0 or new_node_position[1] > (
                    len(board[len(board) - 1]) - 1) or new_node_position[1] < 0):

                if board[new_node_position[1]][new_node_position[0]].passable and board[new_node_position[1]][
                    new_node_position[0]] \
                        not in visited_nodes:
                    node_weight = board[new_node_position[1]][new_node_position[0]].weight
                    new_node = Node(new_node_position, True, previous=current_node, distance=current_node.distance,
                                    weight=node_weight)
                    # Use default color for new node as color doesn't matter

                    if index > 3:  # diagonals
                        increment = increments[new_node.weight]
                    else:
                        increment = new_node.weight
                    new_node.distance += increment
                    stack.append(new_node)
                    visited_nodes.add(new_node)

                    if new_node != end_node:
                        color_visited(board, new_node.position, show_detailed_colors)

        if speed != FASTEST:
            if speed != FAST:
                time.sleep(speed)
            draw_board(board)
            pygame.display.update()

        if current_node != start_node:
            color_closed(board, current_node.position, show_detailed_colors)

    msg = "No possible path found with Depth First Search."
    return (None, 0), msg


def draw_path(board, path, speed, show_detailed_colors=False):
    if path and len(path) != 0:

        for node_position in path[1:len(path) - 1]:
            current = board[node_position[1]][node_position[0]]
            weight = current.weight

            if show_detailed_colors:
                if weight == 1:
                    current.color = GREEN
                elif weight == 2:
                    current.color = DARKER_GREEN
                elif weight == 5:
                    current.color = DARKEST_GREEN
            else:
                current.color = GREEN

            time.sleep(speed)
            draw_board(board)
            pygame.display.update()

def check_valid(start_placed, end_placed):
    if start_placed and end_placed:
        return True
    elif not start_placed:

        error_message = "Must place start node (Press s then left click on board) "
    elif not end_placed:

        error_message = "Must place end node (Press e then left click on board) "
    else:

        error_message = "Must place end and starting nodes (Use keys e and s respectively with left click on board)"
    return error_message


def clear_board(the_board, start_pos, end_pos, clear_walls=True, keep_start_and_end=False, keep_weights=False):
    console_message = "Board, "
    for row in range(len(the_board)):
        for column in range(len(the_board[0])):
            # More concise to make new node instead of resetting each parameter like distance
            if the_board[row][column].color == GREY:
                if clear_walls:
                    the_board[row][column] = Node((column, row), True)
            elif the_board[row][column].color == BROWN \
                    or the_board[row][column].color == PURPLE \
                    or the_board[row][column].color in GREENS or the_board[row][column].color in REDS \
                    or the_board[row][column].color in YELLOWS:

                if keep_weights:
                    weight = the_board[row][column].weight
                    color = the_board[row][column].weight_color
                    the_board[row][column] = Node((column, row), True, color, weight=weight)
                else:

                    the_board[row][column] = Node((column, row), True)
            else:
                the_board[row][column] = Node((column, row), True)
    if clear_walls:
        console_message += "Walls, "

    if not keep_weights:
        console_message += "Weighted tiles, "
    console_message = console_message[:-2] + " Cleared. "

    if not clear_walls:
        console_message += "Walls kept. "

    if keep_start_and_end:
        try:
            the_board[start_pos[1]][start_pos[0]].color = BLUE
            the_board[end_pos[1]][end_pos[0]].color = TEAL
            console_message += "Start and End tiles Kept"

        except IndexError:
            pass
        start_placed = True
        end_placed = True
    else:
        start_placed = False
        end_placed = False
        start_pos = (999, 999)
        end_pos = (999, 999)
        console_message += " Start and End tiles cleared"
    found = False

    return start_placed, end_placed, found, the_board, start_pos, end_pos, console_message


def generate_maze(board):

    move_set = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    for r in range(len(board)):
        for d in range(len(board[r])):
            board[r][d].color = GREY
            board[r][d].passable = False
    starting_nodes = [(0, 0), (COLUMNS-1, 0), (0, ROWS-1), (COLUMNS-1, ROWS-1)]
    starting_position = random.choice(starting_nodes)
    start_node = Node(starting_position, True)
    stack = [start_node]
    visited = set()
    visited.add(start_node)
    while stack:
        n = stack[-1]
        random.shuffle(move_set)

        for move in move_set:
            new_node_position = (n.position[0] + move[0], n.position[1] + move[1])
            if not (new_node_position[0] > (len(board) - 1) or new_node_position[0] < 0 or new_node_position[1] > (
                    len(board[len(board) - 1]) - 1) or new_node_position[1] < 0):
                new_node = Node(new_node_position, True)
                if new_node not in visited:
                    board[n.position[1]][n.position[0]].color = WHITE

                    stack.append(new_node)
                    visited.add(new_node)

        stack.pop()

def main():
    found = False
    can_move_diagonally = False
    mouse_left_pressed = False
    mouse_right_pressed = False
    place_start = False
    place_end = False
    start_placed = False
    end_placed = False

    start_pos = (999, 999)
    end_pos = (999, 999)

    algorithms_dict = {0: " A* Algorithm ", 1: " Dijkstra's Algorithm ", 2: " Breadth First Search ",
                       3: " Depth First Search ", 4: " Best First Search "}
    algorithm_index_selection = 0
    speeds = {0: ("Speed: Slow", SLOW), 1: ("Speed: Fast", FAST),
              2: ("Speed: Fastest", FASTEST)}
    speeds_index = 0

    increments = {1: 1.41, 2: 2.82, 5: 7.07}
    the_board = initialize_board()
    make_buttons()

    instructions_popup_active = False
    legend_popup_active = False
    show_detailed_colors = False
    default_message = "Click on the buttons above to change the options, and view the controls or legend. " \
                      "Hover over buttons to see what they do."
    message = default_message

    while True:

        for btn in buttons:
            if btn.is_hovered():

                btn.change_button_color(DARK_ORANGE)
                if btn.button_name == "Diagonals_option":
                    message = "Turn on or off diagonal movement. "
                    if can_move_diagonally:
                        message += "Currently, diagonal movement is on."
                    else:
                        message += "Currently, diagonal movement is off."

                elif btn.button_name == "Controls":
                    message = "Click to show what keyboard controls you can use."

                elif btn.button_name == "Algorithm_selection":
                    message = "Shows the currently selected path-finding algorithm. Click to cycle through available " \
                              "algorithms. Some only work on unweighted graphs."
                elif btn.button_name == "Speed_select":
                    message = "Change the speed of the visualization."

                elif btn.button_name == "ShowColors":
                    message = "Click to show detailed colors. Doesn't update  the current board, the algorithm must " \
                              "be re-run. "

                elif btn.button_name == "Show_legend":
                    message = "Click to show the legend, detailing what each colored node represents."

                elif btn.button_name == "Maze":
                    message = "Generates a random recursive maze with walls on the board."
            else:
                btn.change_button_color(btn.original_color)

        if instructions_popup_active:
            message = "Click anywhere to dismiss controls window"

        elif legend_popup_active:
            message = "Click anywhere to dismiss legend window"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN and not instructions_popup_active and not legend_popup_active:

                if event.key == pygame.K_s:
                    place_start = True
                    place_end = False
                elif event.key == pygame.K_e:
                    place_start = False
                    place_end = True

                elif event.key == pygame.K_c:
                    start_placed, end_placed, found, the_board, start_pos, end_pos, message = \
                        clear_board(the_board, start_pos, end_pos)

                elif event.key == pygame.K_v:
                    start_placed, end_placed, found, the_board, start_pos, end_pos, message = \
                        clear_board(the_board, start_pos, end_pos,
                                    keep_start_and_end=True,
                                    keep_weights=True)

                elif event.key == pygame.K_b:
                    start_placed, end_placed, found, the_board, start_pos, end_pos, message = \
                        clear_board(the_board, start_pos, end_pos, clear_walls=False,
                                    keep_start_and_end=True)

                elif event.key == pygame.K_n:
                    start_placed, end_placed, found, the_board, start_pos, end_pos, message = \
                        clear_board(the_board, start_pos, end_pos, clear_walls=False,
                                    keep_start_and_end=True, keep_weights=True)

                elif event.key == pygame.K_SPACE:

                    is_valid = check_valid(start_placed, end_placed)
                    if type(is_valid) == bool and is_valid:
                        selected_speed = speeds[speeds_index][1]

                        start_placed, end_placed, found, the_board, start_pos, end_pos, message = \
                            clear_board(the_board, start_pos, end_pos, clear_walls=False, keep_start_and_end=True,
                                        keep_weights=True)

                        message = "Running algorithm: " + str(algorithms_dict[algorithm_index_selection])[:-1] + ". "
                        message += "Press x or c keys to reset board to how it was before the algorithm was started."
                        draw_console(message)
                        for btn in buttons:
                            btn.set_active(False)
                        draw_GUI()
                        draw_console(message)

                        if algorithm_index_selection == 0:
                            p, message = a_star_algorithm(the_board, start_pos, end_pos, can_move_diagonally,
                                                          selected_speed, increments, show_detailed_colors, True)

                        elif algorithm_index_selection == 1:
                            p, message = dijkstras_algorithm(the_board, start_pos, end_pos, can_move_diagonally,
                                                             selected_speed, increments, show_detailed_colors)

                        elif algorithm_index_selection == 2:
                            p, message = breadth_first_search(the_board, start_pos, end_pos, can_move_diagonally,
                                                              selected_speed, increments, show_detailed_colors)

                        elif algorithm_index_selection == 3:
                            p, message = depth_first_search(the_board, start_pos, end_pos, can_move_diagonally,
                                                            selected_speed, increments, show_detailed_colors)

                        elif algorithm_index_selection == 4:
                            p, message = best_first_search(the_board, start_pos, end_pos, can_move_diagonally,
                                                           selected_speed, increments, show_detailed_colors)
                        else:
                            p = None

                        path = None
                        if p:  # Not interrupted
                            if p[0]:
                                path = p[0]

                        draw_path(the_board, path, selected_speed, show_detailed_colors)

                        if path:
                            message = "Path found with" + str(algorithms_dict[algorithm_index_selection])[:-1] + ". "
                            if type(p[1]) == int:
                                message += f"Distance is: {p[1]} "
                            else:
                                message += f"Distance is Approximately: {round(p[1], 3)} "
                            message += "(Including end node)."  # probably obvious...
                            if algorithm_index_selection == 3:
                                message += " Depth First Search does not guarantee the shortest path."
                            elif algorithm_index_selection == 4:
                                message += " Best First Search does not guarantee the shortest path."
                        for btn in buttons:
                            btn.set_active(True)
                        draw_GUI()

                    else:
                        message = is_valid
                draw_console(message)
                pygame.display.update()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_button = event.button
                if not instructions_popup_active and not legend_popup_active:
                    if mouse_button == 1 and not clicked_in_GUI():
                        if place_start:
                            if start_pos[0] != 999 and start_pos[1] != 999:
                                the_board[start_pos[1]][start_pos[0]].color = WHITE  # Clear previously placed start
                            start_pos, end_pos, start_placed, end_placed = color_square(the_board, BLUE, True,
                                                                                        start_pos,
                                                                                        end_pos, start_placed,
                                                                                        end_placed)
                            # Mutability, no need to return the board
                            place_start = False

                        elif place_end:

                            if end_pos[0] != 999 and end_pos[1] != 999:
                                the_board[end_pos[1]][end_pos[0]].color = WHITE  # Clear previously placed end
                            start_pos, end_pos, start_placed, end_placed = color_square(the_board, TEAL, True,
                                                                                        start_pos,
                                                                                        end_pos, start_placed,
                                                                                        end_placed)
                            place_end = False

                        else:
                            mouse_left_pressed = True

                    elif mouse_button == 1 and clicked_in_GUI():

                        # BUTTONS

                        for btn in buttons:
                            if btn.is_clicked(event) and not found and btn.is_active:
                                if btn.button_name == "Diagonals_option":
                                    can_move_diagonally = on_click_diagonals(btn, can_move_diagonally)

                                elif btn.button_name == "Controls":
                                    if instructions_popup_active:
                                        instructions_popup_active = False
                                    else:
                                        instructions_popup_active = True

                                elif btn.button_name == "Algorithm_selection":
                                    algorithm_index_selection = on_click_algorithm_select(btn, algorithms_dict)

                                elif btn.button_name == "Speed_select":
                                    speeds_index = on_click_speed_select(btn, speeds_index, speeds)

                                elif btn.button_name == "ShowColors":
                                    show_detailed_colors = on_click_show_colors(btn, show_detailed_colors)

                                elif btn.button_name == "Show_legend":
                                    if legend_popup_active:
                                        legend_popup_active = False
                                    else:
                                        legend_popup_active = True

                                elif btn.button_name == "Maze":
                                    start_placed, end_placed, found, the_board, start_pos, end_pos, message = \
                                        clear_board(the_board, start_pos, end_pos, clear_walls=True,
                                                    keep_start_and_end=False,
                                                    keep_weights=False)
                                    generate_maze(the_board)

                    elif mouse_button == 3 and clicked_in_GUI():
                        for btn in buttons:
                            if btn.is_clicked(event) and not found and btn.is_active:
                                if btn.button_name == "Algorithm_selection":
                                    algorithm_index_selection = on_click_algorithm_select(btn, algorithms_dict,
                                                                                          reverse=True)

                    elif mouse_button == 3:
                        mouse_right_pressed = True
                elif instructions_popup_active:
                    instructions_popup_active = False
                    message = default_message

                elif legend_popup_active:
                    legend_popup_active = False
                    message = default_message

            elif event.type == pygame.MOUSEBUTTONUP and not instructions_popup_active:
                mouse_button = event.button
                if mouse_button == 1:
                    mouse_left_pressed = False
                elif mouse_button == 3:
                    mouse_right_pressed = False
        pressed = pygame.key.get_pressed()

        if mouse_left_pressed and pressed[pygame.K_r]:
            try:
                start_pos, end_pos, start_placed, end_placed = color_square(the_board, BROWN, True, start_pos, end_pos,
                                                                            start_placed, end_placed)
            except TypeError:  # Dragged off grid/window
                pass
        elif mouse_left_pressed and pressed[pygame.K_t]:
            try:
                start_pos, end_pos, start_placed, end_placed = color_square(the_board, PURPLE, True, start_pos, end_pos,
                                                                            start_placed, end_placed)
            except TypeError:
                pass
        elif mouse_left_pressed:  # Place walls
            try:
                start_pos, end_pos, start_placed, end_placed = color_square(the_board, GREY, False, start_pos, end_pos,
                                                                            start_placed, end_placed)
            except TypeError:
                pass

        elif mouse_right_pressed:  # Remove node, replace with default
            try:
                start_pos, end_pos, start_placed, end_placed = color_square(the_board, WHITE, True, start_pos, end_pos,
                                                                            start_placed, end_placed)
            except TypeError:
                pass

        if instructions_popup_active:

            draw_GUI(instructions_popup_active)
            draw_console(message)
            pygame.display.update()
        elif legend_popup_active:
            draw_GUI(show_legend=legend_popup_active)
            draw_console(message)
            pygame.display.update()

        else:
            screen_display.fill(BLACK)
            draw_GUI()
            draw_board(the_board)
            draw_console(message)

        pygame.display.update()
        clock.tick(120)


if __name__ == "__main__":
    main()
