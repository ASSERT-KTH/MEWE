#![crate_name = "wat2mir"]

use walrus::*;
use std::{default, env::args, path::PathBuf};
use walrus::ir::*;
use std::collections::HashMap;

enum BLOCKTPE {
    LOOP,
    BLOCK,
    IF
}

struct MIRVisitor<'a> {
    minLocal: i32,
    module: &'a walrus::Module,
    localFunction: Option<&'a walrus::LocalFunction>,
    blockHash: HashMap<usize, BLOCKTPE>,
    ret: String,
    blockDepth: Vec<(InstrSeqId, i32)>,
    depth: i32
}

impl MIRVisitor<'_>{

    fn get_depth(&mut self, instrId: InstrSeqId) -> i32{
        self.blockDepth.len() as i32 - self.blockDepth.iter()
        .find(|(r, _)| r == &instrId).expect("Error in DFS traveling").1
    }

    fn emit_mem_kind_store(&mut self, kind: StoreKind){
        match kind {
            StoreKind::I32 { atomic} => self.ret.push_str(&format!("i32.store ")),
            StoreKind::I64 { atomic} => self.ret.push_str(&format!("i64.store ")),
            StoreKind::I32_16 { atomic} => self.ret.push_str(&format!("i32.store16 ")),
            StoreKind::I32_8 { atomic} => self.ret.push_str(&format!("i32.store8 ")),
            StoreKind::I64_8 { atomic} => self.ret.push_str(&format!("i64.store8 ")),
            StoreKind::I64_16 { atomic} => self.ret.push_str(&format!("i64.store16 ")),
            StoreKind::I64_32 { atomic} => self.ret.push_str(&format!("i64.store32 ")),
            StoreKind::F32 => self.ret.push_str(&format!("f32.store ")),
            StoreKind::F64  => self.ret.push_str(&format!("f64.store ")),
            _ => unimplemented!("ERROR {:?}", kind)
        }
    }

    fn emit_mem_kind_load(&mut self, kind: LoadKind){
        match kind {
            LoadKind::I32 {atomic} => self.ret.push_str(&format!("i32.load ")),
            LoadKind::I32_8 { kind} => self.ret.push_str(&format!("i32.load8_u ")),
            LoadKind::I64 { atomic} => self.ret.push_str(&format!("i64.load ")),
            LoadKind::F64 => self.ret.push_str(&format!("f64.load ")),
            LoadKind::I64_32 { kind: ZeroExtend } => self.ret.push_str(&format!("i64.load32_u ")),
            _ => panic!("ERROR {:?}", kind)
        }
    }

    fn emit_mem_arg(&mut self, arg: MemArg){
        self.ret.push_str(&format!("offset={} align={}", arg.offset, arg.align));
    }
}
/// check for the index to start the local operations. To emit the MIR code then, local.idx - minLocal
struct LocalGatheringVisitor<'a> {
    minLocal: i32,
    argsCount: i32,    
    locals: &'a walrus::ModuleLocals,
    usedLocals: HashMap<LocalId,ValType>
}


impl LocalGatheringVisitor<'_>{

    pub fn getMin(&mut self) -> i32
    {
        self.minLocal + self.argsCount
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

    
}

impl Visitor<'_> for MIRVisitor<'_> {
    
    fn visit_instr_seq_id(&mut self, instr: &InstrSeqId){ 
        //self.ret.push_str(&format!("{:?}\n", instr))
    }
    
    fn visit_local_id(&mut self, instr: &LocalId){ 
        self.ret.push_str(& format!("{}\n", (instr.index() as i32) - self.minLocal));
    }

    fn visit_memory_id(&mut self, instr: &MemoryId){ 
        // TODO assume that memoryId is always 0
        // Check ffmpeg example to check
        //unimplemented!("Not implemented visit_memory_id {}", self.ret) 
        self.ret.push_str(&format!("\n"))
    }

    fn visit_table_id(&mut self, instr: &TableId){ unimplemented!("Not implemented visit_table_id {}", self.ret) }

    fn visit_global_id(&mut self, instr: &GlobalId){ 
        self.ret.push_str(& format!("{:?}\n", self.module.globals.get(*instr).id().index()))
    }

    fn visit_function_id(&mut self, instr: &FunctionId){ 
        self.ret.push_str(&format!("{:?} \n", instr))
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
        //TODO
        self.ret.push_str(&format!("{:?}\n", instr.op))
    }

