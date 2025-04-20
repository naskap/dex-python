from typing import Union, Tuple, List
from dataclasses import dataclass, field
from abc import ABC

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

class DexType(ABC): 
    pass


@dataclass
class ArrayType(DexType):
    # Syntax doesn't restrict tau1 to be an index set but type checking does
    index_set : 'Index_Set'  # tau1
    elmt_type : Union[DexType, 'Var'] # tau2
    
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

# Note: Paper doesn't distinguish between unit and unittype, pair and pairtype
# I think our version is more clear

@dataclass
class UnitType(DexType): 
    def __str__(self):
        return "Unit"


@dataclass
class FunctionType(DexType): 
    tau1: Union[DexType, 'Var']
    tau2: Union[DexType, 'Var']
    effect : 'Effect'
    def __str__(self):
        return f"{self.tau1} => {self.effect} {self.tau2}"


@dataclass
class PairType(DexType): 
    tau1: Union[DexType, 'Var']
    tau2: Union[DexType, 'Var']
    def __str__(self):
        return f"{self.tau1} x {self.tau2})"

@dataclass
class RefType(DexType): 
    tau1: Union[DexType, 'Var']
    tau2: Union[DexType, 'Var']
    def __str__(self):
        return f"Ref({self.tau1}, {self.tau2})"

# In the paper Fin has type Int -> Type
# Our version modifies this slightly so that it is always applied to something
@dataclass
class FinType(DexType): 
    end: Union['Int', 'Var']
    def __str__(self):
        return f"Fin({self.end})"


# Needed for polymorphic functions
# For example the polymorphic identity function is: \t:Type.\x:t.x
# In class we had special functions that took a type as a parameter: Omega t.\x:t.x
#       and these would have a universally quantified type: forall t. t->t
# Dex treats polymorphic functions as regular functions
@dataclass
class TypeType(DexType):
    def __str__(self):
        return f"Type"

# ------------------ Values  ------------------

@dataclass
class Var: 
    name: str
    def __str__(self):
        return self.name
    
    def __hash__(self):
        return self.name.__hash__()

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
    init_val : Float | Int = field(default_factory=lambda: Int(0))

    def __str__(self):
        return f"runAccum {self.init_val} {self.update_fun}"

@dataclass
class PlusEquals: 
    dest: Var
    src : 'Expr'
    
    def __str__(self):
        return f"{self.dest} += {self.src}"


# Expressions
@dataclass
class Let: 
    var  : Var | Pair
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
    def __str__(self):
        return "•"

@dataclass
class LetContext: 
    var     : Var
    var_type: DexType
    expr    : 'Expr'
    context : 'Context'
    def __str__(self):
        if isinstance(self.var_type, UnspecifiedType):
            return f"let {self.var} = {self.expr} in\n{indent(self.context)}"
        return f"let {self.var}: {self.var_type} = {self.expr} in\n{indent(self.context)}"

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


Value   = Union[Var, Float, Int, Function, View, Pair, Unit, DexType]
Expr    = Union[Value, Let, Application, Index, For, Fst, Snd, RefSlice, runAccum, PlusEquals, Add, Multiply]
Context = Union[Hole, LetContext]


Index_Set         = Union[UnitType, FinType, PairType]
Vector_Space_Type = Union[Float, Pair, ArrayType]


if __name__ == "__main__": 
    n       = 100
    sum     = Var("sum")
    x       = Var("x")
    i       = Var("i")
    total   = Var("total")
    program = Let(sum, Function(x,
                                Snd(runAccum(Function(total,
                                For(i, PlusEquals(total, Index(x, i)))))), ArrayType(FinType(Int(n)), FloatType())), Unit())
    
    print(program)