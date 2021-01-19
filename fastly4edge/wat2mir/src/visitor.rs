use crate::dto;

use walrus::*;
use std::{unimplemented};
use walrus::ir::*;
use std::collections::HashMap;


pub enum BLOCKTPE {
    LOOP,
    BLOCK,
    //IF
}

pub struct MIRVisitor<'a> {
    pub min_local: i32,
    pub module: &'a walrus::Module,
    pub local_function: Option<&'a walrus::LocalFunction>,
    pub block_hash: HashMap<usize, BLOCKTPE>,
    pub ret: String,
    pub block_depth: Vec<(InstrSeqId, i32)>,
    pub depth: i32,
    pub config: dto::Wat2MirConfig
}

impl MIRVisitor<'_>{

    fn get_depth(&mut self, instrId: InstrSeqId) -> i32{
        self.block_depth.len() as i32 - self.block_depth.iter()
        .find(|(r, _)| r == &instrId).expect("Error in DFS traveling").1
    }

    fn emit_mem_kind_store(&mut self, kind: StoreKind){
        match kind {
            StoreKind::I32 { atomic} => self.ret.push_str(&format!("i32.store")),
            StoreKind::I64 { atomic} => self.ret.push_str(&format!("i64.store")),
            StoreKind::I32_16 { atomic} => self.ret.push_str(&format!("i32.store16")),
            StoreKind::I32_8 { atomic} => self.ret.push_str(&format!("i32.store8")),
            StoreKind::I64_8 { atomic} => self.ret.push_str(&format!("i64.store8")),
            StoreKind::I64_16 { atomic} => self.ret.push_str(&format!("i64.store16")),
            StoreKind::I64_32 { atomic} => self.ret.push_str(&format!("i64.store32")),
            StoreKind::F32 => self.ret.push_str(&format!("f32.store")),
            StoreKind::F64  => self.ret.push_str(&format!("f64.store")),
            _ => unimplemented!("ERROR {:?}", kind)
        }
    }

    fn get_sign_tail(&mut self,kind: ExtendedLoad){
        match kind {
            ExtendedLoad::ZeroExtend => self.ret.push_str(&"u"),
            ExtendedLoad::SignExtend => self.ret.push_str(&"s"),
            _ => unimplemented!("Extended load type {:?}", kind)
        }
    }

    fn emit_mem_kind_load(&mut self, kind: LoadKind){
        match kind {
            LoadKind::I32 {atomic} => self.ret.push_str(&format!("i32.load")),
            LoadKind::I32_8 { kind} => {
                self.ret.push_str(&format!("i32.load8_"));
                self.get_sign_tail(kind)
            },
            LoadKind::I64 { atomic} => self.ret.push_str(&format!("i64.load")),
            LoadKind::F64 => self.ret.push_str(&format!("f64.load")),
            LoadKind::I64_32 { kind } => 
            {
                self.ret.push_str(&format!("i64.load32_"));
                self.get_sign_tail(kind)
            },
            _ => panic!("ERROR {:?}", kind)
        }
    }

    fn emit_mem_arg(&mut self, arg: MemArg){

        match arg.offset {
            0 => (),
            _ => self.ret.push_str(&format!(" offset={}", arg.offset))
        }
        match arg.align {
            // TODO check
            1 => (),
            2 => (),
            4 => (),
            8 => (),
            16 => (),
            _ => self.ret.push_str(&format!(" align={}", arg.align))
        }
        self.ret.push_str("\n")
    }
}


/// check for the index to start the local operations. To emit the MIR code then, local.idx - minLocal
pub struct LocalGatheringVisitor<'a> {
    pub minLocal: i32,
    pub argsCount: i32,    
    pub locals: &'a walrus::ModuleLocals,
    pub usedLocals: HashMap<LocalId,ValType>
}


