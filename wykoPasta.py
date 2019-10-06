import jsonpickle
import os.path
import os
import datetime
import time
import requests
from lxml import html


def ReadPasta():
    words = []
    with open('pasta.txt', encoding="utf-8") as openfileobject:
        for line in openfileobject:
            for word in line.split():
                words.append(word)
    return words

def WriteMetaToFile(meta):
    fname = "pasta_meta.txt"
    if(not os.path.isfile(os.getcwd()+ "\\" + fname)):
        with open(fname, mode="w") as openfileobject:
            openfileobject.write(meta)
    else:
        print("Meta already exists!")

def ReWriteMetaToFile(meta):
    fname = "pasta_meta.txt"
    if(os.path.isfile(os.getcwd()+ "\\" + fname)):
        with open(fname, mode="w") as openfileobject:
            openfileobject.flush()
            openfileobject.write(meta)
    else:
        print("Trying to rewrite non-existing meta!")

def ReadMetaFromFile():
    fname = "pasta_meta.txt"
    if(os.path.isfile(os.getcwd() + "\\" + fname)):
        with open(fname, mode="r") as openfileobject:
            return jsonpickle.decode(openfileobject.read())
    else:
        print("Meta file not found!")
        return None

class StructureElement:
    def __init__(self, index, word):
        self.index = index
        self.word = word
        self.url = None
        self.postTime = datetime.datetime(1900, 1, 1)
    def __str__(self):
        return f'{self.index}: {self.word}, {self.url}, {self.postTime}\n'

def PrepareStructure():
    allWords = ReadPasta()
    print(allWords)
    print(f'Total words count: {len(allWords)}')
    allStructures = []
    index = 1
    for word in allWords:
        allStructures.append(StructureElement(index, word))
        index += 1
    return allStructures

def PrepareMeta():
    meta = ReadMetaFromFile()
    if(meta is None):
        meta = PrepareStructure()
        WriteMetaToFile(jsonpickle.dumps(meta))
    return meta

def UpdateMeta(meta):
    ReWriteMetaToFile(jsonpickle.dumps(meta))

def PreparePostContent(nextPostData):
    nextWord = nextPostData.word
    nextWordIndex = nextPostData.index

    content = f'Słowo numer {nextWordIndex}!\n> {nextWord}\n'

    suffix = "! ==========================================\n! ==========================================\n! ==========================================\n! Pasty pisane słowo po słowie! #pastyananasa"
    return content + suffix

def CreatePostAndGetLink(session, token, postContent):
    payload = {"body" : postContent,
            "parent_id" : ""}
    headers = {
        'sec-fetch-mode': "cors",
        'origin': "https://www.wykop.pl",
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
        'content-type': "application/x-www-form-urlencoded",
        'accept': "application/json, text/javascript, */*; q=0.01",
        'x-requested-with': "XMLHttpRequest",
        'dnt': "1",
        'cache-control': "no-cache",
        }

    url = "https://www.wykop.pl/ajax2/wpis/dodaj/hash/" + token
    response = session.post(url, data=payload, headers=headers)
    urlBeginning = response.text.replace('\\', '').find('https://www.wykop.pl/wpis/')
    textBeginningWithUrl = response.text.replace('\\', '')[urlBeginning : len(response.text.replace('\\', ''))]
    urlEnd = response.text.replace('\\', '')[response.text.replace('\\', '').find('https://www.wykop.pl/wpis/') : len(response.text)].find('/"')
    finalUrl = textBeginningWithUrl[0:urlEnd]
    if finalUrl is None or finalUrl == ''
        print("Coś poszło nie tak [ban? xD]")
    return finalUrl

def mainProgramLoop():
    metaData = PrepareMeta()
    finished = 0
    with requests.Session() as session:

##login
        uName = 'REPLACEME'
        passwd =  'REPLACEME'

        payload = {
        "user[username]" : uName,
        "user[password]" : passwd}

        session.post('https://www.wykop.pl/zaloguj/', data=payload)
        result = session.get('https://www.wykop.pl/mikroblog/')
        if "Zaloguj się" in result.text:
            raise Exception("Nie udało się zalogować! Jestem leniwy, odpal całość od nowa.")
        print("Bardzo ładnie, udało się zalogować.")

        tree = html.fromstring(result.content)
        token = tree.xpath("//p/input[@id='__token']/@value")[0]
##end login

        while(not finished):
            nextPostData = None
            for meta in metaData:
                if(meta.url is None):
                    nextPostData = meta
                    break
            if(nextPostData is None):
                finished = 1
                break
            postValue = PreparePostContent(nextPostData)
            linkToPost = CreatePostAndGetLink(session, token, postValue)
            nextPostData.url = linkToPost
            nextPostData.postTime = datetime.datetime.now()
            UpdateMeta(metaData)
            secondsToSleep = 30
            print(nextPostData)
            print(f"Posted {nextPostData.word}! Sleeping now for {secondsToSleep} seconds!")
            time.sleep(secondsToSleep)

mainProgramLoop()