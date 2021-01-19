#![crate_name = "wat2mir"]
pub mod utils;
pub mod dto;
pub mod visitor;

use std::collections::HashMap;

/// translate wasm function to LLVM MIR format
pub fn translate2mir(file_name: &str, func_name: &str, as_function: &str, config: crate::dto::Wat2MirConfig) -> (String, String, String) {


   let module = walrus::Module::from_file(format!("{}", file_name)).unwrap();
    
   let mut head = String::new();
   let mir_visitor: &mut visitor::MIRVisitor = &mut visitor::MIRVisitor{ 
       block_hash:HashMap::new(), 
        local_function: None,
        depth: 0,
        block_depth:vec![],
        config,
        module: &module, min_local: 0, ret:  String::from("") };

   let (_, func) = module.funcs.iter_local().find(|(func_id, _)| {
       
        let option_name = module.funcs.get(*func_id).name.as_ref();
        let unknown: &String = &String::from("unknown");

        let item_name = match option_name {
            None => unknown,
            Some(x) => x
        };

        item_name == func_name

   }).expect(&format!("Function {} not found. Check if the name section exist.", func_name));
   

   let  local_visitor = &mut visitor::LocalGatheringVisitor{
    minLocal: i32::MAX, 
    locals: &module.locals,
    usedLocals: HashMap::new(),
    argsCount: func.args.len() as i32};

    println!("{}", local_visitor.argsCount);

    local_visitor.initArgs(func, &module.locals);
    walrus::ir::dfs_in_order(local_visitor, func, func.entry_block());

    let locals = &local_visitor.usedLocals.iter().map(|(_k, val)| {
        format!(" {:?}", &val).to_lowercase()
    }).collect::<Vec<_>>();

    let args = &func.args.iter().map(|t| {
        format!(" {:?}", local_visitor.usedLocals.get(t))
    }).collect::<Vec<_>>();

    let fty = module.types.get(func.ty())
    .results().iter().map(|v|{
        format!("{:?}", v).to_lowercase()
    }).collect::<Vec<_>>().join(","); 

    head.push_str(&format!(".type {},@function\n", as_function));
    head.push_str(&format!("{}:\n", as_function));
    head.push_str(&format!(".functype {} ({}) -> ({})\n", as_function,
        args.join(","), fty
    )); 
    head.push_str(".local\t");



    let all_locals = utils::cat(args, locals);

    head.push_str(&all_locals.join(",")); // TODO check if locals and parameters are in the same declaration in the MIR representation
    head.push_str("\n");
    // Emit MIR function header
    mir_visitor.local_function = Some(func);
    mir_visitor.min_local = local_visitor.getMin();
    mir_visitor.ret = String::new();

    walrus::ir::dfs_in_order(mir_visitor, func, func.entry_block());

    println!("{:?}", mir_visitor.ret);

   (head, mir_visitor.ret.clone(), String::from("end_function"))
}