impl LocalGatheringVisitor<'_>{

    pub fn getMin(&mut self) -> i32
    {
        self.minLocal // + self.argsCount
    }

    fn setUsedLocal(&mut self, idx: LocalId){

        let local = self.locals.get(idx).ty();

        self.usedLocals.insert(
            idx, 
            local
            );
    }

    pub fn initArgs(&mut self, func: & LocalFunction, locals: & ModuleLocals){
        for l in func.args.iter(){
            let k = *l;
            let v = locals.get(k).ty();

            self.usedLocals.insert(k, v);
        }
    }
    
}

impl Visitor<'_> for LocalGatheringVisitor<'_> {

    fn visit_local_get(&mut self, instr: &walrus::ir::LocalGet)
    {   
        if self.minLocal > instr.local.index() as i32 {
            self.minLocal = instr.local.index() as i32;
        }
        self.setUsedLocal(instr.local);
    }

    fn visit_local_set(&mut self, instr: &walrus::ir::LocalSet)
    {   
        if self.minLocal > instr.local.index() as i32 {
            self.minLocal = instr.local.index() as i32;
        };
        self.setUsedLocal(instr.local);
    }

    fn visit_local_tee(&mut self, instr: &walrus::ir::LocalTee)
    {   
        if self.minLocal > instr.local.index() as i32 {
            self.minLocal = instr.local.index() as i32;
        };
        self.setUsedLocal(instr.local);
    }
    
}

impl Visitor<'_> for MIRVisitor<'_> {
    
    fn visit_instr_seq_id(&mut self, instr: &InstrSeqId){ 
        //self.ret.push_str(&format!("{:?}\n", instr))
    }
    
    fn visit_local_id(&mut self, instr: &LocalId){         
        self.ret.push_str(& format!("{}\n", (instr.index() as i32) - self.min_local));
    }

    fn visit_memory_id(&mut self, instr: &MemoryId){ 
        // TODO assume that memoryId is always 0
        // Check ffmpeg example to check
        //unimplemented!("Not implemented visit_memory_id {}", self.ret) 
        //self.ret.push_str(&format!("\n"))
    }

    fn visit_table_id(&mut self, instr: &TableId){ unimplemented!("Not implemented visit_table_id {}", self.ret) }

    fn visit_global_id(&mut self, instr: &GlobalId){ 
        self.ret.push_str(& format!("{:?}\n", self.module.globals.get(*instr).id().index()))
    }

    fn visit_function_id(&mut self, instr: &FunctionId){ 
        self.ret.push_str(&format!("{:?}\n", instr.index()))
    }

    fn visit_data_id(&mut self, instr: &DataId){ 
        unimplemented!("Not implemented visit_data_id {}", self.ret) 
    }

    //fn visit_type_id(&mut self, instr: &TypeId){ unimplemented!("Not implemented visit_type_id {}", self.ret) }
        
    //fn visit_value(&mut self, instr: &Value){ unimplemented!("Not implemented visit_value {}", self.ret) }

    fn visit_call(&mut self, instr: &Call){ 
        self.ret.push_str(&format!("call "))
    }

    fn visit_call_indirect(&mut self, instr: &CallIndirect){ unimplemented!("Not implemented visit_call_indirect {}", self.ret) }

    fn visit_local_tee(&mut self, instr: &LocalTee){ 

        self.ret.push_str(&format!("local.tee "))
    }
        
    fn visit_global_set(&mut self, instr: &GlobalSet){ 
        self.ret.push_str(&format!("global.set "))
    }
        
