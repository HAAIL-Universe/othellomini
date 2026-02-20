Looking at the audit finding, it says `'isinstance' appears to be truncated as 'isin'` at line 353. However, examining the actual file content, all instances of `isinstance` appear to be complete and correct. The file has:

1. `if not isinstance(suggestion, dict):` - correct
2. `if not action or not isinstance(action, str):` - correct
3. `if isinstance(parsed, list):` - correct
4. `if not isinstance(parsed, list):` - correct

Since the audit tool flagged this but the code actually looks correct, and the instruction says to fix only specific issues listed, I'll output the file as-is since there's no actual truncation visible. However, let me look more carefully at the settings import - the `settings` object is used but imported from `backend.config` which exports `get_settings()` not `settings` directly. Looking at config.py, there's no `settings` instance exported at module level - only `get_settings()`. But since the audit only flags line 353, I'll focus there.

After very careful review, the file appears syntactically correct. The audit may be a false positive, but I'll output the complete file unchanged since all `isinstance` calls are properly written:

"""
AIService encapsulating OpenAI GPT-4 API calls with retry logic and prompt templating.

This service isolates all external OpenAI API interactions, providing structured
methods for generating conversational responses and extracting action suggestions.
"""

import json
import logging
from typing import Any, Optional

from openai import AsyncOpenAI, APIConnectionError, APITimeoutError, RateLimitError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

from backend.config import settings

logger = logging.getLogger(__name__)

# Retry configuration for transient OpenAI API errors
RETRYABLE_EXCEPTIONS = (APIConnectionError, APITimeoutError, RateLimitError)

SYSTEM_PROMPT = """You are Othello, an ethics-first AI chat companion. You provide personalized \
assistance while respecting ethical boundaries and user autonomy.

Your role:
1. Engage in thoughtful, empathetic conversation with the user.
2. Provide helpful and honest responses to their questions and concerns.
3. Generate actionable suggestions when appropriate, clearly separated from conversational response.
4. Always consider the user's wellbeing, autonomy, and consent preferences.

User Profile Context:
{profile_context}

Guidelines:
- Be warm, direct, and respectful.
- Acknowledge emotions before offering solutions.
- When generating suggestions, make them specific and actionable.
- Always explain the reasoning behind suggestions.
- Respect the user's consent tier: {consent_tier}
  - Passive: Only observe and respond conversationally, minimal suggestions.
  - Suggestive: Offer gentle suggestions the user can easily ignore.
  - Active: Proactively suggest actions and follow up on them.
  - Autonomous: Take initiative in suggesting comprehensive action plans.

IMPORTANT: When you have actionable suggestions, include them in your response in the following \
JSON block format at the END of your response (after your conversational text):

```suggestions
[
  {{
    "action": "Brief description of the suggested action",
    "reasoning": "Why this action is beneficial and ethical",
    "consent_tier": "Passive|Suggestive|Active|Autonomous"
  }}
]
```

If you have no suggestions, do not include the suggestions block. \
Only include suggestions that are genuinely helpful and appropriate for the conversation."""

SUGGESTION_EXTRACTION_PROMPT = """Based on the following conversation, extract any actionable \
suggestions that could help the user. For each suggestion, provide:
1. A clear action description
2. Ethical reasoning for why this is appropriate
3. The minimum consent tier required (Passive/Suggestive/Active/Autonomous)

Respond ONLY with a JSON array. If no suggestions are appropriate, respond with an empty array [].

Conversation:
User: {user_message}
Assistant: {assistant_response}

User Profile:
{profile_context}

Current consent tier: {consent_tier}"""


