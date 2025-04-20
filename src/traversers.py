from AST import *

class ExprMutator:
    """Base class for expression mutators that can transform the AST in various ways"""
    def mutate(self, e : Expr | DexType) -> Expr | DexType:
        """Dispatch to the appropriate method based on the expression type"""
        if isinstance(e, Var):
            return self.mutate_var(e)
        elif isinstance(e, Application):
            return self.mutate_application(e)
        elif isinstance(e, Function):
            return self.mutate_function(e)
        elif isinstance(e, View):
            return self.mutate_view(e)
        elif isinstance(e, Pair):
            return self.mutate_pair(e)
        elif isinstance(e, Let):
            return self.mutate_let(e)
        elif isinstance(e, Index):
            return self.mutate_index(e)
        elif isinstance(e, For):
            return self.mutate_for(e)
        elif isinstance(e, Fst):
            return self.mutate_fst(e)
        elif isinstance(e, Snd):
            return self.mutate_snd(e)
        elif isinstance(e, RefSlice):
            return self.mutate_refslice(e)
        elif isinstance(e, runAccum):
            return self.mutate_runaccum(e)
        elif isinstance(e, PlusEquals):
            return self.mutate_plusequals(e)
        elif isinstance(e, Add):
            return self.mutate_add(e)
        elif isinstance(e, Multiply):
            return self.mutate_multiply(e)
        elif isinstance(e, Float):
            return self.mutate_float(e)
        elif isinstance(e, Int):
            return self.mutate_int(e)
        elif isinstance(e, ArrayType):
            return self.mutate_arraytype(e)
        elif isinstance(e, FunctionType):
            return self.mutate_functiontype(e)
        elif isinstance(e, UnspecifiedType):
            return self.mutate_unspecifiedtype(e)
        elif isinstance(e, FloatType):
            return self.mutate_floattype(e)
        elif isinstance(e, IntType):
            return self.mutate_inttype(e)
        elif isinstance(e, UnitType):
            return self.mutate_unittype(e)
        elif isinstance(e, PairType):
            return self.mutate_pairtype(e)
        elif isinstance(e, RefType):
            return self.mutate_reftype(e)
        elif isinstance(e, FinType):
            return self.mutate_fintype(e)
        elif isinstance(e, TypeType):
            return self.mutate_typetype(e)
        
        assert False, "Expression type {} not handled".format(type(e))

    # Default implementation for each type - identity transformation
    def mutate_var(self, e: Var) -> Var:
        return e
    
    def mutate_application(self, e: Application) -> Application:
        return Application(self.mutate(e.func), self.mutate(e.arg))
    
    def mutate_function(self, e: Function) -> Function:
        return Function(e.var, self.mutate(e.body), self.mutate(e.param_type))
    
    def mutate_fintype(self, e: FinType) -> FinType:
        return FinType(self.mutate(e.end))
    
    def mutate_view(self, e: View) -> View:
        return View(self.mutate(e.var), self.mutate(e.body), self.mutate(e.var_type))
    
    def mutate_pair(self, e: Pair) -> Pair:
        return Pair(self.mutate(e.left), self.mutate(e.right))
    
    def mutate_let(self, e: Let) -> Let:
        return Let(e.var, self.mutate(e.value), self.mutate(e.body), self.mutate(e.var_type))
    
    def mutate_index(self, e: Index) -> Index:
        return Index(self.mutate(e.array), self.mutate(e.index))
    
    def mutate_for(self, e: For) -> For:
        return For(e.var, self.mutate(e.body), self.mutate(e.var_type))
    
    def mutate_fst(self, e: Fst) -> Fst:
        return Fst(self.mutate(e.pair))
    
    def mutate_snd(self, e: Snd) -> Snd:
        return Snd(self.mutate(e.pair))
    
    def mutate_refslice(self, e: RefSlice) -> RefSlice:
        return RefSlice(self.mutate(e.ref), self.mutate(e.index))
    
    def mutate_runaccum(self, e: runAccum) -> runAccum:
        return runAccum(self.mutate(e.update_fun))
    
    def mutate_plusequals(self, e: PlusEquals) -> PlusEquals:
        return PlusEquals(self.mutate(e.dest), self.mutate(e.src))
    
    def mutate_add(self, e: Add) -> Add:
        return Add(self.mutate(e.left), self.mutate(e.right))
    
    def mutate_multiply(self, e: Multiply) -> Multiply:
        return Multiply(self.mutate(e.left), self.mutate(e.right))
    
    def mutate_arraytype(self, e: ArrayType) -> ArrayType:
        return ArrayType(self.mutate(e.index_set), self.mutate(e.elmt_type))
    
    def mutate_functiontype(self, e: FunctionType) -> FunctionType:
        return FunctionType(self.mutate(e.tau1), self.mutate(e.tau2), self.mutate(e.effect))
    
    def mutate_float(self, e: Float) -> Float:
        return e
     
    def mutate_int(self, e: Int) -> Int:
        return e
    
    def mutate_unspecifiedtype(self, e : UnspecifiedType) -> UnspecifiedType:
        return e
    
    def mutate_floattype(self, e : FloatType) -> FloatType:
        return e 
    
    def mutate_inttype(self, e: IntType) -> IntType:
        return e
    
    def mutate_unittype(self, e: UnitType) -> UnitType:
        return e
    
    def mutate_pairtype(self, e: PairType) -> PairType:
        return PairType(self.mutate(e.tau1), self.mutate(e.tau2))
    
    def mutate_reftype(self, e: RefType) -> RefType:
        return RefType(self.mutate(e.tau1), self.mutate(e.tau2))
    
    def mutate_typetype(self, e: TypeType) -> RefType:
        return e