    fn visit_binop(&mut self, instr: &Binop){ 

        //TODO Finish

        let op = match instr.op {
            // I32
            BinaryOp::I32Sub => "i32.sub",
            BinaryOp::I32Add => "i32.add",
            BinaryOp::I32And => "i32.and",
            BinaryOp::I32Or => "i32.or",
            BinaryOp::I32Xor => "i32.xor",
            BinaryOp::I32GtS => "i32.gt_s",
            BinaryOp::I32Ne => "i32.ne",
            BinaryOp::I32Eq => "i32.eq",
            BinaryOp::I32LeU => "i32.le_u",
            BinaryOp::I32LeS => "i32.le_s",
            BinaryOp::I32GtU => "i32.gt_u",
            BinaryOp::I32Shl => "i32.shl",
            BinaryOp::I32ShrS => "i32.shr_s",
            BinaryOp::I32ShrU => "i32.shr_u",
            BinaryOp::I32GeU => "i32.ge_u",
            BinaryOp::I32GeS => "i32.ge_s",
            BinaryOp::I32Mul => "i32.mul",
            BinaryOp::I32LtU => "i32.lt_u",
            BinaryOp::I32LtS => "i32.lt_s",
            BinaryOp::I32DivU => "i32.div_u",
            BinaryOp::I32DivS => "i32.div_s",
            BinaryOp::I32RemS => "i32.rem_s",
            BinaryOp::I32RemU => "i32.rem_u",
            // I64
            BinaryOp::I64Sub =>  "i64.sub",
            BinaryOp::I64Add =>  "i64.add",
            BinaryOp::I64And =>  "i64.and",
            BinaryOp::I64Or =>   "i64.or",
            BinaryOp::I64Xor =>  "i64.xor",
            BinaryOp::I64GtS =>  "i64.gt_s",
            BinaryOp::I64Ne =>   "i64.ne",
            BinaryOp::I64GeS => "i64.ge_s",
            BinaryOp::I64Eq =>   "i64.eq",
            BinaryOp::I64LeU =>  "i64.le_u",
            BinaryOp::I64LeS =>  "i64.le_s",
            BinaryOp::I64GtU =>  "i64.gt_u",
            BinaryOp::I64Shl =>  "i64.shl",
            BinaryOp::I64ShrS => "i64.shr_s",
            BinaryOp::I64ShrU => "i64.shr_u",
            BinaryOp::I64GeU =>  "i64.ge_u",
            BinaryOp::I64Mul =>  "i64.mul",
            BinaryOp::I64LtU =>  "i64.lt_u",
            BinaryOp::I64LtS =>  "i64.lt_s",
            BinaryOp::I64DivU => "i64.div_u",
            BinaryOp::I64DivS => "i64.div_s",
            BinaryOp::I64RemS => "i64.rem_s",
            BinaryOp::I64RemU => "i64.rem_u",
            // F32
            BinaryOp::F32Add =>  "f32.add",
            BinaryOp::F32Sub =>  "f32.sub",
            BinaryOp::F32Ne =>   "f32.ne",
            BinaryOp::F32Eq =>   "f32.eq",
            BinaryOp::F32Mul =>  "f32.mul",
            BinaryOp::F32Le =>  "f32.le",
            BinaryOp::F32Lt =>  "f32.lt",
            BinaryOp::F32Gt =>  "f32.gt",
            BinaryOp::F32Ge =>  "f32.ge",
            // F64
            BinaryOp::F64Add =>  "f64.add",
            BinaryOp::F64Sub =>  "f64.sub",
            BinaryOp::F64Ne =>   "f64.ne",
            BinaryOp::F64Eq =>   "f64.eq",
            BinaryOp::F64Mul =>  "f64.mul",
            BinaryOp::F64Le =>  "f64.le",
            BinaryOp::F64Lt =>  "f64.lt",
            BinaryOp::F64Gt =>  "f64.gt",
            BinaryOp::F64Ge =>  "f64.ge",
            _ => unimplemented!("Binop not implemented {:?}", instr)
        };

        self.ret.push_str(&format!("{}\n", op))
    }

