
import json, urllib.request, websocket, time
BASE='http://127.0.0.1:9222'
tabs=json.load(urllib.request.urlopen(BASE+'/json', timeout=10))
tab=next((t for t in tabs if 'adsterra' in t.get('url','')), None)
ws=websocket.create_connection(tab['webSocketDebuggerUrl'], timeout=90, suppress_origin=True)
mid=[0]
def js(e):
    mid[0]+=1
    ws.send(json.dumps({'id':mid[0],'method':'Runtime.evaluate','params':{'expression':e,'returnByValue':True,'awaitPromise':True}}))
    while True:
        m=json.loads(ws.recv())
        if m.get('id')==mid[0]:
            r=m.get('result',{})
            if 'exceptionDetails' in r: return 'EXC '+json.dumps(r['exceptionDetails'])[:200]
            return r.get('result',{}).get('value')
js("location.href='https://publishers.adsterra.com/websites/6030096/placements'")
time.sleep(9)
print('URL:', js('location.href'))
print('TITLE:', js('document.title'))
print('BODY:', str(js('document.body.innerText'))[:800])
