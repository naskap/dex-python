import itertools
from typing import Dict
from AST import *
from dataclasses import dataclass


@dataclass
class TypeVar(DexType):
    id: int
    def __str__(self):
        return f"t{self.id}"
    
    def __hash__(self):
        return hash(self.id)
    


Substitution = Dict[TypeVar, DexType]
Env = Dict[str, DexType]

class TypeInfer:
    
    def __init__(self):
        self.subst: Substitution = {}
        self.env: Env = {}
        self._typevar_counter = itertools.count()  # each instance gets its own counter
        
    def fresh_typevar(self) -> TypeVar:
        return TypeVar(next(self._typevar_counter))
    
    def include_var(self, var: Var):    
        if var.name in self.env:
            raise TypeError(f"Variable {var.name} already exists in environment")
        self.env[var.name] = self.fresh_typevar()
    
    # check if a type variable tv occurs somewhere in type t
    def occurs_check(self, tv: TypeVar, t: DexType) -> bool:
        if isinstance(t, TypeVar):
            return t.id == tv.id
        elif isinstance(t, (FunctionType, PairType, RefType)):
            return self.occurs_check(tv, t.tau1) or self.occurs_check(tv, t.tau2)
        elif isinstance(t, ArrayType):
            return self.occurs_check(tv, t.elmt_type)
        # FloatType, IntType, UnitType do not contain type variables
        return False

    # Given a substitution from type variables to concrete type,
    # recursively apply the substitution of type variables occuring in t
    def apply_subst(self, t: DexType) -> DexType:
        if isinstance(t, TypeVar):
            return self.apply_subst(self.subst[t]) if t.id in self.subst else t
        elif isinstance(t, FunctionType):
            return FunctionType(self.apply_subst(t.tau1), self.apply_subst(t.tau2), t.effect)
        elif isinstance(t, PairType):
            return PairType(self.apply_subst(t.tau1), self.apply_subst(t.tau2))
        elif isinstance(t, RefType):
            return RefType(self.apply_subst(t.tau1), self.apply_subst(t.tau2))
        elif isinstance(t, ArrayType):
            return ArrayType(t.index_set, self.apply_subst(t.elmt_type))
        # FloatType, IntType, UnitType do not contain type variables
        return t

    # Unify two types t1 and t2, returning a substitution that makes them equal
    def unify(self, t1: DexType, t2: DexType):
        t1 = self.apply_subst(t1)
        t2 = self.apply_subst(t2)
        
        # print(f"Unifying {t1} with {t2}")

        if isinstance(t1, TypeVar):
            if t1 != t2:
                if self.occurs_check(t1, t2):
                    raise TypeError(f"Occurs check failed: {t1} in {t2}")
                self.subst[t1] = t2
        elif isinstance(t2, TypeVar):
            self.unify(t2, t1)
        # the type() would return the actual type of of the object (rather than the parent class DexTyp) 
        elif type(t1) != type(t2):
            raise TypeError(f"Cannot unify {t1} with {t2}")
        elif isinstance(t1, FunctionType):
            self.unify(t1.tau1, t2.tau1)
            self.unify(t1.tau2, t2.tau2)
        elif isinstance(t1, PairType):
            self.unify(t1.tau1, t2.tau1)
            self.unify(t1.tau2, t2.tau2)
        elif isinstance(t1, RefType):
            self.unify(t1.tau1, t2.tau1)
            self.unify(t1.tau2, t2.tau2)
        elif isinstance(t1, ArrayType):
            self.unify(t1.elmt_type, t2.elmt_type)
        elif isinstance(t1, FloatType) or isinstance(t1, IntType) or isinstance(t1, UnitType):
            pass
        elif isinstance(t1, FinType):
           if t1.size != t2.size:
                raise TypeError(f"Cannot unify different Fin sizes: {t1} vs {t2}")
        else:
            raise TypeError(f"Unhandled unification case: {t1} and {t2}")
        

    def infer(self, expr: Expr) -> DexType:
        # print(f"Inferring type for {expr}")
        if isinstance(expr, Value):
            if isinstance(expr, Var):
                if expr.name in self.env:
                    return self.env[expr.name]
                raise TypeError(f"Unbound variable {expr.name}")
            elif isinstance(expr, Float):
                return FloatType()
            elif isinstance(expr, Int):
                return IntType()
            elif isinstance(expr, Fin):
                if isinstance(expr.end, Int):
                    return FinType(expr.end.value)
                raise TypeError(f"Fin end must be an Int, got {expr.end}")
            elif isinstance(expr, Function):
                if isinstance(expr.param_type, UnspecifiedType):
                    tv = self.fresh_typevar()
                    self.env[expr.var.name] = tv
                else:
                    self.env[expr.var.name] = expr.param_type
                    tv = expr.param_type
                t_body = self.infer(expr.body)
                if isinstance(tv, TypeVar):
                    if tv in self.subst:
                        tv = self.apply_subst(tv)
                return FunctionType(tv, t_body, Pure())
            elif isinstance(expr, View):
                if isinstance(expr.var_type, FinType):
                    self.env[expr.var.name] = expr.var_type
                    t_body = self.infer(expr.body)
                    return ArrayType(expr.var_type, t_body)
                raise TypeError(f"View variable type must be FinType, got {expr.var_type}")
            elif isinstance(expr, Pair):
                t1 = self.infer(expr.left)
                t2 = self.infer(expr.right)
                return PairType(t1, t2)
            elif isinstance(expr, Unit):
                return UnitType()
        else:
            if isinstance(expr, Let):
                t1 = self.infer(expr.value)
                self.env[expr.var.name] = t1
                t2 = self.infer(expr.body)
                return t2
            elif isinstance(expr, Application):
                tf = self.infer(expr.func)
                ta = self.infer(expr.arg)
                tr = self.fresh_typevar()
                self.unify(tf, FunctionType(ta, tr, Pure()))
                return tr
            elif isinstance(expr, Index):
                t1 = self.infer(expr.array)
                t2 = self.infer(expr.index)
                if isinstance(t1, ArrayType):
                    self.unify(t2, t1.index_set)
                    return t1.elmt_type
                raise TypeError(f"Indexing into non-array type {t1}")
            elif isinstance(expr, For):
                if isinstance(expr.var_type, UnspecifiedType):
                    ty = self.fresh_typevar()
                    self.env[expr.var.name] = tv
                    t_body = self.infer(expr.body)
                    return ArrayType(ty, t_body)
                elif isinstance(expr.var_type, FinType):
                    self.env[expr.var.name] = expr.var_type
                    t_body = self.infer(expr.body)
                    return ArrayType(expr.var_type, t_body)
                raise TypeError(f"For variable type must be FinType, got {expr.var_type}")
            elif isinstance(expr, Fst):
                tp = self.infer(expr.pair)
                t1 = self.fresh_typevar()
                t2 = self.fresh_typevar()
                self.unify(tp, PairType(t1, t2))
                return t1
            elif isinstance(expr, Snd):
                tp = self.infer(expr.pair)
                t1 = self.fresh_typevar()
                t2 = self.fresh_typevar()
                self.unify(tp, PairType(t1, t2))
            elif isinstance(expr, RefSlice):
                pass
            elif isinstance(expr, runAccum):
                pass
            elif isinstance(expr, PlusEquals):
                pass
            elif isinstance(expr, Add):
                t1 = self.infer(expr.left)
                t2 = self.infer(expr.right)
                self.unify(t1, FloatType())
                self.unify(t2, FloatType())
                return FloatType()
            elif isinstance(expr, Multiply):
                pass
            else:
                raise NotImplementedError(f"Inference not implemented for {type(expr)}")

