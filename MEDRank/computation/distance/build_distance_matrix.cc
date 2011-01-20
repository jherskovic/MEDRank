#include <stdlib.h>
#include <omp.h>
#include <vector>
#include <map>
#include <set>
#include <iterator>
#include <algorithm>
#include <list>
//#include <functors>

using namespace std;

vector<int> neighbors(int* link_matrix, int matrix_size, 
                      int point_of_interest)
{
    vector<int> the_neighbors;
    int row_address=point_of_interest*matrix_size;
    
    for (int i=0; i<matrix_size; i++)
    {
        if (link_matrix[row_address+i]) 
        {
            the_neighbors.push_back(i);
        }
    }
    
    return the_neighbors;
}

typedef map<int, int> path_type;
vector<int> next_level(path_type &path, vector<int> previous_level,
                       int* neighbors_from, int matrix_size)
{
    vector<int> new_level;
    for (int i=0; i<previous_level.size(); i++)
    {
        vector<int> successors=neighbors(neighbors_from, matrix_size, 
            previous_level[i]);
        for (int j=0; j<successors.size(); j++) 
        {
            int candidate_node=successors[j];
            if (path.find(candidate_node)==path.end()) {
                path[candidate_node]=previous_level[i];
                new_level.push_back(candidate_node);
            }
        }
    }
    
    return new_level;
}

#define NULL_PATH -1
//struct comparator
//{
//    bool operator()(const int i1, const int i2) const
//        {
//            return i1<i2;
//        }
//};

set<int> get_path_map_keys(path_type &path)
{
    set<int> keys;
    for (path_type::iterator iter=path.begin(); iter!=path.end();
         ++iter)
    {
        keys.insert(iter->first);
    }
    
    //vector<int> result(keys.size());
    
    //copy(keys.begin(), keys.end(), result.begin());
    return keys;
}

int bidisearch(int* link_matrix, int* transposed_link_matrix, int matrix_size,
               int point_a, int point_b, int unreachable_distance) 
{
    // Prepare computation
    if (point_a==point_b)
        return 0;
    path_type paths_a, paths_b;
    paths_a[point_a]=NULL_PATH;
    paths_b[point_b]=NULL_PATH;
    
    vector<int> last_a, last_b;
    last_a.push_back(point_a);
    last_b.push_back(point_b);

    set<int> middle_nodes;
    
    while (last_a.size() && last_b.size()) 
    {
        set<int> a_nodes=get_path_map_keys(paths_a);
        set<int> b_nodes=get_path_map_keys(paths_b);
//        insert_iterator<set<int> > it=;
        set_intersection(a_nodes.begin(),
                         a_nodes.end(),
                         b_nodes.begin(),
                         b_nodes.end(),
                         inserter(middle_nodes,
                                  middle_nodes.begin()));
        if (middle_nodes.size())
            break; // We found a solution! end the iteration.
        if (a_nodes.size()<=b_nodes.size()) 
            last_a=next_level(paths_a, last_a, link_matrix, matrix_size);
        else
            last_b=next_level(paths_b, last_b, transposed_link_matrix,  
                              matrix_size);
    }
    if (middle_nodes.size()==0)
        return unreachable_distance;

    list<int> result;
    int middle=(*middle_nodes.begin());
    int c=middle;
    // From middle to a
    while (c!=point_a)
    {
        c=paths_a[c];
        result.push_front(c);
    }
    result.push_back(middle);
    c=middle;
    while (c!=point_b)
    {
        c=paths_b[c];
        result.push_back(c);
    }
    return result.size()-1;
}

extern "C" void fill_distance_matrix(int* to_fill, int* link_matrix, 
                          int* transposed_link_matrix, 
                          int matrix_size, int unreachable_distance) 
{
    int i, j;
    // We try to keep the number of library calls down
    for (i=0; i<matrix_size; i++) {
        //printf("Working on row %d.", i);
        #pragma omp parallel for schedule(dynamic)
        for (j=0; j<matrix_size; j++) 
        {
            to_fill[i*matrix_size+j]=bidisearch(link_matrix,
                                        transposed_link_matrix,
                                        matrix_size,
                                        i,
                                        j,
                                        unreachable_distance);
        }
    }
    
    return;
}

