from dataclasses import dataclass
from typing import Union, Tuple, List

# ----------------- Types ---------------------


# Point of confusion: type(Float(0)) = Float, but we also have FloatType -- why?
# Answer: Consider type(Let(Var("x"), Float(0), Var("x"))) =  Let
#         But this should semantically be a float. Therefore our type checking and inference system will need 
#         to conclude this is of type FloatType


class DexType: 
    pass


@dataclass
class IndexSetType(DexType): 
    index_set : 'Index_Set' # Value-dependent type

@dataclass
class ArrayType(DexType):
    index_set : 'Index_Set' # Value-dependent type
    elmt_type : DexType

# Type for a type annotation not filled in
class UnspecifiedType(DexType): 
    pass

@dataclass
class FloatType(DexType): 
    pass

@dataclass
class UnitType(DexType): 
    pass

@dataclass
class FunctionType(DexType): 
    tau1: DexType
    tau2: DexType

@dataclass
class PairType(DexType): 
    tau1: DexType
    tau2: DexType

@dataclass
class RefType(DexType): 
    tau1: DexType
    tau2: DexType



# ------------------ Values  ------------------

@dataclass
class Var: 
    name: str


@dataclass
class Float: 
    value: float


@dataclass
class Fin: 
    end: int


@dataclass
class Pair: 
    left : 'Value' # According to syntax these can't be expressions
    right: 'Value'


@dataclass
class Unit: 
    pass


@dataclass
class For: 
    var       : Var
    body      : 'Expr'
    var_type  : IndexSetType = UnspecifiedType() # Put last because its optional in the constructor


@dataclass
class Index: 
    array: 'Expr'
    index: 'Expr'


@dataclass
class Function: 
    param     : Var
    body      : 'Expr'
    param_type: 'DexType' = UnspecifiedType() 

@dataclass
class View: 
    index_set: 'Index_Set'
    body     : 'Expr'


@dataclass
class RefSlice: 
    ref  : Var
    index: 'Expr'

@dataclass
class runAccum: 
    # Note that function's parameter must be a reference to a VectorSpace
    update_fun: Function


@dataclass
class PlusEquals: 
    dest: Var
    src : 'Expr'


# Expressions
@dataclass
class Let: 
    var  : Var
    value: 'Expr'
    body : 'Expr'

@dataclass
class Application: 
    func: Function
    arg : 'Expr'


@dataclass
class Fst: 
    pair: Pair


@dataclass
class Snd: 
    pair: Pair


@dataclass
class Add: 
    left : 'Expr'
    right: 'Expr'

@dataclass
class Multiply: 
    left : 'Expr'
    right: 'Expr'


# Contexts
@dataclass
class Hole: 
    pass

@dataclass
class LetContext: 
    var     : Var
    var_type: 'DexType'
    expr    : 'Expr'
    context : 'Context'

# Effects
@dataclass
class Pure: 
    pass

@dataclass
class StateEffect: 
    state_type: 'DexType'
    effect    : 'Effect'

@dataclass
class AccumEffect: 
    accum_type: 'DexType'
    effect    : 'Effect'


# Type aliases

Value   = Union[Var, Pair]
Expr    = Union[Value, Let, Application, Index, Fst, Snd, RefSlice, runAccum, Add, Multiply]
Context = Union[Hole, LetContext]
Effect  = Union[Pure, StateEffect, AccumEffect]


Index_Set         = Union[Unit, Fin, Pair]
Vector_Space_Type = Union[Float, Pair, IndexSetType]


if __name__ == "__main__": 
    n       = 100
    sum     = Var("sum")
    x       = Var("x")
    i       = Var("i")
    total   = Var("total")
    program = Let(sum, Function(x, ArrayType(Fin(n), FloatType()),
                                Snd(runAccum(Function(total,
                                For(i, PlusEquals(total, Index(x, i))))))), Unit())
    
    print(program)