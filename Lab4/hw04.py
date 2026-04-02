KB1 = {('A(tony)',),('A(mike)',),('A(john)',),('L(tony,rain)',),('L(tony,snow)',),('~A(x)','S(x)','C(x)'),('~C(y)','~L(y,rain)'),('L(z,snow)','~S(z)'),('~L(tony,u)','~L(mike,u)'),('L(tony,v)','L(mike,v)'),('~A(w)','~C(w)','S(w)')}
KB2 = {('On(tony,mike)',), ('On(mike,john)',), ('Green(tony)',), ('~Green(john)',), ('~On(xx,yy)','~Green(xx)','Green(yy)')}
#1
#任务目标：编写函数 ResolutionProp 实现命题逻辑的归结推理过程。
def ResolutionProp(kb:set):
  clauses = list(sorted(kb))
  res = []
  idx = 1
  for clause in clauses:
    #print(f"{clause}\n")
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
    # 先处理~符号
    if it.startswith('~'):
        return '~' + replace(it[1:], res)
    
    # 先处理~符号
    if it.startswith('~'):
        return '~' + replace(it[1:], res)
    
    if is_var(it):
       if it in res:
          return replace(res[it], res)
       return it
    if is_const(it):
       return it
    """不是变量或常量，则是复合项"""
    paren_idx = it.index('(')
    func_name = it[:paren_idx]
    params_str = it[paren_idx+1:-1]
    
    # 分割参数
    params = [p.strip() for p in params_str.split(',')]
    
    it_changed = func_name + '('
    it_changed += replace(params[0], res)
    for para in params[1:]:
        it_changed += ',' + replace(para, res)
    it_changed += ')'

    return it_changed


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
    
    # 提取谓词名（括号前的部分）
    idx1 = f1.index('(') if '(' in f1 else -1
    idx2 = f2.index('(') if '(' in f2 else -1
    
    pred1 = f1[:idx1]
    pred2 = f2[:idx2]
    
    # 谓词名必须相同
    if pred1 != pred2:
        return None

    clause1 = f1[idx1+1:-1]
    clause2 = f2[idx2+1:-1]
    parameters1 = clause1.split(",")
    parameters2 = clause2.split(",")

    if len(parameters1) != len(parameters2):
       print(f"参数数量不一样，怎么合并喵？")
       return None
    
    for it1, it2 in zip(parameters1, parameters2):
       res = unify(it1, it2, res)
       if res is None:
          print("失败了喵")
          return None

    return res

def ResolutionPrinciple(kb:set):
   clauses = list(sorted(kb))
   res = []
   idx = 1
   for clause in clauses:
      res.append(f"{idx} {clause}")
      idx += 1
   
   while True:
      found = False
      new_clauses = []
      n = len(clauses)
      
      # 完整遍历所有配对（这一轮内）
      for i in range(n):
         for j in range(i+1, n):
            ci = clauses[i]
            cj = clauses[j]

            src_idx = 0
            for src in ci:
               obj_idx = 0
               for obj in cj:
                  # 归结的第一个检查：一个是肯定一个是否定
                  if src.startswith('~') == obj.startswith('~'):
                     obj_idx += 1
                     continue
                  '''判断是否可以合一'''
                  sigma = []
                  if src.startswith('~'):
                     sigma = MGU(src[1:], obj)
                  else:
                     sigma = MGU(src, obj[1:])
                  # 检查是否可以合一
                  if sigma is None:
                     obj_idx += 1
                     continue
                  '''可以合一，进行消解'''
                  # 对所有文字进行替换
                  new_ci = tuple(replace(lit, sigma) for lit in ci)
                  new_cj = tuple(replace(lit, sigma) for lit in cj)
                  
                  # 找到匹配的文字进行消解
                  src_replaced = replace(src, sigma)
                  obj_replaced = replace(obj, sigma)
                  
                  merged = sorted(tuple(x for x in new_ci if x != src_replaced) + tuple(x for x in new_cj if x != obj_replaced))
                  merged = simplify(merged)

                  suffix_i = ""
                  if len(ci) > 1:
                     suffix_i = chr(ord('a') + src_idx)
                  suffix_j = ""
                  if len(cj) > 1:
                     suffix_j = chr(ord('a') + obj_idx)

                  res.append(f"{idx} R[{i+1}{suffix_i}, {j+1}{suffix_j}] = {merged}")
                  idx += 1

                  if not merged: 
                     return res  # 推导出空子句，成功
                  
                  # 检查是否已经存在这个子句
                  if merged not in clauses and merged not in new_clauses:
                     new_clauses.append(merged)
                     found = True
                  
                  break  # 该配对 (i,j) 已处理，跳到下一对
               obj_idx += 1
               if found:
                  break
            src_idx += 1
          
      # 如果这一轮没有产生新子句，停止
      if not found:
         break
      
      # 否则加入新子句，进行下一轮
      clauses.extend(new_clauses)
   
   return res