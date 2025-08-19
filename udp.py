import cv2 as cv
import requests

ROOT = '172.29.197.51:8080'     # GP http endpoint 
RES = '1080'                    # stream res, supported: 480, 720, 1080
PORT = '8554'                   # UDP Port, 8554 = default
FLAGS = '?overrun_nonfatal=1'   # we might overflow the ffmpeg buffer, this prevents the stream from crashing.

req0 = requests.get(url = f'http://{ROOT}/gp/gpWEBCAM/START?res={RES}', timeout = 2)
print(f'🔊 🔊 🔊 Commanded UDP stream to start via {req0.url}')
if req0.status_code == 200:
    print('RC 200, stream is running.')
else:
    print(f'RC was {req0.status_code}. RIP')
    raise RuntimeError('Camera failed to start!')

stream = cv.VideoCapture(f'udp://@:{PORT}{FLAGS}')

while(stream.isOpened() != True):
    print('🚨 ALTA stream is not even open yet!!!!')
print('🔑 GOLD GOLD GOLD Stream is open now!!!')

while(True):
    ret, frame = stream.read()
    
    try:
        cv.imshow("Output", frame)
    except:
        pass
    
    key = cv.waitKey(1)

    if key == ord('q'):
        break
    
cv.destroyAllWindows()
stream.release()
req1 = requests.get(url = f'http://{ROOT}/gp/gpWEBCAM/STOP')
print(f'🔊 🔊 🔊 Commanded UDP stream to stop via {req1.url}')