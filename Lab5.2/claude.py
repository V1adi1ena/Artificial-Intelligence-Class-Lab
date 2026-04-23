"""
中国象棋 - Python tkinter 实现
特性：
- 纯代码绘制棋盘和棋子，无需图片资源
- 完整的象棋规则（将/帅、士/仕、象/相、马、车、炮、兵/卒）
- 玩家 vs AI（AI 暂时跳过，预留 Alpha-Beta 剪枝框架）
- 红黑方互换功能
- 高亮显示合法落点
"""

import tkinter as tk
from tkinter import messagebox
import copy
import time

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

# 棋子编号约定
# 正数 = 红方，负数 = 黑方，0 = 空
# 1=车 2=马 3=象/相 4=士/仕 5=将/帅 6=炮 7=兵/卒
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

# ───────────────────────────── 初始棋盘 ─────────────────────────────
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

# ───────────────────────────── 规则引擎 ─────────────────────────────
def in_board(r, c):
    return 0 <= r < 10 and 0 <= c < 9

def is_red(p):  return p > 0
def is_black(p): return p < 0
def same_side(p1, p2): return (p1 > 0) == (p2 > 0) and p1 != 0 and p2 != 0

def get_moves(board, r, c):
    """返回 (r,c) 棋子的所有合法落点列表（不考虑将军校验）"""
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
        # 将帅照面
        # （不在此处处理，通过 is_in_check 过滤）

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

def find_king(board, red):
    for r in range(10):
        for c in range(9):
            p = board[r][c]
            if abs(p) == JIANG and is_red(p) == red:
                return r, c
    return None

def kings_face(board):
    """判断两将是否照面"""
    rr, rc = find_king(board, True) or (99,99)
    br, bc = find_king(board, False) or (99,99)
    if rc != bc:
        return False
    col = rc
    for row in range(min(rr, br)+1, max(rr, br)):
        if board[row][col] != 0:
            return False
    return True

def is_in_check(board, red):
    """判断 red 方是否被将军"""
    kr, kc = find_king(board, red) or (99,99)
    for r in range(10):
        for c in range(9):
            p = board[r][c]
            if p == 0: continue
            if is_red(p) == red: continue
            if (kr, kc) in get_moves(board, r, c):
                return True
    if kings_face(board):
        return True
    return False

def legal_moves(board, r, c):
    """过滤掉走后仍被将军的落点"""
    p = board[r][c]
    result = []
    for nr, nc in get_moves(board, r, c):
        nb = copy.deepcopy(board)
        nb[nr][nc] = p
        nb[r][c] = 0
        if not is_in_check(nb, is_red(p)):
            result.append((nr, nc))
    return result

def has_any_move(board, red):
    for r in range(10):
        for c in range(9):
            p = board[r][c]
            if p != 0 and is_red(p) == red:
                if legal_moves(board, r, c):
                    return True
    return False

# ───────────────────────────── AI（Alpha-Beta 框架，暂时跳过） ─────────────────────────────
def evaluate(board):
    """简单材料评估"""
    vals = {CHE:900, MA:400, XIANG:200, SHI:200, JIANG:10000, PAO:450, BING:100}
    score = 0
    for r in range(10):
        for c in range(9):
            p = board[r][c]
            if p != 0:
                v = vals.get(abs(p), 0)
                score += v if p > 0 else -v
    return score

def alphabeta(board, depth, alpha, beta, maximizing):
    """Alpha-Beta 剪枝 MinMax（框架，depth=0 时暂时返回评估值）"""
    if depth == 0:
        return evaluate(board), None
    red = maximizing
    best_move = None
    if maximizing:
        best = float('-inf')
        for r in range(10):
            for c in range(9):
                if board[r][c] > 0:
                    for nr, nc in legal_moves(board, r, c):
                        nb = copy.deepcopy(board)
                        nb[nr][nc] = board[r][c]; nb[r][c] = 0
                        val, _ = alphabeta(nb, depth-1, alpha, beta, False)
                        if val > best:
                            best, best_move = val, (r, c, nr, nc)
                        alpha = max(alpha, best)
                        if beta <= alpha: break
        return best, best_move
    else:
        best = float('inf')
        for r in range(10):
            for c in range(9):
                if board[r][c] < 0:
                    for nr, nc in legal_moves(board, r, c):
                        nb = copy.deepcopy(board)
                        nb[nr][nc] = board[r][c]; nb[r][c] = 0
                        val, _ = alphabeta(nb, depth-1, alpha, beta, True)
                        if val < best:
                            best, best_move = val, (r, c, nr, nc)
                        beta = min(beta, best)
                        if beta <= alpha: break
        return best, best_move

