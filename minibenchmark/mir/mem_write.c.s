	.text
	.file	"mem_write.c"
	.section	.text.f,"",@
	.hidden	f                       # -- Begin function f
	.globl	f
	.type	f,@function
f:                                      # @f
	.functype	f (i32, i32) -> (i32)
	.local  	i32
# %bb.0:
	global.get	__stack_pointer // CHECK if is can be changed to a custom stack_pointer
	i32.const	16 // CHECK if is can be changed to a custom stack_pointer
	i32.sub 
	local.tee	2
	local.get	0
	i32.store	12
	local.get	2
	local.get	1
	i32.store	8
	i32.const	m // memory object is loaded as an object, use a different object per program
				  // decide memory size, one page is OK ?
	local.get	2
	i32.load	12
	i32.const	2
	i32.shl 
	i32.add 
	local.get	2
	i32.load	8
	i32.store	0
	local.get	2
	i32.load	8
                                        # fallthrough-return
	end_function
.Lfunc_end0:
	.size	f, .Lfunc_end0-f
                                    # -- End function
	.hidden	m                       # @m // Check for memory object declaration
	.type	m,@object
	.section	.bss.m,"",@
	.globl	m
	.p2align	4
m:  // Check for object declaration
	.skip	400
	.size	m, 400

	.ident	"Apple clang version 12.0.0 (clang-1200.0.32.28)"
	.globaltype	__stack_pointer, i32 // CHECK if is can be changed to a custom stack_pointer
	.section	.custom_section.producers,"",@
	.int8	1
	.int8	12
	.ascii	"processed-by"
	.int8	1
	.int8	11
	.ascii	"Apple clang"
	.int8	27
	.ascii	"12.0.0 (clang-1200.0.32.28)"
	.section	.bss.m,"",@
