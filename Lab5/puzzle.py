import heapq
from collections import deque

def Puzzle(filename):
  puzzle = []
  with open(filename, 'r') as f:
    lines = f.readlines()
    for line in lines:
      puzzle.append([int(x) for x in line.split(" ")])
    return puzzle

def h(cur):
  """曼哈顿距离"""
  distance = 0
  for i in range(len(cur)):
    for j in range(len(cur[i])):
      if(cur[i][j] != 0):
        x, y = (cur[i][j]-1)//len(cur[i]), (cur[i][j]-1)%len(cur[i])
        distance += abs(x-i) + abs(y-j)
  return distance

def get_zero(cur):
  """获取0的位置"""
  for i in range(len(cur)):
    for j in range(len(cur[i])):
      if(cur[i][j] == 0):
        return (i,j)

def neighbors(cur):
  """返回当前状态的邻居状态"""
  zero_x, zero_y = get_zero(cur)
  neighbors = []
  for i, j in [(zero_x-1, zero_y), (zero_x+1, zero_y), (zero_x, zero_y-1), (zero_x, zero_y+1)]:
    if 0 <= i < len(cur) and 0 <= j < len(cur[i]):
      neighbor = [row[:] for row in cur]
      neighbor[zero_x][zero_y], neighbor[i][j] = neighbor[i][j], neighbor[zero_x][zero_y]
      neighbors.append(neighbor)
  return neighbors

def A_star(filename):
  puzzle = Puzzle(filename)
  goal = [[1+i+j*len(puzzle) for i in range(len(puzzle))] for j in range(len(puzzle))]
  goal[-1][-1] = 0

  open = []
  heapq.heappush(open, (h(puzzle), 0, puzzle))
  close = set()
  close.add(tuple(tuple(row) for row in puzzle))

  while(len(open) > 0):
    _, g, cur = heapq.heappop(open)
    if(cur == goal):
      return cur
    
    for neighbor in neighbors(cur):
      neighbor_tuple = tuple(tuple(row) for row in neighbor)
      if neighbor_tuple in close or neighbor_tuple in [x[2] for x in open]:
        continue
      heapq.heappush(open, (h(neighbor)+g+1, g+1, neighbor))
      close.add(neighbor_tuple)
  return None