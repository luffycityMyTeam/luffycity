class BaseResponse(object):

    def __init__(self):
        self.code = 1000

    @property  # 使调用这个方法时可以不加括号
    def dict(self):
        return self.__dict__  # 返回类的所有字典
