	.text
	.file	"mem.c"
	.hidden	m                       # @m
	.type	m,@object
	.section	.bss.m,"",@
	.globl	m
	.p2align	4
m:
	.skip	400
	.size	m, 400

	.ident	"Apple clang version 12.0.0 (clang-1200.0.32.28)"
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
