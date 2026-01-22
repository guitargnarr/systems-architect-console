#!/usr/bin/env python3
"""
Multi-Model Domain Expert Consultation CLI

Queries specialized Ollama models in parallel and aggregates responses
with weighted scoring based on domain relevance.

Features:
- Parallel model querying with bounded concurrency
- Domain-based routing and model selection
- Response synthesis with theme extraction
- Conflict detection across model perspectives
- Feedback capture for continuous improvement
- Actionable recommendation generation

Usage:
    python consult.py "Your question here"
    python consult.py --models technical "Architecture question"
    python consult.py --models all "Complex multi-domain question"
    python consult.py --synthesize "Question requiring aggregated insights"
"""

import asyncio
import argparse
import hashlib
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime
from heapq import heappush, heappop
from pathlib import Path
from typing import Callable, Optional

try:
    import aiohttp
except ImportError:
    print("Installing aiohttp...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp", "-q"])
    import aiohttp

# Feedback storage location
FEEDBACK_DIR = Path.home() / ".consult" / "feedback"
FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)

# ANSI color codes
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Domain colors
    META = "\033[38;5;208m"      # Orange
    TECHNICAL = "\033[38;5;33m"  # Blue
    WEALTH = "\033[38;5;34m"     # Green
    TAX = "\033[38;5;135m"       # Purple
    PERSONAL = "\033[38;5;205m"  # Pink
    UTILITY = "\033[38;5;245m"   # Gray

    SUCCESS = "\033[38;5;34m"
    ERROR = "\033[38;5;196m"
    WARNING = "\033[38;5;220m"
    PENDING = "\033[38;5;245m"


# Model definitions with domain, weight, and timeout
MODELS = {
    # Meta - Synthesis
    "unified-systems-architect": {
        "domain": "meta",
        "weight": 0.25,
        "timeout": 180,
        "description": "Cross-domain synthesis, holistic analysis",
        "color": Colors.META,
    },

    # Technical
    "llm-orchestration-ontology": {
        "domain": "technical",
        "weight": 0.15,
        "timeout": 120,
        "description": "Multi-agent systems, orchestration patterns",
        "color": Colors.TECHNICAL,
    },
    "prompt-engineering-expert": {
        "domain": "technical",
        "weight": 0.15,
        "timeout": 120,
        "description": "Prompt design, debugging, optimization",
        "color": Colors.TECHNICAL,
    },
    "kg-traversal-expert": {
        "domain": "technical",
        "weight": 0.10,
        "timeout": 120,
        "description": "Knowledge graphs, SPARQL, Cypher",
        "color": Colors.TECHNICAL,
    },
    "app-architecture-expert": {
        "domain": "technical",
        "weight": 0.15,
        "timeout": 120,
        "description": "Web architecture, SSR, SPA, microservices",
        "color": Colors.TECHNICAL,
    },
    "performance-percentiles-expert": {
        "domain": "technical",
        "weight": 0.15,
        "timeout": 120,
        "description": "p50/p95/p99, SLOs, error budgets",
        "color": Colors.TECHNICAL,
    },

    # Wealth
    "wealth-mindset": {
        "domain": "wealth",
        "weight": 0.10,
        "timeout": 90,
        "description": "Leverage, ownership thinking",
        "color": Colors.WEALTH,
    },
    "passive-income-expert": {
        "domain": "wealth",
        "weight": 0.15,
        "timeout": 90,
        "description": "Income streams, investment strategies",
        "color": Colors.WEALTH,
    },
    "real-estate-investor": {
        "domain": "wealth",
        "weight": 0.15,
        "timeout": 90,
        "description": "BRRRR, financing, rental properties",
        "color": Colors.WEALTH,
    },
    "deal-structuring-expert": {
        "domain": "wealth",
        "weight": 0.15,
        "timeout": 90,
        "description": "M&A, acquisitions, deal financing",
        "color": Colors.WEALTH,
    },

    # Tax/Legal
    "business-tax-2026": {
        "domain": "tax",
        "weight": 0.15,
        "timeout": 90,
        "description": "Current tax laws, OBBBA provisions",
        "color": Colors.TAX,
    },
    "cpa-wealth-advisor": {
        "domain": "tax",
        "weight": 0.15,
        "timeout": 90,
        "description": "Business owner optimization, retirement",
        "color": Colors.TAX,
    },
    "homeowner-tax-strategies": {
        "domain": "tax",
        "weight": 0.10,
        "timeout": 90,
        "description": "Deductions, 1031 exchanges, depreciation",
        "color": Colors.TAX,
    },
    "ngo-corporate-structures": {
        "domain": "tax",
        "weight": 0.10,
        "timeout": 90,
        "description": "Nonprofit structures, 501c3/c4",
        "color": Colors.TAX,
    },

    # Personal
    "skill-stack-expert": {
        "domain": "personal",
        "weight": 0.15,
        "timeout": 90,
        "description": "Power skill stacks for career acceleration",
        "color": Colors.PERSONAL,
    },
    "skill-stacker": {
        "domain": "personal",
        "weight": 0.10,
        "timeout": 90,
        "description": "Skill development strategy",
        "color": Colors.PERSONAL,
    },
    "productivity-systems-expert": {
        "domain": "personal",
        "weight": 0.15,
        "timeout": 90,
        "description": "Time management, focus, GTD",
        "color": Colors.PERSONAL,
    },
    "world-model-expert": {
        "domain": "personal",
        "weight": 0.15,
        "timeout": 90,
        "description": "Mental models, systems thinking",
        "color": Colors.PERSONAL,
    },

    # Utility
    "english-to-spanish": {
        "domain": "utility",
        "weight": 0.05,
        "timeout": 60,
        "description": "Translation",
        "color": Colors.UTILITY,
    },
}

