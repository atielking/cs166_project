'''
Provides an implementation of a radix-balanced tree in python. This data
structure supports efficient immutable updates with limited copying
How to properly support delete/split?
Implementation based heavily on: http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.1000.6710&rep=rep1&type=pdf
'''
B = 1
NODE_SIZE = 1 << B


class RBNode: # TODO: should each node maintain a depth?
    def __init__(self, slots):
        self.slots = slots
        self.next_free_slot = 0 # index of the next free slot

    def get(self, index, depth):
        '''
        Return what value is stored at index idx stored at the subtree rooted
        at this node
        '''
        if depth == 1: # are we at a leaf?
            return self.slots[index]
        else:
            # read only the first B bits of the number
            slot_idx = index >> (B * (depth - 1))
            # chop off the first B bits of the number
            next_idx = ((1 << (B * (depth - 1))) - 1) & index
            return self.slots[slot_idx].get(next_idx, depth - 1)

    def set(self, index, value, depth):
        if depth == 1:
            new_node = list(self.slots)
            new_node[index] = value
            return RBNode(new_node)
        else:
            new_node = list(self.slots)
            # read only the first B bits of the number
            slot_idx = index >> (B * (depth - 1))
            # chop off the first B bits of the number
            next_idx = ((1 << (B * (depth - 1))) - 1) & index
            new_node[slot_idx] = self.slots[slot_idx].set(next_idx, value, depth - 1)
            return RBNode(new_node)



class RBTree:
    def __init__(self):
        '''
        M = 1 << B is the branching factor
        '''
        self.size = 0
        self.root = RBNode([None for i in range(NODE_SIZE)])
        self.depth = 1

    def get(self, index):
        return self.root.get(index, self.depth)

    def set(self, index, value):
        mod_tree = RBTree()
        mod_tree.size = self.size
        mod_tree.root = self.root.set(index, value, self.depth)
        mod_tree.depth = self.depth
        return mod_tree
    

def index_test():
    # assumes B = 1
    leaf0, leaf1 = RBNode([0, 1]), RBNode([2, 3])
    leaf2, leaf3 = RBNode([4, 5]), RBNode([6, 7])
    internal0, internal1 = RBNode([leaf0, leaf1]), RBNode([leaf2, leaf3])
    root = RBNode([internal0, internal1])
    tree = RBTree()
    tree.depth = 3
    tree.root = root
    for i in range(8):
        assert(i == tree.get(i))
    print('index_test passed!')

def update_test():
    # assumes B = 1
    leaf0, leaf1 = RBNode([0, 1]), RBNode([2, 3])
    leaf2, leaf3 = RBNode([4, 5]), RBNode([6, 7])
    internal0, internal1 = RBNode([leaf0, leaf1]), RBNode([leaf2, leaf3])
    root = RBNode([internal0, internal1])
    tree = RBTree()
    tree.depth = 3
    tree.root = root
    tree_new = tree.set(5, 166)
    print(tree_new.get(5))

def test():
    '''
    Tests the structure
    TODO: also write a nice display function for the structure
    '''
    index_test()
    update_test()

if __name__=='__main__':
    test()

