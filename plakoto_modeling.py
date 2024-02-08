import numpy as np

# Constants
NUM_POINTS = 24
PIECES_PER_PLAYER = 15

# TODO:
# - Implement is_game_over()
# - Include the double rolls mechanic (done)
# - Include the mother checker rule
# - Complete the bearing off mechanic
# - Make robust state representation
# - Maintain a history of moves
# - Reinforce the rules of the game


class Plakoto:
    def __init__(self):
        self.board = self.initialize_board()
        self.current_player = 1 # Player 1 starts first
        self.dice = [0, 0]
        self.borne_off = [0, 0]
        self.move_history = []
        self.moves = []

    def initialize_board(self):
        board = [[0, 0, False, 0] for _ in range(NUM_POINTS)]
        board[23] = [PIECES_PER_PLAYER, 0, False, 0]
        board[0] = [0, PIECES_PER_PLAYER, False, 0]
        return board
    
    def initialize_board_custom(self, board):
        self.board = board
    
    def switch_player(self):
        self.current_player = 2 if self.current_player == 1 else 1

    def roll_dice(self):
        self.dice = [np.random.randint(1, 7), np.random.randint(1, 7)]
        return self.dice
    
    def get_dice(self):
        return self.dice
    
    def dice_moves(self):
        if self.dice[0] == self.dice[1]:
            self.moves = [self.dice[0]] * 4
        else:
            self.moves = self.dice
    
    def get_moves(self):
        return self.moves
    
    def get_move_history(self):
        return self.move_history
    
    def all_pieces_home(self):
        # print(f'Current player: {self.current_player}')
        start, end = (0, 6) if self.current_player == 1 else (18, 24)
        pieces_in = sum(pieces[self.current_player - 1] for _, pieces in enumerate(self.board[start:end]))
        # print(f'Pieces in: {pieces_in}')
        return pieces_in == 15

    def furthermost_piece(self):
        occupation = (np.array([pos[self.current_player - 1] for pos in self.board]) > 0)*1
        if self.current_player == 1:
            max_index = np.max(np.nonzero(occupation))
        elif self.current_player == 2:
            max_index = np.min(np.nonzero(occupation))
        return max_index
    
    def piece_can_born_off(self, start, end):
        if self.furthermost_piece() == start:
            target = -1 if self.current_player == 1 else 24
            if abs(end - target) in self.get_moves:
                return True
        return False




    
    def is_valid_move(self, start, end, verbose=True):
        # print(f"Validating move from {start} to {end}")
        # Ensure start and end are within the board
        # Allow 'off the board' moves for bearing off
        # if not (0 <= start < NUM_POINTS) or (self.current_player == 1 and end > NUM_POINTS) or (self.current_player == 2 and end < -1):
        #     if verbose:
        #         print(f"Invalid start or end point for player {self.current_player}: {start}, {end}")
        #     return False
        
        if not (0 <= start < NUM_POINTS):
            if verbose:
                print(f"Invalid start point for player {self.current_player}: {start}")
            return False
        
        can_bear_off = self.all_pieces_home()
        # print("CAN BEAR OFF -> ", can_bear_off)
        
        if can_bear_off:
            if self.current_player == 1:
                if not (-1 <= end < NUM_POINTS):
                    if verbose:
                        print(f"Invalid end point for player {self.current_player}: {end}")
                    return False
            else:
                if not (0 <= end < NUM_POINTS + 1):
                    if verbose:
                        print(f"Invalid end point for player {self.current_player}: {end}")
                    return False
        else:
            if not (0 <= end < NUM_POINTS):
                if verbose:
                    print(f"Invalid end point for player {self.current_player}: {end}")
                return False
        
        # Ensure start point has at least one piece of the current player
        player_pieces = self.board[start][self.current_player - 1]
        if player_pieces == 0:
            if verbose:
                print(f"No pieces to move at point {start}")
            # print(self.board)
            return False
        
        # Check if the move matches the dice roll
        move_check = abs(end - start) in self.moves
        if not move_check:
            if verbose:
                print(f'Invalid move: {abs(end - start)} does not match the dice roll {self.moves}')
            return False
        
        # Check for blocking or pinning
        # For Plakoto, a piece can pin an opponent's single piece, but cannot move to a point with two or more opponent pieces
        opponent = 2 if self.current_player == 1 else 1
        # print(f'Opponent: {opponent}, end: {end}')
        # print(f'Shape of board: {self.board[end]}')
        if (opponent == 1 and end != -1) and (opponent == 2 and end != 24):
            opponent_pieces = self.board[end][opponent - 1]
            is_pinned = self.board[end][2]
            pinning_player = self.board[end][3]
            if opponent_pieces >= 2:
                if verbose:
                    print(f"Cannot move to a point with two or more opponent pieces at point {end}")
                return False
            if opponent_pieces == 1 and not is_pinned:
                return True
        
            if self.board[end][2] and self.board[end][3] == opponent:
                if verbose:
                    print(f"Cannot move to a pinned point at point {end}")
                return False
            
        if end == -1 or end == 24:
            return False
        
        # print(f'Am I pinned? {self.board[start][2]} by {self.board[start][3]}')
        if self.board[start][2] and self.board[start][3] == opponent:
            if verbose:
                print(f"Cannot move pinned piece at point {start}")
            return False
        

        
        # # Check for bearing off
        # if self.all_pieces_home():
        #     if self.current_player == 1 and end == NUM_POINTS:
        #         # Player 1 is bearing off
        #         if start + self.dice[0] > NUM_POINTS - 1 or start + self.dice[1] > NUM_POINTS - 1:
        #             return True
        #         elif self.current_player == 2 and end == -1:
        #             # Player 2 is bearing off
        #             if start - self.dice[0] < 0 or start - self.dice[1] < 0:
        #                 return True
        #             else:
        #                 return False
                    
        return True
                    
    
    def move_piece(self, start, end):
        print(f"Moving piece from {start} to {end}")
        can_bear_off = self.all_pieces_home()
        # print(f'Can bear off? {can_bear_off}')
        opponent = 2 if self.current_player == 1 else 1
        opponent_pieces = self.board[end][opponent - 1]
        is_pinned = self.board[end][2]
        pinning_player = self.board[end][3]
        # Later make it a while loop
        if self.is_valid_move(start, end):
            player = self.current_player - 1
            self.board[start][player] -= 1

            if self.board[start][player] == 0:
                self.board[start][2] = False
                self.board[start][3] = 0

            if (self.current_player == 1 and end == NUM_POINTS) or (self.current_player == 2 and end == -1):
                self.borne_off[player] += 1
            else:
                self.board[end][player] += 1
                if opponent_pieces == 1 and not is_pinned:
                    print("Pinning opponent piece")
                    self.board[end][2] = True
                    self.board[end][3] = self.current_player

            self.moves.remove(abs(end - start))
            self.move_history.append((start, end))
            return True
        else:
            print("Invalid move")
            return False

    def get_valid_moves(self):
        valid_moves = []
        for start, pieces in enumerate(self.board):
            if pieces[self.current_player - 1] > 0:
                if self.current_player == 1:
                    for move in self.moves:
                        end = start - move
                        if self.is_valid_move(start, end, verbose=False):
                            valid_moves.append((start, end))
                if self.current_player == 2:
                    for move in self.moves:
                        end = start + move
                        if self.is_valid_move(start, end, verbose=False):
                            valid_moves.append((start, end))
        return valid_moves

    def get_state(self):
        pass

    def get_reward(self):
        # 0 for loss
        # 1 for simple win
        # 2 for double win (collecting all pieces without opponent bearing off any pieces)
        # 3 for triple win (capturing the mother checker)
        pass

    def setup_turn(self, verbose=True):
        if verbose:
            print(f"Player {self.current_player}'s turn")
        self.roll_dice()
        self.dice_moves()
        valid_moves = self.get_valid_moves()
        if verbose:
            print(f"Dice roll: {self.dice}")
            print(f"Possible moves: {self.moves}")
            print(f"Valid moves: {valid_moves}")
            can_bear_off = self.all_pieces_home()
            print(f'Can bear off? {can_bear_off}')
        if len(valid_moves) == 0:
            if verbose:
                print("No valid moves")
            self.switch_player()

    def play_turn(self, start, end, verbose=True):
        # valid_moves = self.get_valid_moves()
        # print("VM", len(valid_moves))
        # if len(valid_moves) == 0:
        #     if verbose:
        #         print("No valid moves")
        #     self.switch_player()

        if not self.move_piece(start, end) and verbose:
            print("Try again")

        if verbose:
            print(f"Moves left: {self.moves}")

        if len(self.moves) == 0:
            if verbose:
                print("Round over")
            self.switch_player()

        if verbose:
            self.visualize_board()

        if self.is_game_over() != 0:
            if self.is_game_over() == 1:
                print(f"Player {self.current_player} wins by simple win!")
            elif self.is_game_over() == 2:
                print(f"Player {self.current_player} wins by double win!")
            elif self.is_game_over() == 3:
                print(f"Player {self.current_player} wins by triple win!")
        



    def is_game_over(self):
        # Return 0 if game is not over
        # Return 1 if game is over by simple win
        # Return 2 if game is over by double win
        # Return 3 if game is over by triple win
        if self.borne_off[0] == PIECES_PER_PLAYER or self.borne_off[1] == PIECES_PER_PLAYER:
            return 1
        elif self.borne_off[0] == PIECES_PER_PLAYER and self.borne_off[1] == 0:
            return 2
        elif self.borne_off[1] == PIECES_PER_PLAYER and self.borne_off[0] == 0:
            return 2
        # elif mother checker is captured:
        #     return 3
        else:
            return 0

    def visualize_board(self):
        max_height = 1

        board_visual = []
        for p1_pieces, p2_pieces, _, _ in self.board:
            point_repr = ''
            if p1_pieces > max_height:
                point_repr += f'o{p1_pieces}'
            else:
                point_repr += 'o' * p1_pieces

            if p2_pieces > max_height:
                point_repr += f'x{p2_pieces}'
            else:
                point_repr += 'x' * p2_pieces

            board_visual.append(point_repr.center(max_height, ' '))
            
        # Print the top and bottom halves of the board separately
        top_half = "|".join(board_visual[:12][::-1])  # Reverse to display in correct order
        bottom_half = "|".join(board_visual[12:])
        
        # Print the board representation
        print("Player 1: o | Player 2: x")
        print("—"*len(top_half))  # Separator
        print(top_half)
        print("—"*len(top_half))  # Separator
        print(bottom_half)
        print("—"*len(top_half))  # Separator
        
        # Print borne-off pieces
        print(f"Player 1 has {self.borne_off[0]} borne-off pieces.")
        print(f"Player 2 has {self.borne_off[1]} borne-off pieces.")
