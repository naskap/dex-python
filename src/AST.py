from typing import Union, Tuple, List
from dataclasses import dataclass

# ----------------- Types ---------------------


# Point of confusion: type(Float(0)) = Float, but we also have FloatType -- why?
# Answer: Consider type(Let(Var("x"), Float(0), Var("x"))) =  Let
#         But this should semantically be a float. Therefore our type checking and inference system will need 
#         to conclude this is of type FloatType


class DexType: 
    pass


@dataclass
class ArrayType(DexType):
    # Syntax doesn't restrict tau1 to be an index set but type checking does
    index_set : 'Index_Set' # tau1, Value-dependent type
    elmt_type : DexType     # tau2

# Type for a type annotation not filled in
@dataclass
class UnspecifiedType(DexType): 
    pass

@dataclass
class FloatType(DexType): 
    pass

@dataclass
class IntType(DexType): 
    pass

@dataclass
class UnitType(DexType): 
    pass

@dataclass
class FunctionType(DexType): 
    tau1: DexType
    tau2: DexType
    effect : 'Effect'

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
class Int: 
    value: int


# Has type Int -> ArrayType
@dataclass
class Fin: 
    end: Int


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
    var_type  : 'Index_Set' = UnspecifiedType() # Put last because its optional in the constructor


@dataclass
class Index: 
    array: 'Value'
    index: 'Value'


@dataclass
class Function: 
    var     : Var
    body      : 'Expr'
    param_type: 'DexType' = UnspecifiedType() 

@dataclass
class View: 
    var       : Var
    body      : 'Expr'
    var_type  : 'Index_Set' = UnspecifiedType() # Put last because its optional in the constructor


@dataclass
class RefSlice: 
    ref  : Var
    index: 'Value'

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
    var_type : 'DexType' = UnspecifiedType()

@dataclass
class Application: 
    func: Function
    arg : 'Value'


@dataclass
class Fst: 
    pair: 'Value'


@dataclass
class Snd: 
    pair: 'Value'


@dataclass
class Add: 
    left : 'Value'
    right: 'Value'

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
    var_type: DexType
    expr    : 'Expr'
    context : 'Context'

# Effects

class Effect:
    pass

@dataclass
class Pure(Effect): 
    pass


@dataclass
class AccumEffect(Effect): 
    accum_type: DexType
    effect    : Effect


# Type aliases

Value   = Union[Var, Float, Int, Fin, Function, View, Pair]
Expr    = Union[Value, Let, Application, Index, Fst, Snd, RefSlice, runAccum, Add, Multiply]
Context = Union[Hole, LetContext]


Index_Set         = Union[Unit, Fin, Pair]
Vector_Space_Type = Union[Float, Pair, ArrayType]


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