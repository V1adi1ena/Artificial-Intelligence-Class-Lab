from typing import Tuple

#状态
State = Tuple[Tuple[int, int], ...]
#记忆化
mmry = {}
Card = None

def readCard(filename):
    """读取输入文件, 返回 (总牌数n, 原始行数据)"""
    card = []
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f]
    for line in lines[1:]:
        row = tuple(int(x.strip()) for x in line.split(','))
        card.append(row)
    return int(lines[0]), tuple(card)


def decision(state: State, row_idx: int, side: str) -> State:
    """从第 row_idx 行的 side 端取走一张牌然后返回新的 state"""
    new_state = list(state)
    l, r = new_state[row_idx]
    if side == 'L':
        new_state[row_idx] = (l + 1, r)
    else:  # 'R'
        new_state[row_idx] = (l, r - 1)
    return tuple(new_state)


def minmax(state: State, isMaxPlayer: bool) -> int:
    """返回从 state 开始、轮到 isMaxPlayer 时的最优结果"""
    global mmry, Card

    key = (state, isMaxPlayer)
    if key in mmry:
        return mmry[key]

    # 终局: 所有行无剩余牌
    if all(l == r for l, r in state):
        mmry[key] = 0
        return 0

    if isMaxPlayer:  # 小红回合: 最大化分差
        best = -float('inf')
        for i, (l, r) in enumerate(state):
            if l >= r:
                continue
            # 取左端
            child = decision(state, i, 'L')
            best = max(best, Card[i][l] + minmax(child, False))
            # 取右端 (只在左右不同时尝试, 避免重复)
            if r - l > 1:
                child = decision(state, i, 'R')
                best = max(best, Card[i][r - 1] + minmax(child, False))
        mmry[key] = best
        return best
    else:  # 小蓝回合: 最小化分差 (小蓝得分使分差缩小)
        best = float('inf')
        for i, (l, r) in enumerate(state):
            if l >= r:
                continue
            child = decision(state, i, 'L')
            best = min(best, -Card[i][l] + minmax(child, True))
            if r - l > 1:
                child = decision(state, i, 'R')
                best = min(best, -Card[i][r - 1] + minmax(child, True))
        mmry[key] = best
        return best


def first_step(state: State):
    """枚举小红第一步所有合法走法, 返回 (最优走法, 最优分差)"""
    global Card
    best_diff = -float('inf')
    best_action = None
    for r, (l, r_end) in enumerate(state):
        # 取左端
        child = decision(state, r, 'L')
        diff = Card[r][l] + minmax(child, False)
        print(f"row: {r+1}, side: L, val: {Card[r][l]}, diff: {diff}")
        if diff > best_diff:
            best_diff = diff
            best_action = (r, 'L', Card[r][l])
        # 取右端
        if r_end - l > 1:
            child = decision(state, r, 'R')
            diff = Card[r][r_end - 1] + minmax(child, False)
            print(f"row: {r+1}, side: R, val: {Card[r][r_end - 1]}, diff: {diff}")
            if diff > best_diff:
                best_diff = diff
                best_action = (r, 'R', Card[r][r_end - 1])
    return best_action, best_diff


def solve(filename: str):
    global mmry, Card
    mmry = {}
    total_cards, Card = readCard(filename)
    print(total_cards)
    print(Card)
    total_sum = total_cards * (total_cards + 1) // 2

    # 初始状态: 每行 l=0, r=len(row)
    init_state = tuple((0, len(row)) for row in Card)

    best_action, best_diff = first_step(init_state)
    row_idx, side, val = best_action
    print(f"第{row_idx+1}行 {'左' if side == 'L' else '右'}端 牌点数{val}")

    red = (total_sum + best_diff) / 2
    print(f"小红: {red:.0f} 小蓝: {red - best_diff:.0f}")
