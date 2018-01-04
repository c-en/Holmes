import base64
import time
start = time.time()

from search import count_hits
from googleapiclient import discovery
from googleapiclient import errors
from oauth2client.client import GoogleCredentials

DISCOVERY_URL = 'https://{api}.googleapis.com/$discovery/rest?version={apiVersion}'  # noqa
BATCH_SIZE = 10


class VisionApi:
    """Construct and use the Google Vision API service."""

    def __init__(self, api_discovery_file='vision_api.json'):
        self.credentials = GoogleCredentials.get_application_default()
        self.service = discovery.build(
            'vision', 'v1', credentials=self.credentials,
            discoveryServiceUrl=DISCOVERY_URL)

    def detect_text(self, input_filenames, num_retries=3, max_results=6):
        """Uses the Vision API to detect text in the given file.
        """
        images = {}
        for filename in input_filenames:
            with open(filename, 'rb') as image_file:
                images[filename] = image_file.read()

        batch_request = []
        for filename in images:
            batch_request.append({
                'image': {
                    'content': base64.b64encode(
                            images[filename]).decode('UTF-8')
                },
                'features': [{
                    'type': 'TEXT_DETECTION',
                    'maxResults': max_results,
                }]
            })
        request = self.service.images().annotate(
            body={'requests': batch_request})

        try:
            responses = request.execute(num_retries=num_retries)
            if 'responses' not in responses:
                return {}
            text_response = {}
            for filename, response in zip(images, responses['responses']):
                if 'error' in response:
                    print("API Error for %s: %s" % (
                            filename,
                            response['error']['message']
                            if 'message' in response['error']
                            else ''))
                    continue
                if 'textAnnotations' in response:
                    text_response[filename] = response['textAnnotations']
                else:
                    text_response[filename] = []
            return text_response
        except errors.HttpError as e:
            print("Http Error for %s: %s" % (filename, e))
        except KeyError as e2:
            print("Key error: %s" % e2)

def createDict(text):
    result = {}
    result["question"] = ""
    for i in range(len(text) - 4):
        result["question"] += text[i] + " "
    result["question"] = result["question"].replace("'", " ")
    result["question"] = result["question"].replace('"', " ")

    result["a1"] = text[-4]
    result["a2"] = text[-3]
    result["a3"] = text[-2]
    return result

def singleTest(filename):
    myVision = VisionApi()
    text = myVision.detect_text([filename])[filename][0]["description"].split("\n")
    result = createDict(text)
    print(result)
    print(count_hits(result))

def multipleTests(start, end):
    texts = []
    for i in range(start, end + 1):
        texts.append("questions/Q" + str(i) + ".png")
    myVision = VisionApi()
    result = myVision.detect_text(texts)
    #print(result["questions/Q22.png"])

    for i in range(start, end + 1):
        text = result["questions/Q" + str(i) + ".png"][0]["description"].split("\n")
        final = createDict(text)
        # print(final)
        answer = count_hits(final)
        print(answer)

#singleTest("questions/Q8.png")
multipleTests(13, 24)

