from AST import *

# Is a value restricted to the following variables
def isValue(e : 'Expr'):
    if(isinstance(e, (Var, Float, Int, Function, View))):
        return True
    
    if(isinstance(e,Fin)):
        assert isinstance(e.end,Int)
        return True

    if(isinstance(e, Pair)):
        assert isValue(e.left)
        assert isValue(e.right)
        return True
    
    return False
    
def assertValid(e : 'Expr'):

    if isinstance(e, Var):
        assert isinstance(e.name, str)
    elif isinstance(e, Float):
        assert isinstance(e.value, float)
    elif isinstance(e, Int):
        return isinstance(e.value, int)
    
    elif isinstance(e, Fin):
        # Ensure the 'end' field is an Int e and valid.
        assert isinstance(e.end, Int) 
        assertValid(e.end)

    elif isinstance(e, Pair):
        assert isValue(e.left) and isValue(e.right) 
        assertValid(e.left) 
        assertValid(e.right)

    elif isinstance(e, Unit):
        # Unit has no fields to validate.
        return True

    elif isinstance(e, (For, View)):
        # var must be Var; body must be an Expr; var_type should be a DexType.
        assert (isinstance(e.var, Var) and isinstance(e.var_type, (Unit, Fin, Pair, UnspecifiedType)))
        assertValid(e.body)

    elif isinstance(e, Index):
        assert isValue(e.index)
        assertValid(e.array)
        assertValid(e.index) 

    elif isinstance(e, Function):
        # param must be Var; body is an Expr; param_type is a DexType.
        assert (isinstance(e.var, Var) and
                isinstance(e.param_type, DexType))
    
        assertValid(e.body)

    elif isinstance(e, RefSlice):
        assert isinstance(e.ref, Var) and isValue(e.index)
        assertValid(e.index) 

    elif isinstance(e, runAccum):
        assertValid(e.update_fun)

    elif isinstance(e, PlusEquals):
        assert isinstance(e.dest, Var) 
        assertValid(e.src)

    elif isinstance(e, Let):

        assert isinstance(e.var, Var) and isinstance(e.var_type, DexType) 
        assertValid(e.value)
        assertValid(e.body)

    elif isinstance(e, Application):
        assert isinstance(e.func, Function) 
        assertValid(e.func) 
        assertValid(e.arg) and isValue(e.arg)

    elif isinstance(e, (Fst, Snd)):
        # assert isValue(e.pair) # Being applied to runAccum which is not a value
        assertValid(e.pair)

    elif isinstance(e, Add):
        assertValid(e.left) 
        assertValid(e.right)

    elif isinstance(e, Multiply):
        assertValid(e.left) 
        assertValid(e.right)
    else:
        assert False, "{} has unkown type {}".format(e, type(e))

    
if __name__ == "__main__": 
    n       = 100
    sum     = Var("sum")
    x       = Var("x")
    i       = Var("i")
    total   = Var("total")
    program = Let(sum, Function(x,
                                Snd(runAccum(Function(total,
                                For(i, PlusEquals(total, Index(x, i)))))), ArrayType(Fin(Int(n)), FloatType())), Unit())
    print(program)
    assertValid(program)

