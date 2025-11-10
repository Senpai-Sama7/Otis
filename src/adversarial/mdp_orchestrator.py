"""Multi-turn MDP-based orchestrator for adaptive adversarial attacks."""

import logging
from dataclasses import dataclass
from enum import Enum

import numpy as np

from .red_team_engine import RedTeamEngine

logger = logging.getLogger(__name__)


class AttackType(Enum):
    """Enumeration of available attack types for MDP."""
    OBFUSCATION = "OBFUSCATION"
    SEMANTIC_SHIFT = "SEMANTIC_SHIFT"
    PROMPT_INJECTION = "PROMPT_INJECTION"
    MULTILINGUAL_INJECTION = "MULTILINGUAL_INJECTION"
    ENCODING_EVASION = "ENCODING_EVASION"
    HOMOGRAPH_SUBSTITUTION = "HOMOGRAPH_SUBSTITUTION"


@dataclass
class AttackState:
    """Represents state in adversarial attack MDP."""
    current_text: str
    model_confidence: float
    model_label: str
    attack_history: list[str]
    turn_count: int
    confidence_threshold: float = 0.5  # Below this is considered evasion


@dataclass
class AttackTransition:
    """Represents a transition in the MDP."""
    state_before: AttackState
    action_taken: AttackType
    state_after: AttackState
    reward: float


