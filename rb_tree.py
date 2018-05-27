'''
Provides an implementation of a radix-balanced tree in python. This data
structure supports immutable updates.
'''

class RBNode:
    def __init__(B):
        '''
        M = 1 << Bis the branching factor
        '''
        self.B = B
        self.M = 1 << B
        self.slots = [None for i in range(M)]

    def lookup(idx, shift):
        '''
        Return what value is stored at index idx stored at the subtree rooted
        at this node
        '''
        if shift: # are we at a leaf?
            return self.slots[idx]
        else:
            slot_idx = idx >> shift # read only the first B bits of the number
            return self.slots[slot_idx].lookup(idx << B, shift << 1)

class RBTree:
    def __init__(B):
        '''
        M = 1 << B is the branching factor
        '''
        self.size = 0
        self.B = B
        self.root = RBNode(1 << B)
        self.shift = 0 # B * height
        self.start_idx = 0
        self.end_idx = 0

    def append(elem):
        '''
        Append elem to the data structure
        Cases to handle: space exists in the right most leaf, might have to
        create a new node, might also have to create a new root.
        '''
        pass

    def lookup(idx):
        '''
        Returns what value is stored at index idx
        '''
        return root.lookup(idx, shift)

    def update(idx, val):
        '''
        Returns a new RBTree -- need to copy the path from the root to the
        desired node
        '''
        pass

def test():
    '''
    Tests the structure
    TODO: also write a nice display function for the structure
    '''
    pass

if __name__=='__main__':
    test()

