def read_value():
    try:
        data = open("data.txt")
    except OSError as exc:
        data = None
    finally:
        pass
    return data


print(read_value())
