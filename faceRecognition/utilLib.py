import numpy as np


def printAllDistance(Dict):
    keyList = list(Dict)
    print("=====================================")
    for i in range(len(keyList)):
        print("\n\ndistance between {} and:".format(keyList[i][7:-4]))

        j = i+1
        while(j < len(keyList)):
            print("{} : ".format(
                keyList[j][7:-4]), np.linalg.norm(Dict[keyList[j]]-Dict[keyList[i]]))
            j += 1


def prewhiten(x):
    mean = np.mean(x)
    std = np.std(x)
    # print(mean, std)
    std_adj = np.maximum(std, 1.0/np.sqrt(x.size))
    y = np.multiply(np.subtract(x, mean), 1/std_adj)
    return y


def normL2Vector(bottleNeck):
    sum = 0
    for v in bottleNeck:
        sum += np.power(v, 2)
    sqrt = np.max([np.sqrt(sum), 0.0000000001])
    vector = np.zeros((bottleNeck.shape))
    for (i, v) in enumerate(bottleNeck):
        vector[i] = v/sqrt
    return vector.astype(np.float32)
