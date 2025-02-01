from app import MyApp
from files import FileSizeCalculator

def main():
    worker = FileSizeCalculator()
    app = MyApp(worker)
    app.run()

if __name__ == '__main__':
    main()
