# 单本书籍信息包装模型
class BookViewModel:
    def __init__(self, book_data):
        self.title = book_data["title"]
        self.author = book_data["author"]
        self.publisher = book_data["publisher"] or ""
        self.price = book_data["price"]
        self.summary = book_data["summary"]
        self.image = book_data["pictures"]
        self.pages = book_data["pages"]


# 多本书籍信息包装模型
class BookCollectionViewModel:
    def __init__(self):
        self.total = 0
        self.books = []
        self.keyword = ""

    def fill(self, yushu_book, keyword):
        self.total = yushu_book.total
        self.books = [BookViewModel(book) for book in yushu_book.books]
        self.keyword = keyword


# # 书籍数据包装模型
# class BookViewModel:
#   # 包装单本书籍信息 - 单本也需要是一个数组返回给前端
#   # data: 书籍原始数据

#   @classmethod
#   def pakage_single(cls,data,keyword):
#     returned = {
#       'records': [],
#       'total': 0,
#       'keyword': keyword
#     }
#     if data:
#       returned['records'] = [cls.cut_book_data(data)]
#       returned['total'] = 1
#     return returned

#   # 包装多本书籍信息
#   @classmethod
#   def package_collection(cls,data,keyword):
#     returned = {
#       'records': [],
#       'total': 0,
#       'keyword': keyword
#     }
#     if data:
#       returned['records'] = [cls.cut_book_data(data) for data in data['records']]
#       returned['total'] = len(data['total'])
#     return returned

#   # 剪裁书籍数据
#   @classmethod
#   def cut_book_data(cls,data):
#     book_data = {
#       'title': data['title'],
#       'author': data['author'],
#       'publisher': data['publisher'] or '',
#       'price': data['price'],
#       'summary': data['summary'],
#       'image': data['pictures']
#     }
#     return book_data
