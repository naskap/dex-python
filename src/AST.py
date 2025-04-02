from dataclasses import dataclass
from typing import Union, Tuple, List

# Values (including types)
@dataclass
class Var:
    name: str

@dataclass
class Unspecified:
    pass

@dataclass
class Unit:
    pass

@dataclass
class Float:
    value : float

@dataclass
class Fin:
    end: int
    
    
@dataclass
class Pair:
    left: 'Value'
    right: 'Value'
    
@dataclass
class ArrayType:
    index_set : 'Index_Set_Type'
    elmt_type : 'Type'

Index_Set_Type = Union[Unit, Fin, Pair]
Vector_Space_Type = Union[Float, Pair, ArrayType]

@dataclass
class For:
    var : Var
    body : 'Expr'
    array_type : ArrayType = Unspecified()

@dataclass
class Index:
    array : Union[For, Var]
    index : 'Expr'


@dataclass
class Function:
    param: Var
    body: 'Expr'
    param_type: 'Type' = Unspecified()

@dataclass
class View:
    index_set : Fin
    body: For

@dataclass
class runAccum:
    # Note that function parameter must be a reference to a VectorSpace
    update_fun : Function


# Expressions
@dataclass
class Let:
    var: Var
    value: 'Expr'
    body: 'Expr'

@dataclass
class Application:
    func: Function
    arg: 'Expr'


@dataclass
class Fst:
    pair: Pair


@dataclass
class Snd:
    pair: Pair


@dataclass 
class Ref:
    ref_type : 'Type'


@dataclass
class RefSlice:
    ref: Ref
    index: 'Expr'


@dataclass
class RunAccum:
    accum: 'Expr'
    body: 'Expr'

@dataclass
class PlusEquals:
    dest : Ref
    src : 'Expr'


@dataclass
class Add:
    left: 'Expr'
    right: 'Expr'

@dataclass
class Multiply:
    left: 'Expr'
    right: 'Expr'


# Contexts
@dataclass
class Hole:
    pass

@dataclass
class LetContext:
    var: Var
    var_type: 'Type'
    expr: 'Expr'
    context: 'Context'

# Effects
@dataclass
class Pure:
    pass

@dataclass
class StateEffect:
    state_type: 'Type'
    effect: 'Effect'

@dataclass
class AccumEffect:
    accum_type: 'Type'
    effect: 'Effect'



# Type aliases
Type = Union[Var, Fin, ArrayType]
Value = Union[Var, Pair]
Expr = Union[Value, Let, Application, Index, Fst, Snd, RefSlice, RunAccum, Add, Multiply]
Context = Union[Hole, LetContext]
Effect = Union[Pure, StateEffect, AccumEffect]

if __name__ == "__main__":
    n=100
    sum = Var("sum")
    x = Var("x")
    i = Var("i")
    total = Var("total")
    program = Let(sum, Function(x, ArrayType(Fin(n), Float),
                                Snd(runAccum(Function(total,
                                For(i, PlusEquals(total, Index(x, i))))))), Unit())
    
    print(program)


