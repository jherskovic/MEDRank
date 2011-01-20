CC=/Developer/usr/bin/llvm-g++
#CC=/Developer/usr/bin/g++-4.2
CFLAGS=`python-config --cflags`
LFLAGS="-L/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/config"
LIBS=`python-config --libs`

#g++-4.2 -O3 -fPIC -c -fopenmp build_distance_matrix.cc -march=nocona
#g++-4.2 -shared -fPIC -Wl -o _distmat.so build_distance_matrix.o -lgomp
$CC $CFLAGS -I/usr/local/include -fopenmp -c build_distance_matrix.cc -o build_distance_matrix.o
$CC $LFLAGS $LIBS -bundle -lgomp -fopenmp build_distance_matrix.o -o _distmat.so 
