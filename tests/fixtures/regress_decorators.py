def decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


@decorator
def say(name):
    return f"Hi, {name}"


print(say("Ada"))
