from typing import Union, Tuple, List
from dataclasses import dataclass, field

# ----------------- Helper ------------------

def indent(text, prefix="  "):
    """Indents every line of `text` with `prefix`."""
    return "\n".join(prefix + line if line else line 
                                   for line in str(text).splitlines())


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
    
    def __str__(self):
        return f"{self.index_set} => {self.elmt_type}"

# Type for a type annotation not filled in
@dataclass
class UnspecifiedType(DexType): 
    def __str__(self):
        return ""


@dataclass
class FloatType(DexType): 
    def __str__(self):
        return "Float"


@dataclass
class IntType(DexType): 
    def __str__(self):
        return "Int"


@dataclass
class UnitType(DexType): 
    def __str__(self):
        return "Unit"


@dataclass
class FunctionType(DexType): 
    tau1: DexType
    tau2: DexType
    effect : 'Effect'
    def __str__(self):
        return f"{self.tau1} => {self.effect} {self.tau2}"


@dataclass
class PairType(DexType): 
    tau1: DexType
    tau2: DexType
    def __str__(self):
        return f"{self.tau1} x {self.tau2})"

@dataclass
class RefType(DexType): 
    tau1: DexType
    tau2: DexType
    def __str__(self):
        return f"Ref({self.tau1}, {self.tau2})"



# ------------------ Values  ------------------

@dataclass
class Var: 
    name: str
    def __str__(self):
        return self.name

@dataclass
class Float: 
    value: float
    def __str__(self):
        return str(self.value)

@dataclass
class Int: 
    value: int
    def __str__(self):
        return str(self.value)


# Has type Int -> ArrayType
@dataclass
class Fin: 
    end: Int
    def __str__(self):
        return f"Fin({self.end})"


@dataclass
class Pair: 
    left : 'Value' # According to syntax these can't be expressions
    right: 'Value'
    
    def __str__(self):
        return f"({self.left}, {self.right})"


@dataclass
class Unit: 
    
    def __str__(self):
        return ""


@dataclass
class For: 
    var       : Var
    body      : 'Expr'
    var_type  : 'Index_Set' = field(default_factory=UnspecifiedType)  # Put last because its optional in the constructor
    
    def __str__(self):
        if isinstance(self.var_type, UnspecifiedType):
            return f"for {self.var}. {self.body}"  # Omit param_type if it's the default
        return f"for {self.var}: {self.var_type}. {self.body}"


@dataclass
class Index: 
    array: 'Value'
    index: 'Value'
    
    def __str__(self):
        return f"{self.array}.{self.index}"


@dataclass
class Function: 
    var     : Var
    body      : 'Expr'
    param_type: 'DexType' = field(default_factory=UnspecifiedType) 
    
    def __str__(self):
        if isinstance(self.param_type, UnspecifiedType):
            return f"\\{self.var}.\n{indent(self.body)}"  # Omit param_type if it's the default
        return f"\\{self.var}: {self.param_type}.\n{indent(self.body)}"

@dataclass
class View: 
    var       : Var
    body      : 'Expr'
    var_type  : 'Index_Set' = field(default_factory=UnspecifiedType) # Put last because its optional in the constructor
    
    def __str__(self):
        if isinstance(self.var_type, UnspecifiedType):
            return f"view {self.var}. {self.body}"
        return f"view {self.var}: {self.var_type}. {self.body}"


@dataclass
class RefSlice: 
    ref  : Var
    index: 'Value'
    
    def __str__(self):
        return f"{self.ref} ! {self.index}"

@dataclass
class runAccum: 
    # Note that function's parameter must be a reference to a VectorSpace
    update_fun: Function

    def __str__(self):
        return f"runAccum {self.update_fun}"

@dataclass
class PlusEquals: 
    dest: Var
    src : 'Expr'
    
    def __str__(self):
        return f"{self.dest} += {self.src}"


# Expressions
@dataclass
class Let: 
    var  : Var
    value: 'Expr'
    body : 'Expr'
    var_type : 'DexType' = field(default_factory=UnspecifiedType)
    
    def __str__(self):
        if isinstance(self.var_type, UnspecifiedType):
            return f"{self.var} = {self.value}\n{indent(self.body)}"
        return f"{self.var}: {self.var_type} = {self.value}\n{indent(self.body)}"

@dataclass
class Application: 
    func: Function
    arg : 'Value'
    
    def __str__(self):
        return f"{self.func} {self.arg}"


@dataclass
class Fst: 
    pair: 'Value'
    
    def __str__(self):
        return f"fst $ {self.pair}"


@dataclass
class Snd: 
    pair: 'Value'
    
    def __str__(self):
        return f"snd $ {self.pair}"


@dataclass
class Add: 
    left : 'Value'
    right: 'Value'
    
    def __str__(self):
        return f"{self.left} + {self.right}"

@dataclass
class Multiply: 
    left : 'Expr'
    right: 'Expr'
    
    def __str__(self):
        return f"{self.left} * {self.right}"


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