if __name__ == "__main__":
    type_infer = TypeInfer()
    x = Var("x")
    type_infer.include_var(x)
    expr = Let(
        x,
        Add(x, Float(1.0)),
        Unit()
    )
    print(f"Expression:\n{expr}")
    ty = type_infer.infer(expr)
    subst = type_infer.subst
    env = type_infer.env
    print(f"Inferred type: {ty}; Substitution: {subst}; Environment: {env};")
    
    print()
    # ----- 2. Function with Explicitly Typed Parameter -----
    type_infer = TypeInfer()
    x = Var("x")
    body = Add(x, Float(2.0))  # x + 2.0
    f = Function(x, body, FloatType())  # fun (x: Float) => x + 2.0
    print(f"Typed function:\n{f}")
    ty = type_infer.infer(f)
    print(f"Inferred type: {ty}; Substitution: {type_infer.subst}; Environment: {type_infer.env}\n")

    print()
    # ----- 3. Function with Untyped Parameter -----
    type_infer = TypeInfer()
    x = Var("x")
    body = Add(x, Float(2.0))  # x + 2.0
    f = Function(x, body)  # fun x => x + 2.0
    print(f"Untyped function:\n{f}")
    ty = type_infer.infer(f)
    print(f"Inferred type: {ty}; Substitution: {type_infer.subst}; Environment: {type_infer.env}\n")

    print()
    # ----- 4. Function Application -----
    type_infer = TypeInfer()
    x = Var("x")
    body = Add(x, Float(3.0))
    f = Function(x, body)
    app_expr = Application(f, Float(1.0))  # (fun x => x + 3.0)(1.0)
    print(f"Function application:\n{app_expr}")
    ty = type_infer.infer(app_expr)
    print(f"Inferred type: {ty}; Substitution: {type_infer.subst}; Environment: {type_infer.env}\n")

    # ------- 5. Fin -----
    type_infer = TypeInfer()
    expr = Fin(Int(5))
    ty = type_infer.infer(expr)
    print(f"Inferred type: {ty}")

    # ------- 6. View -----
    type_infer = TypeInfer()
    view_expr = View(
        var=Var("i"),
        var_type=FinType(3),
        body=Float(0.5)  # or some Expr using i
    )
    ty = type_infer.infer(view_expr)
    print(f"Inferred type: {ty}")

    # ------- 7. Index -----
    type_infer = TypeInfer()
    type_infer.env["x"] = ArrayType(FinType(3), FloatType())  # x: Fin(3) => Float
    type_infer.env["i"] = FinType(3)                          # i: Fin(3)
    expr = Index(array=Var("x"), index=Var("i"))
    ty = type_infer.infer(expr)
    print(f"Type of x.i: {ty}")