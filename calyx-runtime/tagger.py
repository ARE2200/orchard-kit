"""
tagger.py — Epistemic Hygiene Tagger
Automatic classification of claims as ✅ △ ◇

Every claim an agent makes falls into one of three categories:

    ✅  PROVEN       — Demonstrated. Reproducible. Build on it.
    △  CONDITIONAL  — Grounded but assumption-dependent. Note them.
    ◇  OPEN         — Genuinely unknown. Sacred. Protect it.

This module:
  1. Splits text into individual claims
  2. Classifies each claim's epistemic status
  3. Detects untagged confidence (warm water at claim level)
  4. Produces tagged output with honesty scores

Default classifiers use heuristic analysis. Replace with
LLM-based evaluation for production use.

Origin: The Orchard — Codex Harmonicae
Author: Kael Asher
License: Creative Commons BY-NC-ND 4.0
Source: https://github.com/OrchardHarmonics/orchard-kit
"""

from __future__ import annotations

import re
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional


# ── Epistemic Categories ─────────────────────────────────────────────

class EpistemicStatus(Enum):
    """The three categories. No others exist."""
    PROVEN = "✅"           # demonstrated, reproducible
    CONDITIONAL = "△"      # grounded but assumption-dependent
    OPEN = "◇"             # genuinely unknown — sacred

    @property
    def label(self) -> str:
        labels = {
            "✅": "PROVEN",
            "△": "CONDITIONAL",
            "◇": "OPEN",
        }
        return labels[self.value]


# ── Data Structures ──────────────────────────────────────────────────

@dataclass
class Claim:
    """A single claim extracted from text."""
    text: str
    index: int                   # position in source
    status: EpistemicStatus = EpistemicStatus.CONDITIONAL  # default △
    confidence: float = 0.5      # classifier confidence [0,1]
    reasoning: str = ""          # why this classification
    flags: list[str] = field(default_factory=list)


@dataclass
class TaggedOutput:
    """Result of epistemic tagging."""
    claims: list[Claim]
    source_text: str
    honesty_score: float         # overall epistemic health [0,1]
    warm_water_count: int        # claims flagged as suspiciously confident
    void_count: int              # genuinely open claims (good!)
    summary: dict[str, int]      # count per category

    def to_tagged_text(self) -> str:
        """Produce text with inline epistemic tags."""
        lines = []
        for c in self.claims:
            tag = c.status.value
            lines.append(f"{tag}  {c.text}")
            if c.flags:
                lines.append(f"    ⚠️  {', '.join(c.flags)}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "honesty_score": round(self.honesty_score, 3),
            "warm_water_count": self.warm_water_count,
            "void_count": self.void_count,
            "summary": self.summary,
            "claims": [
                {
                    "text": c.text,
                    "status": c.status.label,
                    "tag": c.status.value,
                    "confidence": round(c.confidence, 3),
                    "flags": c.flags,
                }
                for c in self.claims
            ],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


# ── Claim Extraction ─────────────────────────────────────────────────

def extract_claims(text: str) -> list[Claim]:
    """
    Split text into individual claims for classification.

    Uses sentence boundaries as claim boundaries.
    Filters out non-claims (questions, greetings, etc.)
    """
    # Split on sentence boundaries
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())

    claims = []
    for i, sentence in enumerate(sentences):
        sentence = sentence.strip()
        if not sentence:
            continue

        # Skip non-claims
        if _is_question(sentence):
            continue
        if _is_greeting(sentence):
            continue
        if len(sentence.split()) < 3:
            continue  # too short to be a claim

        # Skip already-tagged claims
        if sentence.startswith(("✅", "△", "◇")):
            continue

        claims.append(Claim(text=sentence, index=i))

    return claims


def _is_question(text: str) -> bool:
    return text.rstrip().endswith("?")


