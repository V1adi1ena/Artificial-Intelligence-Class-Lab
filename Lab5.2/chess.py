import tkinter as tk
from tkinter import messagebox
import copy
import threading

# ───────────────────────────── 常量 ─────────────────────────────
CELL = 68          # 格子像素
MARGIN = 52        # 棋盘边距
ROWS, COLS = 10, 9
W = MARGIN * 2 + CELL * (COLS - 1)
H = MARGIN * 2 + CELL * (ROWS - 1)

# 颜色
BG        = "#F0C060"
LINE_CLR  = "#8B5E1A"
RED_CLR   = "#CC1111"
BLACK_CLR = "#111111"
HIGH_CLR  = "#00CC66"   # 合法落点高亮
SEL_CLR   = "#FFD700"   # 已选棋子高亮
RIVER_CLR = "#D4A83A"

""" 
棋子编号约定：
正数 = 红方，负数 = 黑方，0 = 空
1=车 2=马 3=象/相 4=士/仕 5=将/帅 6=炮 7=兵/卒
"""
CHE, MA, XIANG, SHI, JIANG, PAO, BING = 1, 2, 3, 4, 5, 6, 7

PIECE_NAMES = {
    ( CHE,   True):  "车",  ( CHE,   False): "車",
    ( MA,    True):  "马",  ( MA,    False): "馬",
    ( XIANG, True):  "相",  ( XIANG, False): "象",
    ( SHI,   True):  "仕",  ( SHI,   False): "士",
    ( JIANG, True):  "帅",  ( JIANG, False): "将",
    ( PAO,   True):  "炮",  ( PAO,   False): "砲",
    ( BING,  True):  "兵",  ( BING,  False): "卒",
}

# 基础子力价值（单位：分）
PIECE_VALUE = {
    CHE: 900,
    MA: 400,
    XIANG: 200,
    SHI: 200,
    JIANG: 10000,
    PAO: 450,
    BING: 100
}

# 位置价值表（10x9，红方视角，黑方使用时需行翻转）
# 表值均为红方优势分，因此红方直接加，黑方需取反

