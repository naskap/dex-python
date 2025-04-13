from AST import *
from typecheck import isValue
from typeinfer import TypeInfer



def subst(e : 'Expr', x : Var, v : Value) -> 'Expr':
    if(e == x):
        return v
    elif(isinstance(e, Var)):
        return e
    elif(isinstance(e, Application)):
        return Application(subst(e.func, x, v), subst(e.arg))
    elif(isinstance(e,Function)):
        if(e.var == x):
            return e
        else:
            return Function(e.var, subst(e.body, x, v), subst(e.param_type,x,v))
    elif(isinstance(e,Fin)):
        return Fin(subst(e.end, x, v))
    elif(isinstance(e,View)):
        # Substitutes propogate through a view expression
        return View(subst(e.var, x, v), subst(e.body, x, v), subst(e.var_type, x, v))
    elif(isinstance(e,Pair)):
        return Pair(subst(e.left, x, v), subst(e.right, x, v))
    elif(isinstance(e,Let)):
        if(e.var == x):
            return e
        else:
            return Let(e.var, subst(e.value, x, v), subst(e.body, x, v), subst(e.var_type,x,v))
    elif(isinstance(e,Index)):
        return Index(subst(e.array, x, v), subst(e.index, x, v))
    elif(isinstance(e,For)):
        if(e.var == x):
            # Variable shadowing, don't substitute in the body
            return e
        else:
            return For(e.var, subst(e.body, x, v), subst(e.var_type, x, v))
    elif(isinstance(e,Fst)):
        return Fst(subst(e.pair, x, v))
    elif(isinstance(e,Snd)):
        return Snd(subst(e.pair, x, v))
    elif(isinstance(e,RefSlice)):
        return RefSlice(subst(e.ref, x, v), subst(e.index, x, v))
    elif(isinstance(e,runAccum)):
        return runAccum(subst(e.update_fun, x, v))
    elif(isinstance(e,PlusEquals)):
        return PlusEquals(subst(e.dest, x, v), subst(e.src, x, v))
    elif(isinstance(e,Add)):
        return Add(subst(e.left, x, v), subst(e.right, x, v))
    elif(isinstance(e,Multiply)):
        return Multiply(subst(e.left, x, v), subst(e.right, x, v))
    elif(isinstance(e, ArrayType)):
        return ArrayType(subst(e.index_set, x, v), subst(e.elmt_type, x, v))
    elif(isinstance(e, FunctionType)):
        return FunctionType(subst(e.tau1, x, v), subst(e.tau2, x, v), subst(e.effect, x, v))
    else:
        return e

def composeContexts(E1 : Context, E2 : Context) -> Context:
    if(isinstance(E1, LetContext)):
        return LetContext(E1.var, E1.var_type, E1.expr, composeContexts(E1.context, E2))
    else:
        assert isinstance(E1, Hole())
        return E2

def binders(E : Context) -> list[tuple[Var, DexType]]:
    toreturn = []

    curContext = E
    while(not isinstance(curContext, Hole)):
        toreturn.append((curContext.var, curContext.var_type))

    return toreturn

def bindingList(Ed : Context, v : Value) -> set[Var]:
    '''
    First approximation calculation of the free variables of v that are bound by Ed
    In the paper denoted binders(Ed) |- v |> result 
    '''
    return bindingListR(binders(Ed), v)

    
def freeVars(v : Value) -> set[Var]:
    pass



def bindingListR(potentialBindings : list[tuple[Var, DexType]], v : Value) -> set[Var]:

    if(len(potentialBindings) == 0):
        return []

    x1, tau1 = potentialBindings.pop()
    ybar = bindingListR(potentialBindings, v)

    freeVarsV = freeVars(v)

    if(x1 in freeVarsV and len(freeVars(tau1).intersection(ybar)) == 0):
        ybar.add(x1)
        return ybar
    elif(x1 not in freeVarsV):
        return ybar

    return []


# def simplify(e : 'Expr') -> Tuple[Context, Value]:
        
#     if(isValue(e)):
#         return Hole(), e
#     elif(isinstance(e, Application)):
#         subst_result = subst(e.func.body, e.func.var, e.arg)
#         return simplify(subst_result)
#     elif(isinstance(e, Let)):
#         E1d, v1 = simplify(e.value)
#         E2d, v2 = simplify(subst(e.body, e.var, v1))
#         return composeContexts(E1d, E2d), v2
#     elif(isinstance(e, Index) and isinstance(e.array, View)):
#         subst_result = subst(e.array.body, e.array.var, e.index)
#         return simplify(subst_result)
#     elif(isinstance(e, Fst)):
#         return simplify(e.pair.left)
#     elif(isinstance(e, Snd)):
#         return simplify(e.pair.right)
#     elif(isinstance(e, For)):
#         pass


#     type_infer = TypeInfer()
#     tau_d = type_infer.infer(e)
#     x = type_infer.fresh_typevar()
#     return LetContext(x, tau_d, e, Hole()), x