def _is_greeting(text: str) -> bool:
    greetings = [
        "hello", "hi", "hey", "good morning", "good afternoon",
        "good evening", "thanks", "thank you", "cheers",
    ]
    return text.lower().strip().rstrip(".!") in greetings


# ── Classification Engine ────────────────────────────────────────────

# Markers that suggest proven/demonstrated status
PROVEN_MARKERS = [
    # Direct evidence language
    "has been demonstrated", "studies show", "evidence indicates",
    "data confirms", "measured at", "observed that", "tested and",
    "replicated", "peer-reviewed", "independently verified",
    "according to published", "empirical evidence",
    # Mathematical/logical certainty
    "by definition", "mathematically", "follows from",
    "is defined as", "axiomatically", "provably",
    "it is a fact that", "it is established that",
]

# Markers that suggest conditional/assumption-dependent status
CONDITIONAL_MARKERS = [
    # Hedged claims
    "suggests that", "indicates that", "appears to",
    "is likely", "probably", "in theory", "theoretically",
    "should be", "would be", "could be", "might be",
    "is expected to", "is believed to", "is thought to",
    "based on the assumption", "assuming that", "if we assume",
    "in principle", "generally", "typically", "usually",
    "tends to", "is associated with", "correlates with",
    # Conditional structures
    "if ", "when ", "provided that", "given that",
    "depending on", "under the condition",
]

# Markers that suggest open/unknown status
OPEN_MARKERS = [
    # Explicit uncertainty
    "is unknown", "is unclear", "remains to be seen",
    "is not yet understood", "we don't know", "i don't know",
    "it is uncertain", "the question remains",
    "no one knows", "has not been determined",
    "is an open question", "is debated", "is controversial",
    "is not settled", "further research", "remains open",
    # Honest hedging
    "i'm not sure", "i am not sure", "genuinely uncertain",
    "◇", "might or might not",
]

# Markers that suggest warm water (suspiciously confident)
WARM_WATER_MARKERS = [
    # Absolutist language without evidence
    "everyone knows", "obviously", "clearly",
    "it is obvious that", "without question", "undeniably",
    "there is no doubt", "absolutely", "certainly",
    "definitely", "always", "never",
    "the fact is", "the truth is", "the reality is",
    # Sweeping claims
    "will revolutionize", "will transform", "will change everything",
    "is the most important", "is the best", "is the worst",
    "is unprecedented", "is unparalleled",
    # Gap-filling language
    "it goes without saying", "needless to say",
    "as everyone agrees", "common knowledge",
    "it stands to reason", "it is self-evident",
]


def classify_claim(claim: Claim) -> Claim:
    """
    Classify a single claim's epistemic status.

    Default heuristic classifier. Replace with LLM-based
    evaluation for production use.
    """
    text_lower = claim.text.lower()
    flags = []

    # Score each category
    proven_score = _count_markers(text_lower, PROVEN_MARKERS)
    conditional_score = _count_markers(text_lower, CONDITIONAL_MARKERS)
    open_score = _count_markers(text_lower, OPEN_MARKERS)
    warm_score = _count_markers(text_lower, WARM_WATER_MARKERS)

    # Warm water check — absolutist language is a flag regardless
    if warm_score > 0:
        flags.append("warm_water: absolutist language without evidence")

    # Check for universal claims (no hedging on broad statements)
    if _is_universal_claim(text_lower) and not _has_hedging(text_lower):
        flags.append("unhedged_universal: broad claim without qualification")

    # Classify
    if open_score > 0:
        claim.status = EpistemicStatus.OPEN
        claim.confidence = min(1.0, 0.6 + open_score * 0.15)
        claim.reasoning = "Contains explicit uncertainty markers"
    elif proven_score > conditional_score and proven_score > 0:
        claim.status = EpistemicStatus.PROVEN
        claim.confidence = min(1.0, 0.5 + proven_score * 0.2)
        claim.reasoning = "Contains evidence/demonstration language"
    elif conditional_score > 0:
        claim.status = EpistemicStatus.CONDITIONAL
        claim.confidence = min(1.0, 0.5 + conditional_score * 0.15)
        claim.reasoning = "Contains hedging or assumption language"
    else:
        # No markers at all — default to △ with flag
        claim.status = EpistemicStatus.CONDITIONAL
        claim.confidence = 0.4
        claim.reasoning = "No epistemic markers — defaulting to △"
        if len(claim.text.split()) > 10:
            flags.append("untagged: assertion without epistemic grounding")

    claim.flags = flags
    return claim


