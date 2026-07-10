# Assignment 2: Voice Agent Workshop

This project builds a practical voice agent for hotel reservations. It runs locally, supports offline rehearsal, and demonstrates how a voice pipeline connects to a phone-call style flow.

The core loop is:

```text
caller speech -> speech-to-text -> LLM agent with tools -> text-to-speech -> spoken reply
```

The agent is scoped to Aurora Hotel reservations. It can:

- Check room availability
- Create a mock booking
- Transfer complex requests to the front desk
- End the call cleanly
- Redirect off-topic questions back to hotel booking support

## Project Structure

```text
Assignment_2_voice_agent/
├── README.md
├── RUNBOOK.md
├── WORKSHOP_SCRIPT.md
├── pipeline/
│   ├── agent.py
│   ├── providers.py
│   ├── voice_loop.py
│   ├── smoke_test.py
│   ├── requirements.txt
│   ├── config.example.env
│   └── README.md
└── mocks/
    ├── demo_call.py
    ├── ivr_menu_mock.py
    └── sip-ivr-call-flow.md
```

## What It Demonstrates

| Layer | Purpose | Demo |
|-------|---------|------|
| Voice loop | Captures caller input, transcribes it, generates a response, and speaks it back | `pipeline/voice_loop.py` |
| Agent brain | Uses a system prompt, tools, and guardrails for hotel reservations | `pipeline/agent.py` |
| Telephony mock | Shows how SIP and RTP would wrap the same agent in a real call path | `mocks/demo_call.py` |

## Agent Behavior

The agent is intentionally narrow. It should not behave like a general assistant. If the caller asks about weather, news, trivia, coding, finance, medical advice, or other unrelated topics, it redirects them to hotel reservation support.

Example:

```text
Caller: Can you tell me the weather?
Agent: I can only help with hotel reservations. Are you looking to book, change, or cancel a stay?
```

Booking example:

```text
Caller: I need a room from August 12 to August 14 for two guests.
Agent: We have several room options available...

Caller: Book it for Priya Shah at priya@example.com.
Agent: Booking confirmed. Confirmation AH-4827...
```

## Quick Start

Run the offline smoke test first. It does not need a key, network access, audio devices, or installed SDKs beyond Python.

```bash
cd FDE/Assignment_2_voice_agent/pipeline
python smoke_test.py
```

Expected result:

```text
RESULT: PASS
```

Run the offline typed demo:

```bash
PROVIDER=mock python voice_loop.py --text
```

Try:

```text
Can you tell me the weather?
I need a room from August 12 to August 14 for two guests.
Book it for Priya Shah at priya@example.com.
Can I talk to the front desk?
```

## Live Voice Mode

Create a local environment file from the example:

```bash
cp config.example.env .env
```

Set your provider and API key in `.env`:

```env
PROVIDER=openai
OPENAI_API_KEY=your_key_here
```

Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run with microphone input:

```bash
python voice_loop.py
```

Run typed mode against the live model:

```bash
python voice_loop.py --text
```

## Cost Control

Use mock mode for development and rehearsal:

```bash
PROVIDER=mock python voice_loop.py --text
```

Use local system speech if you want to avoid cloud text-to-speech during testing:

```env
TTS_BACKEND=system
```

Use provider text-to-speech only for the polished final demo.

## Workshop Format

The session is designed for 90 minutes:

| Time | Segment | Format |
|------|---------|--------|
| 0:00 to 0:15 | Voice agent concepts and architecture | Explanation |
| 0:15 to 1:15 | Build and run the hotel booking agent | Hands-on |
| 1:15 to 1:30 | Questions, review, and next steps | Q&A |

The detailed facilitator plan is in [`WORKSHOP_SCRIPT.md`](WORKSHOP_SCRIPT.md).

## Safety Notes

- Do not commit `.env`.
- Do not commit `.venv`.
- Keep real API keys local.
- Use `config.example.env` for shareable configuration.
