import pygame
import sys

# 初始化 pygame
pygame.init()

# 窗口尺寸
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 1000
BOARD_LEFT = 50
BOARD_TOP = 50
BOARD_WIDTH = 800
BOARD_HEIGHT = 900
CELL_WIDTH = BOARD_WIDTH // 8   # 100
CELL_HEIGHT = BOARD_HEIGHT // 9  # 100

# 颜色
BG_COLOR = (220, 190, 130)
LINE_COLOR = (0, 0, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 0, 255)

# 棋子编码
PIECES = {
    'r_rook':   '俥', 'r_knight': '馬', 'r_bishop': '相', 'r_advisor': '士',
    'r_king':   '帥', 'r_cannon': '炮', 'r_pawn':   '兵',
    'b_rook':   '車', 'b_knight': '馬', 'b_bishop': '象', 'b_advisor': '士',
    'b_king':   '將', 'b_cannon': '炮', 'b_pawn':   '卒'
}
# 简繁转换仅用于显示，不影响逻辑

# 初始棋盘布局 (9x10)
# 用字符串表示棋子类型，None 表示无子
INIT_BOARD = [
    ['b_rook', 'b_knight', 'b_bishop', 'b_advisor', 'b_king', 'b_advisor', 'b_bishop', 'b_knight', 'b_rook'],
    [None, None, None, None, None, None, None, None, None],
    [None, 'b_cannon', None, None, None, None, None, 'b_cannon', None],
    ['b_pawn', None, 'b_pawn', None, 'b_pawn', None, 'b_pawn', None, 'b_pawn'],
    [None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None],
    ['r_pawn', None, 'r_pawn', None, 'r_pawn', None, 'r_pawn', None, 'r_pawn'],
    [None, 'r_cannon', None, None, None, None, None, 'r_cannon', None],
    [None, None, None, None, None, None, None, None, None],
    ['r_rook', 'r_knight', 'r_bishop', 'r_advisor', 'r_king', 'r_advisor', 'r_bishop', 'r_knight', 'r_rook']
]

class ChessGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("中国象棋 - 用户控制红方，AI 尚未实现")
        self.font = pygame.font.SysFont('simsun', 48)  # 显示棋子文字
        self.small_font = pygame.font.SysFont('simsun', 24)
        self.board = [row[:] for row in INIT_BOARD]  # 深拷贝棋盘
        self.turn = 'r'      # r: 红方(用户), b: 黑方(AI)
        self.selected = None  # 当前选中的棋子位置 (row, col)
        self.valid_moves = [] # 当前选中棋子的合法移动位置列表
        self.winner = None    # 'r', 'b', None
        self.running = True

    def draw_board(self):
        """绘制棋盘线"""
        self.screen.fill(BG_COLOR)
        # 画横线
        for i in range(10):
            y = BOARD_TOP + i * CELL_HEIGHT
            pygame.draw.line(self.screen, LINE_COLOR, (BOARD_LEFT, y), (BOARD_LEFT + BOARD_WIDTH, y), 2)
        # 画竖线
        for i in range(9):
            x = BOARD_LEFT + i * CELL_WIDTH
            pygame.draw.line(self.screen, LINE_COLOR, (x, BOARD_TOP), (x, BOARD_TOP + BOARD_HEIGHT), 2)
        # 楚河汉界文字
        text = self.font.render("楚  河", True, BLACK)
        self.screen.blit(text, (BOARD_LEFT + BOARD_WIDTH//2 - 60, BOARD_TOP + 4*CELL_HEIGHT - 20))
        text = self.font.render("汉  界", True, BLACK)
        self.screen.blit(text, (BOARD_LEFT + BOARD_WIDTH//2 - 60, BOARD_TOP + 5*CELL_HEIGHT - 20))
        # 九宫格斜线
        # 红方 (下方)
        start_pos = (BOARD_LEFT + 3*CELL_WIDTH, BOARD_TOP + 7*CELL_HEIGHT)
        end_pos = (BOARD_LEFT + 5*CELL_WIDTH, BOARD_TOP + 9*CELL_HEIGHT)
        pygame.draw.line(self.screen, LINE_COLOR, start_pos, end_pos, 2)
        start_pos = (BOARD_LEFT + 5*CELL_WIDTH, BOARD_TOP + 7*CELL_HEIGHT)
        end_pos = (BOARD_LEFT + 3*CELL_WIDTH, BOARD_TOP + 9*CELL_HEIGHT)
        pygame.draw.line(self.screen, LINE_COLOR, start_pos, end_pos, 2)
        # 黑方 (上方)
        start_pos = (BOARD_LEFT + 3*CELL_WIDTH, BOARD_TOP)
        end_pos = (BOARD_LEFT + 5*CELL_WIDTH, BOARD_TOP + 2*CELL_HEIGHT)
        pygame.draw.line(self.screen, LINE_COLOR, start_pos, end_pos, 2)
        start_pos = (BOARD_LEFT + 5*CELL_WIDTH, BOARD_TOP)
        end_pos = (BOARD_LEFT + 3*CELL_WIDTH, BOARD_TOP + 2*CELL_HEIGHT)
        pygame.draw.line(self.screen, LINE_COLOR, start_pos, end_pos, 2)

    def draw_pieces(self):
        """绘制所有棋子"""
        for row in range(10):
            for col in range(9):
                piece = self.board[row][col]
                if piece:
                    x = BOARD_LEFT + col * CELL_WIDTH
                    y = BOARD_TOP + row * CELL_HEIGHT
                    color = RED if piece.startswith('r') else BLACK
                    text = self.font.render(PIECES[piece], True, color)
                    text_rect = text.get_rect(center=(x + CELL_WIDTH//2, y + CELL_HEIGHT//2))
                    self.screen.blit(text, text_rect)
                    # 绘制选中高亮
                    if self.selected == (row, col):
                        pygame.draw.circle(self.screen, GREEN, (x + CELL_WIDTH//2, y + CELL_HEIGHT//2), 40, 3)
        # 绘制所有合法走位点
        for (row, col) in self.valid_moves:
            x = BOARD_LEFT + col * CELL_WIDTH + CELL_WIDTH//2
            y = BOARD_TOP + row * CELL_HEIGHT + CELL_HEIGHT//2
            pygame.draw.circle(self.screen, BLUE, (x, y), 12)

    def draw_status(self):
        """绘制当前回合及胜利信息"""
        if self.winner:
            winner_text = "红方胜利！" if self.winner == 'r' else "黑方胜利！"
            text = self.small_font.render(winner_text, True, RED if self.winner=='r' else BLACK)
            self.screen.blit(text, (10, 10))
        else:
            turn_text = "轮到红方 (用户)" if self.turn == 'r' else "轮到黑方 (AI) - AI 暂不走棋"
            text = self.small_font.render(turn_text, True, BLACK)
            self.screen.blit(text, (10, 10))

    def board_to_screen(self, row, col):
        """棋盘坐标转屏幕坐标（中心点）"""
        x = BOARD_LEFT + col * CELL_WIDTH + CELL_WIDTH//2
        y = BOARD_TOP + row * CELL_HEIGHT + CELL_HEIGHT//2
        return x, y

    def screen_to_board(self, x, y):
        """屏幕坐标转棋盘坐标 (row, col)，若超出棋盘范围返回 None"""
        if x < BOARD_LEFT or x > BOARD_LEFT + BOARD_WIDTH or y < BOARD_TOP or y > BOARD_TOP + BOARD_HEIGHT:
            return None
        col = (x - BOARD_LEFT) // CELL_WIDTH
        row = (y - BOARD_TOP) // CELL_HEIGHT
        if 0 <= row < 10 and 0 <= col < 9:
            return (row, col)
        return None

    # ---------- 棋子走法合法性检查 ----------
    def is_valid_move(self, piece, from_pos, to_pos):
        """返回移动是否合法（不考虑将帅对面和将军）"""
        fr, fc = from_pos
        tr, tc = to_pos
        if fr == tr and fc == tc:
            return False
        # 目标格子有己方棋子则不可移动
        target = self.board[tr][tc]
        if target and target[0] == piece[0]:
            return False

        # 根据棋子类型判断
        piece_type = piece[2:]  # 去掉 r_ 或 b_
        dr = tr - fr
        dc = tc - fc
        abs_dr = abs(dr)
        abs_dc = abs(dc)

        # 帅/将
        if piece_type in ['king']:
            # 九宫格范围限制
            if piece[0] == 'r':  # 红方
                if not (7 <= tr <= 9 and 3 <= tc <= 5):
                    return False
            else:  # 黑方
                if not (0 <= tr <= 2 and 3 <= tc <= 5):
                    return False
            # 走法：上下左右一格
            if (abs_dr + abs_dc) != 1:
                return False
            return True

        # 士
        if piece_type == 'advisor':
            if piece[0] == 'r':
                if not (7 <= tr <= 9 and 3 <= tc <= 5):
                    return False
            else:
                if not (0 <= tr <= 2 and 3 <= tc <= 5):
                    return False
            if abs_dr != 1 or abs_dc != 1:
                return False
            return True

        # 象
        if piece_type == 'bishop':
            # 不能过河
            if piece[0] == 'r' and tr < 5:
                return False
            if piece[0] == 'b' and tr > 4:
                return False
            if abs_dr != 2 or abs_dc != 2:
                return False
            # 象眼阻塞
            mid_row = (fr + tr) // 2
            mid_col = (fc + tc) // 2
            if self.board[mid_row][mid_col] is not None:
                return False
            return True

        # 马
        if piece_type == 'knight':
            if abs_dr == 2 and abs_dc == 1:
                # 马脚在上/下
                leg_row = fr + dr//2
                leg_col = fc
                if self.board[leg_row][leg_col] is not None:
                    return False
                return True
            elif abs_dr == 1 and abs_dc == 2:
                leg_row = fr
                leg_col = fc + dc//2
                if self.board[leg_row][leg_col] is not None:
                    return False
                return True
            return False

        # 车
        if piece_type == 'rook':
            # 直线移动，中间不能有棋子
            if fr == tr:
                step = 1 if tc > fc else -1
                for c in range(fc+step, tc, step):
                    if self.board[fr][c] is not None:
                        return False
                return True
            elif fc == tc:
                step = 1 if tr > fr else -1
                for r in range(fr+step, tr, step):
                    if self.board[r][fc] is not None:
                        return False
                return True
            return False

        # 炮
        if piece_type == 'cannon':
            cnt = 0
            if fr == tr:
                step = 1 if tc > fc else -1
                for c in range(fc+step, tc, step):
                    if self.board[fr][c] is not None:
                        cnt += 1
                if cnt == 0 and target is None:
                    return True
                elif cnt == 1 and target is not None:
                    return True
                return False
            elif fc == tc:
                step = 1 if tr > fr else -1
                for r in range(fr+step, tr, step):
                    if self.board[r][fc] is not None:
                        cnt += 1
                if cnt == 0 and target is None:
                    return True
                elif cnt == 1 and target is not None:
                    return True
                return False
            return False

        # 兵/卒
        if piece_type == 'pawn':
            forward = -1 if piece[0] == 'b' else 1  # 黑向上(-1)，红向下(+1)
            # 过河前只能前进
            if piece[0] == 'r':
                # 红兵未过河（row > 4）
                if fr > 4:
                    if dr == forward and dc == 0:
                        return True
                    return False
                else:  # 过河后可左右前
                    if (dr == forward and dc == 0) or (dr == 0 and abs_dc == 1):
                        return True
                    return False
            else:  # 黑卒
                if fr < 5:
                    if dr == forward and dc == 0:
                        return True
                    return False
                else:
                    if (dr == forward and dc == 0) or (dr == 0 and abs_dc == 1):
                        return True
                    return False

        return False

    def is_check(self, side, board=None):
        """判断 side 方是否被将军，board 若为 None 则用当前棋盘"""
        if board is None:
            board = self.board
        king_pos = None
        for r in range(10):
            for c in range(9):
                piece = board[r][c]
                if piece == (side + '_king'):
                    king_pos = (r, c)
                    break
            if king_pos:
                break
        if not king_pos:
            return False  # 将不存在（理论上不会）
        # 遍历所有敌方棋子看是否能吃到将
        enemy = 'b' if side == 'r' else 'r'
        for r in range(10):
            for c in range(9):
                piece = board[r][c]
                if piece and piece[0] == enemy:
                    # 检查从(r,c)到king_pos是否合法移动
                    if self.is_valid_move(piece, (r, c), king_pos):
                        # 临时移动验证时需要忽略目标棋子（就是将）
                        # is_valid_move 已经允许吃子，所以直接返回True
                        return True
        return False

    def is_checkmate(self, side):
        """检查 side 方是否被将死（无合法步数）"""
        for r in range(10):
            for c in range(9):
                piece = self.board[r][c]
                if piece and piece[0] == side:
                    moves = self.get_all_valid_moves_for_piece((r, c))
                    for move in moves:
                        # 模拟移动
                        if self.simulate_move((r, c), move):
                            return False
        return True

    def get_all_valid_moves_for_piece(self, pos):
        """返回某个棋子所有合法走位列表（不考虑己方将帅被吃）"""
        r, c = pos
        piece = self.board[r][c]
        if not piece:
            return []
        moves = []
        for tr in range(10):
            for tc in range(9):
                if self.is_valid_move(piece, (r, c), (tr, tc)):
                    # 还需要模拟移动后自己的将不被将军
                    if self.simulate_move((r, c), (tr, tc)):
                        moves.append((tr, tc))
        return moves

    def simulate_move(self, from_pos, to_pos):
        """模拟移动后，己方将是否处于被将军状态"""
        fr, fc = from_pos
        tr, tc = to_pos
        piece = self.board[fr][fc]
        if not piece:
            return False
        target = self.board[tr][tc]
        # 备份
        self.board[tr][tc] = piece
        self.board[fr][fc] = None
        # 检查本方将是否被将军
        side = piece[0]
        in_check = self.is_check(side)
        # 还原
        self.board[fr][fc] = piece
        self.board[tr][tc] = target
        return not in_check

    def is_valid_move_with_check(self, from_pos, to_pos):
        """综合合法性：基本走法 + 移动后己方将不被将军"""
        piece = self.board[from_pos[0]][from_pos[1]]
        if not piece:
            return False
        if not self.is_valid_move(piece, from_pos, to_pos):
            return False
        # 模拟移动
        return self.simulate_move(from_pos, to_pos)

    def move_piece(self, from_pos, to_pos):
        """执行移动，返回是否成功"""
        if not self.is_valid_move_with_check(from_pos, to_pos):
            return False
        fr, fc = from_pos
        tr, tc = to_pos
        piece = self.board[fr][fc]
        target = self.board[tr][tc]
        self.board[tr][tc] = piece
        self.board[fr][fc] = None
        # 切换回合
        self.turn = 'b' if self.turn == 'r' else 'r'
        # 检查胜利
        if target and target[0] == ('b' if piece[0]=='r' else 'r') and target[2:]=='king':
            self.winner = piece[0]
        else:
            # 检查当前被将军且无步可走（将死）
            if self.is_checkmate(self.turn):
                self.winner = 'r' if self.turn == 'b' else 'b'
        return True

    def ai_move(self):
        """AI 走棋（尚未实现）"""
        # 这里什么也不做，直接返回
        # 为了保持回合切换，调用后立刻把回合切回红方
        self.turn = 'r'  # AI 不走棋，立即交还控制权给用户

    def handle_click(self, pos):
        if self.winner:
            return  # 游戏结束
        if self.turn != 'r':
            return  # 黑方回合，用户不能操作
        board_pos = self.screen_to_board(pos[0], pos[1])
        if not board_pos:
            return
        row, col = board_pos
        if self.selected is None:
            # 选中棋子
            piece = self.board[row][col]
            if piece and piece[0] == 'r':  # 只能选红方棋子
                self.selected = (row, col)
                self.valid_moves = self.get_all_valid_moves_for_piece((row, col))
        else:
            # 尝试移动
            if self.move_piece(self.selected, (row, col)):
                self.selected = None
                self.valid_moves = []
                # 移动成功，切换回合后调用 AI
                if self.winner is None and self.turn == 'b':
                    self.ai_move()  # AI 不走棋，但会切换回合回 'r'
                    # 再次检查胜利（AI 不动，所以胜利状态不变）
            else:
                # 非法移动，取消选中
                self.selected = None
                self.valid_moves = []

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # 按R重置游戏
                        self.__init__()
            self.draw_board()
            self.draw_pieces()
            self.draw_status()
            pygame.display.flip()
            clock.tick(60)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = ChessGame()
    game.run()