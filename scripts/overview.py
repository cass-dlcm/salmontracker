import sys

sys.path.insert(0, ".")
import core

if __name__ == "__main__":
    data = core.init("All")
    print(core.getOverview(data))
