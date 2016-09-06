__author__ = 'jialingliu'


# rotate(l,n) takes a list l and an integer n, and returns a new list with the first n elements moved to the end.
#
# Example:
#   rotate([1,2,3,4], 3) -> [4,1,2,3]
def rotate_list(l, n):
    return l[n:] + l[0:n]


# reverse_dict(d) takes a dictionary d, and returns a new dictionary with the keys and values swapped.
# Assume all values of the given dictionary are unique, i.e. don't worry about conflicting keys.
#
# Example:
#   reverse_dict({"apple" : "red", "banana" : "yellow"}) -> {"red" : "apple", "yellow" : "banana"}
def reverse_dict(d):
    return dict((v, k) for k, v in d.iteritems())


def main():
    l = [1, 2, 3, 4]
    n = 3
    print rotate_list(l, n)

    d = {"apple": "red", "banana": "yellow"}
    print reverse_dict(d)


if __name__ == main():
    main()
