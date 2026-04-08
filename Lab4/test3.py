import hw04

KB_A = {
    ('On(tony,mike)',),
    ('On(mike,john)',),
    ('Green(tony)',),
    ('~Green(john)',),
    ('~On(xx,yy)','~Green(xx)','Green(yy)')
}

KB_B = {
    ('A(tony)',),
    ('A(mike)',),
    ('A(john)',),
    ('L(tony,rain)',),
    ('L(tony,snow)',),
    ('~A(x)','S(x)','C(x)'),
    ('~C(y)','~L(y,rain)'),
    ('L(z,snow)','~S(z)'),
    ('~L(tony,u)','~L(mike,u)'),
    ('L(tony,v)','L(mike,v)'),
    ('~A(w)','~C(w)','S(w)')
}

# KB_C: Consistent On/Green (no ~Green(john))
KB_C = {
    ('On(tony,mike)',),
    ('On(mike,john)',),
    ('Green(tony)',),
    ('~On(xx,yy)','~Green(xx)','Green(yy)')
}

# KB_D: Direct unit contradiction
KB_D = {
    ('P(a)',),
    ('~P(a)',)
}

# KB_E: Function unification leading to refutation
KB_E = {
    ('R(f(a))',),
    ('~R(x)',)
}

def run_case(name, kb):
    print(f"=== {name} ===")
    res = hw04.solve(kb)
    for item in res:
        print(item if isinstance(item, str) else f"{item}")
    has_empty = any(isinstance(x, str) and x.endswith('()') for x in res)
    print(f"Empty clause derived: {has_empty}\n")

if __name__ == "__main__":
    run_case("KB_A (On/Green)", KB_A)
    run_case("KB_B (A/L/S/C)", KB_B)
    run_case("KB_C (On/Green, consistent)", KB_C)
    run_case("KB_D (Unit contradiction P/¬P)", KB_D)
    run_case("KB_E (Function unification R(f(a)) vs ¬R(x))", KB_E) 