import os
import sys
from app import MyApp

def main(args):
    print("args:" + str(args))
    root_dir = args[1] if (len(args) > 1) else None
    app = MyApp(root_dir)
    app.run()


if __name__ == '__main__':
    main(sys.argv)
