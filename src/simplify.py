from AST import *
from typecheck import isValue, assertValid, assertContextValid
from typeinfer import TypeInfer
from traversers import ExprMutator, ExprVisitor
from typing import Iterable

var_num = 1

def get_fresh_var():
    global var_num
    toreturn = Var("fvar{}".format(var_num))
    var_num = var_num + 1
    return toreturn


def subst(e : 'Expr', x : Var, v : Value) -> 'Expr':
    class SubstMutator(ExprMutator):
        def __init__(self, x: Var, v: Value):
            self.x = x
            self.v = v
        
        def mutate_var(self, e: Var) -> 'Expr':
            if e == self.x:
                return self.v
            return e
        
        def mutate_function(self, e: Function) -> Function:
            if e.var == self.x:
                # Variable shadowing, don't substitute in the body
                return e
            else:
                return Function(e.var, self.mutate(e.body), self.mutate(e.param_type))
        
        def mutate_let(self, e: Let) -> Let:
            if e.var == self.x:
                return e
            else:
                return Let(e.var, self.mutate(e.value), self.mutate(e.body), self.mutate(e.var_type))
        
        def mutate_for(self, e: For) -> For:
            if e.var == self.x:
                return e
            else:
                return For(e.var, self.mutate(e.body), self.mutate(e.var_type))
    
    substituter = SubstMutator(x, v)
    return substituter.mutate(e)

def composeContexts(E1 : Context, E2 : Context) -> Context:
    if(isinstance(E1, LetContext)):
        return LetContext(E1.var, E1.var_type, E1.expr, composeContexts(E1.context, E2))
    else:
        assert isinstance(E1, Hole)
        return E2

def binders(E : Context) -> list[tuple[Var, DexType]]:
    toreturn = []

    curContext = E
    while(not isinstance(curContext, Hole)):
        toreturn.append((curContext.var, curContext.var_type))
        curContext = curContext.context

    return toreturn


def freeVars(v : Value) -> set[Var]:
    class FreeVarsVisitor(ExprVisitor):
        def __init__(self):
            self.free_vars = set()
        
        def visit_var(self, e):
            self.free_vars.add(e)
            return super().visit_var(e)
        
    visitor = FreeVarsVisitor()
    visitor.visit(v)
    return visitor.free_vars


def bindingList(Ed : Context, v : Value, extraBinding : tuple[Var, DexType] = None) -> set[Var]:
    '''
    First approximation calculation of the free variables of v that are bound by Ed
    In the paper denoted binders(Ed) |- v |> result 
    '''

    EdBinders = binders(Ed)
    if(extraBinding is not None):
        EdBinders.insert(0, extraBinding)

    return bindingListR(EdBinders, v)


def bindingListR(potentialBindings : list[tuple[Var, DexType]], v : Value) -> set[Var]:

    if(len(potentialBindings) == 0):
        return set()

    x1, tau1 = potentialBindings.pop()
    ybar = bindingListR(potentialBindings, v)

    freeVarsV = freeVars(v)

    # Rule Used and NotUsed
    if(x1 in freeVarsV):
        assert len(freeVars(tau1).intersection(ybar)) == 0, " Not supported, see bottom of page 13 of Dex paper for explanation"
        ybar.add(x1)
        return ybar
    elif(x1 not in freeVarsV):
        return ybar

    return set()

def applyContext(Ed : Context, v : Value) -> Expr:
    if(isinstance(Ed, Hole)):
        return v
    elif(isinstance(Ed, LetContext)):
        return Let(Ed.var, Ed.expr, applyContext(Ed.context, v), Ed.var_type)
    
    assert False, "Invalid context type {}".format(type(Ed))

def createTuple(vars : Iterable[Var]) -> Pair:
    assert len(vars) > 0, "Not handled"

    var_iterator = iter(vars)
    if(len(vars) == 1):
        return next(var_iterator) # Note: doesn't follow type annotation
    
    cur_pair = Pair(next(var_iterator), next(var_iterator))
    to_add = next(var_iterator, None)
    while(to_add is not None):
        cur_pair = Pair(to_add, cur_pair)
        to_add = next(var_iterator, None)
    
    return cur_pair


def simplify(e : 'Expr') -> Tuple[Context, Value]:
        
    if(isValue(e)):
        return Hole(), e
    elif(isinstance(e, Application)):
        subst_result = subst(e.func.body, e.func.var, e.arg)
        return simplify(subst_result)
    elif(isinstance(e, Let)):
        E1d, v1 = simplify(e.value)
        E2d, v2 = simplify(subst(e.body, e.var, v1))
        return composeContexts(E1d, E2d), v2
    elif(isinstance(e, Index) and isinstance(e.array, View)):
        subst_result = subst(e.array.body, e.array.var, e.index)
        return simplify(subst_result)
    elif(isinstance(e, Fst)):
        return simplify(e.pair.left)
    elif(isinstance(e, Snd)):
        return simplify(e.pair.right)
    
    if(isinstance(e, For)):
        Ed, v = simplify(e.body)
        x1_n = bindingList(Ed, v)

        if(len(x1_n) == 0):
            return Ed, For(e.var, v, e.var_type)

        if(e.var not in x1_n):
            y = get_fresh_var()
            x = e.var
            tau = e.var_type
            x1_n_tuple = createTuple(x1_n)
            Ed_with_subst = applyContext(Ed, x1_n_tuple)
            return LetContext(y, UnspecifiedType(), For(x, Ed_with_subst, tau), Hole()), \
                    View(x, Let(x1_n_tuple, Index(y, x), v, tau))


    if(isinstance(e, runAccum)):
        Ed, v1 = simplify(e.update_fun.body)
        x1_n = bindingList(Ed, v1, extraBinding=(e.update_fun.var, e.update_fun.param_type))
        s = get_fresh_var()
        x1_n_tuple = createTuple(x1_n)

        return LetContext(Pair(x1_n_tuple, s), UnspecifiedType(), \
                          runAccum(Function(e.update_fun.var, applyContext(Ed, x1_n_tuple), e.update_fun.param_type), e.init_val), Hole()), \
                Pair(v1, s)


    x = get_fresh_var()
    return LetContext(x, UnspecifiedType(), e, Hole()), x

if __name__ == "__main__":

    p1 = Var("p1")
    p2 = Var("p2")
    
    expr = Let(Var("f1"), Function(p1, Multiply(p1,p1)), \
        Let(Var("f2"), Function(p2, Add(p2, p2)), \
            Let(Var("xs"), For(Var("i"), Int(123), Fin(Int(99))),
    For(Var("i"), 
        Let(Var("y1"), Application(Var("f1"), Index(Var("xs"),Var("i"))),
        Let(Var("y2"), Application(Var("f2"), Var("y1")),
            Function(Var("z"), Add(Add(Var("y1"), Var("y2")), Var("z")))
            ))))))
    
    expr = Let(Var("f1"), Function(p1, Multiply(p1,p1)), \
        Let(Var("f2"), Function(p2, Add(p2, p2)), \
            Let(Var("xs"), For(Var("i"), Int(123), Fin(Int(99))),
    For(Var("i"), 
        Let(Var("y1"), Application(Var("f1"), Index(Var("xs"),Var("i"))),
        Let(Var("y2"), Application(Var("f2"), Var("y1")),
            Function(Var("z"), Add(Add(Var("y1"), Var("y2")), Var("z")))
            ))))))
    
    assertValid(expr)
    Ed, v = simplify(expr)
    assertContextValid(Ed)
    print("Simplification context = \n{}".format(Ed))
    print("Value = \n{}".format(v))