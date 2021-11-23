import sys

from utils.entity.appentity import AppEntity

if __name__ == "__main__":
    app = AppEntity(sys.argv[1])
    app.run()
