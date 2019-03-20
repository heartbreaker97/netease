def saveFile(fileName, data):
    with open(fileName, 'a+', encoding='utf-8') as file:
        file.write(data)


def saveBinary(fileName, data):
    with open(fileName, 'ab+') as file:
        file.write(data)
    return file.name
