"""
Flask voice-assistant webhook for Twilio
---------------------------------------
 • Blocks calls mentioning loans/finance/etc.
 • Forwards legitimate calls to your cell
"""

import re
import sys
from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather, Dial

app = Flask(__name__)

# 1️⃣ Regex of spam terms (word-boundary, case-insensitive)
SPAM_REGEX = re.compile(
    r"\b(loan|loans?|finance|financial|refinance|refinancing|debt|interest\s+rate)\b",
    re.IGNORECASE,
)

# 2️⃣ Forwarding + caller-ID numbers (E.164 format)
FORWARDING_NUMBER = "+12154319224"   # ← your cellphone
CALLER_ID        = "+18338621007"    # ← a Twilio number you own

@app.route("/voice", methods=["POST"])
def voice():
    """Greets the caller and asks why they're calling."""
    resp = VoiceResponse()

    gather = Gather(
        input="speech",
        action="/gather",
        method="POST",          # Twilio will POST to /gather
        timeout=7,              # a little more time to speak
        speech_timeout="auto",
        language="en-US",
        hints="loan, finance, refinance, debt, interest rate",
    )
    gather.say(
        "Hi, this is Eric's assistant. "
        "May I ask why you're calling today?",
        voice="Polly.Joanna",
    )
    resp.append(gather)

    # If nothing was said
    resp.say("Sorry, I didn't catch that. Goodbye.", voice="Polly.Joanna")
    return Response(str(resp), mimetype="text/xml")


@app.route("/gather", methods=["POST"])
def gather():
    """Blocks spam or forwards the call."""
    speech_result = request.form.get("SpeechResult", "")

    # 🔍 See exactly what Twilio heard
    print(f"[Twilio STT] → {speech_result}", file=sys.stderr, flush=True)

    resp = VoiceResponse()

    if SPAM_REGEX.search(speech_result):
        resp.say(
            "Thank you. We're not interested. "
            "Please remove us from your call list.",
            voice="Polly.Joanna",
        )
        resp.hangup()
    else:
        resp.say("Thanks. Connecting you now.", voice="Polly.Joanna")
        dial = Dial(caller_id=CALLER_ID)   # show your Twilio number on caller-ID
        dial.number(FORWARDING_NUMBER)
        resp.append(dial)

    return Response(str(resp), mimetype="text/xml")


if __name__ == "__main__":
    app.run(debug=True)
