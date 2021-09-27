import socketio

def my_headers():
    return {"origin": "*"}

#socketEndpoint = 'https://stream.coindcx.com (https://stream.coindcx.com/)'
socketEndpoint = 'wss://stream.coindcx.com/'
sio = socketio.Client(engineio_logger=True, logger=True)
sio.connect(socketEndpoint)
sio.emit('join', {'channelName': 'B-BTC_USDT'})

@sio.event
def connect():
    print("I'm connected!")

@sio.event
def connect_error(data):
    print("The connection failed!")

@sio.on('depth-update')
def on_message(response):
    print(response['data'])