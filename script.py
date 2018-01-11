# Main Script

def singleTest(filename, ocr="google", search="multithread"):
    start = time.time()
    myVision = VisionApi()
    text = myVision.detect_text([filename])[filename][0]["description"].split("\n")
    result = createDict(text)
    print(process(result))

def multipleTests(setNum, start, end, ocr="google", search="multithread"):
    texts = []
    for i in range(start, end + 1):
        texts.append("questions/Set-" + str(setNum) + "/Q" + str(i) + ".png")
    myVision = VisionApi()
    result = myVision.detect_text(texts)

    for i in range(start, end + 1):
        start = time.time()
        text = result["questions/Set-" + str(setNum) + "/Q" + str(i) + ".png"][0]["description"].split("\n")
        final = createDict(text)
        answer = process(final)
        print("Total time for search: " + str(time.time() - start))
        print(answer)

#singleTest("question2.png")
multipleTests(1, 1, 12)

