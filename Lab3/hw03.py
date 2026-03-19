import sys
filename = input()
# 题目一
def func1(filename):
  line_cnt = 0
  words = {}
  with open(filename, 'r') as f:
    for line in f:
      line_cnt += 1
      for word in line.split():
        if word in words:
          words[word] += 1
        else:
          words[word] = 1
    #或者直接使用get()方法
    #words[word] = words.get(word, 0) + 1
  most = max(words, key=words.get)
  print(f"行数：{line_cnt}\n单词数：{len(words)}\n出现最多的单词：{most}({words[most]}次)")

########################################
# 题目二
#程序要求：
# 读取文件数据并存入合适的数据结构
# 实现以下功能函数：
# 1）计算平均成绩
# 2）找出最高分和对应学生
# 3）按成绩从高到低排序输出
def func2(filename):
  stu = {}
  total = 0
  with open(filename, 'r') as f:
    for line in f:
      name = line.split()[0]
      score = int(line.split()[1])
      total += score
      stu[name] = score
  avg = total//len(stu)
  r1 = max(stu, key=stu.get)

  def helper(e):
      return stu[e]
  sorted_keys = sorted(stu, reverse=True, key=helper)
  #也可以直接让key=stu.get

  print(f"平均成绩：{avg}\n最高分：{r1} {stu[r1]}\n成绩排名：")
  i = 1
  for k in sorted_keys:
    print(f"{i} {k} {stu[k]}")

###################################
#题目三
#设计一个简单的 命令行计算器程序。
# 用户输入表达式：
# 请输入表达式： 10 / 2
# 程序输出：
# 结果：5.0
# 要求：
# 支持运算符
#  + - * /
# 必须处理以下异常：
# 除零错误
# 输入格式错误
# 非数字输入
def func3(filename):
  op1 = filename.split()[0]
  op2 = filename.split()[2]
  op = filename.split()[1]

  if op1.isalnum() and op2.isalnum():
    op1 = int(op1)
    op2 = int(op2)
  else:
    print("输入格式错误！")
    return
  
  if op=='/' and op2==0:
    print("除零错误！")
    return
  
  if op == '+': print(op1 + op2) 
  if op == '-': print(op1 - op2) 
  if op == '*': print(op1 * op2) 
  if op == '/': print(op1 / op2) 

#################################
#题目四
# 4.给定一个服务器访问日志文件 access.log，格式如下：
# 192.168.1.1 2026-03-10 /index.html  
# 192.168.1.2 2026-03-10 /login  
# 192.168.1.1 2026-03-11 /home  
# 192.168.1.3 2026-03-11 /index.html
# 每一行含义：IP地址 日期 访问页面
# 要求实现程序：
# 统计 访问次数最多的IP地址
# 统计 访问最多的页面
# 按日期统计访问次数

# 要求：
# 使用 函数模块化设计
# 使用 字典统计
# 代码需有 异常处理（文件不存在）

# 示例输出：
# 访问最多的IP：192.168.1.1 (2次)  
# 访问最多的页面：/index.html (2次)  
# 每日访问量：  
# 2026-03-10 : 2  
# 2026-03-11 : 2
def read_log(filename):
    """读取日志文件，返回记录列表，每条记录为 (ip, date, page)。"""
    ip_count = {}
    page_count = {}
    date_count = {}
    try:
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) < 3:
                    continue
                ip, date, page = parts[0], parts[1], parts[2]
                ip_count[ip] = ip_count.get(ip, 0) + 1
                page_count[page] = page_count.get(page, 0) + 1
                date_count[date] = date_count.get(date, 0) + 1
    except FileNotFoundError:
        print(f"错误: 文件 '{filename}' 不存在")
        sys.exit(1)
    except PermissionError:
        print(f"错误: 无权限读取文件 '{filename}'")
        sys.exit(1)
    except OSError as e:
        print(f"错误: 读取文件时出错 — {e}")
        sys.exit(1)
    return ip_count, page_count, date_count

def func4(filename):
  ip_count, page_count, date_count = read_log(filename)
  max_ip = max(ip_count, key=ip_count.get)
  max_page = max(page_count, key=page_count.get)
  max_date = max(date_count, key=date_count.get)
  print(f"Most visited IP:{max_ip}\nMost visited Page:{max_page}\nMost visited date:{max_date}")