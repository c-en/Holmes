from PIL import Image
from script import VisionApi
import time
import pytesseract

def testOCR(setNum, start, end):
    totalPy = 0
    totalGoog = 0
    for i in range(start, end + 1):
        img = 'questions/Set-' + str(setNum) + '/Q' + str(i) + '.png'
        print("***************************")
        startTime = time.time()
        res = pytesseract.image_to_string(Image.open(img)).split('\n')
        stop = time.time() - startTime
        print("Q" + str(i) + " (pytesseract): " + str(stop))
        totalPy += stop
        print(res)

        myVision = VisionApi()
        startTime = time.time()
        res = myVision.detect_text([img])[img][0]["description"].split("\n")
        stop = time.time() - startTime
        print("Q" + str(i) + " (google OCR): " + str(stop))
        totalGoog += stop
        print(res)

    print("\nAvg (pytesseract): " + str(totalPy / (end - start + 1)))
    print("Avg (google OCR): " + str(totalGoog / (end - start + 1)))

testOCR(1, 1, 12)