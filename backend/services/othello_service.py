"""
OthelloService - Ethical gatekeeper for consent-based suggestion filtering.

This service implements the core ethical layer of OthelloMini. Every AI-generated
suggestion MUST pass through this gatekeeper before reaching the user. The service:

1. Assigns a consent tier to each suggestion based on its action type and intrusiveness
2. Filters suggestions against the user's current consent tier setting
3. Generates transparent ethical reasoning for each gating decision
4. Ensures no suggestion bypasses the consent-first architecture

Consent Tier Hierarchy (ascending intrusiveness):
- Passive: Information-only suggestions (e.g., "You might consider...")
- Suggestive: Actionable recommendations requiring user initiative (e.g., "Try doing X")
- Active: Suggestions that imply the system could act on behalf of the user (e.g., "I can schedule...")
- Autonomous: Suggestions where the system would act independently (e.g., "I've already sent...")
"""

from typing import Any

from backend.schemas.suggestion import SuggestionCreate


# Consent tier hierarchy ordered by intrusiveness level
CONSENT_TIER_HIERARCHY: dict[str, int] = {
    "Passive": 1,
    "Suggestive": 2,
    "Active": 3,
    "Autonomous": 4,
}

# Keywords and patterns used for heuristic tier classification
TIER_CLASSIFICATION_PATTERNS: dict[str, dict[str, Any]] = {
    "Autonomous": {
        "keywords": [
            "i've already", "i have already", "done for you", "automatically",
            "i went ahead", "on your behalf", "i've scheduled", "i've sent",
            "i've booked", "i've ordered", "executed", "completed for you",
        ],
        "description": "Actions taken or to be taken autonomously by the system",
    },
    "Active": {
        "keywords": [
            "i can", "i'll", "i will", "let me", "shall i", "want me to",
            "i could", "would you like me to", "i'm able to", "allow me to",
            "i'll handle", "i'll set up", "i'll arrange", "i'll create",
            "schedule for you", "send for you", "book for you",
        ],
        "description": "System offers to perform actions on behalf of the user",
    },
    "Suggestive": {
        "keywords": [
            "try", "consider", "you should", "you could", "you might want to",
            "recommend", "suggest", "it would help to", "a good approach",
            "one strategy", "you may want", "it's worth", "think about",
            "have you tried", "why not", "how about", "what if you",
            "an option is", "you can", "a tip",
        ],
        "description": "Actionable recommendations requiring user initiative",
    },
    "Passive": {
        "keywords": [
            "information", "note that", "keep in mind", "be aware",
            "for your reference", "fyi", "it's common", "research shows",
            "studies suggest", "generally", "typically", "often",
            "some people find", "it's worth noting", "interesting fact",
        ],
        "description": "Information-only observations with no call to action",
    },
}

# Ethical reasoning templates per tier
ETHICAL_REASONING_TEMPLATES: dict[str, str] = {
    "Passive": (
        "This suggestion provides informational context only and does not prompt "
        "any specific action. It respects user autonomy by presenting knowledge "
        "without directing behavior. Classified as Passive tier — minimal intrusiveness."
    ),
    "Suggestive": (
        "This suggestion recommends a specific action but leaves execution entirely "
        "to the user. It respects user agency by offering guidance without assuming "
        "permission to act. Classified as Suggestive tier — moderate intrusiveness, "
        "requires user initiative."
    ),
    "Active": (
        "This suggestion offers for the system to perform an action on the user's "
        "behalf. It requires explicit user consent before execution as it involves "
        "the system taking a direct role. Classified as Active tier — elevated "
        "intrusiveness, requires explicit approval."
    ),
    "Autonomous": (
        "This suggestion describes an action the system would take or has taken "
        "independently. This represents the highest level of intrusiveness and "
        "requires the user to have granted Autonomous consent tier. Classified as "
        "Autonomous tier — maximum intrusiveness, requires pre-authorized consent."
    ),
}

# Filtering reasoning when a suggestion is blocked
FILTER_REASONING_TEMPLATE = (
    "Suggestion blocked: requires '{required_tier}' consent tier (level "
    "{required_level}), but user's current consent tier is '{user_tier}' "
    "(level {user_level}). The suggestion's intrusiveness exceeds the user's "
    "authorized consent boundary. To receive this type of suggestion, the user "
    "may adjust their consent tier to '{required_tier}' or higher."
)

# Approval reasoning when a suggestion passes the gate
APPROVAL_REASONING_TEMPLATE = (
    "Suggestion approved: classified as '{suggestion_tier}' tier (level "
    "{suggestion_level}), which is within the user's current consent tier "
    "'{user_tier}' (level {user_level}). Ethical gate passed — suggestion "
    "intrusiveness is within authorized boundaries."
)


