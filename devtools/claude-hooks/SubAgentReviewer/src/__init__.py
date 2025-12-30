"""
SubAgentReviewer2 source package.

Re-exports core classes for convenient imports.
"""

from .Paths import Paths
from .loggers import AgentLogger, BaseLogger, GlobalLogger, ReviewLogger
from .models import (
    AgentReview,
    ReviewerConfig,
    ReviewerSettings,
    HookInput,
    ReviewDetails,
    ReviewFileChange,
    Session,
    TrackedAgent,
    TranscriptAnalysis,
    FileChange,
    FileChangeAction,
    ToolCall,
    TranscriptEntry,
)
from .services import (
    ReviewerService,
    ReviewResult,
    ReviewMarkdownFormatter,
    ReviewContext,
    AgentPathResolver,
    SessionPathResolver,
    SessionStorageService,
    DiscoveredAgent,
    TranscriptDiscoveryService,
    TranscriptParserService,
)

__all__ = [
    # Core
    "Paths",
    # Loggers
    "AgentLogger",
    "BaseLogger",
    "GlobalLogger",
    "ReviewLogger",
    # Models
    "AgentReview",
    "ReviewerConfig",
    "ReviewerSettings",
    "HookInput",
    "ReviewDetails",
    "ReviewFileChange",
    "Session",
    "TrackedAgent",
    "TranscriptAnalysis",
    "FileChange",
    "FileChangeAction",
    "ToolCall",
    "TranscriptEntry",
    # Services
    "ReviewerService",
    "ReviewResult",
    "ReviewMarkdownFormatter",
    "ReviewContext",
    "AgentPathResolver",
    "SessionPathResolver",
    "SessionStorageService",
    "DiscoveredAgent",
    "TranscriptDiscoveryService",
    "TranscriptParserService",
]