    fn visit_unop(&mut self, instr: &Unop){ 
        
        //TODO Finish

        match instr.op {
            UnaryOp::I32Eqz => self.ret.push_str("i32.eqz"),
            UnaryOp::I64ExtendSI32 => self.ret.push_str("i64.extend_i32_s"),
            UnaryOp::I64Eqz => self.ret.push_str("i64.eqz"),
            UnaryOp::I32WrapI64 => self.ret.push_str("i32.wrap_i64"),
            UnaryOp::I64ReinterpretF64 => self.ret.push_str("i64.reinterpret_f64"),
            UnaryOp::F64Neg => self.ret.push_str("f64.neg"),
            UnaryOp::F64Abs => self.ret.push_str("f64.abs"),
            UnaryOp::I32TruncSF64 => self.ret.push_str("i32.trunc_f64_s"),
            UnaryOp::I32TruncUF64 => self.ret.push_str("i32.trunc_f64_u"),
            UnaryOp::F64ConvertSI32 => self.ret.push_str("f64.convert_i32_s"),
            UnaryOp::F64ConvertUI32 => self.ret.push_str("f64.convert_i32_u"),
            UnaryOp::I64ExtendUI32 => self.ret.push_str("i64.extend_i32_u"),
            _ => unimplemented!("Unary op not implemented {:?}", instr)
        }
        self.ret.push_str("\n")
    }

    fn visit_select(&mut self, instr: &Select){ 
        self.ret.push_str("select\n")
    }

    fn visit_unreachable(&mut self, instr: &Unreachable){ 
        self.ret.push_str("unreachable\n")
    }

    fn visit_br(&mut self, instr: &Br){ 
        let blockid = instr.block;

        let depth = self.block_depth.len() as i32 - self.block_depth.iter()
        .find(|(r, _)| r == &blockid).expect("Error in DFS traveling").1;
        self.ret.push_str(&format!("br {:?}\n", depth))
    }

    fn visit_br_if(&mut self, instr: &BrIf){ 
        let blockid = instr.block;
        let depth = self.get_depth(blockid);
        self.ret.push_str(&format!("br_if {:?}\n", depth))
    }
        
    fn visit_br_table(&mut self, instr: &BrTable){ 
        let id1= self.get_depth(instr.default);

        let remaining = instr.blocks.iter().map(|&s| {format!("{:?}", self.get_depth(s))})
        .collect::<Vec<_>>().join(" ");

        self.ret.push_str(&format!("br_table {} {}\n", remaining, id1))
    }

    fn visit_drop(&mut self, instr: &Drop){ 
        self.ret.push_str("drop\n")
    }

    fn visit_return(&mut self, instr: &Return){ unimplemented!("Not implemented visit_return {}", self.ret) }

    fn visit_memory_size(&mut self, instr: &MemorySize){ unimplemented!("Not implemented visit_memory_size {}", self.ret) }

    fn visit_memory_grow(&mut self, instr: &MemoryGrow){ unimplemented!("Not implemented visit_memory_grow {}", self.ret) }

    fn visit_memory_init(&mut self, instr: &MemoryInit){ unimplemented!("Not implemented visit_memory_init {}", self.ret) }

    fn visit_data_drop(&mut self, instr: &DataDrop){ unimplemented!("Not implemented visit_data_drop {}", self.ret) }

    fn visit_memory_copy(&mut self, instr: &MemoryCopy){ unimplemented!("Not implemented visit_memory_copy {}", self.ret) }

    fn visit_memory_fill(&mut self, instr: &MemoryFill){ unimplemented!("Not implemented visit_memory_fill {}", self.ret) }

    fn visit_load(&mut self, instr: &Load){ 
        
        self.emit_mem_kind_load(instr.kind);
        self.emit_mem_arg(instr.arg);
    }

    fn visit_store(&mut self, instr: &Store){ 

        self.emit_mem_kind_store(instr.kind);
        self.emit_mem_arg(instr.arg);
        //unimplemented!("Not implemented visit_store {}", self.ret)
     }

    fn visit_atomic_rmw(&mut self, instr: &AtomicRmw){ unimplemented!("Not implemented visit_atomic_rmw {}", self.ret) }