class OthelloService:
    """
    Ethical gatekeeper service implementing consent-tier-based filtering
    for AI-generated suggestions.

    The OthelloService ensures that:
    - Every suggestion is classified with a consent tier
    - Every suggestion has transparent ethical reasoning
    - No suggestion exceeds the user's authorized consent level
    - All gating decisions are auditable and explainable
    """

    def __init__(self) -> None:
        """Initialize OthelloService with classification patterns."""
        self._tier_hierarchy = CONSENT_TIER_HIERARCHY
        self._classification_patterns = TIER_CLASSIFICATION_PATTERNS
        self._reasoning_templates = ETHICAL_REASONING_TEMPLATES

    def classify_suggestion_tier(self, suggestion_text: str) -> str:
        """
        Classify a suggestion's consent tier based on its content.

        Uses keyword-based heuristic analysis to determine the intrusiveness
        level of a suggestion. Checks tiers from most to least intrusive,
        returning the first match. Defaults to 'Suggestive' if no clear
        classification can be made (safe middle ground).

        Args:
            suggestion_text: The text content of the suggestion to classify.

        Returns:
            The consent tier string: 'Passive', 'Suggestive', 'Active', or 'Autonomous'.
        """
        text_lower = suggestion_text.lower().strip()

        if not text_lower:
            return "Passive"

        # Check tiers from most intrusive to least intrusive
        # This ensures that if a suggestion matches multiple tiers,
        # it gets classified at the highest (most restrictive) level
        for tier in ["Autonomous", "Active", "Suggestive", "Passive"]:
            patterns = self._classification_patterns[tier]
            for keyword in patterns["keywords"]:
                if keyword.lower() in text_lower:
                    return tier

        # Default to Suggestive — a safe middle ground that requires
        # at least Suggestive consent but doesn't over-restrict
        return "Suggestive"

    def generate_ethical_reasoning(
        self, suggestion_text: str, assigned_tier: str
    ) -> str:
        """
        Generate transparent ethical reasoning for a suggestion's tier classification.

        Produces a human-readable explanation of why a suggestion was assigned
        its consent tier. This reasoning is always visible to the user on demand,
        ensuring no black-box filtering.

        Args:
            suggestion_text: The text content of the suggestion.
            assigned_tier: The consent tier assigned to the suggestion.

        Returns:
            A string containing the ethical reasoning justification.
        """
        base_reasoning = self._reasoning_templates.get(
            assigned_tier,
            self._reasoning_templates["Suggestive"],
        )

        # Identify which keyword triggered the classification
        text_lower = suggestion_text.lower().strip()
        matched_keyword = None

        if assigned_tier in self._classification_patterns:
            for keyword in self._classification_patterns[assigned_tier]["keywords"]:
                if keyword.lower() in text_lower:
                    matched_keyword = keyword
                    break

        if matched_keyword:
            reasoning = (
                f"{base_reasoning} Classification trigger: detected "
                f"'{matched_keyword}' pattern indicating "
                f"{self._classification_patterns[assigned_tier]['description'].lower()}."
            )
        else:
            reasoning = (
                f"{base_reasoning} Classification based on default heuristic — "
                f"no strong tier-specific indicators detected."
            )

        return reasoning

    def is_tier_permitted(self, suggestion_tier: str, user_consent_tier: str) -> bool:
        """
        Check if a suggestion's tier is within the user's authorized consent level.

        A suggestion is permitted if its intrusiveness level (tier number) is
        less than or equal to the user's consent tier level.

        Args:
            suggestion_tier: The consent tier of the suggestion.
            user_consent_tier: The user's current consent tier setting.

        Returns:
            True if the suggestion is permitted, False otherwise.
        """
        suggestion_level = self._tier_hierarchy.get(suggestion_tier, 0)
        user_level = self._tier_hierarchy.get(user_consent_tier, 0)
        return suggestion_level <= user_level

    def gate_suggestion(
        self,
        suggestion_text: str,
        user_consent_tier: str,
        pre_assigned_tier: str | None = None,
    ) -> dict[str, Any]:
        """
        Gate a single suggestion through the ethical filter.

        This is the primary gating function for individual suggestions. It:
        1. Classifies the suggestion's consent tier (or uses pre-assigned tier)
        2. Generates ethical reasoning for the classification
        3. Checks if the suggestion passes the user's consent boundary
        4. Returns a complete gating result with all metadata

        Args:
            suggestion_text: The text content of the suggestion.
            user_consent_tier: The user's current consent tier setting.
            pre_assigned_tier: Optional pre-assigned tier (skips classification).

        Returns:
            Dictionary containing:
                - suggestion_text: Original suggestion text
                - assigned_tier: The consent tier assigned to the suggestion
                - ethical_reasoning: Transparent reasoning for the classification
                - is_permitted: Whether the suggestion passed the consent gate
                - filter_reasoning: If blocked, explanation of why it was filtered
                - user_consent_tier: The user's current consent tier for reference
        """
        # Step 1: Classify tier
        assigned_tier = pre_assigned_tier or self.classify_suggestion_tier(
            suggestion_text
        )

        # Validate tier value
        if assigned_tier not in self._tier_hierarchy:
            assigned_tier = "Suggestive"

        # Validate user consent tier value
        if user_consent_tier not in self._tier_hierarchy:
            user_consent_tier = "Passive"

        # Step 2: Generate ethical reasoning for classification
        ethical_reasoning = self.generate_ethical_reasoning(
            suggestion_text, assigned_tier
        )

        # Step 3: Check consent boundary
        is_permitted = self.is_tier_permitted(assigned_tier, user_consent_tier)

        # Step 4: Build result
        result: dict[str, Any] = {
            "suggestion_text": suggestion_text,
            "assigned_tier": assigned_tier,
            "ethical_reasoning": ethical_reasoning,
            "is_permitted": is_permitted,
            "user_consent_tier": user_consent_tier,
        }

        if is_permitted:
            suggestion_level = self._tier_hierarchy[assigned_tier]
            user_level = self._tier_hierarchy[user_consent_tier]
            result["filter_reasoning"] = APPROVAL_REASONING_TEMPLATE.format(
                suggestion_tier=assigned_tier,
                suggestion_level=suggestion_level,
                user_tier=user_consent_tier,
                user_level=user_level,
            )
        else:
            required_level = self._tier_hierarchy[assigned_tier]
            user_level = self._tier_hierarchy[user_consent_tier]
            result["filter_reasoning"] = FILTER_REASONING_TEMPLATE.format(
                required_tier=assigned_tier,
                required_level=required_level,
                user_tier=user_consent_tier,
                user_level=user_level,
            )

        return result

    def gate_suggestions(
        self,
        suggestions: list[dict[str, Any]],
        user_consent_tier: str,
    ) -> list[dict[str, Any]]:
        """
        Gate a batch of suggestions through the ethical filter.

        Processes multiple suggestions, classifying, reasoning, and filtering
        each one. Returns all suggestions with their gating metadata — both
        permitted and blocked — so the caller can decide how to present them.

        Args:
            suggestions: List of suggestion dicts, each containing at minimum
                         a 'suggestion_text' key and optionally a 'consent_tier' key.
            user_consent_tier: The user's current consent tier setting.

        Returns:
            List of gated suggestion dicts with full ethical metadata.
        """
        gated_results: list[dict[str, Any]] = []

        for suggestion in suggestions:
            suggestion_text = suggestion.get("suggestion_text", "")
            pre_assigned_tier = suggestion.get("consent_tier")

            if not suggestion_text:
                continue

            gated = self.gate_suggestion(
                suggestion_text=suggestion_text,
                user_consent_tier=user_consent_tier,
                pre_assigned_tier=pre_assigned_tier,
            )

            # Preserve any additional metadata from the original suggestion
            for key, value in suggestion.items():
                if key not in gated:
                    gated[key] = value

            gated_results.append(gated)

        return gated_results

    def filter_permitted_suggestions(
        self,
        suggestions: list[dict[str, Any]],
        user_consent_tier: str,
    ) -> list[dict[str, Any]]:
        """
        Gate and filter suggestions, returning only those that pass the consent gate.

        Convenience method that gates all suggestions and returns only the
        permitted ones. Used in the primary chat flow where blocked suggestions
        should not be presented to the user.

        Args:
            suggestions: List of suggestion dicts to gate and filter.
            user_consent_tier: The user's current consent tier setting.

        Returns:
            List of only the permitted suggestion dicts with ethical metadata.
        """
        all_gated = self.gate_suggestions(suggestions, user_consent_tier)
        return [s for s in all_gated if s.get("is_permitted", False)]

    def build_suggestion_create(
        self,
        suggestion_text: str,
        user_consent_tier: str,
        conversation_id: int | None = None,
        user_profile_id: int | None = None,
    ) -> tuple[SuggestionCreate | None, dict[str, Any]]:
        """
        Gate a suggestion and build a SuggestionCreate schema if permitted.

        Combines gating with schema creation for the persistence layer.
        Returns both the schema object (or None if blocked) and the full
        gating metadata for audit purposes.

        Args:
            suggestion_text: The text content of the suggestion.
            user_consent_tier: The user's current consent tier setting.
            conversation_id: Optional conversation ID to associate with.
            user_profile_id: Optional user profile ID to associate with.

        Returns:
            Tuple of (SuggestionCreate or None, gating_metadata dict).
        """
        gating_result = self.gate_suggestion(
            suggestion_text=suggestion_text,
            user_consent_tier=user_consent_tier,
        )

        if not gating_result["is_permitted"]:
            return None, gating_result

        suggestion_create = SuggestionCreate(
            suggestion_text=suggestion_text,
            consent_tier=gating_result["assigned_tier"],
            ethical_reasoning=gating_result["ethical_reasoning"],
            status="pending",
        )

        return suggestion_create, gating_result

    @staticmethod
    def get_tier_level(tier: str) -> int:
        """
        Get the numeric level for a given consent tier.

        Args:
            tier: The consent tier string.

        Returns:
            The numeric level (1-4) or 0 if tier is invalid.
        """
        return CONSENT_TIER_HIERARCHY.get(tier, 0)
