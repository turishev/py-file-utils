import os
import sys
from app import MyApp
from files import FileOps

def main(args):
    print("args:" + str(args))
    if (len(args) > 1):
        root_dir = args[1]
        auto_run = True
    else:
        root_dir = os.getcwd()
        auto_run = False

    worker = FileOps(root_dir)
    app = MyApp(worker, __file__, auto_run)
    app.run()


if __name__ == '__main__':
    main(sys.argv)