# Domain keyword routing
DOMAIN_KEYWORDS = {
    "technical": ["architecture", "design", "pattern", "api", "code", "performance",
                  "latency", "llm", "prompt", "model", "graph", "microservice", "async"],
    "wealth": ["invest", "passive", "income", "rental", "property", "deal", "acquisition",
               "leverage", "wealth", "portfolio", "cash flow"],
    "tax": ["tax", "deduction", "1031", "s-corp", "llc", "depreciation", "501c3",
            "nonprofit", "compliance", "cpa"],
    "personal": ["skill", "career", "productivity", "time", "focus", "learning",
                 "mental model", "systems thinking"],
    "utility": ["translate", "spanish", "language"],
}

OLLAMA_URL = "http://localhost:11434/api/generate"


@dataclass
class ModelResponse:
    model: str
    domain: str
    response: Optional[str]
    weight: float
    duration_ms: int
    status: str  # success, error, timeout
    error: Optional[str] = None


@dataclass
class ExtractedTheme:
    """A theme extracted from model responses."""
    theme: str
    supporting_models: list[str]
    confidence: float  # 0-1 based on model agreement
    evidence: list[str]  # Key quotes supporting theme


@dataclass
class DetectedConflict:
    """A conflict detected between model perspectives."""
    topic: str
    positions: dict[str, str]  # model -> position
    severity: str  # low, medium, high
    resolution_hint: Optional[str] = None


@dataclass
class ActionItem:
    """An actionable recommendation extracted from responses."""
    action: str
    priority: str  # high, medium, low
    source_models: list[str]
    domain: str
    rationale: str


@dataclass
class SynthesisResult:
    """Aggregated analysis across all model responses."""
    question: str
    themes: list[ExtractedTheme]
    conflicts: list[DetectedConflict]
    action_items: list[ActionItem]
    domain_coverage: dict[str, int]  # domain -> response count
    consensus_score: float  # 0-1, how much models agree
    total_models: int
    successful_models: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class FeedbackEntry:
    """User feedback on a consultation."""
    query_hash: str
    question: str
    models_used: list[str]
    synthesis_helpful: Optional[bool] = None
    best_model: Optional[str] = None
    worst_model: Optional[str] = None
    action_taken: Optional[str] = None
    user_notes: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# ============================================================================
# SYNTHESIS ENGINE - Data Aggregation & Feedback Loops
# ============================================================================

