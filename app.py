"""
Flask voice-assistant webhook for Twilio
• Blocks calls that mention loans/finance/etc.
• Forwards anything else to your cellphone
"""

import re
import sys
import string
from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather, Dial

app = Flask(__name__)

# 1️⃣ Spam term regex (word-boundary, case-insensitive)
SPAM_REGEX = re.compile(
    r"\b(loan|loans?|finance|financial|refinance|refinancing|debt|interest\s+rate)\b",
    re.IGNORECASE,
)

# 2️⃣ Forwarding + caller-ID numbers (E.164)
FORWARDING_NUMBER = "+12154319224"   # your cellphone
CALLER_ID        = "+18338621007"    # your Twilio number

def normalize(text: str) -> str:
    """
    Lower-case and strip punctuation so
    'Loan.'  -> 'loan'
    'interest-rate,' -> 'interest rate'
    """
    text = text.lower()
    return text.translate(str.maketrans(string.punctuation, " " * len(string.punctuation)))

@app.route("/voice", methods=["POST"])
def voice():
    """Greets the caller and asks why they're calling."""
    resp = VoiceResponse()
    gather = Gather(
        input="speech",
        action="/gather",
        method="POST",
        timeout=7,
        speech_timeout="auto",
        language="en-US",
        hints="loan, finance, refinance, debt, interest rate",
    )
    gather.say(
        "Hi, this is Eric's assistant. "
        "May I ask why you’re calling today?",
        voice="Polly.Joanna",
    )
    resp.append(gather)

    # Runs only if Twilio never got any speech at all
    resp.say("Sorry, I didn't catch that. Goodbye.", voice="Polly.Joanna")
    return Response(str(resp), mimetype="text/xml")

@app.route("/gather", methods=["POST"])
def gather():
    """Blocks spam or forwards the call."""
    raw_speech = request.form.get("SpeechResult", "")
    clean_speech = normalize(raw_speech)

    # 🔍 Log what Twilio heard after normalization
    print(f"[Twilio STT] raw='{raw_speech}'  clean='{clean_speech}'",
          file=sys.stderr, flush=True)

    resp = VoiceResponse()

    if SPAM_REGEX.search(clean_speech):
        # -- Block the call
        resp.say(
            "Thank you. We're not interested. "
            "Please remove us from your call list.",
            voice="Polly.Joanna",
        )
        resp.hangup()
    else:
        # -- Forward legitimate calls
        resp.say("Thanks. Connecting you now.", voice="Polly.Joanna")
        dial = Dial(caller_id=CALLER_ID)
        dial.number(FORWARDING_NUMBER)
        resp.append(dial)

    return Response(str(resp), mimetype="text/xml")

if __name__ == "__main__":
    app.run(debug=True)