# 车：越开放、越靠近对方阵地越好
POS_CHE = [
    [14, 14, 12, 18, 16, 18, 12, 14, 14],
    [16, 20, 18, 24, 26, 24, 18, 20, 16],
    [12, 12, 12, 18, 18, 18, 12, 12, 12],
    [12, 18, 16, 22, 22, 22, 16, 18, 12],
    [12, 14, 12, 18, 18, 18, 12, 14, 12],
    [12, 16, 14, 20, 20, 20, 14, 16, 12],
    [8, 10, 8, 14, 14, 14, 8, 10, 8],
    [6, 8, 6, 10, 10, 10, 6, 8, 6],
    [4, 6, 4, 8, 8, 8, 4, 6, 4],
    [2, 4, 2, 6, 6, 6, 2, 4, 2],
]
# 马：中央位置佳，边缘位置差
POS_MA = [
    [2, 2, 4, 4, 6, 4, 4, 2, 2],
    [2, 4, 6, 8, 10, 8, 6, 4, 2],
    [4, 6, 8, 12, 14, 12, 8, 6, 4],
    [6, 8, 12, 16, 18, 16, 12, 8, 6],
    [8, 10, 14, 18, 20, 18, 14, 10, 8],
    [6, 8, 12, 16, 18, 16, 12, 8, 6],
    [4, 6, 8, 12, 14, 12, 8, 6, 4],
    [2, 4, 6, 8, 10, 8, 6, 4, 2],
    [0, 2, 4, 4, 6, 4, 4, 2, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
]
# 炮：与车类似，但架炮位置有加成
POS_PAO = [
    [6, 8, 6, 10, 12, 10, 6, 8, 6],
    [8, 10, 12, 18, 22, 18, 12, 10, 8],
    [12, 14, 16, 24, 28, 24, 16, 14, 12],
    [10, 14, 18, 28, 32, 28, 18, 14, 10],
    [8, 12, 16, 24, 28, 24, 16, 12, 8],
    [6, 10, 14, 20, 24, 20, 14, 10, 6],
    [4, 8, 12, 16, 20, 16, 12, 8, 4],
    [2, 4, 8, 12, 14, 12, 8, 4, 2],
    [0, 2, 4, 8, 10, 8, 4, 2, 0],
    [0, 0, 2, 4, 6, 4, 2, 0, 0],
]
# 兵/卒：未过河低分，过河后大幅加分，近九宫更高
POS_BING = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2, 4, 6, 8, 12, 8, 6, 4, 2],
    [4, 6, 8, 14, 18, 14, 8, 6, 4],
    [6, 10, 16, 20, 24, 20, 16, 10, 6],
    [8, 16, 22, 28, 32, 28, 22, 16, 8],
    [12, 20, 28, 36, 40, 36, 28, 20, 12],
    [18, 28, 36, 48, 56, 48, 36, 28, 18],
]
# 相/象 和 士/仕 的位置价值（简单，九宫内）
POS_XIANG = [
    [0, 0, 2, 0, 0, 0, 2, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2, 0, 4, 0, 8, 0, 4, 0, 2],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 8, 0, 12, 0, 8, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2, 0, 4, 0, 8, 0, 4, 0, 2],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 2, 0, 0, 0, 2, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
]
POS_SHI = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 6, 0, 0, 0, 6, 0, 0],
    [0, 0, 0, 10, 12, 10, 0, 0, 0],
    [0, 0, 0, 12, 18, 12, 0, 0, 0],
]
# 将帅的位置价值（鼓励待在底线，九宫中央稍好）
POS_JIANG = [
    [0, 0, 6, 10, 12, 10, 6, 0, 0],
    [0, 0, 8, 12, 16, 12, 8, 0, 0],
    [0, 0, 10, 16, 22, 16, 10, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
]
POS_TABLES = {
    CHE: POS_CHE,
    MA: POS_MA,
    PAO: POS_PAO,
    BING: POS_BING,
    XIANG: POS_XIANG,
    SHI: POS_SHI,
    JIANG: POS_JIANG,
}

"""===============初始化棋盘=============="""
def init_board():
    """返回 10x9 的二维列表，正数=红，负数=黑，0=空"""
    b = [[0]*9 for _ in range(10)]
    # 黑方（上方，行0-4）
    back = [CHE, MA, XIANG, SHI, JIANG, SHI, XIANG, MA, CHE]
    for c, p in enumerate(back):
        b[0][c] = -p
    b[2][1] = b[2][7] = -PAO
    for c in range(0, 9, 2):
        b[3][c] = -BING
    # 红方（下方，行5-9）
    for c, p in enumerate(back):
        b[9][c] = p
    b[7][1] = b[7][7] = PAO
    for c in range(0, 9, 2):
        b[6][c] = BING
    return b
"""===============规则函数=============="""
"""判断 (r,c) 是否在棋盘上"""
def in_board(r, c):
    return 0 <= r < 10 and 0 <= c < 9
"""判断红黑方"""
def is_red(p):  return p > 0
def is_black(p): return p < 0
"""判断是否是同方"""
def same_side(p1, p2): return (p1 > 0) == (p2 > 0) and p1 != 0 and p2 != 0
"""返回 (r,c) 位置棋子的所有合法落点列表（不考虑将帅照面）"""
def get_moves(board, r, c):
    p = board[r][c]
    if p == 0:
        return []
    red = is_red(p)
    t = abs(p)
    moves = []

    if t == CHE:
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r+dr, c+dc
            while in_board(nr, nc):
                if board[nr][nc] == 0:
                    moves.append((nr, nc))
                else:
                    if not same_side(p, board[nr][nc]):
                        moves.append((nr, nc))
                    break
                nr += dr; nc += dc

    elif t == MA:
        for dr, dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
            # 蹩马腿检查
            if abs(dr) == 2:
                br, bc = r + dr//2, c
            else:
                br, bc = r, c + dc//2
              # 增加边界检查
            if not in_board(br, bc):
                continue
            if board[br][bc] != 0:
                continue
            nr, nc = r+dr, c+dc
            if in_board(nr, nc) and not same_side(p, board[nr][nc]):
                moves.append((nr, nc))

    elif t == XIANG:
        # 象走田，不能过河
        for dr, dc in [(-2,-2),(-2,2),(2,-2),(2,2)]:
            nr, nc = r+dr, c+dc
            if not in_board(nr, nc): continue
            # 不能过河
            if red and nr < 5: continue
            if not red and nr > 4: continue
            # 塞象眼
            er, ec = r+dr//2, c+dc//2
            if board[er][ec] != 0: continue
            if not same_side(p, board[nr][nc]):
                moves.append((nr, nc))

    elif t == SHI:
        for dr, dc in [(-1,-1),(-1,1),(1,-1),(1,1)]:
            nr, nc = r+dr, c+dc
            if not in_board(nr, nc): continue
            if red and not (7 <= nr <= 9 and 3 <= nc <= 5): continue
            if not red and not (0 <= nr <= 2 and 3 <= nc <= 5): continue
            if not same_side(p, board[nr][nc]):
                moves.append((nr, nc))

    elif t == JIANG:
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r+dr, c+dc
            if not in_board(nr, nc): continue
            if red and not (7 <= nr <= 9 and 3 <= nc <= 5): continue
            if not red and not (0 <= nr <= 2 and 3 <= nc <= 5): continue
            if not same_side(p, board[nr][nc]):
                moves.append((nr, nc))
        # （将帅照面在合法性过滤中处理）

    elif t == PAO:
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r+dr, c+dc
            jumped = False
            while in_board(nr, nc):
                if not jumped:
                    if board[nr][nc] == 0:
                        moves.append((nr, nc))
                    else:
                        jumped = True
                else:
                    if board[nr][nc] != 0:
                        if not same_side(p, board[nr][nc]):
                            moves.append((nr, nc))
                        break
                nr += dr; nc += dc

    elif t == BING:
        if red:
            # 红兵向上（行减小）
            moves_dir = [(-1, 0)]
            if r <= 4:  # 过河后
                moves_dir += [(0, -1), (0, 1)]
        else:
            # 黑卒向下（行增大）
            moves_dir = [(1, 0)]
            if r >= 5:
                moves_dir += [(0, -1), (0, 1)]
        for dr, dc in moves_dir:
            nr, nc = r+dr, c+dc
            if in_board(nr, nc) and not same_side(p, board[nr][nc]):
                moves.append((nr, nc))

    return moves
"""返回 red 方的将帅位置"""
def find_king(board, isRed):
    for r in range(10):
        for c in range(9):
            p = board[r][c]
            if abs(p) == JIANG and is_red(p) == isRed:
                return r, c
    return None
"""判断两将是否照面"""
def kings_face(board):
    rr, rc = find_king(board, True) or (99,99)
    br, bc = find_king(board, False) or (99,99)
    """不在同一列"""
    if rc != bc:
        return False
    """在同一列，就判断是否照面（中间无棋子）"""
    col = rc
    for row in range(min(rr, br)+1, max(rr, br)):
        if board[row][col] != 0:
            return False
    return True
"""判断 isRed 方是否被将军"""
def is_in_check(board, isRed):
    kr, kc = find_king(board, isRed) or (99,99)
    for r in range(10):
        for c in range(9):
            p = board[r][c]
            if p == 0 or is_red(p) == isRed:
                continue
            if (kr, kc) in get_moves(board, r, c):
                return True
    if kings_face(board):
        return True
    return False
"""给出合法走法，过滤掉走后会被将军的落点"""
def legal_moves(board, r, c):
    p = board[r][c]
    result = []
    for nr, nc in get_moves(board, r, c):
        nb = copy.deepcopy(board)
        nb[nr][nc] = p
        nb[r][c] = 0
        if not is_in_check(nb, is_red(p)):
            result.append((nr, nc))
    return result
"""判断 isRed 方是否有合法走法"""
def has_any_move(board, isRed):
    for r in range(10):
        for c in range(9):
            p = board[r][c]
            if p != 0 and is_red(p) == isRed:
                if legal_moves(board, r, c):
                    return True
    return False
"""增强评估函数：材料分 + 位置分 + 少量灵活性/阵型奖励"""
def evaluate(board):
    score = 0
    """遍历直接计算子力和位置分"""
    for r in range(10):
        for c in range(9):
            p = board[r][c]
            if p == 0:
                continue
            red = is_red(p)
            ptype = abs(p)
            # 1. 子力分
            base_val = PIECE_VALUE.get(ptype, 0)
            # 2. 位置分（根据棋子类型查表，黑方需翻转行）
            pos_table = POS_TABLES.get(ptype, None)
            pos_val = 0
            if pos_table:
                # 红方从 row 0=黑底线 到 row 9=红底线，位置表也是红方视角
                row = r
                if not red:
                    # 黑方使用位置表时，行翻转
                    row = 9 - r
                pos_val = pos_table[row][c]
            # 总和
            piece_score = base_val + pos_val
            score += piece_score if red else -piece_score
    # 3. 额外阵型/灵活性奖励（简单示例）
    score += _mobility_bonus(board, True)   # 红方机动性
    score -= _mobility_bonus(board, False)  # 黑方机动性
    return score
def _mobility_bonus(board, red):
    """机动性奖励：己方走法总数 * 2 分"""
    total = 0
    for r in range(10):
        for c in range(9):
            p = board[r][c]
            if p != 0 and is_red(p) == red:
                # 使用 get_moves 而非 legal_moves 为了速度，而且评估不需要考虑将军
                total += len(get_moves(board, r, c))
    return total * 2  # 每走法 2 分
#  def alphabeta(board, depth, alpha, beta, maximizing, evaluate_fn)
#  参数含义：
#     board       : 10x9 棋盘列表
#     depth       : 搜索深度（int）
#     alpha, beta : 剪枝窗口（float）
#     isMaximizing : 当前是否红方（红方极大化，黑方极小化）
#  返回值： (best_score, best_move)
#     best_score : 当前局面最佳得分
#     best_move  : 五元组 (from_r, from_c, to_r, to_c, promoted?)，
#                  中国象棋没有升变，最后一项为 None 即可；
#                  若无合法走法返回 (score, None)
def alphabeta(board, depth, alpha, beta, isMaximizing):
    """
    返回 (best_score, best_move)。
    best_move 格式示例：(2, 1, 7, 1) 表示从 (2,1) 移动到 (7,1)。
    """
    if depth == 0 or not has_any_move(board, isMaximizing):
        return evaluate(board), None
    moves = []
    value = -float('inf') if isMaximizing else float('inf')
    for r in range(10):
        for c in range(9):
            if board[r][c] == 0 or is_red(board[r][c]) != isMaximizing:
                continue
            for nr, nc in legal_moves(board, r, c):
                new_board = copy.deepcopy(board)
                new_board[nr][nc] = board[r][c]
                new_board[r][c] = 0
                new_board_score = alphabeta(new_board, depth-1, alpha, beta, not isMaximizing)[0]
                if isMaximizing:
                    """极大化搜索，分数更高则更新value以及move"""
                    if new_board_score > value:
                        value = new_board_score
                        moves = [(r, c, nr, nc)]
                    """剪枝"""
                    alpha = max(alpha, value)
                    if beta <= alpha:
                        return value, moves
                else:
                    """极小化搜索，分数更低则更新value以及move"""
                    if new_board_score < value:
                        value = new_board_score
                        moves = [(r, c, nr, nc)]
                    """剪枝"""
                    beta = min(beta, value)
                    if beta <= alpha:
                        return value, moves
    return evaluate(board), moves
# ───────────────────────────── GUI ─────────────────────────────
class ChessGame:
    def __init__(self, root):
        self.root = root
        self.root.title("中国象棋")
        self.root.resizable(False, False)
        self.root.configure(bg="#2C1810")

        self.board = init_board()
        self.selected = None
        self.highlights = []
        self.red_is_human = True      # 红方=人类
        self.current_red = True       # 当前轮到红方
        self.status_msg = ""
        self.move_history = []

        self._build_ui()
        self.draw()
        self._update_status()

    def _build_ui(self):
        # 顶部标题
        title_frame = tk.Frame(self.root, bg="#2C1810")
        title_frame.pack(pady=(10, 0))
        tk.Label(title_frame, text="中国象棋", font=("楷体", 28, "bold"),
                 fg="#FFD700", bg="#2C1810").pack()

        # 主区域
        main = tk.Frame(self.root, bg="#2C1810")
        main.pack(padx=15, pady=8)

        # 棋盘 Canvas
        self.canvas = tk.Canvas(main, width=W, height=H,
                                bg=BG, highlightthickness=3,
                                highlightbackground="#8B5E1A")
        self.canvas.grid(row=0, column=0, rowspan=10)
        self.canvas.bind("<Button-1>", self.on_click)

        # 右侧面板
        panel = tk.Frame(main, bg="#2C1810", padx=14)
        panel.grid(row=0, column=1, sticky="ns")

        self.status_var = tk.StringVar(value="红方先走")
        tk.Label(panel, textvariable=self.status_var,
                 font=("楷体", 14, "bold"), fg="#FFD700", bg="#2C1810",
                 wraplength=160, justify="center").pack(pady=(8, 4))

        self.turn_canvas = tk.Canvas(panel, width=140, height=44,
                                     bg="#2C1810", highlightthickness=0)
        self.turn_canvas.pack(pady=4)

        sep = tk.Frame(panel, height=2, bg="#8B5E1A")
        sep.pack(fill="x", pady=8)

        btn_cfg = dict(font=("楷体", 13), relief="flat", cursor="hand2",
                       padx=10, pady=6, width=12)

        self.swap_btn = tk.Button(panel, text="⇄ 红黑互换",
                                   command=self.swap_sides,
                                   bg="#8B2020", fg="white",
                                   activebackground="#AA3030",
                                   activeforeground="white", **btn_cfg)
        self.swap_btn.pack(pady=4)

        tk.Button(panel, text="↩ 悔棋",
                  command=self.undo_move,
                  bg="#4A6741", fg="white",
                  activebackground="#5A7751",
                  activeforeground="white", **btn_cfg).pack(pady=4)

        tk.Button(panel, text="⟳ 重新开始",
                  command=self.restart,
                  bg="#4A5568", fg="white",
                  activebackground="#5A6578",
                  activeforeground="white", **btn_cfg).pack(pady=4)

        sep2 = tk.Frame(panel, height=2, bg="#8B5E1A")
        sep2.pack(fill="x", pady=8)

        tk.Label(panel, text="棋  谱", font=("楷体", 13, "bold"),
                 fg="#C8A060", bg="#2C1810").pack()
        log_frame = tk.Frame(panel, bg="#1A0F08")
        log_frame.pack(fill="both", expand=True, pady=4)
        self.log_text = tk.Text(log_frame, width=14, height=18,
                                font=("楷体", 11), bg="#1A0F08", fg="#C8A060",
                                relief="flat", state="disabled",
                                selectbackground="#4A3020")
        sb = tk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=sb.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def rc_to_xy(self, r, c):
        return MARGIN + c * CELL, MARGIN + r * CELL

    def xy_to_rc(self, x, y):
        c = round((x - MARGIN) / CELL)
        r = round((y - MARGIN) / CELL)
        return r, c

    def draw(self):
        self.canvas.delete("all")
        self._draw_board()
        self._draw_highlights()
        self._draw_pieces()
        self._update_turn_indicator()

    def _draw_board(self):
        cv = self.canvas
        cv.create_rectangle(MARGIN-6, MARGIN-6,
                             MARGIN+(COLS-1)*CELL+6, MARGIN+(ROWS-1)*CELL+6,
                             fill="#E8B848", outline=LINE_CLR, width=3)
        for r in range(ROWS):
            x0, y0 = self.rc_to_xy(r, 0)
            x1, _  = self.rc_to_xy(r, COLS-1)
            cv.create_line(x0, y0, x1, y0, fill=LINE_CLR, width=1)
        for c in range(COLS):
            x, y0 = self.rc_to_xy(0, c)
            _, y4 = self.rc_to_xy(4, c)
            _, y5 = self.rc_to_xy(5, c)
            _, y9 = self.rc_to_xy(9, c)
            if c == 0 or c == COLS-1:
                cv.create_line(x, y0, x, y9, fill=LINE_CLR, width=1)
            else:
                cv.create_line(x, y0, x, y4, fill=LINE_CLR, width=1)
                cv.create_line(x, y5, x, y9, fill=LINE_CLR, width=1)
        _, y4 = self.rc_to_xy(4, 0)
        _, y5 = self.rc_to_xy(5, 0)
        mid_y = (y4 + y5) // 2
        x0, _ = self.rc_to_xy(0, 0)
        x8, _ = self.rc_to_xy(0, 8)
        cv.create_rectangle(x0, y4, x8, y5, fill=RIVER_CLR, outline=LINE_CLR, width=1)
        cv.create_text((x0+x8)//2 - CELL, mid_y, text="楚  河",
                       font=("楷体", 18, "bold"), fill=LINE_CLR)
        cv.create_text((x0+x8)//2 + CELL, mid_y, text="汉  界",
                       font=("楷体", 18, "bold"), fill=LINE_CLR)
        for (r1,c1,r2,c2) in [(0,3,2,5),(0,5,2,3),(7,3,9,5),(7,5,9,3)]:
            x1,y1 = self.rc_to_xy(r1,c1)
            x2,y2 = self.rc_to_xy(r2,c2)
            cv.create_line(x1,y1,x2,y2, fill=LINE_CLR, width=1)
        markers = [(2,1),(2,7),(7,1),(7,7)]
        for c in range(0,9,2):
            markers.append((3,c)); markers.append((6,c))
        for (mr,mc) in markers:
            self._draw_cross(mr, mc)

    def _draw_cross(self, r, c):
        x, y = self.rc_to_xy(r, c)
        s, g = 8, 3
        cv = self.canvas
        if c > 0:
            cv.create_line(x-s, y-g, x-g, y-g, fill=LINE_CLR, width=1)
            cv.create_line(x-s, y+g, x-g, y+g, fill=LINE_CLR, width=1)
            cv.create_line(x-g, y-s, x-g, y-g, fill=LINE_CLR, width=1)
            cv.create_line(x-g, y+g, x-g, y+s, fill=LINE_CLR, width=1)
        if c < 8:
            cv.create_line(x+g, y-g, x+s, y-g, fill=LINE_CLR, width=1)
            cv.create_line(x+g, y+g, x+s, y+g, fill=LINE_CLR, width=1)
            cv.create_line(x+g, y-s, x+g, y-g, fill=LINE_CLR, width=1)
            cv.create_line(x+g, y+g, x+g, y+s, fill=LINE_CLR, width=1)

    def _draw_highlights(self):
        cv = self.canvas
        if self.selected:
            r, c = self.selected
            x, y = self.rc_to_xy(r, c)
            rad = CELL//2 - 2
            cv.create_oval(x-rad, y-rad, x+rad, y+rad,
                           fill=SEL_CLR, outline="", stipple="gray50")
        for (nr, nc) in self.highlights:
            x, y = self.rc_to_xy(nr, nc)
            r = 10
            cv.create_oval(x-r, y-r, x+r, y+r,
                           fill=HIGH_CLR, outline=HIGH_CLR)

    def _draw_pieces(self):
        cv = self.canvas
        rad = CELL//2 - 4
        for r in range(10):
            for c in range(9):
                p = self.board[r][c]
                if p == 0: continue
                x, y = self.rc_to_xy(r, c)
                red = is_red(p)
                bg_col  = "#F5E6D0" if red else "#2A1A1A"
                rim_col = RED_CLR   if red else BLACK_CLR
                txt_col = RED_CLR   if red else "#E8E8E8"
                cv.create_oval(x-rad-3, y-rad-3, x+rad+3, y+rad+3,
                               fill=rim_col, outline="")
                cv.create_oval(x-rad, y-rad, x+rad, y+rad,
                               fill=bg_col, outline=rim_col, width=2)
                cv.create_oval(x-rad+4, y-rad+4, x+rad-4, y+rad-4,
                               fill="", outline=rim_col, width=1)
                name = PIECE_NAMES.get((abs(p), red), "?")
                cv.create_text(x, y, text=name,
                               font=("楷体", 17, "bold"), fill=txt_col)

    def _update_turn_indicator(self):
        cv = self.turn_canvas
        cv.delete("all")
        r_col = RED_CLR if self.current_red else "#666"
        cv.create_oval(8, 6, 38, 36, fill=r_col, outline="")
        cv.create_text(23, 21, text="红", font=("楷体", 13, "bold"), fill="white")
        cv.create_text(70, 21, text="➤" if self.current_red else "◀",
                       font=("Arial", 14), fill="#FFD700")
        b_col = BLACK_CLR if not self.current_red else "#666"
        cv.create_oval(102, 6, 132, 36, fill=b_col, outline="")
        cv.create_text(117, 21, text="黑", font=("楷体", 13, "bold"), fill="white")

    def _update_status(self):
        side = "红方" if self.current_red else "黑方"
        human = (self.current_red == self.red_is_human)
        who = "（您）" if human else "（AI）"
        self.status_var.set(f"{side}{who}走棋")
        self.root.update()

    def _log_move(self, r, c, nr, nc, piece):
        red = is_red(piece)
        name = PIECE_NAMES.get((abs(piece), red), "?")
        side = "红" if red else "黑"
        cols_zh = "一二三四五六七八九"
        fc = (8-c) if red else c
        tc = (8-nc) if red else nc
        from_col = cols_zh[fc]
        to_col = cols_zh[tc]
        if r == nr:
            direction = "平"
            pos = to_col
        elif (red and nr < r) or (not red and nr > r):
            direction = "进"
            pos = str(abs(nr-r))
        else:
            direction = "退"
            pos = str(abs(nr-r))
        text = f"{side}{name}{from_col}{direction}{pos}"
        self.log_text.configure(state="normal")
        step = len(self.move_history)
        prefix = f"{step//2+1}." if red else "   "
        self.log_text.insert("end", f"{prefix}{text}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def on_click(self, event):
        human_turn = (self.current_red == self.red_is_human)
        if not human_turn:
            return
        r, c = self.xy_to_rc(event.x, event.y)
        if not in_board(r, c):
            return
        p = self.board[r][c]
        if self.selected is None:
            if p != 0 and is_red(p) == self.current_red:
                self.selected = (r, c)
                self.highlights = legal_moves(self.board, r, c)
                self.draw()
        else:
            sr, sc = self.selected
            if (r, c) == (sr, sc):
                self.selected = None
                self.highlights = []
                self.draw()
            elif (r, c) in self.highlights:
                self._do_move(sr, sc, r, c)
            elif p != 0 and is_red(p) == self.current_red:
                self.selected = (r, c)
                self.highlights = legal_moves(self.board, r, c)
                self.draw()
            else:
                self.selected = None
                self.highlights = []
                self.draw()

    def _do_move(self, r, c, nr, nc):
        piece = self.board[r][c]
        captured = self.board[nr][nc]
        self.move_history.append((r, c, nr, nc, piece, captured,
                                   copy.deepcopy(self.board)))
        self._log_move(r, c, nr, nc, piece)
        self.board[nr][nc] = piece
        self.board[r][c] = 0
        self.selected = None
        self.highlights = []
        self.current_red = not self.current_red
        self.draw()
        if not has_any_move(self.board, self.current_red):
            winner = "红方" if not self.current_red else "黑方"
            self.draw()
            messagebox.showinfo("游戏结束", f"🎉 {winner}获胜！")
            return
        self._update_status()
        # AI 回合
        if self.current_red != self.red_is_human:
            self.root.after(300, self._ai_move)

    def _ai_move(self):
        side = "黑方" if not self.current_red else "红方"
        self.status_var.set(f"{side} AI思考中…")
        self.root.update()
        isMaximizing = self.current_red

        # 使用线程避免界面卡死
        def search_and_apply():
            # 调用用户实现的 alphabeta 函数
            _, best_move = alphabeta(
                self.board,
                depth=4,      # 搜索深度，可根据需要调整
                alpha=-float("inf"),
                beta=float("inf"),
                isMaximizing=isMaximizing
            )
            # 在主线程中应用走法
            self.root.after(0, self._apply_ai_move, best_move)

        threading.Thread(target=search_and_apply, daemon=True).start()

    def _apply_ai_move(self, best_move):
        if best_move is None:
            winner = "红方" if not self.current_red else "黑方"
            messagebox.showinfo("游戏结束", f"🎉 {winner}获胜！")
            return
        r, c, nr, nc = best_move[0]
        self._do_move(r, c, nr, nc)

    def swap_sides(self):
        self.red_is_human = not self.red_is_human
        side = "红方" if self.red_is_human else "黑方"
        self.status_var.set(f"已切换：您现在执{side}")
        self.selected = None
        self.highlights = []
        self.draw()
        self.root.after(800, self._update_status)
        if self.current_red != self.red_is_human:
            self.root.after(1000, self._ai_move)

    def undo_move(self):
        if not self.move_history:
            messagebox.showinfo("悔棋", "没有可悔的棋步")
            return
        steps = 2 if len(self.move_history) >= 2 and \
                      (self.move_history[-1][4] > 0) != self.red_is_human else 1
        steps = min(steps, len(self.move_history))
        for _ in range(steps):
            r, c, nr, nc, piece, captured, saved_board = self.move_history.pop()
            self.board = saved_board
            self.current_red = is_red(piece)
        self.selected = None
        self.highlights = []
        self.draw()
        self._update_status()
        self.log_text.configure(state="normal")
        for _ in range(steps):
            self.log_text.delete("end-2l", "end-1c")
        self.log_text.configure(state="disabled")

    def restart(self):
        if messagebox.askyesno("重新开始", "确定要重新开始吗？"):
            self.board = init_board()
            self.selected = None
            self.highlights = []
            self.current_red = True
            self.move_history = []
            self.log_text.configure(state="normal")
            self.log_text.delete("1.0", "end")
            self.log_text.configure(state="disabled")
            self.draw()
            self._update_status()

# ───────────────────────────── 入口 ─────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = ChessGame(root)
    root.mainloop()