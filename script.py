# Main Script
import time
from search import process
from ocr import detect_text
import pyscreenshot as ImageGrab

def single_test(filename, ocr="google", searchMethod="multithread"):
    result = detect_text(filename, ocr)
    print process(result, searchMethod)

def multiple_tests(setNum, start, end, ocr="google", searchMethod="multithread"):
    for i in range(start, end + 1):
        print "***********************************"
        start = time.time()
        filename = 'questions/Set-' + str(setNum) + '/Q' + str(i) + '.png'
        result = detect_text(filename, ocr)
        print process(result, searchMethod)
        print "Total time: " + str(time.time() - start)

def run_holmes():
    print "Running Holmes...."
    while True:
        raw_input("Press enter when next question is ready. ")
        im = ImageGrab.grab(bbox=(1314,140,1659,480))
        im.save("question.png")
        single_test("question.png", "pytesseract", "multithread")

# single_test("questions/Set-6/Q3.png")
# multiple_tests(6, 1, 4)
run_holmes()