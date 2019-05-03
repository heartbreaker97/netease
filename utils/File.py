"""
文件IO
"""
def saveFile(fileName, data):
    with open(fileName, 'a+', encoding='utf-8') as file:
        file.write(data)


def saveBinary(fileName, data):
    with open(fileName, 'ab+') as file:
        file.write(data)
    return file.name

def readFile(fileName):
    data = []
    try:
        with open(fileName, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip('\n')
                data.append(line)
    except Exception as e:
        print(str(e))
    return data

