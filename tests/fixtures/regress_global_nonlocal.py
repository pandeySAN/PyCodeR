count = 0


def increment():
    global count
    count = count + 1
    return count


def outer():
    total = 0

    def inner():
        nonlocal total
        total = total + 1
        return total

    return inner()


increment()
outer()
print(count)
