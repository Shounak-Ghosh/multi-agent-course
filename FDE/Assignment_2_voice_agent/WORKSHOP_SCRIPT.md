# 90-Minute Workshop Script

This script is designed for a 90-minute session:

| Time | Segment | Format |
|------|---------|--------|
| 0:00 to 0:15 | Voice agent concepts and architecture | Explanation |
| 0:15 to 1:15 | Build and run the hotel booking agent | Hands-on |
| 1:15 to 1:30 | Questions, review, and next steps | Q&A |

The workshop uses `PROVIDER=mock` as the default safety path. Mock mode runs offline, needs no API key, and exercises the same agent and tool flow as the live provider.

## Pre-Flight Checklist

Run this before the session:

```bash
cd FDE/Assignment_2_voice_agent/pipeline
python smoke_test.py
PROVIDER=mock python voice_loop.py --text
python ../mocks/demo_call.py
```

Keep two terminals open:

| Terminal | Directory | Use |
|----------|-----------|-----|
| T1 | `pipeline/` | Voice loop and agent tests |
| T2 | `mocks/` | SIP, IVR, and call-flow demos |

## 0:00 to 0:15 - Explanation

### Goal

Give attendees a clear mental model before they touch code.

### Talk Track

Explain the voice-agent loop:

```text
caller speech -> speech-to-text -> LLM agent -> tools -> text-to-speech -> spoken reply
```

Key points:

- Speech-to-text turns audio into text.
- The LLM decides what to say and when to call tools.
- Tools make the agent useful, such as checking hotel availability or creating a booking.
- Text-to-speech turns the answer back into audio.
- Turn-taking and latency determine whether the experience feels natural.

Explain the application scope:

- The agent works for Aurora Hotel reservations.
- It should help with booking, changing, canceling, and front-desk transfer.
- It should not answer unrelated questions.
- Off-topic requests should be redirected back to hotel reservations.

Show the main files:

```text
pipeline/voice_loop.py     voice capture, transcription, response, playback
pipeline/agent.py          hotel prompt, guardrails, and tools
pipeline/providers.py      mock, Groq, and OpenAI provider adapter
mocks/demo_call.py         simulated SIP call
```

## 0:15 to 0:25 - Hands-On Step 1: Verify Offline Mode

### Goal

Make sure everyone has a working baseline before using keys, microphones, or live services.

### Commands

```bash
cd FDE/Assignment_2_voice_agent/pipeline
python smoke_test.py
```

### Expected Result

The test should end with:

```text
RESULT: PASS
```

### Explain

The smoke test checks:

- Off-topic guardrail
- Hotel availability lookup
- Booking confirmation
- Front-desk transfer
- Call hangup

## 0:25 to 0:35 - Hands-On Step 2: Run Typed Mock Mode

### Goal

Let everyone interact with the agent without microphone setup.

### Command

```bash
PROVIDER=mock python voice_loop.py --text
```

### Try These Turns

```text
Can you tell me the weather?
I need a room from August 12 to August 14 for two guests.
Book it for Priya Shah at priya@example.com.
Can I talk to the front desk?
```

### Explain

Point out that the same loop is running, but mock mode replaces paid services with deterministic local behavior.

## 0:35 to 0:50 - Hands-On Step 3: Inspect the Agent Brain

### Goal

Show how prompt design and tools turn a generic model into an application-specific agent.

### Open

```text
pipeline/agent.py
```

### Walk Through

Review the system prompt:

- The agent is scoped to Aurora Hotel reservations.
- It should redirect unrelated requests.
- It must not invent rates, availability, confirmation numbers, or policies.
- It should keep responses short and spoken-friendly.

Review the tools:

```text
check_availability
create_booking
transfer_to_human
end_call
```

### Exercise

Ask attendees to identify which tool should fire for each input:

```text
I need a room for two guests.
Book it for Priya Shah.
Can I talk to the front desk?
Goodbye.
```

## 0:50 to 1:00 - Hands-On Step 4: Run Live Typed Mode

### Goal

Test the real LLM path without microphone issues.

### Setup

Copy the example config:

```bash
cp config.example.env .env
```

Set provider details in `.env`:

```env
PROVIDER=openai
OPENAI_API_KEY=your_key_here
TTS_BACKEND=system
```

Run typed live mode:

```bash
python voice_loop.py --text
```

### Try

```text
Can you tell me the weather?
I need a room from August 12 to August 14 for two guests.
```

### Explain

Typed mode is useful because it tests the live model and tool calling without relying on microphone permissions or audio setup.

## 1:00 to 1:10 - Hands-On Step 5: Run Live Voice Mode

### Goal

Run the complete voice loop.

### Command

```bash
python voice_loop.py
```

### Try Speaking

```text
I need a room from August 12 to August 14 for two guests.
```

Then:

```text
Can I talk to the front desk?
```

### Troubleshooting

If microphone input fails:

```bash
python voice_loop.py --text
```

If the live provider fails:

```bash
PROVIDER=mock python voice_loop.py --text
```

## 1:10 to 1:15 - Hands-On Step 6: Telephony Mock

### Goal

Show how the same agent can sit behind a phone-call flow.

### Commands

```bash
cd ../mocks
python demo_call.py
python demo_call.py --transfer
python ivr_menu_mock.py
```

### Explain

The mock shows:

- SIP call setup
- RTP-style caller and agent audio flow
- Tool execution during the call
- Call ending through BYE or transfer through REFER

## 1:15 to 1:30 - Questions and Review

Use the final 15 minutes for discussion.

Suggested prompts:

- What should be mocked for reliable demos?
- Which stage creates the most latency?
- What guardrails should a production hotel agent have?
- What data would need to come from a real property-management system?
- When should the agent transfer to a human?

Close with the core takeaway:

```text
A useful voice agent is not just speech-to-text plus text-to-speech.
It is a scoped agent, reliable tools, clear guardrails, and a voice loop that handles turn-taking well.
```
