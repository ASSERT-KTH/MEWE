#!/bin/sh

clang -Wformat -Werror=format-security -D_FORTIFY_SOURCE=2 listen.c -lpcap -o ../bin/nanown-listen
