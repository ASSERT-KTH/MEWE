#![crate_name = "wat2mir"]

use walrus::{LocalFunction, ModuleFunctions, ModuleLocals, ValType, ir::Visitor};
use std::path::PathBuf;
use walrus::ir::*;
use std::collections::HashMap;

enum BLOCKTPE {
    LOOP,
    BLOCK,
    IF
}

struct MIRVisitor<'a> {
    minLocal: i32,
    locals: &'a walrus::ModuleLocals,
    localFunction: Option<&'a walrus::LocalFunction>,
    blockHash: HashMap<usize, BLOCKTPE>,
    ret: String
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

    fn visit_call(&mut self, instr: &walrus::ir::Call){
        
    }


    fn visit_local_get(&mut self, instr: &walrus::ir::LocalGet)
    {   
        self.ret.push_str(& format!("local.get {}\n", (instr.local.index() as i32) - self.minLocal));
    }


    fn visit_global_get(&mut self, instr: &walrus::ir::GlobalGet)
    {   
        //println!("global.get {:?}", (instr.global.index() as i32) - self.minLocal);
    }

    fn visit_local_set(&mut self, instr: &walrus::ir::LocalSet)
    {  
        self.ret.push_str(& format!("local.set {}\n", (instr.local.index() as i32) - self.minLocal));
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
        locals: &module.locals, minLocal: 0, ret:  String::from("") };

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
            format!(" {:?}", val).to_lowercase()
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