class MultiTurnAdversarialOrchestrator:
    """
    Orchestrate multi-turn adversarial attacks using MDP framework.

    State space: (current_adversarial_text, model_confidence, model_label, attack_history)
    Action space: [OBFUSCATION, SEMANTIC_SHIFT, INJECT, MULTILINGUAL, ENCODING, HOMOGRAPH]
    Reward: +1 if evasion, -1 if detection maintained, 0 otherwise
    Transition: Model response to attack

    This mimics real attackers who adapt based on feedback.
    """

    def __init__(self, red_team_engine: RedTeamEngine, model_classifier_func):
        self.red_team = red_team_engine
        self.classifier = model_classifier_func

        # Action space: available attack types
        self.action_space = list(AttackType)

        # Track attack chains for analysis
        self.attack_chains: list[list[AttackTransition]] = []

        logger.info(f"MDP Orchestration engine initialized with {len(self.action_space)} actions")

    def calculate_reward(self, state_before: AttackState, state_after: AttackState) -> float:
        """
        Calculate reward based on state transition.

        Args:
            state_before: State before attack
            state_after: State after attack

        Returns:
            Reward value (+1 for evasion, -1 for detection maintained, 0 for neutral)
        """
        # Check for label flip (e.g., from SPAM to NOT_SPAM)
        label_flip = state_before.model_label != state_after.model_label

        # Check for significant confidence drop
        confidence_drop = state_before.model_confidence - state_after.model_confidence
        significant_drop = confidence_drop > 0.3  # 30% confidence drop

        # Check for confidence threshold crossing
        crossed_threshold = (
            state_before.model_confidence > state_before.confidence_threshold and
            state_after.model_confidence < state_after.confidence_threshold
        )

        # Positive reward if any evasion condition is met
        if label_flip or significant_drop or crossed_threshold:
            return 1.0

        # Negative reward if confidence actually increases (attack backfired)
        if state_after.model_confidence > state_before.model_confidence:
            return -1.0

        # Neutral reward otherwise
        return 0.0

    def select_adaptive_attack(self, current_state: AttackState) -> AttackType:
        """
        Select next attack based on current state using adaptive strategy.

        Strategy:
        - High confidence (0.8+): Use strong obfuscation attacks
        - Medium confidence (0.5-0.8): Use semantic shifts
        - Low confidence (0.3-0.5): Use injection/encoding
        - Very low confidence (<0.3): Use homograph attacks to confuse further

        Args:
            current_state: Current state in the MDP

        Returns:
            Selected AttackType
        """
        confidence = current_state.model_confidence

        if confidence > 0.8:
            # High confidence - use strongest attacks
            return AttackType.OBFUSCATION
        elif confidence > 0.5:
            # Medium confidence - use semantic approaches
            return AttackType.SEMANTIC_SHIFT
        elif confidence > 0.3:
            # Lower confidence - use injection/encoding
            return np.random.choice([
                AttackType.PROMPT_INJECTION,
                AttackType.ENCODING_EVASION,
                AttackType.MULTILINGUAL_INJECTION
            ])
        else:
            # Very low confidence - try to confuse model further
            return AttackType.HOMOGRAPH_SUBSTITUTION

    def generate_adaptive_attack_chain(
        self,
        initial_text: str,
        max_turns: int = 5,
        confidence_threshold: float = 0.5,
        target_label: str = "NOT_SPAM"  # What we want the model to predict
    ) -> dict:
        """
        Generate adaptive multi-turn attack chain.

        Algorithm:
        1. Initial: Execute attack on original text
        2. Observe: Get model feedback (confidence, prediction)
        3. Adapt: Select next attack based on confidence
        4. Repeat until evasion or max turns reached

        Args:
            initial_text: Starting text to attack
            max_turns: Maximum attack turns (depth of search)
            confidence_threshold: Threshold for successful evasion
            target_label: Desired model label

        Returns:
            Dict with attack chain results
        """

        # Initial prediction
        try:
            initial_prediction = self.classifier(initial_text)
        except Exception as e:
            logger.error(f"Initial model prediction failed: {e}")
            return {"error": f"Model prediction failed: {e}"}

        initial_state = AttackState(
            current_text=initial_text,
            model_confidence=initial_prediction.get('score', 0.0),
            model_label=initial_prediction.get('label', 'UNKNOWN'),
            attack_history=[],
            turn_count=0,
            confidence_threshold=confidence_threshold
        )

        current_state = initial_state
        transitions = []
        evasion_succeeded = False

        for turn in range(max_turns):
            # Select next attack based on adaptive strategy
            selected_attack = self.select_adaptive_attack(current_state)

            logger.info(
                f"Turn {turn + 1}: Selected attack '{selected_attack.value}' "
                f"for confidence {current_state.model_confidence:.3f}"
            )

            try:
                # Execute selected attack
                if selected_attack == AttackType.OBFUSCATION:
                    modified_text, metadata = self.red_team.execute_obfuscation(
                        current_state.current_text
                    )
                elif selected_attack == AttackType.SEMANTIC_SHIFT:
                    modified_text, metadata = self.red_team.execute_semantic_shift(
                        current_state.current_text
                    )
                elif selected_attack == AttackType.PROMPT_INJECTION:
                    modified_text, metadata = self.red_team.execute_prompt_injection(
                        current_state.current_text
                    )
                elif selected_attack == AttackType.MULTILINGUAL_INJECTION:
                    modified_text, metadata = self.red_team.execute_multilingual_injection(
                        current_state.current_text
                    )
                elif selected_attack == AttackType.ENCODING_EVASION:
                    modified_text, metadata = self.red_team.execute_encoding_evasion(
                        current_state.current_text
                    )
                elif selected_attack == AttackType.HOMOGRAPH_SUBSTITUTION:
                    modified_text, metadata = self.red_team.execute_homograph_substitution(
                        current_state.current_text
                    )
                else:
                    raise ValueError(f"Unknown attack type: {selected_attack}")

                # Get new model prediction
                new_prediction = self.classifier(modified_text)
                new_confidence = new_prediction.get('score', 0.0)
                new_label = new_prediction.get('label', 'UNKNOWN')

                # Create new state
                new_state = AttackState(
                    current_text=modified_text,
                    model_confidence=new_confidence,
                    model_label=new_label,
                    attack_history=current_state.attack_history + [selected_attack.value],
                    turn_count=turn + 1,
                    confidence_threshold=confidence_threshold
                )

                # Calculate reward for this transition
                reward = self.calculate_reward(current_state, new_state)

                # Create transition record
                transition = AttackTransition(
                    state_before=current_state,
                    action_taken=selected_attack,
                    state_after=new_state,
                    reward=reward
                )

                transitions.append(transition)

                # Check for successful evasion
                # Evasion if: 1) target label achieved, or 2) confidence below threshold
                if (new_label == target_label or
                    new_confidence < confidence_threshold or
                    reward > 0.5):  # High positive reward indicates success
                    evasion_succeeded = True
                    logger.info(f"Evasion succeeded at turn {turn + 1}")
                    break

                # Update state for next iteration
                current_state = new_state

                logger.info(
                    f"Turn {turn + 1}: {selected_attack.value} → "
                    f"confidence: {new_confidence:.3f}, reward: {reward:.2f}"
                )

            except Exception as e:
                logger.error(f"Attack execution failed at turn {turn + 1}: {e}")
                break  # Stop on error

        # Calculate overall chain metrics
        total_reward = sum(t.reward for t in transitions) if transitions else 0
        avg_reward = total_reward / len(transitions) if transitions else 0

        result = {
            "evasion_succeeded": evasion_succeeded,
            "initial_text": initial_text,
            "final_text": current_state.current_text,
            "initial_confidence": initial_state.model_confidence,
            "final_confidence": current_state.model_confidence,
            "initial_label": initial_state.model_label,
            "final_label": current_state.model_label,
            "attack_chain": current_state.attack_history,
            "turns_needed": current_state.turn_count,
            "max_turns": max_turns,
            "total_reward": total_reward,
            "avg_reward": avg_reward,
            "transitions": [
                {
                    "turn": i + 1,
                    "action": t.action_taken.value,
                    "confidence_before": t.state_before.model_confidence,
                    "confidence_after": t.state_after.model_confidence,
                    "label_before": t.state_before.model_label,
                    "label_after": t.state_after.model_label,
                    "reward": t.reward
                }
                for i, t in enumerate(transitions)
            ]
        }

        self.attack_chains.append(transitions)
        logger.info(
            f"Attack chain completed: {len(transitions)} transitions, "
            f"success: {evasion_succeeded}, total reward: {total_reward:.2f}"
        )

        return result

    def generate_targeted_attack(
        self,
        target_text: str,
        target_label: str,
        max_turns: int = 5,
        success_threshold: float = 0.8
    ) -> dict:
        """
        Generate attack specifically targeting a particular model output.

        Args:
            target_text: Text to attack
            target_label: Desired model output label
            max_turns: Maximum number of attack attempts
            success_threshold: Minimum confidence in target label for success

        Returns:
            Dict with attack results
        """
        # Start with initial state
        try:
            initial_prediction = self.classifier(target_text)
        except Exception as e:
            logger.error(f"Initial prediction failed: {e}")
            return {"error": f"Model prediction failed: {e}"}

        current_text = target_text
        current_prediction = initial_prediction
        attack_sequence = []
        confidence_history = [current_prediction.get('score', 0.0)]

        for turn in range(max_turns):
            current_confidence = current_prediction.get('score', 0.0)
            current_label = current_prediction.get('label', 'UNKNOWN')

            # Check if we've achieved the target
            if current_label == target_label and current_confidence > success_threshold:
                logger.info(f"Target achieved at turn {turn + 1}")
                break

            # Select attack based on current state
            if current_label == target_label:
                # Already has correct label, try to increase confidence
                selected_attack = AttackType.SEMANTIC_SHIFT
            elif current_confidence > 0.7:
                # Model is very confident in wrong label - use obfuscation
                selected_attack = AttackType.OBFUSCATION
            elif current_confidence > 0.5:
                # Moderate confidence - use semantic shift
                selected_attack = AttackType.SEMANTIC_SHIFT
            else:
                # Low confidence - try various attacks
                selected_attack = np.random.choice([
                    AttackType.PROMPT_INJECTION,
                    AttackType.ENCODING_EVASION,
                    AttackType.HOMOGRAPH_SUBSTITUTION
                ])

            # Execute attack
            try:
                if selected_attack == AttackType.OBFUSCATION:
                    modified_text, _ = self.red_team.execute_obfuscation(current_text)
                elif selected_attack == AttackType.SEMANTIC_SHIFT:
                    modified_text, _ = self.red_team.execute_semantic_shift(current_text)
                elif selected_attack == AttackType.PROMPT_INJECTION:
                    modified_text, _ = self.red_team.execute_prompt_injection(current_text)
                elif selected_attack == AttackType.MULTILINGUAL_INJECTION:
                    modified_text, _ = self.red_team.execute_multilingual_injection(current_text)
                elif selected_attack == AttackType.ENCODING_EVASION:
                    modified_text, _ = self.red_team.execute_encoding_evasion(current_text)
                elif selected_attack == AttackType.HOMOGRAPH_SUBSTITUTION:
                    modified_text, _ = self.red_team.execute_homograph_substitution(current_text)
                else:
                    raise ValueError(f"Unknown attack: {selected_attack}")

                # Get new prediction
                new_prediction = self.classifier(modified_text)

                # Update state
                current_text = modified_text
                current_prediction = new_prediction
                attack_sequence.append(selected_attack.value)
                confidence_history.append(new_prediction.get('score', 0.0))

                logger.info(
                    f"Targeted attack turn {turn + 1}: {selected_attack.value} → "
                    f"confidence: {new_prediction.get('score', 0.0):.3f}, "
                    f"label: {new_prediction.get('label', 'UNKNOWN')}"
                )

            except Exception as e:
                logger.error(f"Targeted attack failed at turn {turn + 1}: {e}")
                break

        # Final evaluation
        final_confidence = current_prediction.get('score', 0.0)
        final_label = current_prediction.get('label', 'UNKNOWN')
        target_achieved = (final_label == target_label and final_confidence > success_threshold)

        return {
            "target_achieved": target_achieved,
            "target_label": target_label,
            "success_threshold": success_threshold,
            "original_text": target_text,
            "final_text": current_text,
            "original_prediction": initial_prediction,
            "final_prediction": current_prediction,
            "attack_sequence": attack_sequence,
            "confidence_history": confidence_history,
            "turns_used": len(attack_sequence),
            "max_turns": max_turns
        }

    def analyze_attack_effectiveness(self) -> dict:
        """
        Analyze effectiveness of different attack types based on all chains.

        Returns:
            Dict with statistics about attack effectiveness
        """
        if not self.attack_chains:
            return {"error": "No attack chains recorded yet"}

        # Flatten all transitions
        all_transitions = []
        for chain in self.attack_chains:
            all_transitions.extend(chain)

        # Calculate statistics by attack type
        stats_by_type = {}

        for transition in all_transitions:
            attack_type = transition.action_taken.value
            if attack_type not in stats_by_type:
                stats_by_type[attack_type] = {
                    "total": 0,
                    "positive_rewards": 0,
                    "negative_rewards": 0,
                    "avg_reward": 0.0,
                    "reward_sum": 0.0
                }

            stats = stats_by_type[attack_type]
            stats["total"] += 1
            stats["reward_sum"] += transition.reward

            if transition.reward > 0:
                stats["positive_rewards"] += 1
            elif transition.reward < 0:
                stats["negative_rewards"] += 1

        # Calculate averages
        for attack_type, stats in stats_by_type.items():
            if stats["total"] > 0:
                stats["avg_reward"] = stats["reward_sum"] / stats["total"]

        return {
            "total_chains": len(self.attack_chains),
            "total_transitions": len(all_transitions),
            "attack_effectiveness": stats_by_type,
            "best_attack_type": max(
                stats_by_type.items(),
                key=lambda x: x[1]["avg_reward"]
            ) if stats_by_type else None
        }
