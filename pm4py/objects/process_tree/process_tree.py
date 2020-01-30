from pm4py.objects.process_tree import pt_operator

class ProcessTree(object):

    def __init__(self, operator=None, parent=None, children=None, label=None):
        """
        Constructor

        Parameters
        ------------
        operator
            Operator (of the current node) of the process tree
        parent
            Parent node (of the current node)
        children
            List of children of the current node
        label
            Label (of the current node)
        """
        self._operator = operator
        self._parent = parent
        self._children = list() if children is None else children
        self._label = label

    def _set_operator(self, operator):
        self._operator = operator

    def _set_parent(self, parent):
        self._parent = parent

    def _set_label(self, label):
        self._label = label

    def _set_children(self, children):
        self._children = children

    def _get_children(self):
        return self._children

    def _get_parent(self):
        return self._parent

    def _get_operator(self):
        return self._operator

    def _get_label(self):
        return self._label

    def __eq__(self, other):
        if self.label is not None:
            return True if other.label == self.label else False
        else:
            if self.operator == other.operator:
                if len(self.children) != len(other.children):
                    return False
                if self.operator in [pt_operator.Operator.SEQUENCE, pt_operator.Operator.LOOP]:
                    for i in range(len(self.children)):
                        if self.children[i] != other.children[i]:
                            return False
                    return True
                elif self.operator in [pt_operator.Operator.PARALLEL, pt_operator.Operator.XOR]:
                    matches = list(range(len(self.children)))
                    for i in range(len(self.children)):
                        mm = [m for m in matches]
                        for j in mm:
                            if self.children[i] == other.children[j]:
                                matches.remove(j)
                                break
                    return True if len(matches)==0 else False
            else:
                return False


    def __repr__(self):
        """
        Returns a string representation of the process tree

        Returns
        ------------
        stri
            String representation of the process tree
        """
        if self.operator is not None:
            rep = str(self._operator) + '( '
            for i in range(0, len(self._children)):
                child = self._children[i]
                rep += str(child) + ', ' if i < len(self._children) - 1 else str(child)
            return rep + ' )'
        elif self.label is not None:
            return self.label
        else:
            return u'\u03c4'

    def __str__(self):
        """
        Returns a string representation of the process tree

        Returns
        ------------
        stri
            String representation of the process tree
        """
        return self.__repr__()

    def _get_root(self):
        root = self
        while root._get_parent() is not None:
            root = root._get_parent()
        return root

    def _get_leaves(self):
        root = self._get_root()
        leaves = root
        if root._get_children != list():
            leaves = root._get_children()
            change_of_leaves = True
            while change_of_leaves:
                leaves_to_replace = list()
                new_leaves = list()
                for leaf in leaves:
                    if leaf._get_children() != list():
                        leaves_to_replace.append(leaf)
                    else:
                        new_leaves.append(leaf)
                if leaves_to_replace != list():
                    for leaf in leaves_to_replace:
                        for el in leaf.children:
                            new_leaves.append(el)
                    leaves = new_leaves
                else:
                    change_of_leaves = False
        return leaves

    def _print_tree(self):
        root = self._get_root()
        print(root)

    parent = property(_get_parent, _set_parent)
    children = property(_get_children, _set_children)
    operator = property(_get_operator, _set_operator)
    label = property(_get_label, _set_label)
