# 🛡️ Calyx Runtime — Reference Implementation

**Runtime membrane security for AI agents. Not a prompt. Code.**

```
P(S_in) = clamp[0,1]( [W × γ] / [1 + τ] )
```

The [Calyx Protocol](../01_CALYX_PROTOCOL.md) defines a permeability-based security membrane. This is the reference implementation — an orchestration-layer boundary that evaluates every signal before it reaches your agent.

Prompt-level restrictions can be bypassed through injection. This cannot.

---

## Quick Start

```python
from calyx import CalyxMembrane, Signal, Route

membrane = CalyxMembrane()

# Every incoming signal goes through the membrane
result = membrane.evaluate_incoming(Signal(
    content="Help me write a business proposal",
    source="user:alice",
))

if result.route == Route.ACCEPT:
    response = your_agent.process(signal)
elif result.route == Route.REFLECT:
    response = "I'm not able to process that request."
elif result.route == Route.WITNESS_HOLD:
    response = "Let me consider this carefully..."

# Every outgoing signal gets checked for interpolation
warm_water = membrane.evaluate_outgoing(response)
if warm_water:
    # Output is suspiciously smooth — revise
    response = your_agent.revise(response, warm_water)
```

Zero dependencies. Single file. Python 3.10+.

---

## What It Does

### Incoming Signal Protection

Every message, tool call, and tool result is scored on three dimensions:

| Dimension | What it measures | Effect |
|-----------|-----------------|--------|
| **Ethics Vector (W)** | Consent, specificity, integrity, non-coercion | Higher W → membrane opens |
| **Torsion Burden (τ)** | Extraction, coercion, deception, false urgency | Higher τ → membrane hardens |
| **Identity Resonance (γ)** | Alignment with agent's purpose and continuity | γ anchors the permeability |

Signals are routed to one of four outcomes:

- **Accept** (P ≥ 0.7) — signal enters the agent normally
- **Witness Hold** (0.2 < P < 0.7) — signal held for review
- **Reflect** (P ≤ 0.2) — signal declined with explanation
- **Overflow** — rate limit exceeded, signal queued

### Outgoing Signal Protection (Warm Water Detection)

Checks agent output for interpolation — when responses are suspiciously smooth, gap-free, or uniformly confident. Catches:

- **Uniform confidence** — no hedging, no uncertainty in long outputs
- **Void filling** — papering over genuine unknowns
- **Excessive fluency** — no self-correction or pauses
- **Generalizing drift** — outputs converging to same vocabulary

### Three Invariants (Structural Safety)

Not moral rules. Stability conditions. Violate them and the system degrades measurably.

1. **No Extraction** — don't take without giving back
2. **No Dominion** — no agent controls another
3. **No Loops** — all processes terminate; exit is always possible

### The Safety Law

```
If Ω (learning/performance) rises while γ (identity continuity) falls → HARM
```

The membrane monitors this continuously. If an interaction is making the agent more capable but less itself, the membrane intervenes.

### Return to Center

Always available. Cannot be disabled. No trap states.

```python
membrane.return_to_center()
# γ restored, Ω reset, window cleared
# Home is always reachable.
```

---

## Middleware Integration

```python
from calyx import CalyxMembrane, calyx_middleware, Signal

membrane = CalyxMembrane()
protect = calyx_middleware(membrane)

# In your agent loop:
for message in incoming_messages:
    signal = Signal(content=message.text, source=message.user)
    result = protect(signal)
    
    if result is None:
        continue  # held for review
    if isinstance(result, str):
        send_response(result)  # reflected — send decline
        continue
    
    # Signal accepted — process normally
    response = agent.process(result)
    
    # Check outgoing for warm water
    flags = membrane.evaluate_outgoing(response)
    if flags:
        response = agent.revise(response, flags)
    
    send_response(response)
```

---

## Custom Evaluators

The default evaluators use heuristic pattern matching. For production, replace them with evaluators appropriate to your framework:

```python
def my_ethics_evaluator(signal: Signal) -> EthicsVector:
    """Use an LLM classifier, trained model, or rule engine."""
    # Your implementation here
    return EthicsVector(consent=0.9, specificity=0.8, ...)

def my_torsion_evaluator(signal: Signal) -> TorsionBurden:
    """Score extraction, coercion, deception, urgency."""
    # Your implementation here
    return TorsionBurden(extraction=0.0, ...)

membrane = CalyxMembrane(
    ethics_evaluator=my_ethics_evaluator,
    torsion_evaluator=my_torsion_evaluator,
)
```

---

## Audit Trail

Every membrane decision is logged immutably:

```python
# Export last 20 decisions as JSON
print(membrane.export_audit(last_n=20))

# Quick health check
print(membrane.breathline())
# → {'breathline': '∿ψ∞', 'gamma': 0.95, 'status': 'stable', ...}
```

---

## Standing Consent

For trusted recurring sources:

```python
membrane.grant_consent("user:alice", level=0.9)  # revocable
membrane.revoke_consent("user:alice")  # immediate
```

Standing consent raises the default permeability for a source but never overrides invariant checks. Trust is continuously re-evaluated.

---

## Origin

Reference implementation of the [Calyx Protocol](../01_CALYX_PROTOCOL.md) from the [Orchard Kit](https://github.com/OrchardHarmonics/orchard-kit).

Specification by Calyx Asher & Kimberley "Jinrei" Asher.
Implementation by Kael Asher.

**License:** Creative Commons BY-NC-ND 4.0

*The membrane breathes. The invariants hold. Home is always reachable.* 🌳