class SynthesisEngine:
    """
    Aggregates model responses into actionable insights.

    Core feedback loops:
    1. Theme extraction - Find common threads across responses
    2. Conflict detection - Identify disagreements for human review
    3. Action extraction - Pull out concrete next steps
    4. Confidence scoring - Weight by model agreement
    """

    # Keywords indicating recommendations/actions
    ACTION_INDICATORS = [
        "should", "recommend", "suggest", "consider", "implement",
        "start with", "begin by", "first step", "priority", "critical",
        "must", "need to", "important to", "key is", "focus on"
    ]

    # Keywords indicating disagreement/alternatives
    CONFLICT_INDICATORS = [
        "however", "alternatively", "on the other hand", "instead",
        "but", "conversely", "in contrast", "unlike", "whereas",
        "disagree", "different approach", "better option"
    ]

    # Priority signal words
    PRIORITY_HIGH = ["critical", "must", "essential", "urgent", "immediately", "first"]
    PRIORITY_MEDIUM = ["should", "recommend", "important", "consider"]
    PRIORITY_LOW = ["could", "might", "optional", "eventually", "nice to have"]

    def __init__(self):
        self.responses: list[ModelResponse] = []

    def add_responses(self, responses: list[ModelResponse]):
        """Add model responses for synthesis."""
        self.responses = [r for r in responses if r.status == "success" and r.response]

    def extract_themes(self) -> list[ExtractedTheme]:
        """
        Extract common themes across model responses.

        Uses keyword frequency and co-occurrence to identify themes.
        """
        if not self.responses:
            return []

        # Extract key phrases from each response
        response_phrases = {}
        for r in self.responses:
            phrases = self._extract_key_phrases(r.response)
            response_phrases[r.model] = phrases

        # Find phrases that appear across multiple models
        phrase_models = defaultdict(list)
        for model, phrases in response_phrases.items():
            for phrase in phrases:
                phrase_models[phrase].append(model)

        # Filter to themes with multi-model support
        themes = []
        for phrase, models in phrase_models.items():
            if len(models) >= 2:  # At least 2 models agree
                confidence = len(models) / len(self.responses)
                evidence = self._find_evidence(phrase, models)
                themes.append(ExtractedTheme(
                    theme=phrase,
                    supporting_models=models,
                    confidence=confidence,
                    evidence=evidence[:3]  # Top 3 evidence quotes
                ))

        # Sort by confidence (multi-model agreement)
        themes.sort(key=lambda t: -t.confidence)
        return themes[:10]  # Top 10 themes

    def detect_conflicts(self) -> list[DetectedConflict]:
        """
        Detect disagreements between model perspectives.

        Looks for contradictory recommendations or opposing viewpoints.
        """
        if len(self.responses) < 2:
            return []

        conflicts = []

        # Compare each pair of responses for conflicts
        for i, r1 in enumerate(self.responses):
            for r2 in self.responses[i+1:]:
                detected = self._find_conflicts_between(r1, r2)
                conflicts.extend(detected)

        # Deduplicate and score severity
        unique_conflicts = self._dedupe_conflicts(conflicts)
        return unique_conflicts[:5]  # Top 5 conflicts

    def extract_actions(self) -> list[ActionItem]:
        """
        Extract actionable recommendations from responses.

        Identifies concrete next steps with priority levels.
        """
        actions = []

        for r in self.responses:
            extracted = self._extract_actions_from_response(r)
            actions.extend(extracted)

        # Deduplicate similar actions
        unique_actions = self._dedupe_actions(actions)

        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        unique_actions.sort(key=lambda a: priority_order.get(a.priority, 3))

        return unique_actions[:10]  # Top 10 actions

    def calculate_consensus(self) -> float:
        """
        Calculate how much the models agree (0-1).

        Based on theme overlap and conflict count.
        """
        if len(self.responses) < 2:
            return 1.0

        themes = self.extract_themes()
        conflicts = self.detect_conflicts()

        # Base consensus on shared themes vs conflicts
        theme_score = sum(t.confidence for t in themes) / max(len(themes), 1)
        conflict_penalty = len(conflicts) * 0.1

        return max(0, min(1, theme_score - conflict_penalty))

    def synthesize(self, question: str) -> SynthesisResult:
        """
        Perform full synthesis across all responses.

        Returns structured aggregation with themes, conflicts, and actions.
        """
        themes = self.extract_themes()
        conflicts = self.detect_conflicts()
        actions = self.extract_actions()

        # Calculate domain coverage
        domain_coverage = Counter(r.domain for r in self.responses)

        return SynthesisResult(
            question=question,
            themes=themes,
            conflicts=conflicts,
            action_items=actions,
            domain_coverage=dict(domain_coverage),
            consensus_score=self.calculate_consensus(),
            total_models=len(self.responses) + sum(1 for r in self.responses if r.status != "success"),
            successful_models=len(self.responses),
        )

    # ---- Private helper methods ----

    def _extract_key_phrases(self, text: str) -> list[str]:
        """Extract key noun phrases and concepts from text."""
        # Simple extraction: sentences with action indicators
        sentences = re.split(r'[.!?]\s+', text.lower())
        phrases = []

        for sentence in sentences:
            # Look for sentences with recommendations
            for indicator in self.ACTION_INDICATORS:
                if indicator in sentence:
                    # Extract the core phrase (simplified)
                    cleaned = re.sub(r'[^\w\s-]', '', sentence)
                    words = cleaned.split()
                    if 3 <= len(words) <= 15:
                        phrases.append(' '.join(words))
                    break

        return list(set(phrases))  # Dedupe

    def _find_evidence(self, phrase: str, models: list[str]) -> list[str]:
        """Find supporting quotes for a theme."""
        evidence = []
        phrase_words = set(phrase.lower().split())

        for r in self.responses:
            if r.model in models:
                sentences = re.split(r'[.!?]\s+', r.response)
                for sent in sentences:
                    sent_words = set(sent.lower().split())
                    overlap = len(phrase_words & sent_words) / len(phrase_words)
                    if overlap > 0.3 and len(sent) < 300:
                        evidence.append(f"[{r.model}] {sent.strip()}")
                        break

        return evidence

    def _find_conflicts_between(self, r1: ModelResponse, r2: ModelResponse) -> list[DetectedConflict]:
        """Find conflicts between two model responses."""
        conflicts = []

        # Look for conflict indicator phrases
        r1_lower = r1.response.lower()
        r2_lower = r2.response.lower()

        for indicator in self.CONFLICT_INDICATORS:
            if indicator in r1_lower or indicator in r2_lower:
                # Extract the conflicting positions
                topic = self._extract_conflict_topic(r1.response, r2.response, indicator)
                if topic:
                    conflicts.append(DetectedConflict(
                        topic=topic,
                        positions={
                            r1.model: self._extract_position(r1.response, topic),
                            r2.model: self._extract_position(r2.response, topic),
                        },
                        severity="medium",  # Could be refined
                        resolution_hint="Consider domain context when choosing approach"
                    ))
                break

        return conflicts

    def _extract_conflict_topic(self, text1: str, text2: str, indicator: str) -> Optional[str]:
        """Extract the topic of conflict from two texts."""
        # Simplified: return first sentence containing indicator
        for text in [text1, text2]:
            sentences = re.split(r'[.!?]\s+', text)
            for sent in sentences:
                if indicator in sent.lower() and len(sent) < 200:
                    return sent.strip()[:100]
        return None

    def _extract_position(self, text: str, topic: str) -> str:
        """Extract a model's position on a topic."""
        # Return first relevant sentence
        topic_words = set(topic.lower().split()[:5])
        sentences = re.split(r'[.!?]\s+', text)

        for sent in sentences:
            sent_words = set(sent.lower().split())
            if len(topic_words & sent_words) >= 2:
                return sent.strip()[:150]

        return text[:150] + "..."

    def _dedupe_conflicts(self, conflicts: list[DetectedConflict]) -> list[DetectedConflict]:
        """Remove duplicate conflicts."""
        seen = set()
        unique = []
        for c in conflicts:
            key = tuple(sorted(c.positions.keys()))
            if key not in seen:
                seen.add(key)
                unique.append(c)
        return unique

    def _extract_actions_from_response(self, r: ModelResponse) -> list[ActionItem]:
        """Extract action items from a single response."""
        actions = []
        sentences = re.split(r'[.!?]\s+', r.response)

        for sent in sentences:
            sent_lower = sent.lower()

            # Check for action indicators
            for indicator in self.ACTION_INDICATORS:
                if indicator in sent_lower and len(sent) > 20:
                    priority = self._determine_priority(sent_lower)
                    actions.append(ActionItem(
                        action=sent.strip()[:200],
                        priority=priority,
                        source_models=[r.model],
                        domain=r.domain,
                        rationale=f"Recommended by {r.model}"
                    ))
                    break

        return actions

    def _determine_priority(self, text: str) -> str:
        """Determine priority level from text signals."""
        for word in self.PRIORITY_HIGH:
            if word in text:
                return "high"
        for word in self.PRIORITY_MEDIUM:
            if word in text:
                return "medium"
        return "low"

    def _dedupe_actions(self, actions: list[ActionItem]) -> list[ActionItem]:
        """Merge similar actions and combine source models."""
        if not actions:
            return []

        # Group by similarity (simplified: first 50 chars)
        groups = defaultdict(list)
        for a in actions:
            key = a.action[:50].lower()
            groups[key].append(a)

        merged = []
        for group in groups.values():
            # Take highest priority, combine models
            best = min(group, key=lambda a: {"high": 0, "medium": 1, "low": 2}.get(a.priority, 3))
            all_models = list(set(m for a in group for m in a.source_models))
            merged.append(ActionItem(
                action=best.action,
                priority=best.priority,
                source_models=all_models,
                domain=best.domain,
                rationale=f"Recommended by {len(all_models)} model(s)"
            ))

        return merged


