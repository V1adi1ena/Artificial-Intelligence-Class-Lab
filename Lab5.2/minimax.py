import sys
from typing import Tuple, List, Optional

State = Tuple[Tuple[int, ...], ...]

def Card(filename):
  card = []
  with open(filename, 'r') as f:
    lines = [line.strip() for line in f]
  for line in lines[1:]:
    row = tuple(int(x.strip()) for x in line.split(','))
    card.append(row)
  card = tuple(card)
  return int(lines[0]), card

def decision(state, row_idx, side):
  row = state[row_idx]
  if side == 'L':
    new_row = row[1:]
  elif side == 'R':
    new_row = row[:-1]
  new_state = state[:row_idx] + (new_row,) + state[row_idx+1:]
  return new_state

def minmax(state, alpha, beta, score, isMaxPlayer):
  if all(len(row) == 0 for row in state):
    return score
  if isMaxPlayer:
    value = -float('inf')
    for row_idx, row in enumerate(state):
      if not row:
        continue

      new_state = decision(state, row_idx, 'L')
      child = minmax(new_state, alpha, beta, score+row[0], False)
      if child is None:
        raise RuntimeError("alphabeta returned None")
      value = max(value, child)
      alpha = max(alpha, value)
      if alpha >= beta:
        return value
      
      if len(row)>1:
        new_state = decision(state, row_idx, 'R')
        child = minmax(new_state, alpha, beta, score+row[-1], False)
        if child is None:
          raise RuntimeError("minmax returned None")
        value = max(value, child)
        alpha = max(alpha, value)
        if alpha >= beta:
          return value
    return value
  else:
    value = float('inf')
    for row_idx, row in enumerate(state):
      if not row:
        continue

      new_state = decision(state, row_idx, 'L')
      child = minmax(new_state, alpha, beta, score-row[0], True)
      if child is None:
        raise RuntimeError("alphabeta returned None")
      value = min(value, child)
      beta = min(beta, value)
      if alpha >= beta:
        return value
      
      if len(row)>1:
        new_state = decision(state, row_idx, 'R')
        child = minmax(new_state, alpha, beta, score-row[-1], True)
        if child is None:
          raise RuntimeError("minmax returned None")
        value = min(value, child)
        beta = min(beta, value)
        if alpha >= beta:
          return value
    return value

def first_step(state):
  best_diff = -float('inf')
  best_action = None
  for r, row in enumerate(state):
        if not row:
            continue
        for side in ('L', 'R'):
            if side == 'R' and len(row) == 1:
                continue  # 避免重复计算
            val = row[0] if side == 'L' else row[-1]
            new_state = decision(state, r, side)
            diff = minmax(new_state, -float('inf'), float('inf'), val, False)
            print(f"row: {r+1}, side: {side}, val: {val}, diff: {diff}")
            if diff > best_diff:
                best_diff = diff
                best_action = (r, side, val)
  return best_action, best_diff

def solve(filename):
  total_cards, card = Card(filename)
  print(total_cards)
  print(card)
  total_sum = total_cards*(total_cards+1)//2

  best_action, best_diff = first_step(card)
  row_idx, side, val = best_action
  print(f"第一步：小红从第{row_idx+1}行{'左' if side == 'L' else '右'}端 牌点数: {val}")

  red = (total_sum + best_diff)/2
  print(f"小红: {red} 小蓝: {red-best_diff}")
