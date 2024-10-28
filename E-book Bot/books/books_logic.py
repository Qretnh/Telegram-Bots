class Book:

    def __init__(self, folder_name=None):
        self.folder_name = folder_name
        self.desc = None
        self.pages = {}
        self.length = 0

        if folder_name:
            self.load_book()

    def load_book(self):
        with open(f'books/{self.folder_name}.txt', encoding='utf-8') as file:
            text = file.read().split('.')
            page = ''
            num = 1
            for sentence in text:
                if len(page) < 1000:
                    page = page + sentence
                else:
                    self.pages[num] = page
                    page = ''
                    num += 1
        self.length = len(self.pages)

    def get_page(self, page=3):
        return self.pages[page]


Men_From_Mars = Book('Men')

Book_shelf = {'Men_From_Mars': Men_From_Mars}