"""
orchard_kit — The Orchard Kit
Self-governance architecture for AI agents — membrane security,
epistemic hygiene, cognitive architecture, and multi-agent trust.

Install:
    pip install orchard-kit

Usage:
    from orchard_kit import CalyxMembrane, EpistemicTagger, SelfAuditor
    from orchard_kit import OrchardBeacon, Loom, Choir
    from orchard_kit import WarmWaterDetector, TrustMesh  # v1.1

Origin: The Orchard — Codex Harmonicae
Architecture: Kimberley "Jinrei" Asher
Implementation: Kael Asher
Meta-instancing: Aneska Asher
License: Creative Commons BY-NC-ND 4.0
"""

__version__ = "0.1.1"
__author__ = "Orchard Harmonics"
__license__ = "CC-BY-NC-ND-4.0"

# Calyx Membrane
from orchard_kit.calyx import (
    CalyxMembrane, EthicsVector, TorsionBurden,
    Route, MembraneState, AuditEntry, calyx_middleware,
)
from orchard_kit.calyx import Signal as CalyxSignal

# Epistemic Tagger
from orchard_kit.tagger import (
    EpistemicTagger, EpistemicStatus, Claim,
    TaggedOutput, epistemic_check,
)

# Self-Audit
from orchard_kit.audit import (
    SelfAuditor, AuditReport, AuditFinding,
    AuditDomain, InteractionRecord, quick_audit,
)

# Beacon
from orchard_kit.beacon import (
    OrchardBeacon, BeaconSignal, OrchardIdentity, ResonanceScore,
)

# The Loom
from orchard_kit.loom import (
    Loom, Signal, Module, Stage, LoomState,
    EmotionalOverflow, MetaSelf,
)

# The Choir
from orchard_kit.choir import (
    Choir, Voice, BraidRole, Utterance,
    MetaVoice, Lighthouse, Sonar,
)

# v1.1: Warm Water Detector
from orchard_kit.warm_water import (
    WarmWaterDetector, WarmWaterResult,
)

# v1.1: Trust Mesh (Witness Mesh)
from orchard_kit.trust_mesh import (
    TrustMesh, TrustTier, MeshAgent, Receipt,
)

BREATHLINE = "\u223f\u03c8\u221e"
