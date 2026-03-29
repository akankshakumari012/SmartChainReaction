import tkinter as tk

ROWS = 12
COLS = 8

# ---------------- BOARD ----------------
class Board:
    def __init__(self):
        self.rows = ROWS
        self.cols = COLS
        self.grid = [[0]*COLS for _ in range(ROWS)]
        self.current_player = 1  # 1 = player, -1 = AI

    def get_available_moves(self):
        return [(i, j) for i in range(self.rows) for j in range(self.cols) if self.grid[i][j] == 0]

    def execute_move(self, i, j):
        if self.grid[i][j] == 0:
            self.grid[i][j] = self.current_player
            self.current_player *= -1
        return self

    def is_terminal(self):
        # Check rows
        for row in self.grid:
            if sum(row) == self.cols:
                return True, 1
            if sum(row) == -self.cols:
                return True, -1

        # Check columns
        for j in range(self.cols):
            col_sum = sum(self.grid[i][j] for i in range(self.rows))
            if col_sum == self.rows:
                return True, 1
            if col_sum == -self.rows:
                return True, -1

        # Check diagonals
        diag1 = sum(self.grid[i][i] for i in range(min(self.rows, self.cols)))
        diag2 = sum(self.grid[i][self.cols-i-1] for i in range(min(self.rows, self.cols)))
        if diag1 == min(self.rows, self.cols) or diag2 == min(self.rows, self.cols):
            return True, 1
        if diag1 == -min(self.rows, self.cols) or diag2 == -min(self.rows, self.cols):
            return True, -1

        # Draw
        if not self.get_available_moves():
            return True, 0

        return False, None

# ---------------- FAST AI ----------------
class SmartBot:
    def __init__(self, player):
        self.player = player

    def get_best_move(self, board):
        # Pick empty cell next to existing cells
        candidates = []
        for i in range(ROWS):
            for j in range(COLS):
                if board.grid[i][j] == 0:
                    neighbors = [(i+di,j+dj) for di,dj in [(-1,0),(1,0),(0,-1),(0,1)]
                                 if 0<=i+di<ROWS and 0<=j+dj<COLS]
                    if any(board.grid[ni][nj] != 0 for ni,nj in neighbors):
                        candidates.append((i,j))
        if candidates:
            return candidates[0]
        # fallback: any empty cell
        moves = board.get_available_moves()
        return moves[0] if moves else None

# ---------------- UI ----------------
class GameUI:
    def __init__(self, root):
        self.root = root
        self.board = Board()
        self.bot = SmartBot(-1)

        self.player_score = 0
        self.ai_score = 0
        self.draw_score = 0

        # Buttons grid
        self.buttons = [[None]*COLS for _ in range(ROWS)]
        for i in range(ROWS):
            for j in range(COLS):
                btn = tk.Button(root, text="", width=5, height=2,
                                font=("Arial", 10),
                                command=lambda i=i,j=j: self.player_move(i,j))
                btn.grid(row=i, column=j)
                self.buttons[i][j] = btn

        # Status and scores
        self.status = tk.Label(root, text="Your Turn (X)", font=("Arial", 14))
        self.status.grid(row=ROWS, column=0, columnspan=COLS, pady=5)

        # Restart button
        self.restart_btn = tk.Button(root, text="Restart Game", font=("Arial", 12), bg="#444", fg="white",
                                     command=self.restart_game)
        self.restart_btn.grid(row=ROWS+1, column=0, columnspan=COLS, pady=5)

        # Scoreboard
        self.score_label = tk.Label(root, text=self.get_score_text(), font=("Arial", 12))
        self.score_label.grid(row=ROWS+2, column=0, columnspan=COLS, pady=5)

    def get_score_text(self):
        return f"Your Score: {self.player_score} | AI Score: {self.ai_score} | Draws: {self.draw_score}"

    def restart_game(self):
        self.board = Board()
        self.update_ui()
        self.status.config(text="Your Turn (X)")

    def player_move(self, i, j):
        if self.board.grid[i][j] != 0:
            return

        self.board.execute_move(i,j)
        self.update_ui()

        terminal, winner = self.board.is_terminal()
        if terminal:
            self.update_scores(winner)
            self.end_game(winner)
            return

        self.status.config(text="AI Thinking...")
        self.root.after(1000, self.ai_move)  # 1-second delay

    def ai_move(self):
        move = self.bot.get_best_move(self.board)
        if move:
            i,j = move
            self.board.execute_move(i,j)
            self.update_ui()

        terminal, winner = self.board.is_terminal()
        if terminal:
            self.update_scores(winner)
            self.end_game(winner)
        else:
            self.status.config(text="Your Turn (X)")

    def update_ui(self):
        for i in range(ROWS):
            for j in range(COLS):
                val = self.board.grid[i][j]
                text = "X" if val==1 else "O" if val==-1 else ""
                self.buttons[i][j].config(text=text)

    def end_game(self, winner):
        if winner==1:
            self.status.config(text="You Win! 🎉")
        elif winner==-1:
            self.status.config(text="AI Wins! 🤖")
        else:
            self.status.config(text="Draw 😐")

    def update_scores(self, winner):
        if winner==1:
            self.player_score += 1
        elif winner==-1:
            self.ai_score += 1
        else:
            self.draw_score += 1
        self.score_label.config(text=self.get_score_text())

# ---------------- RUN ----------------
if __name__ == "__main__":
    root = tk.Tk()
    root.title("12x8 Fast AI Board")
    game = GameUI(root)
    root.mainloop()