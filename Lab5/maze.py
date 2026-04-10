"""把起点终点和墙壁路径转换为int"""
def toInt(x):
  if x == 'S':
    return 2
  elif x == 'E':
    return 3
  else:
    return int(x)
"""将迷宫文件转换为int列表"""
def  Maze(filename):
  maze = []
  with open(filename, 'r', encoding='utf-8') as f:
    for line in f:
      maze.append([toInt(x) for x in line.strip()])
  for i in range(len(maze)):
    for j in range(len(maze[0])):
      if maze[i][j] == 2:
        start = (i, j)
      elif maze[i][j] == 3:
        goal = (i, j)
  return maze, start, goal
"""判断是否在迷宫内且未访问过"""
def is_valid(x, y, visited):
  return (x>=0 and x<height and y>=0 and y<width and maze[x][y] != 1 and not visited[x][y])
"""重置访问矩阵"""
def reset_visited():
  for i in range(height):
    for j in range(width):
      visited[i][j] = False

def dfs(x, y, path=None):
  if path is None:
    path = []
  if not is_valid(x, y, visited):
    return False
  visited[x][y] = True

  path.append((x, y))
  if((x, y) == goal):
    return True
  for dx, dy in directions:
    if(dfs(x+dx, y+dy, path)):
      return True
  path.pop()
  
  return False

def bfs():
  visited = [[False for _ in range(width)] for _ in range(height)]
  visited[start[0]][start[1]] = True
  que = [(start, [start])]

  while(len(que) > 0):
    pos, state = que.pop(0)
    if pos == goal:
      state.append(pos)
      return state
    for dx, dy in directions:
        cur_state = state.copy()
        if not is_valid(pos[0]+dx, pos[1]+dy, visited):
          continue
        visited[pos[0]+dx][pos[1]+dy] = True
        cur_state.append((pos[0]+dx, pos[1]+dy))
        que.append(((pos[0]+dx, pos[1]+dy), cur_state))
  return [] 

def dls(x, y, path, limit = 40):
  if(limit == 0):
    return False
  if not is_valid(x, y, visited):
    return False
  visited[x][y] = True

  path.append((x, y))
  if((x, y) == goal):
    return True
  for dx, dy in directions:
    if(dls(x+dx, y+dy, path, limit-1)):
      return True
  path.pop()
  
  return False

def iddfs(x, y, max_limit, path):
  for limit in range(1, max_limit+1):
    reset_visited()
    path.clear()
    if(dls(x, y, path, limit)):
      print(f"IDDFS 找到路径，最大深度为{limit}")
      return True
  return False

def dedfs():
  v = [[0 for _ in range(width)] for _ in range(height)]
  v[start[0]][start[1]] = 1
  v[goal[0]][goal[1]] = 2
  
  que_1 = [(start, [start])]
  que_2 = [(goal, [goal])]
  
  paths_1 = {start: [start]}
  paths_2 = {goal: [goal]}

  while que_1 and que_2:
    pos_1, state_1 = que_1.pop(0)
    for dx, dy in directions:
      x, y = pos_1[0]+dx, pos_1[1]+dy
      if 0 <= x < height and 0 <= y < width and maze[x][y] != 1:
        if v[x][y] == 2:
          return state_1 + paths_2[(x, y)][::-1][1:]
        if v[x][y] == 0:
          v[x][y] = 1
          new_state = state_1 + [(x, y)]
          paths_1[(x, y)] = new_state
          que_1.append(((x, y), new_state))

    pos_2, state_2 = que_2.pop(0)
    for dx, dy in directions:
      x, y = pos_2[0]+dx, pos_2[1]+dy
      if 0 <= x < height and 0 <= y < width and maze[x][y] != 1:
        if v[x][y] == 1:
          return paths_1[(x, y)] + state_2[::-1][1:]
        if v[x][y] == 0:
          v[x][y] = 2
          new_state = state_2 + [(x, y)]
          paths_2[(x, y)] = new_state
          que_2.append(((x, y), new_state))
    
  return []

filename = input("请输入文件名")
maze, start, goal = Maze(filename)
width, height = len(maze[0]), len(maze)

visited = [[False for _ in range(width)] for _ in range(height)]
directions = []

if(start[0]<goal[0]): 
  if(start[1]<goal[1]): directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
  else: directions = [(1, 0), (0, -1), (-1, 0), (0, 1)]
else:
  if(start[1]<goal[1]): directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
  else: directions = [(-1, 0), (0, -1), (1, 0), (0, 1)]