    fn visit_unop(&mut self, instr: &Unop){ 
        //TODO
        self.ret.push_str(&format!("{:?}\n", instr.op))
    }

    fn visit_select(&mut self, instr: &Select){ 
        self.ret.push_str("select")
    }

    fn visit_unreachable(&mut self, instr: &Unreachable){ 
        self.ret.push_str("unreachable")
    }

    fn visit_br(&mut self, instr: &Br){ 
        let blockid = instr.block;

        let depth = self.blockDepth.len() as i32 - self.blockDepth.iter()
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

        let remaining = instr.blocks.iter().map(|&s| {format!(" {:?}", self.get_depth(s))})
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
        self.blockHash.insert(instr.seq.index(), BLOCKTPE::LOOP);
    }
    fn visit_block(&mut self, instr: &Block){
        self.ret.push_str("block\n");
        self.blockHash.insert(instr.seq.index(), BLOCKTPE::BLOCK);
    }

    fn visit_if_else(&mut self, instr: &IfElse){
        self.ret.push_str("if\n");
    }

    fn start_instr_seq(&mut self, instr_seq: &InstrSeq)
    {
        self.depth += 1;
        self.blockDepth.push((instr_seq.id(), self.depth))
    }

    fn end_instr_seq(&mut self, instr_seq: &InstrSeq)
    {
        let tpe = self.blockHash.get(&instr_seq.id().index());

        match tpe {
            None => println!("Non registered block"),
            Some(x) => match x {
                BLOCKTPE::LOOP => self.ret.push_str("end_loop\n"),
                BLOCKTPE::BLOCK => self.ret.push_str("end_block\n"),
                _ => println!("Unknown")
            }
        }
        let id = instr_seq.id();
        self.depth -= 1;
        self.blockDepth.pop();
    }
}    

fn cat<T: Clone>(a: &[T], b: &[T]) -> Vec<T> {
    [a, b].concat()
}

/// translate wasm function to LLVM MIR format
pub fn translate2mir(file_name: &str, func_name: &str, as_function: &str) -> String {


   let module = walrus::Module::from_file(format!("{}", file_name)).unwrap();
    
   let mirVisitor = &mut MIRVisitor{ 
       blockHash:HashMap::new(), 
        localFunction: None,
        depth: 0,
        blockDepth:vec![],
        module: &module, minLocal: 0, ret:  String::from("") };

   module.funcs.iter_local().for_each(|(fromFuncId, item )| {


       let optionName = module.funcs.get(fromFuncId).name.as_ref();
        let mut unknown = &String::from("unknown");

       let fromFuncName = match optionName {
           None => unknown,
           Some(x) => x
       };
       if fromFuncName == func_name {

        let  localVisitor = &mut LocalGatheringVisitor{
            minLocal: i32::MAX, 
            locals: &module.locals,
            usedLocals: HashMap::new(),
            argsCount: item.args.len() as i32};
        
        localVisitor.initArgs(item, &module.locals);
        walrus::ir::dfs_in_order(localVisitor, item, item.entry_block());

        let locals = &localVisitor.usedLocals.iter().map(|(_k, val)| {
            format!(" {:?}", &val).to_lowercase()
        }).collect::<Vec<_>>();

        let args = &item.args.iter().map(|t| {
            format!(" {:?}", localVisitor.usedLocals.get(t))
        }).collect::<Vec<_>>();
        
        let fty = module.types.get(item.ty())
        .results().iter().map(|v|{
            format!("{:?}", v).to_lowercase()
        }).collect::<Vec<_>>().join(","); 

        mirVisitor.ret.push_str(&format!(".type {},@function\n", as_function));
        mirVisitor.ret.push_str(&format!("{}:\n", as_function));
        mirVisitor.ret.push_str(&format!(".functype {} ({}) -> ({})\n", as_function,
            args.join(","), fty
        )); 
        mirVisitor.ret.push_str(".local\t");

        
        
        let all_locals = cat(args, locals);

        mirVisitor.ret.push_str(&all_locals.join(",")); // TODO check if locals and parameters are in the same declaration in the MIR representation
        mirVisitor.ret.push_str("\n");
        // Emit MIR function header
        mirVisitor.localFunction = Some(item);
        mirVisitor.minLocal = localVisitor.getMin();
        walrus::ir::dfs_in_order(mirVisitor, item, item.entry_block());

        mirVisitor.ret.push_str("end_function\n");
        // Emit function body

        // Emit function closing
       }
   });

   mirVisitor.ret.clone()
}