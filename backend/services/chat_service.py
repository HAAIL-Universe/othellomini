"""
ChatService orchestrating the complete chat interaction flow.

This service is the primary orchestrator for user chat interactions. It coordinates:
1. User profile retrieval and context building
2. Conversation history retrieval for AI context
3. AI response generation via AIService
4. Suggestion extraction and ethical gating via OthelloService
5. Persistence of conversation messages and gated suggestions
6. Profile update tracking

The ChatService enforces the core invariant that every AI-generated suggestion
MUST pass through the OthelloService ethical gatekeeper before reaching the user.
No bypass paths exist — suggestions are filtered, tagged, and reasoned about
before inclusion in the response.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backend.repositories.conversation_repository import ConversationRepository
from backend.repositories.profile_repository import ProfileRepository
from backend.repositories.suggestion_repository import SuggestionRepository
from backend.services.ai_service import AIService
from backend.services.othello_service import OthelloService

logger = logging.getLogger(__name__)

# Default user ID for single-user MVP scope
DEFAULT_USER_ID = "default_user"


class ChatService:
    """
    Orchestrator service for the chat interaction flow.

    Coordinates AI response generation, ethical gating of suggestions,
    conversation persistence, and profile updates. This service is the
    central hub that enforces consent-first architecture by ensuring
    all suggestions pass through OthelloService before presentation.

    Attributes:
        ai_service: Service for generating AI responses via OpenAI.
        othello_service: Ethical gatekeeper for consent-tier filtering.
        profile_repo: Repository for user profile data access.
        conversation_repo: Repository for conversation message persistence.
        suggestion_repo: Repository for suggestion persistence and status tracking.
    """

    def __init__(
        self,
        ai_service: AIService,
        othello_service: OthelloService,
        profile_repo: ProfileRepository,
        conversation_repo: ConversationRepository,
        suggestion_repo: SuggestionRepository,
    ) -> None:
        """
        Initialize ChatService with all required dependencies.

        Args:
            ai_service: AIService instance for OpenAI GPT-4 integration.
            othello_service: OthelloService instance for ethical gating.
            profile_repo: ProfileRepository for user profile operations.
            conversation_repo: ConversationRepository for message persistence.
            suggestion_repo: SuggestionRepository for suggestion persistence.
        """
        self.ai_service = ai_service
        self.othello_service = othello_service
        self.profile_repo = profile_repo
        self.conversation_repo = conversation_repo
        self.suggestion_repo = suggestion_repo

    async def process_message(
        self,
        message: str,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process a user chat message through the complete interaction flow.

        This is the primary entry point for chat interactions. The flow:
        1. Retrieve or create user profile
        2. Fetch recent conversation history for AI context
        3. Generate AI response with suggestions via AIService
        4. Gate all suggestions through OthelloService ethical filter
        5. Persist user message, assistant response, and gated suggestions
        6. Update user profile with interaction metadata
        7. Return structured response with conversation ID, AI response,
           and consent-gated suggestions

        Args:
            message: The user's chat message text.
            user_id: Optional user identifier. Defaults to DEFAULT_USER_ID
                     for single-user MVP scope.
            context: Optional additional context dict (mood, timestamp, etc.).

        Returns:
            Dictionary containing:
                - conversation_id: UUID string identifying this conversation turn
                - message: Echo of the user's original message
                - response: AI-generated conversational response text
                - suggestions: List of consent-gated suggestion dicts with
                  ethical reasoning and tier badges
                - profile_updated: Boolean indicating if profile was updated

        Raises:
            Exception: Propagates exceptions from AI service or database
                       operations after logging.
        """
        effective_user_id = user_id or DEFAULT_USER_ID
        conversation_id = str(uuid.uuid4())

        logger.info(
            "Processing chat message",
            extra={
                "conversation_id": conversation_id,
                "user_id": effective_user_id,
                "message_length": len(message),
            },
        )

        try:
            # Step 1: Retrieve or create user profile
            profile = await self.profile_repo.get_or_create_default(effective_user_id)
            profile_dict = self._profile_to_dict(profile)
            consent_tier = profile_dict.get("consent_tier", "Passive")

            logger.info(
                "User profile loaded",
                extra={
                    "user_id": effective_user_id,
                    "consent_tier": consent_tier,
                    "profile_version": profile_dict.get("profile_version"),
                },
            )

            # Step 2: Fetch recent conversation history for AI context
            conversation_history = await self._get_conversation_history(profile.id)

            # Step 3: Generate AI response with suggestions
            ai_result = await self.ai_service.generate_response(
                user_message=message,
                profile=profile_dict,
                conversation_history=conversation_history,
                context=context,
            )

            ai_response_text = ai_result.get("response", "")
            raw_suggestions = ai_result.get("suggestions", [])

            logger.info(
                "AI response generated",
                extra={
                    "conversation_id": conversation_id,
                    "response_length": len(ai_response_text),
                    "raw_suggestion_count": len(raw_suggestions),
                },
            )

            # Step 3b: If no suggestions from primary response, attempt extraction
            if not raw_suggestions and consent_tier != "Passive":
                try:
                    raw_suggestions = await self.ai_service.extract_suggestions(
                        user_message=message,
                        assistant_response=ai_response_text,
                        profile=profile_dict,
                    )
                    logger.info(
                        "Suggestions extracted via fallback",
                        extra={
                            "conversation_id": conversation_id,
                            "extracted_count": len(raw_suggestions),
                        },
                    )
                except Exception as extraction_error:
                    logger.warning(
                        "Suggestion extraction fallback failed",
                        extra={
                            "conversation_id": conversation_id,
                            "error": str(extraction_error),
                        },
                    )
                    raw_suggestions = []

            # Step 4: Gate ALL suggestions through OthelloService ethical filter
            # This is the core invariant — no suggestion reaches the user without gating
            gated_suggestions = self._gate_suggestions(
                raw_suggestions=raw_suggestions,
                consent_tier=consent_tier,
            )

            # Filter to only permitted suggestions for the response
            permitted_suggestions = [
                s for s in gated_suggestions if s.get("is_permitted", False)
            ]

            logger.info(
                "Suggestions gated through Othello",
                extra={
                    "conversation_id": conversation_id,
                    "total_gated": len(gated_suggestions),
                    "permitted_count": len(permitted_suggestions),
                    "blocked_count": len(gated_suggestions) - len(permitted_suggestions),
                },
            )

            # Step 5: Persist conversation messages
            # Save user message
            message_metadata = {}
            if context:
                message_metadata["context"] = context
            message_metadata["conversation_id"] = conversation_id

            user_msg = await self.conversation_repo.create_message(
                user_profile_id=profile.id,
                role="user",
                content=message,
                metadata=message_metadata,
            )

            # Save assistant response
            assistant_metadata: Dict[str, Any] = {
                "conversation_id": conversation_id,
                "suggestion_count": len(permitted_suggestions),
                "total_suggestions_generated": len(raw_suggestions),
                "suggestions_blocked": len(gated_suggestions) - len(permitted_suggestions),
            }

            assistant_msg = await self.conversation_repo.create_message(
                user_profile_id=profile.id,
                role="assistant",
                content=ai_response_text,
                metadata=assistant_metadata,
            )

            # Step 5b: Persist permitted suggestions to database
            persisted_suggestions = await self._persist_suggestions(
                permitted_suggestions=permitted_suggestions,
                user_profile_id=profile.id,
                conversation_id=assistant_msg.id,
            )

            # Step 6: Update user profile with interaction metadata
            profile_updated = await self._update_profile_from_interaction(
                user_id=effective_user_id,
                message=message,
                context=context,
            )

            # Step 7: Build and return response
            response_suggestions = self._format_suggestions_for_response(
                persisted_suggestions
            )

            result: Dict[str, Any] = {
                "conversation_id": conversation_id,
                "message": message,
                "response": ai_response_text,
                "suggestions": response_suggestions,
                "profile_updated": profile_updated,
            }

            logger.info(
                "Chat message processed successfully",
                extra={
                    "conversation_id": conversation_id,
                    "user_id": effective_user_id,
                    "suggestion_count": len(response_suggestions),
                },
            )

            return result

        except Exception as e:
            logger.error(
                "Error processing chat message",
                extra={
                    "conversation_id": conversation_id,
                    "user_id": effective_user_id,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )
            raise

    async def _get_conversation_history(
        self,
        user_profile_id: int,
        limit: int = 20,
    ) -> List[Dict[str, str]]:
        """
        Retrieve recent conversation history formatted for AI context.

        Fetches the most recent messages for the user profile and formats
        them as a list of role/content dicts suitable for the OpenAI API.

        Args:
            user_profile_id: The database ID of the user profile.
            limit: Maximum number of recent messages to retrieve.

        Returns:
            List of message dicts with 'role' and 'content' keys,
            ordered chronologically (oldest first).
        """
        try:
            recent_messages = await self.conversation_repo.get_recent_by_user_profile_id(
                user_profile_id=user_profile_id,
                limit=limit,
            )

            history: List[Dict[str, str]] = []
            for msg in recent_messages:
                if msg.role in ("user", "assistant"):
                    history.append({
                        "role": msg.role,
                        "content": msg.content,
                    })

            return history

        except Exception as e:
            logger.warning(
                "Failed to retrieve conversation history, proceeding without context",
                extra={
                    "user_profile_id": user_profile_id,
                    "error": str(e),
                },
            )
            return []

    def _gate_suggestions(
        self,
        raw_suggestions: List[Dict[str, Any]],
        consent_tier: str,
    ) -> List[Dict[str, Any]]:
        """
        Gate raw AI suggestions through the OthelloService ethical filter.

        Transforms raw suggestion dicts from the AI service into the format
        expected by OthelloService and runs them through the consent gate.

        Args:
            raw_suggestions: List of suggestion dicts from AIService with
                             'action', 'reasoning', and 'consent_tier' keys.
            consent_tier: The user's current consent tier setting.

        Returns:
            List of gated suggestion dicts with ethical metadata.
        """
        if not raw_suggestions:
            return []

        # Transform AI service suggestion format to OthelloService format
        othello_input: List[Dict[str, Any]] = []
        for suggestion in raw_suggestions:
            othello_input.append({
                "suggestion_text": suggestion.get("action", ""),
                "consent_tier": suggestion.get("consent_tier"),
                "ai_reasoning": suggestion.get("reasoning", ""),
            })

        # Gate through OthelloService — the core ethical invariant
        gated = self.othello_service.gate_suggestions(
            suggestions=othello_input,
            user_consent_tier=consent_tier,
        )

        # Preserve original AI reasoning alongside Othello's ethical reasoning
        for i, gated_item in enumerate(gated):
            if i < len(raw_suggestions):
                ai_reasoning = raw_suggestions[i].get("reasoning", "")
                if ai_reasoning:
                    gated_item["ai_reasoning"] = ai_reasoning

        return gated

    async def _persist_suggestions(
        self,
        permitted_suggestions: List[Dict[str, Any]],
        user_profile_id: int,
        conversation_id: int,
    ) -> List[Dict[str, Any]]:
        """
        Persist permitted suggestions to the database.

        Creates suggestion records for each permitted (gated and approved)
        suggestion, linking them to the user profile and conversation.

        Args:
            permitted_suggestions: List of suggestion dicts that passed the
                                   OthelloService ethical gate.
            user_profile_id: The database ID of the user profile.
            conversation_id: The database ID of the assistant conversation message.

        Returns:
            List of persisted suggestion dicts with database IDs.
        """
        persisted: List[Dict[str, Any]] = []

        for suggestion in permitted_suggestions:
            suggestion_text = suggestion.get("suggestion_text", "")
            if not suggestion_text:
                continue

            assigned_tier = suggestion.get("assigned_tier", "Suggestive")
            ethical_reasoning = suggestion.get("ethical_reasoning", "")
            ai_reasoning = suggestion.get("ai_reasoning", "")

            # Combine ethical reasoning with AI reasoning for transparency
            combined_reasoning = ethical_reasoning
            if ai_reasoning:
                combined_reasoning = (
                    f"AI Reasoning: {ai_reasoning}\n\n"
                    f"Ethical Assessment: {ethical_reasoning}"
                )

            try:
                db_suggestion = await self.suggestion_repo.create_suggestion({
                    "user_profile_id": user_profile_id,
                    "conversation_id": conversation_id,
                    "suggestion_text": suggestion_text,
                    "consent_tier": assigned_tier,
                    "ethical_reasoning": combined_reasoning,
                    "status": "pending",
                    "metadata": {
                        "filter_reasoning": suggestion.get("filter_reasoning", ""),
                        "user_consent_tier": suggestion.get("user_consent_tier", ""),
                    },
                })

                persisted.append({
                    "id": db_suggestion.id,
                    "suggestion_text": suggestion_text,
                    "consent_tier": assigned_tier,
                    "ethical_reasoning": combined_reasoning,
                    "status": "pending",
                    "created_at": db_suggestion.created_at.isoformat()
                    if db_suggestion.created_at
                    else datetime.now(timezone.utc).isoformat(),
                })

            except Exception as e:
                logger.error(
                    "Failed to persist suggestion",
                    extra={
                        "suggestion_text": suggestion_text[:100],
                        "error": str(e),
                    },
                )
                continue

        return persisted

    async def _update_profile_from_interaction(
        self,
        user_id: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Update user profile with metadata from the current interaction.

        Performs lightweight profile updates based on the interaction context.
        For the MVP, this updates behavioral patterns with interaction timestamps
        and mood data when available. Full psychological trait extraction is
        deferred to the full build.

        Args:
            user_id: The user's unique identifier.
            message: The user's chat message.
            context: Optional context dict with mood, timestamp, etc.

        Returns:
            Boolean indicating whether the profile was successfully updated.
        """
        try:
            profile = await self.profile_repo.get_or_create_default(user_id)
            
            # Build update metadata
            update_data: Dict[str, Any] = {}
            
            # Update behavioral patterns with interaction timestamp
            behavioral_patterns = profile.behavioral_patterns or {}
            interactions = behavioral_patterns.get("interactions", [])
            interactions.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message_length": len(message),
                "context": context,
            })
            
            # Keep only recent interactions (last 100)
            behavioral_patterns["interactions"] = interactions[-100:]
            update_data["behavioral_patterns"] = behavioral_patterns
            
            # Update profile
            await self.profile_repo.update(profile.id, update_data)
            
            return True
            
        except Exception as e:
            logger.warning(
                "Failed to update profile from interaction",
                extra={
                    "user_id": user_id,
                    "error": str(e),
                },
            )
            return False

    def _profile_to_dict(self, profile: Any) -> Dict[str, Any]:
        """
        Convert a profile ORM object to a dictionary.

        Args:
            profile: The profile ORM object.

        Returns:
            Dictionary representation of the profile.
        """
        return {
            "id": profile.id,
            "user_id": profile.user_id,
            "consent_tier": profile.consent_tier,
            "profile_version": profile.profile_version,
            "preferences": profile.preferences,
            "behavioral_patterns": profile.behavioral_patterns,
            "psychological_traits": profile.psychological_traits,
        }

    def _format_suggestions_for_response(
        self,
        suggestions: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Format persisted suggestions for the API response.

        Args:
            suggestions: List of persisted suggestion dicts.

        Returns:
            List of formatted suggestion dicts for the response.
        """
        formatted = []
        for suggestion in suggestions:
            formatted.append({
                "id": suggestion.get("id"),
                "text": suggestion.get("suggestion_text"),
                "consent_tier": suggestion.get("consent_tier"),
                "reasoning": suggestion.get("ethical_reasoning"),
                "status": suggestion.get("status"),
                "created_at": suggestion.get("created_at"),
            })
        return formatted
