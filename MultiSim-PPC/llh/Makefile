ifdef I3_PORTS
ver	=	gsl-1.14
#dir	=	-I$(I3_PORTS)/include/$(ver) -L$(I3_PORTS)/lib/$(ver)
dir = -I/cvmfs/icecube.opensciencegrid.org/py2-v1/RHEL_6_x86_64/i3ports/include/gsl-1.14/ -L/cvmfs/icecube.opensciencegrid.org/py2-v1/RHEL_6_x86_64/i3ports/lib/$(ver)

else
dir	=
endif
gsl	=	$(dir) -lgsl -lgslcblas
#gsl = $(dir)
ifdef opcl
opts	=	-I$(opcl)/include -L$(opcl)/lib/x86_64 -lOpenCL
else
opts	=	-I/usr/local/cuda-8.0/targets/x86_64-linux/include/CL/cl.h -lOpenCL

endif

gcpp	=	g++ -O2 --fast-math
nvcc	=	nvcc -O2 --use_fast_math

all:	ocl

ocl:
	g++ llh.cxx -o llh $(gsl) ../ocl/ppc.o $(opts)

inv:
	c++ inv.cxx -o inv $(gsl)

ico:
	c++ ico.cxx -o ico
