class MyClass:
    def my_method(self):
        flag = bool(self)
        try:
            raise ValueError("oops")
        except ValueError as e:
            print(e)
        return flag