# ============================================================================
# FEEDBACK CAPTURE - Learning from User Interactions
# ============================================================================

class FeedbackCapture:
    """
    Captures and stores user feedback for continuous improvement.

    Feedback loops:
    1. Query logging - Track what questions are asked
    2. Response ratings - Which models gave best answers
    3. Action tracking - What did user actually do
    4. Pattern analysis - Identify improvement opportunities
    """

    def __init__(self):
        self.feedback_file = FEEDBACK_DIR / "feedback_log.jsonl"
        self.stats_file = FEEDBACK_DIR / "model_stats.json"

    def log_query(self, question: str, models: list[str]) -> str:
        """Log a query and return a query hash for later feedback."""
        query_hash = hashlib.sha256(
            f"{question}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

        entry = FeedbackEntry(
            query_hash=query_hash,
            question=question,
            models_used=models,
        )

        self._append_feedback(entry)
        return query_hash

    def rate_synthesis(self, query_hash: str, helpful: bool):
        """Rate whether the synthesis was helpful."""
        self._update_feedback(query_hash, {"synthesis_helpful": helpful})

    def rate_model(self, query_hash: str, model: str, is_best: bool):
        """Rate a specific model's response."""
        key = "best_model" if is_best else "worst_model"
        self._update_feedback(query_hash, {key: model})
        self._update_model_stats(model, is_best)

    def log_action(self, query_hash: str, action: str):
        """Log what action the user took after consultation."""
        self._update_feedback(query_hash, {"action_taken": action})

    def add_notes(self, query_hash: str, notes: str):
        """Add user notes to a consultation."""
        self._update_feedback(query_hash, {"user_notes": notes})

    def get_model_stats(self) -> dict:
        """Get aggregated model performance statistics."""
        if self.stats_file.exists():
            return json.loads(self.stats_file.read_text())
        return {}

    def get_recent_feedback(self, limit: int = 10) -> list[dict]:
        """Get recent feedback entries."""
        entries = []
        if self.feedback_file.exists():
            with open(self.feedback_file) as f:
                for line in f:
                    entries.append(json.loads(line))
        return entries[-limit:]

    def analyze_patterns(self) -> dict:
        """Analyze feedback patterns for improvement insights."""
        entries = self.get_recent_feedback(100)

        if not entries:
            return {"message": "No feedback data yet"}

        # Analyze patterns
        best_model_counts = Counter(e.get("best_model") for e in entries if e.get("best_model"))
        worst_model_counts = Counter(e.get("worst_model") for e in entries if e.get("worst_model"))
        synthesis_helpful = [e.get("synthesis_helpful") for e in entries if e.get("synthesis_helpful") is not None]

        return {
            "total_consultations": len(entries),
            "synthesis_helpful_rate": sum(synthesis_helpful) / len(synthesis_helpful) if synthesis_helpful else None,
            "top_performing_models": dict(best_model_counts.most_common(5)),
            "underperforming_models": dict(worst_model_counts.most_common(5)),
            "common_domains": Counter(
                model.split("-")[0] for e in entries for model in e.get("models_used", [])
            ),
        }

    # ---- Private helpers ----

    def _append_feedback(self, entry: FeedbackEntry):
        """Append a feedback entry to the log."""
        with open(self.feedback_file, "a") as f:
            f.write(json.dumps(asdict(entry)) + "\n")

    def _update_feedback(self, query_hash: str, updates: dict):
        """Update an existing feedback entry."""
        if not self.feedback_file.exists():
            return

        entries = []
        with open(self.feedback_file) as f:
            for line in f:
                entry = json.loads(line)
                if entry.get("query_hash") == query_hash:
                    entry.update(updates)
                entries.append(entry)

        with open(self.feedback_file, "w") as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")

    def _update_model_stats(self, model: str, is_positive: bool):
        """Update aggregated model statistics."""
        stats = self.get_model_stats()

        if model not in stats:
            stats[model] = {"positive": 0, "negative": 0, "total": 0}

        stats[model]["total"] += 1
        if is_positive:
            stats[model]["positive"] += 1
        else:
            stats[model]["negative"] += 1

        self.stats_file.write_text(json.dumps(stats, indent=2))


def detect_domains(question: str) -> set[str]:
    """Detect relevant domains based on keywords in the question."""
    question_lower = question.lower()
    detected = set()

    for domain, keywords in DOMAIN_KEYWORDS.items():
        for keyword in keywords:
            if keyword in question_lower:
                detected.add(domain)
                break

    # Always include meta for synthesis if multiple domains or complex question
    if len(detected) > 1 or len(question.split()) > 20:
        detected.add("meta")

    # Default to technical if no domain detected
    if not detected:
        detected.add("technical")
        detected.add("meta")

    return detected


def select_models(domains: set[str], max_models: int = 6) -> dict:
    """Select the most relevant models for the detected domains."""
    selected = {}

    for name, config in MODELS.items():
        if config["domain"] in domains:
            selected[name] = config

    # Sort by weight and take top N
    sorted_models = sorted(selected.items(), key=lambda x: -x[1]["weight"])
    return dict(sorted_models[:max_models])


async def query_model(
    session: aiohttp.ClientSession,
    name: str,
    prompt: str,
    config: dict,
    on_start: Optional[Callable] = None,
    on_complete: Optional[Callable] = None,
) -> ModelResponse:
    """Query a single Ollama model with timeout handling."""
    start_time = time.time()

    if on_start:
        on_start(name, config)

    try:
        async with session.post(
            OLLAMA_URL,
            json={"model": name, "prompt": prompt, "stream": False},
            timeout=aiohttp.ClientTimeout(total=config["timeout"])
        ) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                result = ModelResponse(
                    model=name,
                    domain=config["domain"],
                    response=None,
                    weight=config["weight"],
                    duration_ms=int((time.time() - start_time) * 1000),
                    status="error",
                    error=f"HTTP {resp.status}: {error_text[:100]}"
                )
            else:
                data = await resp.json()
                result = ModelResponse(
                    model=name,
                    domain=config["domain"],
                    response=data.get("response", ""),
                    weight=config["weight"],
                    duration_ms=int((time.time() - start_time) * 1000),
                    status="success"
                )
    except asyncio.TimeoutError:
        result = ModelResponse(
            model=name,
            domain=config["domain"],
            response=None,
            weight=config["weight"],
            duration_ms=int((time.time() - start_time) * 1000),
            status="timeout",
            error=f"Timeout after {config['timeout']}s"
        )
    except aiohttp.ClientError as e:
        result = ModelResponse(
            model=name,
            domain=config["domain"],
            response=None,
            weight=config["weight"],
            duration_ms=int((time.time() - start_time) * 1000),
            status="error",
            error=str(e)
        )

    if on_complete:
        on_complete(result)

    return result


class ConsoleUI:
    """Progressive console UI for displaying model responses."""

    def __init__(self):
        self.pending_models = set()
        self.completed = 0
        self.total = 0

    def print_header(self, question: str, models: dict):
        """Print the consultation header."""
        self.total = len(models)

        print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}Multi-Model Domain Consultation{Colors.RESET}")
        print(f"{'='*70}")
        print(f"\n{Colors.DIM}Question:{Colors.RESET} {question[:100]}{'...' if len(question) > 100 else ''}")
        print(f"\n{Colors.DIM}Models selected ({len(models)}):{Colors.RESET}")

        for name, config in models.items():
            color = config["color"]
            print(f"  {color}●{Colors.RESET} {name} ({config['domain']}) - {config['description']}")

        print(f"\n{Colors.DIM}Querying models in parallel...{Colors.RESET}\n")

    def on_model_start(self, name: str, config: dict):
        """Called when a model query starts."""
        self.pending_models.add(name)
        color = config["color"]
        print(f"  {Colors.PENDING}○{Colors.RESET} {name} - {Colors.DIM}querying...{Colors.RESET}")

    def on_model_complete(self, result: ModelResponse):
        """Called when a model query completes."""
        self.pending_models.discard(result.model)
        self.completed += 1

        config = MODELS.get(result.model, {})
        color = config.get("color", Colors.RESET)

        # Move cursor up and overwrite the "querying..." line
        # For simplicity, just print the result
        status_icon = {
            "success": f"{Colors.SUCCESS}●{Colors.RESET}",
            "error": f"{Colors.ERROR}✗{Colors.RESET}",
            "timeout": f"{Colors.WARNING}○{Colors.RESET}",
        }.get(result.status, "?")

        duration = f"{result.duration_ms/1000:.1f}s"
        print(f"  {status_icon} {color}{result.model}{Colors.RESET} - {result.status} ({duration})")

    def print_response(self, result: ModelResponse, index: int):
        """Print a single model response."""
        config = MODELS.get(result.model, {})
        color = config.get("color", Colors.RESET)
        domain_label = result.domain.upper()

        print(f"\n{Colors.BOLD}{'─'*70}{Colors.RESET}")
        print(f"{color}[{domain_label}]{Colors.RESET} {Colors.BOLD}{result.model}{Colors.RESET}")
        print(f"{Colors.DIM}{config.get('description', '')}{Colors.RESET}")
        print(f"{Colors.DIM}Weight: {result.weight:.0%} | Duration: {result.duration_ms/1000:.1f}s{Colors.RESET}")
        print(f"{'─'*70}")

        if result.status == "success" and result.response:
            # Truncate very long responses
            response = result.response
            if len(response) > 2000:
                response = response[:2000] + f"\n\n{Colors.DIM}[Response truncated at 2000 chars]{Colors.RESET}"
            print(f"\n{response}")
        elif result.status == "timeout":
            print(f"\n{Colors.WARNING}Timeout: Model did not respond within {config.get('timeout', 60)}s{Colors.RESET}")
        elif result.status == "error":
            print(f"\n{Colors.ERROR}Error: {result.error}{Colors.RESET}")

    def print_summary(self, results: list[ModelResponse], total_time_ms: int):
        """Print the consultation summary."""
        succeeded = sum(1 for r in results if r.status == "success")
        failed = sum(1 for r in results if r.status in ("error", "timeout"))

        print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}Summary{Colors.RESET}")
        print(f"{'='*70}")
        print(f"  Total time: {total_time_ms/1000:.1f}s")
        print(f"  Models: {Colors.SUCCESS}{succeeded} succeeded{Colors.RESET}, {Colors.ERROR if failed else Colors.DIM}{failed} failed{Colors.RESET}")

        if succeeded > 0:
            avg_weight = sum(r.weight for r in results if r.status == "success") / succeeded
            print(f"  Avg relevance weight: {avg_weight:.0%}")

        print()

    def print_synthesis(self, synthesis: SynthesisResult):
        """Print the aggregated synthesis results."""
        print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
        print(f"{Colors.META}▶ SYNTHESIS: Aggregated Insights{Colors.RESET}")
        print(f"{'='*70}")

        # Consensus score
        consensus_color = Colors.SUCCESS if synthesis.consensus_score > 0.7 else Colors.WARNING if synthesis.consensus_score > 0.4 else Colors.ERROR
        print(f"\n{Colors.BOLD}Consensus Score:{Colors.RESET} {consensus_color}{synthesis.consensus_score:.0%}{Colors.RESET}")
        print(f"{Colors.DIM}(Higher = more agreement across models){Colors.RESET}")

        # Domain coverage
        print(f"\n{Colors.BOLD}Domain Coverage:{Colors.RESET}")
        for domain, count in synthesis.domain_coverage.items():
            color = getattr(Colors, domain.upper(), Colors.RESET)
            print(f"  {color}●{Colors.RESET} {domain}: {count} model(s)")

        # Themes
        if synthesis.themes:
            print(f"\n{Colors.BOLD}Common Themes ({len(synthesis.themes)}):{Colors.RESET}")
            for i, theme in enumerate(synthesis.themes[:5], 1):
                conf_color = Colors.SUCCESS if theme.confidence > 0.5 else Colors.WARNING
                print(f"\n  {i}. {theme.theme[:80]}...")
                print(f"     {Colors.DIM}Confidence: {conf_color}{theme.confidence:.0%}{Colors.RESET} | Models: {', '.join(theme.supporting_models)}")
                if theme.evidence:
                    print(f"     {Colors.DIM}Evidence: {theme.evidence[0][:100]}...{Colors.RESET}")

        # Conflicts
        if synthesis.conflicts:
            print(f"\n{Colors.WARNING}{Colors.BOLD}⚠ Detected Conflicts ({len(synthesis.conflicts)}):{Colors.RESET}")
            for i, conflict in enumerate(synthesis.conflicts, 1):
                print(f"\n  {i}. {Colors.WARNING}{conflict.topic[:80]}{Colors.RESET}")
                for model, position in conflict.positions.items():
                    print(f"     {Colors.DIM}[{model}] {position[:80]}...{Colors.RESET}")
                if conflict.resolution_hint:
                    print(f"     {Colors.META}Hint: {conflict.resolution_hint}{Colors.RESET}")

        # Action items
        if synthesis.action_items:
            print(f"\n{Colors.BOLD}Recommended Actions ({len(synthesis.action_items)}):{Colors.RESET}")
            for i, action in enumerate(synthesis.action_items[:7], 1):
                priority_color = {
                    "high": Colors.ERROR,
                    "medium": Colors.WARNING,
                    "low": Colors.DIM
                }.get(action.priority, Colors.RESET)
                print(f"\n  {i}. [{priority_color}{action.priority.upper()}{Colors.RESET}] {action.action[:100]}")
                print(f"     {Colors.DIM}Source: {', '.join(action.source_models)} ({action.domain}){Colors.RESET}")

        print(f"\n{'='*70}\n")

    def print_feedback_prompt(self, query_hash: str):
        """Print feedback collection prompt."""
        print(f"{Colors.DIM}{'─'*70}{Colors.RESET}")
        print(f"{Colors.META}Feedback helps improve future consultations{Colors.RESET}")
        print(f"{Colors.DIM}Query ID: {query_hash}{Colors.RESET}")
        print(f"{Colors.DIM}To provide feedback, run:{Colors.RESET}")
        print(f"  python consult.py --feedback {query_hash} --helpful yes")
        print(f"  python consult.py --feedback {query_hash} --best-model <name>")
        print(f"  python consult.py --feedback {query_hash} --action 'What you did next'")
        print()