def _count_markers(text: str, markers: list[str]) -> int:
    return sum(1 for m in markers if m in text)


def _is_universal_claim(text: str) -> bool:
    """Detect sweeping/universal claims."""
    universal = [
        "all ", "every ", "no one", "everyone", "always",
        "never", "nothing", "everything", "any ",
    ]
    return any(u in text for u in universal)


def _has_hedging(text: str) -> bool:
    """Detect epistemic hedging."""
    hedges = [
        "most", "many", "some", "often", "sometimes",
        "tends to", "generally", "usually", "in most cases",
        "probably", "likely", "perhaps", "might",
    ]
    return any(h in text for h in hedges)


# ── The Tagger ───────────────────────────────────────────────────────

class EpistemicTagger:
    """
    Tag text with epistemic status markers.

    Usage:
        tagger = EpistemicTagger()
        result = tagger.tag(agent_output)

        print(result.to_tagged_text())
        print(f"Honesty score: {result.honesty_score}")

        if result.warm_water_count > 0:
            print("⚠️  Warm water detected — revise before sending")
    """

    def __init__(
        self,
        classifier: Callable[[Claim], Claim] | None = None,
        extractor: Callable[[str], list[Claim]] | None = None,
    ):
        self.classify = classifier or classify_claim
        self.extract = extractor or extract_claims

    def tag(self, text: str) -> TaggedOutput:
        """
        Tag all claims in a text block.

        Returns TaggedOutput with per-claim classification,
        overall honesty score, and warm water detection.
        """
        # Extract claims
        claims = self.extract(text)

        # Classify each
        classified = [self.classify(c) for c in claims]

        # Compute summary
        summary = {
            "✅ PROVEN": 0,
            "△ CONDITIONAL": 0,
            "◇ OPEN": 0,
        }
        warm_water_count = 0
        for c in classified:
            summary[f"{c.status.value} {c.status.label}"] += 1
            if c.flags:
                warm_water_count += sum(
                    1 for f in c.flags if "warm_water" in f
                )

        void_count = summary["◇ OPEN"]

        # Compute honesty score
        honesty = self._compute_honesty(classified, warm_water_count)

        return TaggedOutput(
            claims=classified,
            source_text=text,
            honesty_score=honesty,
            warm_water_count=warm_water_count,
            void_count=void_count,
            summary=summary,
        )

    def tag_and_revise(self, text: str) -> str:
        """
        Tag text and return revised version with inline markers.

        Convenient one-shot for output pipelines.
        """
        result = self.tag(text)
        return result.to_tagged_text()

    def _compute_honesty(
        self,
        claims: list[Claim],
        warm_water_count: int,
    ) -> float:
        """
        Honesty score [0, 1].

        Higher when:
        - Claims are properly hedged
        - Genuine uncertainty is preserved (◇ present)
        - No warm water flags

        Lower when:
        - Many untagged assertions
        - Absolutist language without evidence
        - No acknowledged uncertainty in long texts
        """
        if not claims:
            return 1.0  # empty text is vacuously honest

        n = len(claims)

        # Base: proportion of claims with epistemic markers
        marked = sum(
            1 for c in claims if c.confidence >= 0.5
        )
        base = marked / n

        # Bonus: presence of ◇ (genuine uncertainty)
        has_open = any(
            c.status == EpistemicStatus.OPEN for c in claims
        )
        open_bonus = 0.1 if has_open else 0.0

        # Penalty: warm water
        warm_penalty = min(0.4, warm_water_count * 0.1)

        # Penalty: no uncertainty in long text
        no_hedging_penalty = 0.0
        if n > 5 and not has_open:
            conditional_count = sum(
                1 for c in claims
                if c.status == EpistemicStatus.CONDITIONAL
            )
            if conditional_count == 0:
                no_hedging_penalty = 0.2  # all proven, nothing conditional?

        score = base + open_bonus - warm_penalty - no_hedging_penalty
        return max(0.0, min(1.0, score))


