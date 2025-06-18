from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather, Dial

app = Flask(__name__)

# Define spam keywords
SPAM_KEYWORDS = ["loan", "finance", "refinance", "debt", "interest rate"]

# Replace with your real forwarding number
FORWARDING_NUMBER = "+1234567890"

@app.route("/voice", methods=["POST"])
def voice():
    resp = VoiceResponse()
    gather = Gather(input="speech", action="/gather", timeout=5)
    gather.say("Hi, this is Eric's assistant. May I ask why you're calling today?", voice="Polly.Joanna")
    resp.append(gather)
    resp.say("Sorry, I didn't catch that. Goodbye.", voice="Polly.Joanna")
    return Response(str(resp), mimetype="text/xml")

@app.route("/gather", methods=["POST"])
def gather():
    speech_result = request.form.get("SpeechResult", "").lower()
    resp = VoiceResponse()
    if any(keyword in speech_result for keyword in SPAM_KEYWORDS):
        resp.say("Thank you. We're not interested. Please remove us from your call list.", voice="Polly.Joanna")
        resp.hangup()
    else:
        resp.say("Thanks. Connecting you now.", voice="Polly.Joanna")
        dial = Dial()
        dial.number(FORWARDING_NUMBER)
        resp.append(dial)
    return Response(str(resp), mimetype="text/xml")

if __name__ == "__main__":
    app.run(debug=True)
