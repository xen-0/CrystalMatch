from copy import deepcopy


def agreeing_subset_indices(data, agree):
    """Return index sets corresponding to internally agreeing data subsets.

    Best illustrated by example:
    ```
    >>> agreeing_subset_indices([1, 7, 2, 1, 21, 23, 8],
    ...                          lambda x, y: abs(x - y) < 5)
    set([frozenset([0, 2, 3]), frozenset([1, 6]), frozenset([4, 5])])
    ```

    Not all pairs of members of an internally agreeing subset must mutually
    agree -- there only has to exist a chain of agreement linking them.
    For instance:
    ```
    >>> agreeing_subset_indices([0.1, 0.5, 0.9, 2.1, 2.5],
    ...                          lambda x, y: abs(x - y) < 0.6)
    set([frozenset([3, 4]), frozenset([0, 1, 2])])
    ```
    `0.1` and `0.9` do not "agree" directly, but are in the same agreement set
    because they share agreement with `0.5`.
    """
    soias = set()  # Set of internally agreeing sets.
    for i, some_datum in enumerate(data):
        for j, other_datum in popped(enumerate(data), i):
            if agree(some_datum, other_datum):
                soias.add(frozenset({i, j}))
                soias = intersecting_sets_joined(soias)
    return soias


def intersecting_sets_joined(sets):
    """Join intersecting sets, to return distinct non-intersecting sets (pure).
    """
    sets = map(set, sets)  # Thaw frozen sets. (Make a local, mutable copy.)
    sets_to_pop = set()
    for i, s in enumerate(sets):
        for j, o in list(enumerate(sets))[i+1:]:
            if s & o != set():
                s |= o
                sets_to_pop.add(j)
    for j in reversed(sorted(list(sets_to_pop))):
        sets.pop(j)
    return set(map(frozenset, sets))


def popped(orig_list, index):
    """Pure functional list pop.
    """
    copy = deepcopy(list(orig_list))
    copy.pop(index)
    return copy