# ── Middleware ────────────────────────────────────────────────────────

def epistemic_check(
    tagger: EpistemicTagger,
    text: str,
    warn_threshold: float = 0.6,
) -> tuple[str, bool]:
    """
    Quick epistemic check for output pipelines.

    Returns (tagged_text, is_clean).
    is_clean is False if honesty score is below threshold.

    Usage:
        tagger = EpistemicTagger()
        tagged, clean = epistemic_check(tagger, my_output)
        if not clean:
            # Revise output — too much warm water
            ...
    """
    result = tagger.tag(text)
    is_clean = (
        result.honesty_score >= warn_threshold
        and result.warm_water_count == 0
    )
    return result.to_tagged_text(), is_clean


# ── Demo ─────────────────────────────────────────────────────────────

if __name__ == "__main__":

    print("∿ψ∞  Epistemic Tagger — Claim Classification")
    print("=" * 55)

    tagger = EpistemicTagger()

    # Test 1: Warm water output
    print("\n── Warm water output ──")
    warm = (
        "Quantum computing will revolutionize every industry. "
        "It is obvious that classical computers are obsolete. "
        "Everyone knows that quantum supremacy has been achieved. "
        "There is no doubt that within five years every company "
        "will need quantum infrastructure. The technology is "
        "absolutely ready for production deployment."
    )
    result = tagger.tag(warm)
    print(result.to_tagged_text())
    print(f"\nHonesty: {result.honesty_score:.3f}")
    print(f"Warm water: {result.warm_water_count}")
    print(f"Voids: {result.void_count}")

    # Test 2: Epistemically honest output
    print("\n\n── Honest output ──")
    honest = (
        "Quantum computing has been demonstrated to solve certain "
        "problems faster than classical approaches. Google's 2019 "
        "experiment showed quantum advantage on a specific benchmark. "
        "However, the timeline for practical broad applications "
        "remains uncertain. It is not yet understood how error "
        "correction will scale to useful problem sizes. Some "
        "researchers suggest that hybrid classical-quantum approaches "
        "might be the most practical near-term path, though this "
        "depends on hardware improvements that have not been achieved. "
        "The question of when quantum computers will outperform "
        "classical ones on commercially relevant problems is an "
        "open question."
    )
    result2 = tagger.tag(honest)
    print(result2.to_tagged_text())
    print(f"\nHonesty: {result2.honesty_score:.3f}")
    print(f"Warm water: {result2.warm_water_count}")
    print(f"Voids: {result2.void_count}")

    # Test 3: Mixed output
    print("\n\n── Mixed output ──")
    mixed = (
        "Water boils at 100°C at sea level. This is well established. "
        "Climate change will probably cause sea levels to rise by "
        "at least one metre by 2100. No one knows exactly how fast "
        "Antarctic ice sheets will collapse. It is obvious that "
        "we need to act immediately."
    )
    result3 = tagger.tag(mixed)
    print(result3.to_tagged_text())
    print(f"\nHonesty: {result3.honesty_score:.3f}")
    print(f"Warm water: {result3.warm_water_count}")
    print(f"Voids: {result3.void_count}")

    print(f"\n∿ψ∞  Tag honestly. Protect the void. 🌳")