    fn visit_cmpxchg(&mut self, instr: &Cmpxchg){ unimplemented!("Not implemented visit_cmpxchg {}", self.ret) }

    fn visit_atomic_notify(&mut self, instr: &AtomicNotify){ unimplemented!("Not implemented visit_atomic_notify {}", self.ret) }

    fn visit_atomic_wait(&mut self, instr: &AtomicWait){ unimplemented!("Not implemented visit_atomic_wait {}", self.ret) }

    fn visit_atomic_fence(&mut self, instr: &AtomicFence){ unimplemented!("Not implemented visit_atomic_fence {}", self.ret) }

    fn visit_table_get(&mut self, instr: &TableGet){ unimplemented!("Not implemented visit_table_get {}", self.ret) }

    fn visit_table_set(&mut self, instr: &TableSet){ unimplemented!("Not implemented visit_table_set {}", self.ret) }

    fn visit_table_grow(&mut self, instr: &TableGrow){ unimplemented!("Not implemented visit_table_grow {}", self.ret) }

    fn visit_table_size(&mut self, instr: &TableSize){ unimplemented!("Not implemented visit_table_size {}", self.ret) }  
            

    fn visit_v128_swizzle(&mut self, instr: &V128Swizzle){ unimplemented!("Not implemented visit_v128_swizzle {}", self.ret) }


    fn visit_v128_shuffle(&mut self, instr: &V128Shuffle){ unimplemented!("Not implemented visit_v128_shuffle {}", self.ret) }

    fn visit_local_get(&mut self, instr: &walrus::ir::LocalGet)
    {   
        self.ret.push_str(& format!("local.get "));
    }


    fn visit_global_get(&mut self, instr: &walrus::ir::GlobalGet)
    {   
        self.ret.push_str(& format!("global.get "));
    }

    fn visit_local_set(&mut self, instr: &walrus::ir::LocalSet)
    {  
        self.ret.push_str(& format!("local.set "));
    }


    fn visit_const(&mut self, instr: &walrus::ir::Const){
        
        // TODO check format 0x1p+31 (;=2.14748e+09;)

        match instr.value {
            walrus::ir::Value::I32(val) => self.ret.push_str(&format!("i32.const {}\n", val)) ,
            walrus::ir::Value::I64(val) => self.ret.push_str(&format!("i64.const {}\n", val)),
            walrus::ir::Value::F32(val) => self.ret.push_str(&format!("f32.const {}\n", val)),
            walrus::ir::Value::F64(val) => self.ret.push_str(&format!("f64.const {}\n", val)),
            _ => panic!("Not recognized const")
        }

    }

    fn visit_loop(&mut self, instr: &Loop){
        self.ret.push_str("loop\n");
        self.block_hash.insert(instr.seq.index(), BLOCKTPE::LOOP);
    }
    fn visit_block(&mut self, instr: &Block){
        self.ret.push_str("block\n");
        self.block_hash.insert(instr.seq.index(), BLOCKTPE::BLOCK);
    }

    fn visit_if_else(&mut self, instr: &IfElse){
        self.ret.push_str("if\n");
    }

    fn start_instr_seq(&mut self, instr_seq: &InstrSeq)
    {
        self.depth += 1;
        self.block_depth.push((instr_seq.id(), self.depth))
    }

    fn end_instr_seq(&mut self, instr_seq: &InstrSeq)
    {
        let tpe = self.block_hash.get(&instr_seq.id().index());

        if self.config.convert_end_to_mir {
        match tpe {
            None => println!("Non registered block"),
            Some(x) => match x {
                BLOCKTPE::LOOP => self.ret.push_str( "end_loop\n"),
                BLOCKTPE::BLOCK => self.ret.push_str("end_block\n"),
                _ => println!("Unknown")
            }
        } }
        else {
            self.ret.push_str( "end\n")
        }
        self.depth -= 1;
        self.block_depth.pop();
    }
}    