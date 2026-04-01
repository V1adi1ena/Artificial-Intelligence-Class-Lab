#1
#任务目标：编写函数 ResolutionProp 实现命题逻辑的归结推理过程。
KB = {('FirstGrade',), ('~FirstGrade', 'Child'), ('~Child',)}
def ResolutionProp(kb:set):
  clauses = list(kb)
  res = []
  idx = 1
  for clause in clauses:
    res.append(f"{idx} {clause}")
    idx += 1
  
  found = True
  visited_clauses = []
  while found:
      found = False
      n = len(clauses)
      for i in range(n):
          for j in range(i+1, n):
              if i in visited_clauses or j in visited_clauses:
                 continue
              ci = clauses[i]
              cj = clauses[j]
              src_idx = 0
              for src in ci:
                obj_idx = 0
                for obj in cj:
                  if obj=='~'+src or src=='~'+obj:
                    merged = sorted(tuple(x for x in ci if x != src) + tuple(x for x in cj if x != obj))
                    merged = simplify(merged)

                    suffix_i = ""
                    if len(ci) > 1:
                        suffix_i = chr(ord('a') + src_idx)
                    suffix_j = ""
                    if len(cj) > 1:
                        suffix_j = chr(ord('a') + obj_idx)

                    res.append(f"{idx} R[{i+1}{suffix_i}, {j+1}{suffix_j}] = {merged}")
                    idx += 1

                    if not merged: return res
                    
                    found = True
                    visited_clauses.append(i)
                    clauses[j] = merged
                    break;
                  obj_idx += 1
                src_idx += 1
                if found:
                  break
              if found:
                break
          if found:
            break
  return res


def simplify(clause):
    """删除互补文字对"""
    clause = list(clause)  # 转为列表
    changed = True
    while changed:
        changed = False
        # 检查任意两个文字是否互补
        n = len(clause)
        for i in range(n):
            for j in range(i+1, n):
                a, b = clause[i], clause[j]
                if a == '~' + b or b == '~' + a:
                    # 删除这两个互补文字
                    del clause[j]
                    del clause[i]
                    changed = True
                    break
            if changed:
                break
    # 去重并排序，返回元组
    return tuple(sorted(set(clause)))

#2
def is_var(it):
    return it in {'x', 'xx', 'y', 'yy', 'z', 'zz', 'w', 'ww', 'u', 'uu', 'p', 'q', 'r', 's', 't'}
def is_const(it):
    if(is_var(it)):
       return False
    if('(' in it):
       return False
    return True

def replace(it, res):
    if is_var(it):
       if it in res:
          return replace(res[it], res)
       return it
    if is_const(it):
       return it
    """不是变量或常量，则是复合项"""
    it_paras = it[2:-1]
    return it[0] + '(' + replace(it_paras, res) + ')'

def is_occurred(var, term, res):
    """检查var是否出现在term中（防止循环替换"""
    term = replace(term, res)
    if var == term:
        return True
    if is_var(term) or is_const(term):
       return False
    else:
       return any(is_occurred(var, arg, res) for arg in term[2:-1].split(','))

def unify(it1, it2, res):
    if res == None:
       res = {}
    t1 = replace(it1, res)
    t2 = replace(it2, res)

    if t1 == t2:
       return res
    
    """有一个是变量"""
    if is_var(t1):
       if is_occurred(t1, t2, res):
          print(f"{t1}在{t1}中出现了喵")
          return None
       res[t1] = t2
       return res
    if is_var(t2):
       if is_occurred(t2, t1, res):
          print(f"{t2}在{t1}中出现了喵")
          return None
       res[t2] = t1
       return res
    """两个常量，或一个常量一个复合项"""
    if is_const(t1) or is_const(t2):
       print(f"常量不能替换喵")
       return None
    """两个复合项"""
    if t1[0] != t2[0]:
       print(f"函数不一样喵")
       return None
    for arg1, arg2 in zip(t1[2:-1].split(','), t2[2:-1].split(',')):
        print(arg1, arg2)
        res = unify(arg1, arg2, res)
        if res is None:
           print(f"{t1}和{t2}没法合一喵")
           return None
    return res

def MGU(f1, f2):
    res = {}

    clause1 = f1[2:-1]
    clause2 = f2[2:-1]
    parameters1 = clause1.split(",")
    parameters2 = clause2.split(",")

    if len(parameters1) != len(parameters2):
       return None, f"参数数量不一样，怎么合并喵？"
    
    for it1, it2 in zip(parameters1, parameters2):
       res = unify(it1, it2, res)
       if res is None:
          return None, "失败了喵"

    return res, "成功了喵"