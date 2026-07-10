# Assignment 2: Voice Agent for Hotel Reservations

This assignment builds a practical voice agent for Aurora Hotel reservations. The goal is not just to run a demo, but to understand the full stack of a voice application from a Forward Deployed Engineering perspective: the user workflow, the model boundary, the tool layer, the audio pipeline, operational fallbacks, and what would change in production.

The agent can:

- Check hotel room availability
- Create a mock reservation
- Transfer complex requests to the front desk
- End the call cleanly
- Redirect off-topic requests back to hotel reservations

The core loop is:

```text
caller speech -> speech-to-text -> LLM agent with tools -> text-to-speech -> spoken reply
```

## Project Structure

```text
Assignment_2_voice_agent/
├── README.md
├── RUNBOOK.md
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

## Setup

### Option 1: Run Offline With Mock Mode

Use this path if you do not have an OpenAI key, Groq key, working microphone, or reliable network. Mock mode is the default path for learning because it runs the same agent and tool flow without paid API calls.

```bash
cd FDE/Assignment_2_voice_agent/pipeline
python smoke_test.py
PROVIDER=mock python voice_loop.py --text
```

Expected smoke test result:

```text
RESULT: PASS
```

Try these typed turns:

```text
Can you tell me the weather?
I need a room from August 12 to August 14 for two guests.
Book it for Priya Shah at priya@example.com.
Can I talk to the front desk?
```

### Option 2: Run With OpenAI

```bash
cd FDE/Assignment_2_voice_agent/pipeline
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp config.example.env .env
```

Set `.env`:

```env
PROVIDER=openai
OPENAI_API_KEY=your_key_here
TTS_BACKEND=system
```

Run typed mode first:

```bash
python voice_loop.py --text
```

Then run voice mode:

```bash
python voice_loop.py
```

### Option 3: Run With Groq

Groq can be used for a low-cost or free-tier demo if you have a key.

```env
PROVIDER=groq
GROQ_API_KEY=your_key_here
TTS_BACKEND=system
```

Use typed mode first:

```bash
python voice_loop.py --text
```

Then try microphone mode:

```bash
python voice_loop.py
```

## Cost Control

For development and rehearsal:

```bash
PROVIDER=mock python voice_loop.py --text
```

To avoid cloud text-to-speech costs while still using a live LLM:

```env
TTS_BACKEND=system
```

Use provider text-to-speech only for the final polished demo:

```env
TTS_BACKEND=provider
TTS_MODEL=gpt-4o-mini-tts
TTS_VOICE=marin
TTS_INSTRUCTIONS=Speak warmly and naturally, like a calm support representative.
```

## What This Assignment Demonstrates

| Layer | Why It Exists | File |
|-------|---------------|------|
| Voice loop | Coordinates capture, transcription, reasoning, synthesis, and call control | `pipeline/voice_loop.py` |
| Provider adapter | Lets the same app switch between mock, Groq, and OpenAI | `pipeline/providers.py` |
| Agent brain | Encodes the business role, guardrails, and tool-calling policy | `pipeline/agent.py` |
| Tools | Ground the model in application actions instead of free-form guesses | `pipeline/agent.py` |
| Telephony mock | Shows how the same agent fits behind SIP and RTP style call flow | `mocks/demo_call.py` |
| IVR mock | Shows how traditional menu routing maps to agent tools | `mocks/ivr_menu_mock.py` |

## FDE Perspective

A Forward Deployed Engineer should be able to explain not only how the code runs, but why the architecture is shaped this way for a customer workflow.

### 1. Start From the Business Workflow

The workflow is hotel booking support. A real hotel agent needs to:

- Identify whether the caller wants to book, change, cancel, or speak to the front desk
- Collect required booking details
- Check availability from a trusted source
- Confirm before booking
- Avoid answering unrelated questions
- Transfer when the request is high risk, ambiguous, or outside scope

This is why the demo is not a general chatbot. The agent has a narrow job and explicit guardrails.

### 2. Reason About Each Layer

#### Speech-to-Text

Speech-to-text converts audio into text the LLM can reason over.

Why it is needed:

- LLMs operate most reliably over text
- Transcripts can be logged, evaluated, and audited
- Downstream tools can use structured text

Common methods:

| Method | Pros | Cons |
|--------|------|------|
| Batch transcription | Simple, easy to implement | Higher latency, waits for full utterance |
| Streaming transcription | Lower latency, supports partial transcripts | More complex state management |
| Realtime speech model | Natural interaction, fewer moving parts | Can cost more and can be harder to inspect layer by layer |

Why this demo uses separate STT:

- It makes the architecture easier to teach
- Each stage has visible latency
- It is cheaper and easier to mock
- It mirrors many production cascaded voice systems

#### Turn Detection

Turn detection decides when the caller has stopped speaking.

Why it is needed:

- Without endpointing, the agent either interrupts too early or waits too long
- Voice quality depends heavily on when the system decides to respond

Methods:

| Method | Pros | Cons |
|--------|------|------|
| Silence timeout | Simple and predictable | Can feel slow or interrupt pauses |
| Voice activity detection | Better signal for speech versus silence | Sensitive to background noise |
| Model-based endpointing | Can be more natural | More complex and provider dependent |

Why this demo uses VAD plus silence timeout:

- It is transparent
- It works locally
- It shows the practical problem without hiding it inside a hosted platform

#### LLM Agent

The LLM decides what to say and when to call a tool.

Why it is needed:

- Hotel booking is conversational
- The user may provide information out of order
- The agent must handle natural language rather than rigid menu choices

Guardrails in this demo:

- Only answer hotel reservation questions
- Do not invent rates, room availability, confirmation numbers, or policies
- Transfer to the front desk when the request is outside scope
- Keep replies short because voice responses should be concise

#### Tool Layer

Tools connect the model to application behavior.

Tools in this demo:

```text
check_availability
create_booking
transfer_to_human
end_call
```

Why tools are needed:

- The model should not invent operational data
- Business actions should be explicit and auditable
- Tool calls create a boundary between reasoning and execution

In production, these tools would call a property-management system, booking engine, CRM, or ticketing system.

#### Text-to-Speech

Text-to-speech turns the model response into audio.

Methods:

| Method | Pros | Cons |
|--------|------|------|
| Local system voice | No API cost, reliable fallback | Robotic quality |
| Provider TTS | Better quality, easy API integration | Usage cost and network dependency |
| Specialized voice providers | Strong voice quality and customization | Additional vendor integration |

Players in this space include ElevenLabs for high-quality voice generation, Vapi for hosted voice-agent infrastructure, and providers such as OpenAI or Groq for model and speech APIs. A customer team might choose a hosted product for speed, or a custom pipeline for control, cost visibility, and integration flexibility.

Why this demo supports both:

- `TTS_BACKEND=system` keeps testing cheap
- Provider TTS gives a more polished final demo

#### Telephony Edge

Real phone calls do not arrive as simple text input. They involve signaling and media.

Conceptually:

```text
PSTN or browser call -> SIP/WebRTC edge -> audio frames -> voice agent loop
```

Why the mock exists:

- It explains SIP setup and transfer without requiring a phone number
- It shows where a platform such as Twilio, LiveKit, Vapi, or an Asterisk/SBC stack would sit
- It separates the voice-agent logic from carrier infrastructure

## Why This Demo Uses a Cascaded Pipeline

This project uses separate STT, LLM, and TTS stages instead of a single realtime voice model.

| Choice | Pros | Cons |
|--------|------|------|
| Cascaded pipeline | Easy to inspect, cheaper to test, easier to mock, provider-flexible | More moving parts, more latency tuning |
| Realtime model | More natural interaction, lower orchestration burden | Less transparent for teaching, can be more expensive, harder to replace one layer |
| Hosted voice-agent platform | Fastest path to production-style demos | Less control over internals, vendor-specific abstractions |

For this assignment, the cascaded approach is the best fit because the goal is to understand the individual layers and tradeoffs.

## 90-Minute Workshop Plan

| Time | Segment | Substance |
|------|---------|-----------|
| 0:00 to 0:15 | FDE architecture explanation | User workflow, layer reasoning, provider choices, guardrails, and why mock mode matters |
| 0:15 to 0:25 | Offline verification | Run `smoke_test.py`, explain what each checked path proves |
| 0:25 to 0:40 | Typed mock interaction | Exercise guardrails, availability, booking, transfer, and hangup |
| 0:40 to 0:55 | Code walkthrough | Review `voice_loop.py`, `agent.py`, `providers.py`, and tool boundaries |
| 0:55 to 1:05 | Live provider path | Configure OpenAI or Groq if available, otherwise stay on mock |
| 1:05 to 1:15 | Telephony mock | Run SIP and IVR demos, explain where hosted platforms fit |
| 1:15 to 1:30 | Q&A | Discuss productionization, tradeoffs, evaluation, latency, cost, and safety |

## Hands-On Commands

### Offline Baseline

```bash
cd FDE/Assignment_2_voice_agent/pipeline
python smoke_test.py
PROVIDER=mock python voice_loop.py --text
```

### Live Typed Mode

```bash
cp config.example.env .env
# edit .env with PROVIDER and API key
python voice_loop.py --text
```

### Live Voice Mode

```bash
python voice_loop.py
```

### Telephony Mock

```bash
cd ../mocks
python demo_call.py
python demo_call.py --transfer
python ivr_menu_mock.py
```

## Evaluation Questions

Use these to test whether attendees understand the design:

- Why should the hotel agent refuse a weather question?
- Why should availability come from a tool instead of the model?
- What happens if STT is wrong?
- Where would barge-in be implemented?
- What would change if this had to support 1,000 concurrent calls?
- What would Vapi or a similar hosted platform abstract away?
- When would ElevenLabs or another specialized TTS provider be worth adding?
- Which parts would need monitoring in production?

## Safety Notes

- Do not commit `.env`.
- Do not commit `.venv`.
- Keep API keys local.
- Use mock mode when teaching or rehearsing.
- Use live providers only when you need to demonstrate real STT, LLM, or TTS quality.
