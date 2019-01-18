# MultiSim-PPC
This repository was made to store the current version of the PPC runs done by the UTA-REST group.

## Getting Started
The following instructions are tailored for usage in the IceCube cobalt cluster.

### Initilization
* [Git Clone](https://www.atlassian.com/git/tutorials/setting-up-a-repository/git-clone) - Clone the project into a directory.

### Compiling
After cloning the repository, the C++ scripts need to be made.

In the gpu directory, run the following.
```
$ make cpu
```
In the ocl directory, run the following.
```
$ make obj
```
In the llh directory, run the following.
```
$ make
```

### Linking

If on the cobalts, make the following SymLinks in the MultiSim-PPC/dat directory

       flasher -> /data/user/dima/I3/flashers/flasher
       flasher-1LED -> /data/user/dima/I3/flashers/flasher-1LED
       all -> /data/user/dima/I3/flashers/oux

Please note that you might need to source the src files in those directories. Please also note that a server admin might have moved the path to a library that is used by the make scripts.

### Setting up the jobs

After setting up all the C++ scripts. Copy the desired ice modeled into a directory in the Ice a directory. Next, Go into the llh.sh script in the llh directory, and edit the ICEM variable to the name of\
 the directory that you stored your ice models in.

Upon that, run the ./llh/scripts/setup_fit.sh file. Make sure to pass the absolute path of the ice models directory as an argument.

### Submitting the jobs

Finally, log into the cluster, and run the submit.sh file in the llh directory. Make sure to pass the absolute path of the ice models directory as an argument.

## Other notes
Please make sure to have the dat at the same level of the other directores (i.e llh, ice, ...)

