ifdef opcl
opts	=	-I$(opcl)/include -L$(opcl)/lib/x86_64 -lOpenCL
else
opts	=	-I/usr/local/cuda-8.0/targets/x86_64-linux/include/CL/cl.h -lOpenCL
endif

gcpp = g++ ppc.cxx --fast-math -O2 $(opts) -Wall -Wextra
#above should have --fast-math
mlib	=	-fPIC -DXLIB -c -o ppc.o && gcc -shared \
		-fPIC -Wl,-soname,xppc ppc.o -o libxppc.so

warn	=	2>&1 | grep -v assuming

all:
	@echo "	make obj: compile the object code"
	@echo "	make lib: compile the xppc library"
	@echo "	make ocl: compile the ppc executable"

obj:
	$(gcpp) -o ppc.o -DXLIB -c

ocl:
	$(gcpp) -o ppc

lib:
	$(gcpp) $(mlib)

clean:
	rm ppc.o ppc libxppc.so || true
