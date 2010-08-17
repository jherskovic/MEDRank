import bz2
import struct
from MEDRank.mesh.tree import Tree
from multiprocessing import Pool
import array
import time
import sys
try:
    import psyco; psyco.full()
except ImportError: pass

MeSH=Tree(sys.argv[1]) 
# Read the entire tree, once, and set up a copy in memory. This makes 
# the process MUCH faster (about a 6x improvement!)
print "Replacing on-disk tree with in-memory one. Reading entire tree."
in_mem_tree={}
for t, v in MeSH._tree.iteritems():
    in_mem_tree[t]=v
MeSH._tree=in_mem_tree
print "Replacement done."

numterms=len(MeSH.terms)
#matrix=sparse.lil_matrix((numterms, numterms), dtype=numpy.float32)

# This process renders the matrix row by row to memory, then writes it out.
# The old struct-based version is commented out below.

def distance_computation(i):
    line=[0] * numterms
    t1=MeSH.terms[i]
    for j in xrange(numterms):
        t2=MeSH.terms[j]
        result=MeSH.distance(t1, t2)
        if result==-1:
            result=255
        line[j]=result
    return array.array('B', line).tostring()

outfile=open(sys.argv[2], "wb")

def map_coordinates_to_array_position(i, j, array_size):
    return i*array_size+j

def pack_dimensions(i, j):
    return struct.pack(">HH", i, j)

outfile.write(pack_dimensions(numterms, numterms))

# We won't leverage the symmetry of the matrix
start=time.time()
worker_pool=Pool()
#for i in xrange(numterms):

    #matrix_storage=[0] * numterms
    #for j in xrange(numterms):
    #    matrix_storage[j]=worker_pool.apply_async(distance_computation, 
     #                                             (t1, t2))
        # result=MeSH.distance(t1, t2)
        # Omit inter-tree distances
        #if result==-1:
        #    result=255
        #matrix_storage[j]=result
i=0
for this_line in worker_pool.imap(distance_computation, xrange(numterms), 10):
    i+=1
    #this_line=lines.pop(0)
    #print this_line
    outfile.write(this_line)
    end=time.time()
    print "Computed and stored up to row %d. Processing at %s rows per " \
           "second" % (i, (i+1)/(end-start))

worker_pool.close()

worker_pool.join()
    
print "Done!"
outfile.close()

#outfile=bz2.BZ2File("distance_matrix.bin.bz2", "wb")
# outfile=open(sys.argv[2], "wb")
# def pack_row(row):
#     output=[struct.pack('>B', int(x)) for x in row]
#     return ''.join(output)
# 
# def pack_dimensions(i, j):
#     return struct.pack(">HH", i, j)
# 
# # Divide and conquer...
# outfile.write(pack_dimensions(numterms, numterms))
# 
# nnz=0
# 
# for i in xrange(numterms):
#     print "Computing pass %d of %d. %d non-zero elements written." % (i+1, numterms, nnz)
#     this_row=[]
#     for j in xrange(numterms):
#         t1, t2 = MeSH.terms[i], MeSH.terms[j]
#         result = MeSH.distance(t1, t2)
# 	if result != 0.0:
#             nnz+=1
#         if result==-1:
#             result=255
#         this_row.append(result)
#     outfile.write(pack_row(this_row))
# 
# print "Done!"
# outfile.close()
