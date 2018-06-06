'''
Based off of the implementation in rb_tree.py
Augments internal node information with the minimum value of the subtree rooted
at that internal node.
'''
B = 1
NODE_SIZE = 1 << B


class RBNode: # TODO: should each node maintain a depth?
    def __init__(self, slots):
        self.slots = slots
        self.min_val = float('inf')

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

    def min_slice(self, i, j, depth):
        # traverse until the indices diverge and accumulate accordingly
        diverging = False
        overall_min = float('inf')
        i_slots = self.slots
        j_slots = self.slots
        while depth > 0:
            if depth == 1:
                if NODE_SIZE - i > 0:
                    overall_min = min(overall_min, min(i_slots[k]
                        for k in range(i, NODE_SIZE)))
                if j + 1 > 0:
                    overall_min = min(overall_min, min(j_slots[k]
                        for k in range(0, j + 1)))
                break
            i_slot_idx = i >> (B * (depth - 1))
            j_slot_idx = j >> (B * (depth - 1))
            if i_slot_idx != j_slot_idx and not diverging:
                # diverging for the first time
                diverging = True
                if j_slot_idx - i_slot_idx - 1 > 0:
                    overall_min = min(i_slots[k].min_val
                        for k in range(i_slot_idx + 1, j_slot_idx))
            if diverging:
                if NODE_SIZE - i_slot_idx - 1 > 0:
                    overall_min = min(overall_min, min(i_slots[k].min_val
                        for k in range(i_slot_idx + 1, NODE_SIZE)))
                if j_slot_idx > 0:
                    overall_min = min(overall_min, min(j_slots[k].min_val
                        for k in range(0, j_slot_idx)))
            depth -= 1
            i_slots = i_slots[i_slot_idx].slots
            j_slots = j_slots[j_slot_idx].slots
            i = ((1 << (B * (depth - 1))) - 1) & i
            j = ((1 << (B * (depth - 1))) - 1) & j

        return overall_min

    def updated(self, index, value, depth):
        new_slots = list(self.slots)
        new_node = RBNode(new_slots)
        new_node.min_val = self.min_val
        if depth == 1:
            new_node.slots[index] = value
            if value < self.min_val:
                new_node.min_val = value
        else:
            # read only the first B bits of the number
            slot_idx = index >> (B * (depth - 1))
            # chop off the first B bits of the number
            next_idx = ((1 << (B * (depth - 1))) - 1) & index
            new_slots[slot_idx] = self.slots[slot_idx].updated(next_idx, value, depth - 1)
            node_min = float('inf')
            for child in new_node.slots:
                if child and child.min_val < new_node.min_val:
                    new_node.min_val = child.min_val
        return new_node

    def create_new_branch(self, value, depth):
        new_slots = [None for i in range(NODE_SIZE)]
        new_node = RBNode(new_slots)
        new_node.min_val = value
        if depth == 1: # return a new node
            new_node.slots[0] = value # a new branch always starts on the left
        else:
            new_node.slots[0] = self.create_new_branch(value, depth - 1)
        return new_node


    def appended(self, index, value, depth):
        # the index is assumed to be the last index of the newly appended vector
        # assumes we've checked to make sure that the tree is not full
        new_slots = list(self.slots)
        new_node = RBNode(new_slots)
        new_node.min_val = self.min_val
        if depth == 1:
            new_node.slots[index] = value
            if value < new_node.min_val:
                new_node.min_val = value
        else:
            # read only the first B bits of the number
            slot_idx = index >> (B * (depth - 1))
            # chop off the first B bits of the number
            next_idx = ((1 << (B * (depth - 1))) - 1) & index
            if self.slots[slot_idx]:
                new_node.slots[slot_idx] = self.slots[slot_idx].appended(next_idx, value, depth - 1)
            else: # need to create a new branch
                new_node.slots[slot_idx] = self.create_new_branch(value, depth - 1)
            for child in new_node.slots:
                if child and child.min_val < new_node.min_val:
                    new_node.min_val = child.min_val
        return new_node



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

    def min_slice(self, i, j):
        if i == 0 and j == self.size - 1:
            return self.root.min_val
        else:
            return self.root.min_slice(i, j, self.depth)

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

def min_slice_test():
    tree = RBTree()
    tree = tree.appended(3) # 0
    tree = tree.appended(2) # 1
    tree = tree.appended(5) # 2
    tree = tree.appended(0) # 3
    tree = tree.appended(1) # 4
    tree = tree.appended(7) # 5
    tree = tree.appended(8) # 6
    tree = tree.appended(10) # 7
    assert(tree.min_slice(2, 5) == 0)
    assert(tree.min_slice(4, 7) == 1)
    assert(tree.min_slice(0, 2) == 2)
    print('min_slice test passed!')

def test():
    '''
    Tests the structure
    TODO: also write a nice display function for the structure
    '''
    index_test()
    update_test()
    append_test()
    min_slice_test()

if __name__=='__main__':
    test()

