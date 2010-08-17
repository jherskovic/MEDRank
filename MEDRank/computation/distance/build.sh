#CC=/Developer/usr/bin/llvm-g++
CC=/Developer/usr/bin/g++-4.2
#g++-4.2 -O3 -fPIC -c -fopenmp build_distance_matrix.cc -march=nocona
#g++-4.2 -shared -fPIC -Wl -o _distmat.so build_distance_matrix.o -lgomp
$CC -arch ppc -arch i386 -isysroot /Developer/SDKs/MacOSX10.5.sdk -fopenmp -no-cpp-precomp -mno-fused-madd -fno-common -ftree-vectorize  -dynamic -DNDEBUG -g -O3 -I/usr/local/include -I/Library/Frameworks/Python.framework/Versions/2.6/include/python2.6 -c build_distance_matrix.cc -o build_distance_matrix.o
$CC -arch ppc -arch i386 -isysroot /Developer/SDKs/MacOSX10.5.sdk -g -bundle -undefined dynamic_lookup -lgomp build_distance_matrix.o -o _distmat.so 
