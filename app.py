from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather, Dial

app = Flask(__name__)

# ➊ List of spam phrases
SPAM_KEYWORDS = ["loan", "finance", "refinance", "debt", "interest rate"]

# ➋ Where to send real calls
FORWARDING_NUMBER = "+12154319224"          # your cellphone

# ➌ A Twilio number you own (shows up on caller-ID)
CALLER_ID = "+1XXXYYYZZZZ"                  # replace with your Twilio number

@app.route("/voice", methods=["POST"])
def voice():
    """Initial webhook: ask why the caller is calling."""
    resp = VoiceResponse()

    # Tell Twilio to POST results to /gather
    gather = Gather(
        input="speech",
        action="/gather",
        method="POST",      # ← make sure it’s POST
        timeout=5,
        speech_timeout="auto",
        language="en-US"
    )
    gather.say(
        "Hi, this is Eric's assistant. "
        "May I ask why you're calling today?",
        voice="Polly.Joanna"
    )
    resp.append(gather)

    # Runs only if no speech is captured
    resp.say("Sorry, I didn't catch that. Goodbye.", voice="Polly.Joanna")
    return Response(str(resp), mimetype="text/xml")

@app.route("/gather", methods=["POST"])
def gather():
    """Handle the speech result and decide to block or forward."""
    speech_result = request.form.get("SpeechResult", "").lower()
    resp = VoiceResponse()

    if any(keyword in speech_result for keyword in SPAM_KEYWORDS):
        resp.say(
            "Thank you. We're not interested. "
            "Please remove us from your call list.",
            voice="Polly.Joanna"
        )
        resp.hangup()
    else:
        resp.say("Thanks. Connecting you now.", voice="Polly.Joanna")

        # Forward the call and set a proper caller ID
        dial = Dial(caller_id=CALLER_ID)
        dial.number(FORWARDING_NUMBER)
        resp.append(dial)

    return Response(str(resp), mimetype="text/xml")

if __name__ == "__main__":
    app.run(debug=True)