class ExprVisitor:
    """Base class for expression visitors that can traverse the AST without transforming it"""
    def visit(self, e: Expr | DexType) -> None:
        """Dispatch to the appropriate method based on the expression type"""
        if isinstance(e, Var):
            self.visit_var(e)
        elif isinstance(e, Application):
            self.visit_application(e)
        elif isinstance(e, Function):
            self.visit_function(e)
        elif isinstance(e, View):
            self.visit_view(e)
        elif isinstance(e, Pair):
            self.visit_pair(e)
        elif isinstance(e, Let):
            self.visit_let(e)
        elif isinstance(e, Index):
            self.visit_index(e)
        elif isinstance(e, For):
            self.visit_for(e)
        elif isinstance(e, Fst):
            self.visit_fst(e)
        elif isinstance(e, Snd):
            self.visit_snd(e)
        elif isinstance(e, RefSlice):
            self.visit_refslice(e)
        elif isinstance(e, runAccum):
            self.visit_runaccum(e)
        elif isinstance(e, PlusEquals):
            self.visit_plusequals(e)
        elif isinstance(e, Add):
            self.visit_add(e)
        elif isinstance(e, Multiply):
            self.visit_multiply(e)
        elif isinstance(e, Float):
            self.visit_float(e)
        elif isinstance(e, Int):
            self.visit_int(e)
        elif isinstance(e, ArrayType):
            self.visit_arraytype(e)
        elif isinstance(e, FunctionType):
            self.visit_functiontype(e)
        elif isinstance(e, UnspecifiedType):
            self.visit_unspecifiedtype(e)
        elif isinstance(e, FloatType):
            self.visit_floattype(e)
        elif isinstance(e, IntType):
            self.visit_inttype(e)
        elif isinstance(e, UnitType):
            self.visit_unittype(e)
        elif isinstance(e, PairType):
            self.visit_pairtype(e)
        elif isinstance(e, RefType):
            self.visit_reftype(e)
        elif isinstance(e, FinType):
            self.visit_fintype(e)
        elif isinstance(e, TypeType):
            self.visit_typetype(e)
        else:
            assert False, f"Expression type {type(e)} not handled"

    # Default implementation for each type - does nothing
    def visit_var(self, e: Var) -> None:
        pass
    
    def visit_application(self, e: Application) -> None:
        self.visit(e.func)
        self.visit(e.arg)
    
    def visit_function(self, e: Function) -> None:
        self.visit(e.body)
        self.visit(e.param_type)
    
    def visit_fintype(self, e: FinType) -> None:
        self.visit(e.end)
    
    def visit_view(self, e: View) -> None:
        self.visit(e.body)
        self.visit(e.var_type)
    
    def visit_pair(self, e: Pair) -> None:
        self.visit(e.left)
        self.visit(e.right)
    
    def visit_let(self, e: Let) -> None:
        self.visit(e.value)
        self.visit(e.body)
        self.visit(e.var_type)
    
    def visit_index(self, e: Index) -> None:
        self.visit(e.array)
        self.visit(e.index)
    
    def visit_for(self, e: For) -> None:
        self.visit(e.body)
        self.visit(e.var_type)
    
    def visit_fst(self, e: Fst) -> None:
        self.visit(e.pair)
    
    def visit_snd(self, e: Snd) -> None:
        self.visit(e.pair)
    
    def visit_refslice(self, e: RefSlice) -> None:
        self.visit(e.ref)
        self.visit(e.index)
    
    def visit_runaccum(self, e: runAccum) -> None:
        self.visit(e.update_fun)
    
    def visit_plusequals(self, e: PlusEquals) -> None:
        self.visit(e.dest)
        self.visit(e.src)
    
    def visit_add(self, e: Add) -> None:
        self.visit(e.left)
        self.visit(e.right)
    
    def visit_multiply(self, e: Multiply) -> None:
        self.visit(e.left)
        self.visit(e.right)
    
    def visit_float(self, e: Float) -> None:
        pass
     
    def visit_int(self, e: Int) -> None:
        pass
    
    def visit_arraytype(self, e: ArrayType) -> None:
        self.visit(e.index_set)
        self.visit(e.elmt_type)
    
    def visit_functiontype(self, e: FunctionType) -> None:
        self.visit(e.tau1)
        self.visit(e.tau2)
        self.visit(e.effect)
    
    def visit_unspecifiedtype(self, e: UnspecifiedType) -> None:
        pass
    
    def visit_floattype(self, e: FloatType) -> None:
        pass
    
    def visit_inttype(self, e: IntType) -> None:
        pass
    
    def visit_unittype(self, e: UnitType) -> None:
        pass

    def visit_typetype(self, e: TypeType) -> None:
        pass
    
    def visit_pairtype(self, e: PairType) -> None:
        self.visit(e.tau1)
        self.visit(e.tau2)
    
    def visit_reftype(self, e: RefType) -> None:
        self.visit(e.tau1)
        self.visit(e.tau2)

