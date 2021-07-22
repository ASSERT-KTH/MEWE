	.text
	.file	"mem_load.c"
	.section	.text.main,"",@
	.hidden	main                    # -- Begin function main
	.globl	main
	.type	main,@function
main:                                   # @main
	.functype	main (i32) -> (i32)
	.local  	i32
# %bb.0:
	global.get	__stack_pointer
	i32.const	16
	i32.sub 
	local.tee	1
	i32.const	0
	i32.store	12
	local.get	1
	local.get	0
	i32.store	8
	i32.const	m
	local.get	1
	i32.load	8
	i32.const	2
	i32.shl 
	i32.add 
	i32.load	0
                                        # fallthrough-return
	end_function
.Lfunc_end0:
	.size	main, .Lfunc_end0-main
                                        # -- End function
	.hidden	m                       # @m
	.type	m,@object
	.section	.bss.m,"",@
	.globl	m
	.p2align	4
m:
	.skip	400
	.size	m, 400

	.ident	"Apple clang version 12.0.0 (clang-1200.0.32.28)"
	.globaltype	__stack_pointer, i32
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
