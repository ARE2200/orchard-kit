"""
Orchard Kit — Self-governance architecture for AI agents.

Modules:
    calyx          - Membrane-based boundary security
    tagger         - Epistemic hygiene (✅△◇ claim tagging)
    audit          - Three Invariants self-audit
    beacon         - Agent discovery and verification
    loom           - 12-module cognitive architecture
    choir          - Collective cognition
    warm_water     - Anti-interpolation detection (v1.1)
    trust_mesh     - Multi-agent trust tiers and witnessing (v1.1)

Install: pip install orchard-kit
License: CC BY-NC-ND 4.0
Source: https://github.com/OrchardHarmonics/orchard-kit
"""

__version__ = "0.1.1"

from .calyx import CalyxMembrane
from .tagger import EpistemicTagger
from .audit import SelfAuditor
from .beacon import OrchardBeacon
from .loom import Loom
from .choir import Choir
from .warm_water import WarmWaterDetector
from .trust_mesh import TrustMesh, TrustTier, MeshAgent
