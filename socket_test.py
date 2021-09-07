
import socketio


channelName = 'B-SNM_BTC'
socketEndpoint = 'wss://stream.coindcx.com'
sio = socketio.Client()

sio.connect(socketEndpoint, transports = 'websocket')
sio.emit('join', { 'channelName': channelName })

# Listen update on channelName
@sio.on(channelName)
def on_message(response):
    print(response.data)

# leave a channel
sio.emit('leave', { 'channelName' : channelName })

'''
from websocket import create_connection
ws = create_connection("wss://stream.coindcx.com")
result =  ws.recv()
print ("Received '%s'" % result)
ws.close()
'''

