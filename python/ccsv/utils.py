
def pairwise(iterable):
    "s - > (s0, s1), (s1, s2), (s2, s3), ..."
    a = iter(iterable)
    b = iter(iterable)
    next(b, None)
    return zip(a, b)

