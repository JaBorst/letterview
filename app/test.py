import requests
res = requests.post('http://0.0.0.0:5000/ptagcloudapi', s={"sql":"Select * from letters;"})#json={"mytext":"lalala"})
