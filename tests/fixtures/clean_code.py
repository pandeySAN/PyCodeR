def add(a, b):
    return a + b


def multiply(a, b):
    return a * b


def greet(name):
    return f"Hello, {name}!"


def main():
    x = 5
    y = 10
    
    result = add(x, y)
    print(result)
    
    product = multiply(x, y)
    print(product)
    
    message = greet("World")
    print(message)
    
    return 0


if __name__ == "__main__":
    main()