# ───────────────────────────── GUI ─────────────────────────────
class ChessGame:
    def __init__(self, root):
        self.root = root
        self.root.title("中国象棋")
        self.root.resizable(False, False)
        self.root.configure(bg="#2C1810")

        self.board = init_board()
        self.selected = None          # (r, c)
        self.highlights = []          # 合法落点
        self.red_is_human = True      # 红方=人类
        self.current_red = True       # 当前轮到红方
        self.status_msg = ""
        self.move_history = []

        self._build_ui()
        self.draw()
        self._update_status()

    # ── 构建 UI ──
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

        # 状态信息
        self.status_var = tk.StringVar(value="红方先走")
        tk.Label(panel, textvariable=self.status_var,
                 font=("楷体", 14, "bold"), fg="#FFD700", bg="#2C1810",
                 wraplength=160, justify="center").pack(pady=(8, 4))

        # 轮次指示
        self.turn_canvas = tk.Canvas(panel, width=140, height=44,
                                     bg="#2C1810", highlightthickness=0)
        self.turn_canvas.pack(pady=4)

        sep = tk.Frame(panel, height=2, bg="#8B5E1A")
        sep.pack(fill="x", pady=8)

        # 控制按钮
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

        # 棋谱
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

        # 规则说明
        sep3 = tk.Frame(panel, height=2, bg="#8B5E1A")
        sep3.pack(fill="x", pady=6)
        info = tk.Label(panel, text="红方=人类 / 黑方=AI\nAI走棋功能开发中...",
                        font=("楷体", 10), fg="#886644", bg="#2C1810",
                        justify="center")
        info.pack(pady=(0, 6))

    # ── 坐标转换 ──
    def rc_to_xy(self, r, c):
        return MARGIN + c * CELL, MARGIN + r * CELL

    def xy_to_rc(self, x, y):
        c = round((x - MARGIN) / CELL)
        r = round((y - MARGIN) / CELL)
        return r, c

    # ── 绘制 ──
    def draw(self):
        self.canvas.delete("all")
        self._draw_board()
        self._draw_highlights()
        self._draw_pieces()
        self._update_turn_indicator()

    def _draw_board(self):
        cv = self.canvas
        # 棋盘底色纹理
        cv.create_rectangle(MARGIN-6, MARGIN-6,
                             MARGIN+(COLS-1)*CELL+6, MARGIN+(ROWS-1)*CELL+6,
                             fill="#E8B848", outline=LINE_CLR, width=3)

        # 横线
        for r in range(ROWS):
            x0, y0 = self.rc_to_xy(r, 0)
            x1, _  = self.rc_to_xy(r, COLS-1)
            cv.create_line(x0, y0, x1, y0, fill=LINE_CLR, width=1)

        # 竖线（楚河汉界断开）
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

        # 楚河汉界
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

        # 九宫斜线
        for (r1,c1,r2,c2) in [(0,3,2,5),(0,5,2,3),(7,3,9,5),(7,5,9,3)]:
            x1,y1 = self.rc_to_xy(r1,c1)
            x2,y2 = self.rc_to_xy(r2,c2)
            cv.create_line(x1,y1,x2,y2, fill=LINE_CLR, width=1)

        # 炮/兵位标记
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
        # 已选棋子
        if self.selected:
            r, c = self.selected
            x, y = self.rc_to_xy(r, c)
            rad = CELL//2 - 2
            cv.create_oval(x-rad, y-rad, x+rad, y+rad,
                           fill=SEL_CLR, outline="", stipple="gray50")
        # 合法落点
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

                # 外圈
                cv.create_oval(x-rad-3, y-rad-3, x+rad+3, y+rad+3,
                               fill=rim_col, outline="")
                # 棋子底
                cv.create_oval(x-rad, y-rad, x+rad, y+rad,
                               fill=bg_col, outline=rim_col, width=2)
                # 内细圈装饰
                cv.create_oval(x-rad+4, y-rad+4, x+rad-4, y+rad-4,
                               fill="", outline=rim_col, width=1)
                # 文字
                name = PIECE_NAMES.get((abs(p), red), "?")
                cv.create_text(x, y, text=name,
                               font=("楷体", 17, "bold"), fill=txt_col)

    def _update_turn_indicator(self):
        cv = self.turn_canvas
        cv.delete("all")
        # 红方
        r_col = RED_CLR if self.current_red else "#666"
        cv.create_oval(8, 6, 38, 36, fill=r_col, outline="")
        cv.create_text(23, 21, text="红", font=("楷体", 13, "bold"), fill="white")
        # 箭头
        cv.create_text(70, 21, text="➤" if self.current_red else "◀",
                       font=("Arial", 14), fill="#FFD700")
        # 黑方
        b_col = BLACK_CLR if not self.current_red else "#666"
        cv.create_oval(102, 6, 132, 36, fill=b_col, outline="")
        cv.create_text(117, 21, text="黑", font=("楷体", 13, "bold"), fill="white")

    # ── 状态更新 ──
    def _update_status(self):
        side = "红方" if self.current_red else "黑方"
        human = (self.current_red == self.red_is_human)
        who = "（您）" if human else "（AI）"
        self.status_var.set(f"{side}{who}走棋")

    def _log_move(self, r, c, nr, nc, piece):
        red = is_red(piece)
        name = PIECE_NAMES.get((abs(piece), red), "?")
        side = "红" if red else "黑"
        cols_zh = "一二三四五六七八九"
        # 红方列从右数，黑方列从左数
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

    # ── 点击处理 ──
    def on_click(self, event):
        # 非玩家回合不响应
        human_turn = (self.current_red == self.red_is_human)
        if not human_turn:
            return

        r, c = self.xy_to_rc(event.x, event.y)
        if not in_board(r, c):
            return

        p = self.board[r][c]

        if self.selected is None:
            # 选择棋子
            if p != 0 and is_red(p) == self.current_red:
                self.selected = (r, c)
                self.highlights = legal_moves(self.board, r, c)
                self.draw()
        else:
            sr, sc = self.selected
            if (r, c) == (sr, sc):
                # 取消选择
                self.selected = None
                self.highlights = []
                self.draw()
            elif (r, c) in self.highlights:
                # 落子
                self._do_move(sr, sc, r, c)
            elif p != 0 and is_red(p) == self.current_red:
                # 换选另一个己方棋子
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
        # 记录历史（用于悔棋）
        self.move_history.append((r, c, nr, nc, piece, captured,
                                   copy.deepcopy(self.board)))
        self._log_move(r, c, nr, nc, piece)

        self.board[nr][nc] = piece
        self.board[r][c] = 0
        self.selected = None
        self.highlights = []
        self.current_red = not self.current_red
        self.draw()

        # 胜负判断
        if not has_any_move(self.board, self.current_red):
            winner = "红方" if not self.current_red else "黑方"
            self.draw()
            messagebox.showinfo("游戏结束", f"🎉 {winner}获胜！")
            return

        self._update_status()

        # AI 回合
        if self.current_red != self.red_is_human:
            self.root.after(600, self._ai_move)

    def _ai_move(self):
        """AI 走棋（暂时跳过，仅提示）"""
        # TODO: 调用 alphabeta(self.board, depth=3, ...)
        side = "黑方" if not self.current_red else "红方"
        self.status_var.set(f"{side}（AI）思考中…已跳过")
        # 暂时跳过 AI 走棋，直接切换回玩家
        self.current_red = not self.current_red
        self.draw()
        self._update_status()

    # ── 功能按钮 ──
    def swap_sides(self):
        """红黑方互换：人类改控对方"""
        self.red_is_human = not self.red_is_human
        side = "红方" if self.red_is_human else "黑方"
        self.status_var.set(f"已切换：您现在执{side}")
        self.selected = None
        self.highlights = []
        self.draw()
        self.root.after(800, self._update_status)
        # 若现在轮到 AI，触发 AI 走棋
        if self.current_red != self.red_is_human:
            self.root.after(1000, self._ai_move)

    def undo_move(self):
        if not self.move_history:
            messagebox.showinfo("悔棋", "没有可悔的棋步")
            return
        # 若 AI 已走，撤回两步；否则撤回一步
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
        # 撤销棋谱最后几行
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