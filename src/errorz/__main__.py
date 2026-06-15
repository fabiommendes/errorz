import doctest

import errorz

if __name__ == "__main__":
    doctest.testmod(errorz, globs={"rz": errorz})
