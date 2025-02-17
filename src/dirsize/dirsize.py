import os
import sys
from app import MyApp

def main(args):
    print("args:" + str(args))
    if (len(args) > 1):
        root_dir = args[1]
    else:
        root_dir = None

    app = MyApp(__file__, root_dir)
    app.run()


if __name__ == '__main__':
    main(sys.argv)
