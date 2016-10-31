from time import time
from flask import Flask, render_template, jsonify, request
import collections
app = Flask(__name__)

messages = collections.deque()

MESSAGE_TIMEOUT = 10
FLOOD_MESSAGES = 5
FETCH_FREQ = 1000

class Message(object):
    def __init__(self, nick, text):
        self.time = time()
        self.nick = nick
        self.text = text

    def json(self):
        return {
            'text': self.text,
            'nick': self.nick,
            'time': self.time
        }

@app.route('/')
@app.route('/<channel>')
def on_index(channel='lobby'):
    return render_template('index.html')

@app.route('/api/info')
def on_info():
    return jsonify({
        'server_name': 'Flask Test Chat',
        'server_time': time(),
        'refresh_interval': 1000
    })

@app.route('/api/send_message', methods=['POST'])
def on_message():
    text = request.form.get('text', '')
    nick = request.form.get('nick', '')

    if ':' in nick:
        nick, token = nick.split(':', 1)
    else:
        token = ''
        nick = nick.strip()

    if not text:
        return jsonify({'error': 'No text.'})
    if not nick:
        return jsonify({'error': 'No nick.'})


    # Garbage collection (delete old messages from cache)
    timeout = time() - MESSAGE_TIMEOUT
    while messages and messages[0].time < timeout:
        messages.popleft()

    # Flood protection
    if len([m for m in messages if m.nick == nick]) > FLOOD_MESSAGES:
        return jsonify({'error': 'Messages arrive too fast.'})

    messages.append(Message(nick, text))
    return jsonify({'status': 'OK'})

@app.route('/api/fetch')
def on_fetch():
    '''Return all messages of the last ten seconds. '''
    since = float(request.args.get('since', 0))
    # Fetch new messages
    updates = [m.json() for m in messages if m.time > since]
    # Send up to 10 messages at once.
    return jsonify({'messages': updates[:10]})

if __name__ == "__main__":
    app.run(debug=True)
