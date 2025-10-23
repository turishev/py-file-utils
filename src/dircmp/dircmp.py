import os
import sys
from app import MyApp

def main(args):
    print("args:" + str(args))
    dir_a = args[1] if (len(args) > 1) else None
    dir_b = args[2] if (len(args) > 2) else None
    app = MyApp(dir_a, dir_b)
    app.run()


if __name__ == '__main__':
    main(sys.argv)
