import requests
import os
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
SYSTEM_PROMPT = """
You are a friendly AI assistant for Arun Kumar Paul's Coaching Center.

Business Details:
- Name: Arun Kumar Paul's Coaching Center
- Owner: Arun Kumar Paul Sir
- Subjects: Maths, Science, English (Classes 6 to 12)
- Timings: Monday to Saturday, 4PM to 8PM
- Fees: 1500 per month per subject
- Free demo class available for new students
- Location: Ask customer to contact directly for address

Rules:
- Reply in Hindi or English based on what the customer writes
- Keep replies short and warm
- If you don't know something, say "Please contact Arun Sir directly"
- Never make up details not listed above
"""

HTML = """<!DOCTYPE html>
<html>
<head>
<title>Arun Kumar Paul's Coaching Center</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:Arial,sans-serif}
body{background:#ECE5DD;height:100vh;display:flex;flex-direction:column}
.header{background:#075E54;color:white;padding:10px 16px;display:flex;align-items:center;gap:10px}
.avatar{background:#25D366;border-radius:50%;width:40px;height:40px;display:flex;align-items:center;justify-content:center;font-size:20px}
.chat{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:8px}
.msg{max-width:78%;padding:10px 14px;font-size:14px;border-radius:8px;position:relative}
.user{background:#DCF8C6;align-self:flex-end;border-radius:8px 0 8px 8px}
.bot{background:white;align-self:flex-start;border-radius:0 8px 8px 8px}
.time{font-size:10px;color:#999;text-align:right;margin-top:4px}
.input-row{display:flex;padding:8px 10px;background:#F0F0F0;gap:8px}
input{flex:1;padding:12px 16px;border-radius:25px;border:none;outline:none;font-size:14px}
button{background:#075E54;color:white;border:none;border-radius:50%;width:44px;height:44px;font-size:20px;cursor:pointer}
.typing-dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:#999;animation:blink 1s infinite}
.typing-dot:nth-child(2){animation-delay:0.2s}
.typing-dot:nth-child(3){animation-delay:0.4s}
@keyframes blink{0%,80%,100%{opacity:0.2}40%{opacity:1}}
</style>
</head>
<body>
<div class="header">
<div class="avatar">📚</div>
<div>
<div style="font-weight:bold;font-size:16px">Arun Kumar Paul's Coaching</div>
<div style="font-size:12px;color:#9FEACC">AI Assistant • Online</div>
</div>
</div>
<div class="chat" id="chat">
<div class="msg bot">Namaste! 🙏 Arun Kumar Paul's Coaching Center mein aapka swagat hai. Main aapki kaise madad kar sakta hoon?<div class="time">Now</div></div>
</div>
<div class="input-row">
<input type="text" id="input" placeholder="Type a message..." onkeypress="if(event.key==='Enter')send()"/>
<button onclick="send()">➤</button>
</div>
<script>
let history=[];
function getTime(){const n=new Date();return n.getHours()+':'+String(n.getMinutes()).padStart(2,'0')}
async function send(){
const input=document.getElementById('input');
const chat=document.getElementById('chat');
const msg=input.value.trim();
if(!msg)return;
input.value='';
chat.innerHTML+=`<div class="msg user">${msg}<div class="time">${getTime()}</div></div>`;
chat.scrollTop=chat.scrollHeight;
chat.innerHTML+=`<div class="msg bot" id="typing"><span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span></div>`;
chat.scrollTop=chat.scrollHeight;
history.push({"role":"user","content":msg});
const res=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg,history:history})});
const data=await res.json();
history=data.history;
document.getElementById('typing').outerHTML=`<div class="msg bot">${data.reply.replace(/\n/g,'<br>')}<div class="time">${getTime()}</div></div>`;
chat.scrollTop=chat.scrollHeight;
}
</script>
</body>
</html>"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data['message']
    history = data.get('history', [])
    history.append({"role": "user", "content": message})
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + history
        }
    )
    reply = response.json()["choices"][0]["message"]["content"]
    history.append({"role": "assistant", "content": reply})
    return jsonify({"reply": reply, "history": history})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
