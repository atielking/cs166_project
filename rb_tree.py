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

    def updated(self, index, value, depth):
        new_slots = list(self.slots)
        if depth == 1:

            new_slots[index] = value
        else:
            # read only the first B bits of the number
            slot_idx = index >> (B * (depth - 1))
            # chop off the first B bits of the number
            next_idx = ((1 << (B * (depth - 1))) - 1) & index
            new_slots[slot_idx] = self.slots[slot_idx].updated(next_idx, value, depth - 1)
        return RBNode(new_slots)

    def create_new_branch(self, value, depth):
        new_slots = [None for i in range(NODE_SIZE)]
        if depth == 1: # return a new node
            new_slots[0] = value # a new branch always starts on the left
        else:
            new_slots[0] = self.create_new_branch(value, depth - 1)
        return RBNode(new_slots)


    def appended(self, index, value, depth):
        # the index is assumed to be the last index of the newly appended vector
        # assumes we've checked to make sure that the tree is not full
        new_slots = list(self.slots)
        if depth == 1:
            new_slots[index] = value
        else:
            # read only the first B bits of the number
            slot_idx = index >> (B * (depth - 1))
            # chop off the first B bits of the number
            next_idx = ((1 << (B * (depth - 1))) - 1) & index
            if self.slots[slot_idx]:
                new_slots[slot_idx] = self.slots[slot_idx].appended(next_idx, value, depth - 1)
            else: # need to create a new branch
                new_slots[slot_idx] = self.create_new_branch(value, depth - 1)
        return RBNode(new_slots)



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

    def updated(self, index, value):
        mod_tree = RBTree()
        mod_tree.size = self.size
        mod_tree.root = self.root.updated(index, value, self.depth)
        mod_tree.depth = self.depth
        return mod_tree

    def is_full(self):
        return self.size == 1 << B * self.depth

    def appended(self, value): # TODO: check edge cases
        mod_tree = RBTree()
        mod_tree.size = self.size + 1
        if self.is_full(): # need to create a new root
            mod_tree.depth = self.depth + 1
            new_slots = [None for i in range(NODE_SIZE)]
            new_slots[0] = self.root
            new_node = RBNode(new_slots)
            new_node.slots[1] = new_node.create_new_branch(value, self.depth)
            mod_tree.root = new_node
        else:
            mod_tree.depth = self.depth
            mod_tree.root = self.root.appended(self.size, value, self.depth)
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
    print('index test passed!')

def update_test():
    # assumes B = 1
    leaf0, leaf1 = RBNode([0, 1]), RBNode([2, 3])
    leaf2, leaf3 = RBNode([4, 5]), RBNode([6, 7])
    internal0, internal1 = RBNode([leaf0, leaf1]), RBNode([leaf2, leaf3])
    root = RBNode([internal0, internal1])
    tree = RBTree()
    tree.depth = 3
    tree.root = root
    tree_new = tree.updated(5, 166)
    assert(tree.get(5) == 5)
    assert(tree_new.get(5) == 166)
    print('update test passed!')

def append_test():
    vec = RBTree()
    trees = []
    for i in range(8):
        trees.append(vec.appended(i))
        vec = trees[i] # create many persistent versions
    for i in range(8):
        for j in range(i):
            assert(trees[i].get(j) == j)
    print('append test passed!')

# TODO: make a print function to display the tree

def test():
    '''
    Tests the structure
    TODO: also write a nice display function for the structure
    '''
    index_test()
    update_test()
    append_test()

if __name__=='__main__':
    test()