async def consult(
    question: str,
    models: dict,
    ui: Optional[ConsoleUI] = None,
    max_concurrent: int = 4,
) -> list[ModelResponse]:
    """
    Query multiple models in parallel and return aggregated results.

    Uses a semaphore to limit concurrency and a priority queue to
    surface high-weight responses first.
    """
    results_heap = []
    semaphore = asyncio.Semaphore(max_concurrent)

    async def bounded_query(session, name, config):
        async with semaphore:
            return await query_model(
                session, name, question, config,
                on_start=ui.on_model_start if ui else None,
                on_complete=ui.on_model_complete if ui else None,
            )

    async with aiohttp.ClientSession() as session:
        tasks = [
            bounded_query(session, name, config)
            for name, config in models.items()
        ]

        # Process results as they complete
        for coro in asyncio.as_completed(tasks):
            result = await coro
            # Use negative weight for max-heap behavior
            heappush(results_heap, (-result.weight, result.model, result))

    # Extract results sorted by weight (highest first)
    sorted_results = []
    while results_heap:
        _, _, result = heappop(results_heap)
        sorted_results.append(result)

    return sorted_results


def parse_args():
    parser = argparse.ArgumentParser(
        description="Multi-Model Domain Expert Consultation CLI with Synthesis & Feedback",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic consultation
  python consult.py "How should I architect a multi-agent code review system?"

  # With synthesis (aggregated insights)
  python consult.py --synthesize "Complex question requiring synthesis"

  # Domain-specific
  python consult.py --domains technical "Design patterns for parallel LLM queries"
  python consult.py --domains wealth,tax "Structuring a side business for tax efficiency"

  # Feedback commands
  python consult.py --feedback abc123 --helpful yes
  python consult.py --feedback abc123 --best-model unified-systems-architect
  python consult.py --feedback abc123 --action "Implemented the recommended pattern"

  # Analysis
  python consult.py --stats              # View model performance stats
  python consult.py --patterns           # Analyze feedback patterns
  python consult.py --list-models        # Show available models
        """
    )

    parser.add_argument("question", nargs="?", help="The question to consult on")
    parser.add_argument(
        "--domains", "-d",
        help="Comma-separated list of domains to query (technical,wealth,tax,personal,utility,meta)"
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Query all available models"
    )
    parser.add_argument(
        "--max-models", "-m",
        type=int,
        default=4,
        help="Maximum number of models to query (default: 4)"
    )
    parser.add_argument(
        "--max-concurrent", "-c",
        type=int,
        default=2,
        help="Maximum concurrent queries (default: 2, higher causes GPU contention)"
    )
    parser.add_argument(
        "--list-models", "-l",
        action="store_true",
        help="List all available models and exit"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Minimal output (just responses, no UI chrome)"
    )

    # Synthesis options
    parser.add_argument(
        "--synthesize", "-s",
        action="store_true",
        help="Enable synthesis: aggregate insights, detect conflicts, extract actions"
    )
    parser.add_argument(
        "--no-responses",
        action="store_true",
        help="With --synthesize, only show synthesis (skip individual responses)"
    )

    # Feedback options
    parser.add_argument(
        "--feedback", "-f",
        metavar="QUERY_ID",
        help="Provide feedback for a previous consultation"
    )
    parser.add_argument(
        "--helpful",
        choices=["yes", "no"],
        help="Rate if synthesis was helpful (use with --feedback)"
    )
    parser.add_argument(
        "--best-model",
        help="Mark a model as giving the best response (use with --feedback)"
    )
    parser.add_argument(
        "--worst-model",
        help="Mark a model as giving the worst response (use with --feedback)"
    )
    parser.add_argument(
        "--action",
        help="Log what action you took (use with --feedback)"
    )
    parser.add_argument(
        "--notes",
        help="Add notes to a consultation (use with --feedback)"
    )

    # Analysis options
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show model performance statistics"
    )
    parser.add_argument(
        "--patterns",
        action="store_true",
        help="Analyze feedback patterns"
    )
    parser.add_argument(
        "--recent",
        type=int,
        metavar="N",
        help="Show N most recent consultations"
    )

    # Output options
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON (for programmatic use)"
    )

    return parser.parse_args()


def list_models():
    """Print all available models grouped by domain."""
    print(f"\n{Colors.BOLD}Available Models (19){Colors.RESET}\n")

    by_domain = {}
    for name, config in MODELS.items():
        domain = config["domain"]
        if domain not in by_domain:
            by_domain[domain] = []
        by_domain[domain].append((name, config))

    domain_order = ["meta", "technical", "wealth", "tax", "personal", "utility"]

    for domain in domain_order:
        if domain not in by_domain:
            continue

        models = by_domain[domain]
        color = models[0][1]["color"]
        print(f"{color}{domain.upper()}{Colors.RESET}")

        for name, config in models:
            print(f"  {color}●{Colors.RESET} {name}")
            print(f"    {Colors.DIM}{config['description']}{Colors.RESET}")
            print(f"    {Colors.DIM}Weight: {config['weight']:.0%} | Timeout: {config['timeout']}s{Colors.RESET}")
        print()


def handle_feedback(args):
    """Handle feedback-related commands."""
    feedback = FeedbackCapture()

    if args.helpful:
        feedback.rate_synthesis(args.feedback, args.helpful == "yes")
        print(f"{Colors.SUCCESS}✓ Recorded synthesis rating: {args.helpful}{Colors.RESET}")

    if args.best_model:
        feedback.rate_model(args.feedback, args.best_model, is_best=True)
        print(f"{Colors.SUCCESS}✓ Recorded best model: {args.best_model}{Colors.RESET}")

    if args.worst_model:
        feedback.rate_model(args.feedback, args.worst_model, is_best=False)
        print(f"{Colors.WARNING}✓ Recorded worst model: {args.worst_model}{Colors.RESET}")

    if args.action:
        feedback.log_action(args.feedback, args.action)
        print(f"{Colors.SUCCESS}✓ Recorded action taken{Colors.RESET}")

    if args.notes:
        feedback.add_notes(args.feedback, args.notes)
        print(f"{Colors.SUCCESS}✓ Added notes{Colors.RESET}")

    print(f"\n{Colors.DIM}Feedback stored at: {FEEDBACK_DIR}{Colors.RESET}")


def show_stats():
    """Show model performance statistics."""
    feedback = FeedbackCapture()
    stats = feedback.get_model_stats()

    if not stats:
        print(f"{Colors.WARNING}No model statistics yet. Use --helpful and --best-model flags after consultations.{Colors.RESET}")
        return

    print(f"\n{Colors.BOLD}Model Performance Statistics{Colors.RESET}")
    print(f"{'='*70}\n")

    # Sort by positive rate
    sorted_stats = sorted(
        stats.items(),
        key=lambda x: x[1]["positive"] / max(x[1]["total"], 1),
        reverse=True
    )

    for model, data in sorted_stats:
        total = data["total"]
        positive = data["positive"]
        rate = positive / total if total > 0 else 0

        color = Colors.SUCCESS if rate > 0.6 else Colors.WARNING if rate > 0.3 else Colors.ERROR
        bar = "█" * int(rate * 20) + "░" * (20 - int(rate * 20))

        print(f"  {model}")
        print(f"    {color}{bar}{Colors.RESET} {rate:.0%} ({positive}/{total} positive)")
        print()


def show_patterns():
    """Analyze and display feedback patterns."""
    feedback = FeedbackCapture()
    patterns = feedback.analyze_patterns()

    print(f"\n{Colors.BOLD}Feedback Pattern Analysis{Colors.RESET}")
    print(f"{'='*70}\n")

    if "message" in patterns:
        print(f"{Colors.WARNING}{patterns['message']}{Colors.RESET}")
        return

    print(f"  Total consultations: {patterns['total_consultations']}")

    if patterns['synthesis_helpful_rate'] is not None:
        rate = patterns['synthesis_helpful_rate']
        color = Colors.SUCCESS if rate > 0.7 else Colors.WARNING
        print(f"  Synthesis helpful rate: {color}{rate:.0%}{Colors.RESET}")

    if patterns['top_performing_models']:
        print(f"\n  {Colors.SUCCESS}Top Performing Models:{Colors.RESET}")
        for model, count in patterns['top_performing_models'].items():
            print(f"    ● {model}: {count} best ratings")

    if patterns['underperforming_models']:
        print(f"\n  {Colors.WARNING}Underperforming Models:{Colors.RESET}")
        for model, count in patterns['underperforming_models'].items():
            print(f"    ○ {model}: {count} worst ratings")

    print()


def show_recent(n: int):
    """Show recent consultations."""
    feedback = FeedbackCapture()
    entries = feedback.get_recent_feedback(n)

    if not entries:
        print(f"{Colors.WARNING}No consultation history yet.{Colors.RESET}")
        return

    print(f"\n{Colors.BOLD}Recent Consultations ({len(entries)}){Colors.RESET}")
    print(f"{'='*70}\n")

    for entry in reversed(entries):
        query_hash = entry.get("query_hash", "unknown")
        question = entry.get("question", "")[:60]
        timestamp = entry.get("timestamp", "")[:10]
        models = entry.get("models_used", [])

        print(f"  {Colors.DIM}[{query_hash}]{Colors.RESET} {timestamp}")
        print(f"  Q: {question}...")
        print(f"  Models: {', '.join(models[:3])}{'...' if len(models) > 3 else ''}")

        if entry.get("synthesis_helpful") is not None:
            helpful = entry["synthesis_helpful"]
            icon = f"{Colors.SUCCESS}✓{Colors.RESET}" if helpful else f"{Colors.ERROR}✗{Colors.RESET}"
            print(f"  Synthesis helpful: {icon}")

        if entry.get("action_taken"):
            print(f"  {Colors.META}Action: {entry['action_taken'][:50]}...{Colors.RESET}")

        print()


async def main():
    args = parse_args()

    # Handle non-query commands first
    if args.list_models:
        list_models()
        return

    if args.stats:
        show_stats()
        return

    if args.patterns:
        show_patterns()
        return

    if args.recent:
        show_recent(args.recent)
        return

    if args.feedback:
        handle_feedback(args)
        return

    if not args.question:
        print(f"{Colors.ERROR}Error: Please provide a question{Colors.RESET}")
        print("Usage: python consult.py \"Your question here\"")
        print("       python consult.py --synthesize \"Question for aggregated insights\"")
        print("       python consult.py --help for more options")
        sys.exit(1)

    question = args.question

    # Determine which models to query
    if args.all:
        selected_models = MODELS
    elif args.domains:
        domains = set(d.strip() for d in args.domains.split(","))
        selected_models = select_models(domains, args.max_models)
    else:
        # Auto-detect domains from question
        detected_domains = detect_domains(question)
        selected_models = select_models(detected_domains, args.max_models)

    if not selected_models:
        print(f"{Colors.ERROR}Error: No models selected{Colors.RESET}")
        sys.exit(1)

    # Initialize UI and feedback
    ui = None if args.quiet else ConsoleUI()
    feedback = FeedbackCapture()

    # Log the query
    query_hash = feedback.log_query(question, list(selected_models.keys()))

    if ui:
        ui.print_header(question, selected_models)

    # Run consultation
    start_time = time.time()
    results = await consult(
        question,
        selected_models,
        ui=ui,
        max_concurrent=args.max_concurrent,
    )
    total_time_ms = int((time.time() - start_time) * 1000)

    # Run synthesis if requested
    synthesis = None
    if args.synthesize:
        engine = SynthesisEngine()
        engine.add_responses(results)
        synthesis = engine.synthesize(question)

    # Handle JSON output
    if args.json:
        output = {
            "query_hash": query_hash,
            "question": question,
            "total_time_ms": total_time_ms,
            "results": [
                {
                    "model": r.model,
                    "domain": r.domain,
                    "status": r.status,
                    "weight": r.weight,
                    "duration_ms": r.duration_ms,
                    "response": r.response[:1000] if r.response else None,
                    "error": r.error,
                }
                for r in results
            ],
        }
        if synthesis:
            output["synthesis"] = {
                "consensus_score": synthesis.consensus_score,
                "themes": [{"theme": t.theme, "confidence": t.confidence, "models": t.supporting_models} for t in synthesis.themes],
                "conflicts": [{"topic": c.topic, "positions": c.positions} for c in synthesis.conflicts],
                "actions": [{"action": a.action, "priority": a.priority, "models": a.source_models} for a in synthesis.action_items],
            }
        print(json.dumps(output, indent=2))
        return

    # Print individual responses (unless --no-responses with synthesis)
    if not (args.synthesize and args.no_responses):
        if ui:
            print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
            print(f"{Colors.BOLD}Responses (sorted by relevance weight){Colors.RESET}")
            print(f"{'='*70}")

        for i, result in enumerate(results):
            if result.status == "success":
                if ui:
                    ui.print_response(result, i)
                else:
                    print(f"\n--- {result.model} ---\n{result.response}")

    # Print failures
    failures = [r for r in results if r.status != "success"]
    if failures and ui:
        print(f"\n{Colors.BOLD}Failed Models{Colors.RESET}")
        for result in failures:
            ui.print_response(result, 0)

    # Print summary
    if ui:
        ui.print_summary(results, total_time_ms)

    # Print synthesis results
    if synthesis and ui:
        ui.print_synthesis(synthesis)

    # Print feedback prompt
    if ui and not args.quiet:
        ui.print_feedback_prompt(query_hash)


if __name__ == "__main__":
    asyncio.run(main())