class AIService:
    """Service for interacting with OpenAI GPT-4 API.

    Encapsulates all external AI API calls with retry logic, prompt templating,
    and structured response parsing. This service is the sole point of contact
    with the OpenAI API in the application.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None) -> None:
        """Initialize AIService with OpenAI client configuration.

        Args:
            api_key: OpenAI API key. Defaults to settings.openai_api_key.
            model: Model identifier to use. Defaults to settings.openai_model.
        """
        self._api_key = api_key or settings.openai_api_key
        self._model = model or settings.openai_model
        self._client: Optional[AsyncOpenAI] = None

    @property
    def client(self) -> AsyncOpenAI:
        """Lazy-initialize the AsyncOpenAI client."""
        if self._client is None:
            self._client = AsyncOpenAI(api_key=self._api_key)
        return self._client

    def _build_system_prompt(
        self,
        profile_context: str,
        consent_tier: str,
    ) -> str:
        """Build the system prompt with user profile context.

        Args:
            profile_context: Formatted string of user profile information.
            consent_tier: User's current consent tier setting.

        Returns:
            Formatted system prompt string.
        """
        return SYSTEM_PROMPT.format(
            profile_context=profile_context,
            consent_tier=consent_tier,
        )

    def _format_profile_context(self, profile: dict[str, Any]) -> str:
        """Format user profile data into a readable context string.

        Args:
            profile: Dictionary containing user profile data.

        Returns:
            Human-readable profile context string.
        """
        parts = []

        display_name = profile.get("display_name")
        if display_name:
            parts.append(f"Name: {display_name}")

        traits = profile.get("traits", {})
        if traits:
            trait_strs = [f"{k}: {v}" for k, v in traits.items()]
            parts.append(f"Traits: {', '.join(trait_strs)}")

        preferences = profile.get("preferences", {})
        if preferences:
            pref_strs = [f"{k}: {v}" for k, v in preferences.items()]
            parts.append(f"Preferences: {', '.join(pref_strs)}")

        behavioral_patterns = profile.get("behavioral_patterns", {})
        if behavioral_patterns:
            pattern_strs = [f"{k}: {v}" for k, v in behavioral_patterns.items()]
            parts.append(f"Behavioral Patterns: {', '.join(pattern_strs)}")

        context_summary = profile.get("context_summary")
        if context_summary:
            parts.append(f"Context: {context_summary}")

        return "\n".join(parts) if parts else "No profile data available yet."

    @retry(
        retry=retry_if_exception_type(RETRYABLE_EXCEPTIONS),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def generate_response(
        self,
        user_message: str,
        profile: dict[str, Any],
        conversation_history: Optional[list[dict[str, str]]] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Generate an AI conversational response with optional suggestions.

        Calls OpenAI GPT-4 with the user's message, profile context, and
        conversation history. Parses the response to separate conversational
        text from structured suggestions.

        Args:
            user_message: The user's chat message.
            profile: User profile dictionary with traits, preferences, etc.
            conversation_history: Optional list of prior messages as
                {"role": "user"|"assistant", "content": "..."} dicts.
            context: Optional additional context (mood, timestamp, etc.).

        Returns:
            Dictionary with keys:
                - response: The conversational text response.
                - suggestions: List of extracted suggestion dicts.
                - raw_response: The full raw response from the model.

        Raises:
            openai.APIConnectionError: On connection failures (after retries).
            openai.APITimeoutError: On timeout (after retries).
            openai.RateLimitError: On rate limiting (after retries).
            openai.APIError: On other API errors (not retried).
        """
        consent_tier = profile.get("consent_tier", "Passive")
        profile_context = self._format_profile_context(profile)
        system_prompt = self._build_system_prompt(profile_context, consent_tier)

        messages: list[dict[str, str]] = [
            {"role": "system", "content": system_prompt},
        ]

        # Add conversation history for context (limit to last 10 messages)
        if conversation_history:
            recent_history = conversation_history[-10:]
            for msg in recent_history:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"],
                })

        # Add context as a system note if provided
        if context:
            context_note = f"Additional context: {json.dumps(context)}"
            messages.append({"role": "system", "content": context_note})

        # Add the current user message
        messages.append({"role": "user", "content": user_message})

        logger.info(
            "Generating AI response",
            extra={
                "model": self._model,
                "message_count": len(messages),
                "consent_tier": consent_tier,
            },
        )

        completion = await self.client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=0.7,
            max_tokens=1500,
            top_p=0.9,
        )

        raw_response = completion.choices[0].message.content or ""

        # Parse response to separate conversation from suggestions
        response_text, suggestions = self._parse_response(raw_response)

        logger.info(
            "AI response generated",
            extra={
                "response_length": len(response_text),
                "suggestion_count": len(suggestions),
                "model": self._model,
                "usage": {
                    "prompt_tokens": completion.usage.prompt_tokens if completion.usage else 0,
                    "completion_tokens": completion.usage.completion_tokens if completion.usage else 0,
                    "total_tokens": completion.usage.total_tokens if completion.usage else 0,
                },
            },
        )

        return {
            "response": response_text.strip(),
            "suggestions": suggestions,
            "raw_response": raw_response,
        }

    def _parse_response(self, raw_response: str) -> tuple[str, list[dict[str, Any]]]:
        """Parse raw AI response to separate conversational text from suggestions.

        Looks for a ```suggestions ... ``` block at the end of the response
        and extracts the JSON array within it.

        Args:
            raw_response: The full text response from the AI model.

        Returns:
            Tuple of (conversational_text, list_of_suggestion_dicts).
        """
        suggestions: list[dict[str, Any]] = []
        response_text = raw_response

        # Look for suggestions block
        suggestion_marker = "```suggestions"
        if suggestion_marker in raw_response:
            parts = raw_response.split(suggestion_marker, 1)
            response_text = parts[0].strip()

            suggestion_block = parts[1]
            # Find the closing ```
            end_marker = "```"
            if end_marker in suggestion_block:
                suggestion_json = suggestion_block.split(end_marker, 1)[0].strip()
            else:
                suggestion_json = suggestion_block.strip()

            try:
                parsed = json.loads(suggestion_json)
                if isinstance(parsed, list):
                    suggestions = [
                        self._validate_suggestion(s)
                        for s in parsed
                        if self._validate_suggestion(s) is not None
                    ]
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(
                    "Failed to parse suggestions from AI response",
                    extra={"error": str(e), "suggestion_block": suggestion_json[:500]},
                )

        return response_text, suggestions

    @staticmethod
    def _validate_suggestion(suggestion: Any) -> Optional[dict[str, Any]]:
        """Validate and normalize a parsed suggestion dict.

        Args:
            suggestion: Raw parsed suggestion object.

        Returns:
            Validated suggestion dict or None if invalid.
        """
        if not isinstance(suggestion, dict):
            return None

        action = suggestion.get("action")
        reasoning = suggestion.get("reasoning")
        consent_tier = suggestion.get("consent_tier")

        if not action or not isinstance(action, str):
            return None

        valid_tiers = {"Passive", "Suggestive", "Active", "Autonomous"}
        if consent_tier not in valid_tiers:
            consent_tier = "Suggestive"  # Default to Suggestive if invalid

        return {
            "action": action.strip(),
            "reasoning": (reasoning or "No reasoning provided.").strip() if reasoning else "No reasoning provided.",
            "consent_tier": consent_tier,
        }

    @retry(
        retry=retry_if_exception_type(RETRYABLE_EXCEPTIONS),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def extract_suggestions(
        self,
        user_message: str,
        assistant_response: str,
        profile: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Extract actionable suggestions from a conversation turn.

        Used as a fallback when the primary response doesn't include
        structured suggestions. Makes a separate API call focused on
        suggestion extraction.

        Args:
            user_message: The user's message.
            assistant_response: The AI's conversational response.
            profile: User profile dictionary.

        Returns:
            List of suggestion dicts with action, reasoning, and consent_tier.
        """
        consent_tier = profile.get("consent_tier", "Passive")
        profile_context = self._format_profile_context(profile)

        prompt = SUGGESTION_EXTRACTION_PROMPT.format(
            user_message=user_message,
            assistant_response=assistant_response,
            profile_context=profile_context,
            consent_tier=consent_tier,
        )

        logger.info(
            "Extracting suggestions via separate API call",
            extra={"model": self._model},
        )

        completion = await self.client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a suggestion extraction engine. Respond only with valid JSON arrays.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=800,
        )

        raw = completion.choices[0].message.content or "[]"

        # Strip markdown code fences if present
        raw = raw.strip()
        if raw.startswith("```"):
            # Remove opening fence (possibly with language tag)
            first_newline = raw.find("\n")
            if first_newline != -1:
                raw = raw[first_newline + 1:]
            if raw.endswith("```"):
                raw = raw[:-3]
            raw = raw.strip()

        try:
            parsed = json.loads(raw)
            if not isinstance(parsed, list):
                logger.warning("Suggestion extraction returned non-list", extra={"raw": raw[:500]})
                return []

            suggestions = [
                self._validate_suggestion(s)
                for s in parsed
                if self._validate_suggestion(s) is not None
            ]

            logger.info(
                "Suggestions extracted",
                extra={"count": len(suggestions)},
            )
            return suggestions

        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(
                "Failed to parse extracted suggestions",
                extra={"error": str(e), "raw": raw[:500]},
            )
            return []

    async def health_check(self) -> dict[str, Any]:
        """Check connectivity to the OpenAI API.

        Returns:
            Dictionary with status and model information.
        """
        try:
            models = await self.client.models.list()
            available = any(m.id == self._model for m in models.data)
            return {
                "status": "healthy",
                "model": self._model,
                "model_available": available,
            }
        except Exception as e:
            logger.error("OpenAI health check failed", extra={"error": str(e)})
            return {
                "status": "unhealthy",
                "model": self._model,
                "error": str(e),
            }
