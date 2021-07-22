	.text
	.file	"static_mem_two.c"
	.hidden	m                       # @m
	.type	m,@object
	.section	.bss.m,"",@
	.globl	m
	.p2align	4
m:
	.skip	400
	.size	m, 400

	.hidden	n                       # @n
	.type	n,@object
	.section	.bss.n,"",@
	.globl	n
	.p2align	4
n:
	.skip	200
	.size	n, 200

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
	.section	.bss.n,"",@
