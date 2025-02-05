from app import MyApp
from files import FileOps

def main():
    worker = FileOps()
    app = MyApp(worker)
    app.run()

if __name__ == '__main__':
    main()
