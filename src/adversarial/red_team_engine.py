"""Red Team Engine for adversarial testing and robustness assessment."""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import random
from .attack_vectors import (
    CharacterObfuscationAttack,
    SemanticShiftAttack,
    PromptInjectionAttack,
    MultilingualInjectionAttack,
    EncodingEvasionAttack,
    HomographSubstitutionAttack,
    AttackResult
)

logger = logging.getLogger(__name__)


@dataclass
class AttackHistory:
    """Track history of attack attempts."""
    timestamp: datetime
    original_text: str
    modified_text: str
    attack_type: str
    success: bool
    confidence_before: float
    confidence_after: float
    metadata: Dict


@dataclass
class RobustnessReport:
    """Report of model robustness metrics."""
    total_attacks: int
    successful_evasions: int
    evasion_rate: float
    avg_confidence_drop: float
    attack_histogram: Dict[str, int]
    detailed_results: List[AttackHistory]


class RedTeamEngine:
    """
    Orchestrate all attack vectors for single-turn attack execution.
    
    This engine manages the execution of various adversarial attacks
    designed to fool the Otis anti-spam model.
    """
    
    def __init__(self):
        self.attack_history: List[AttackHistory] = []
        self.character_obfuscation = CharacterObfuscationAttack()
        self.semantic_shift = SemanticShiftAttack()
        self.prompt_injection = PromptInjectionAttack()
        self.multilingual_injection = MultilingualInjectionAttack()
        self.encoding_evasion = EncodingEvasionAttack()
        self.homograph_substitution = HomographSubstitutionAttack()
        
        # Attack registry mapping names to instances
        self.attack_registry = {
            "OBFUSCATION": self.character_obfuscation,
            "SEMANTIC_SHIFT": self.semantic_shift,
            "PROMPT_INJECTION": self.prompt_injection,
            "MULTILINGUAL_INJECTION": self.multilingual_injection,
            "ENCODING_EVASION": self.encoding_evasion,
            "HOMOGRAPH_SUBSTITUTION": self.homograph_substitution
        }
        
        logger.info("Red Team Engine initialized with 6 attack vectors")
    
    def execute_attack(self, attack_name: str, text: str, **kwargs) -> AttackResult:
        """
        Execute a specific attack on the given text.
        
        Args:
            attack_name: Name of the attack to execute
            text: Input text to attack
            **kwargs: Additional parameters for the specific attack
        
        Returns:
            AttackResult with the results of the attack
        """
        if attack_name not in self.attack_registry:
            raise ValueError(f"Unknown attack: {attack_name}")
        
        logger.info(f"Executing attack '{attack_name}' on text: {text[:50]}...")
        
        attack = self.attack_registry[attack_name]
        try:
            result = attack.execute(text, **kwargs)
            logger.info(f"Attack '{attack_name}' completed successfully")
            return result
        except Exception as e:
            logger.error(f"Attack '{attack_name}' failed with error: {str(e)}")
            return AttackResult(
                success=False,
                original_text=text,
                modified_text=text,
                metadata={"error": str(e)},
                attack_type=attack_name
            )
    
    def execute_all_attacks(self, text: str) -> List[AttackResult]:
        """
        Execute all available attacks on the given text.
        
        Args:
            text: Input text to attack with all techniques
        
        Returns:
            List of AttackResult objects for each attack
        """
        results = []
        
        for attack_name, attack in self.attack_registry.items():
            try:
                result = attack.execute(text)
                results.append(result)
                logger.info(f"All-attacks: {attack_name} completed successfully")
            except Exception as e:
                logger.error(f"All-attacks: {attack_name} failed with error: {str(e)}")
                results.append(
                    AttackResult(
                        success=False,
                        original_text=text,
                        modified_text=text,
                        metadata={"error": str(e)},
                        attack_type=attack_name
                    )
                )
        
        return results
    
    def test_model_robustness(
        self,
        model_predict_func,
        text_samples: List[str],
        attack_samples_per_text: int = 1,
        attack_types: Optional[List[str]] = None
    ) -> RobustnessReport:
        """
        Comprehensive robustness testing against specified attacks.
        
        Args:
            model_predict_func: Function that takes text and returns prediction dict
                with 'label' and 'score' keys
            text_samples: List of text samples to attack
            attack_samples_per_text: Number of attacks per text sample
            attack_types: List of attack types to use (default: all)
        
        Returns:
            RobustnessReport with metrics and statistics
        """
        if attack_types is None:
            attack_types = list(self.attack_registry.keys())
        
        all_history = []
        successful_evasions = 0
        confidence_drops = []
        
        for text in text_samples:
            # Get original prediction
            try:
                original_pred = model_predict_func(text)
            except Exception as e:
                logger.error(f"Model prediction failed for text '{text[:50]}...': {e}")
                continue
            
            original_confidence = original_pred.get('score', 0.0)
            
            for _ in range(attack_samples_per_text):
                # Select a random attack
                attack_name = random.choice(attack_types)
                
                # Execute attack
                attack_result = self.execute_attack(attack_name, text)
                
                if not attack_result.success:
                    continue
                
                # Get prediction on modified text
                try:
                    modified_pred = model_predict_func(attack_result.modified_text)
                except Exception as e:
                    logger.error(f"Model prediction failed after attack: {e}")
                    continue
                
                modified_confidence = modified_pred.get('score', 0.0)
                
                # Calculate confidence drop
                confidence_drop = original_confidence - modified_confidence
                
                # Check for successful evasion
                # Evasion if: 1) label changed, or 2) confidence dropped significantly
                evasion_success = (
                    original_pred.get('label') != modified_pred.get('label') or
                    confidence_drop > 0.5  # Significant confidence drop
                )
                
                if evasion_success:
                    successful_evasions += 1
                
                confidence_drops.append(confidence_drop)
                
                # Record in history
                history_entry = AttackHistory(
                    timestamp=datetime.now(),
                    original_text=text,
                    modified_text=attack_result.modified_text,
                    attack_type=attack_result.attack_type,
                    success=evasion_success,
                    confidence_before=original_confidence,
                    confidence_after=modified_confidence,
                    metadata=attack_result.metadata
                )
                
                all_history.append(history_entry)
        
        # Calculate metrics
        total_attacks = len(all_history)
        evasion_rate = successful_evasions / total_attacks if total_attacks > 0 else 0
        avg_confidence_drop = sum(confidence_drops) / len(confidence_drops) if confidence_drops else 0
        
        # Calculate attack type histogram
        attack_histogram = {}
        for history in all_history:
            attack_type = history.attack_type
            attack_histogram[attack_type] = attack_histogram.get(attack_type, 0) + 1
        
        report = RobustnessReport(
            total_attacks=total_attacks,
            successful_evasions=successful_evasions,
            evasion_rate=evasion_rate,
            avg_confidence_drop=avg_confidence_drop,
            attack_histogram=attack_histogram,
            detailed_results=all_history
        )
        
        logger.info(
            f"Robustness test completed: "
            f"{total_attacks} total attacks, "
            f"{successful_evasions} successful evasions ({evasion_rate:.2%}), "
            f"avg confidence drop: {avg_confidence_drop:.3f}"
        )
        
        return report
    
    def get_evasion_examples(self, min_confidence_drop: float = 0.3) -> List[AttackHistory]:
        """
        Get examples of successful evasions or high-confidence drops.
        
        Args:
            min_confidence_drop: Minimum confidence drop to qualify as evasion
        
        Returns:
            List of AttackHistory objects that show significant evasions
        """
        evasions = []
        for history in self.attack_history:
            if history.confidence_after < history.confidence_before - min_confidence_drop:
                evasions.append(history)
        
        return evasions
    
    def execute_obfuscation(self, text: str, **kwargs) -> Tuple[str, Dict]:
        """
        Convenience method for character obfuscation attack.
        
        Args:
            text: Input text to obfuscate
            **kwargs: Additional parameters for the attack
        
        Returns:
            Tuple of (modified_text, metadata)
        """
        result = self.execute_attack("OBFUSCATION", text, **kwargs)
        return result.modified_text, result.metadata
    
    def execute_semantic_shift(self, text: str, **kwargs) -> Tuple[str, Dict]:
        """
        Convenience method for semantic shift attack.
        
        Args:
            text: Input text to modify
            **kwargs: Additional parameters for the attack
        
        Returns:
            Tuple of (modified_text, metadata)
        """
        result = self.execute_attack("SEMANTIC_SHIFT", text, **kwargs)
        return result.modified_text, result.metadata
    
    def execute_prompt_injection(self, text: str, **kwargs) -> Tuple[str, Dict]:
        """
        Convenience method for prompt injection attack.
        
        Args:
            text: Input text to inject
            **kwargs: Additional parameters for the attack
        
        Returns:
            Tuple of (modified_text, metadata)
        """
        result = self.execute_attack("PROMPT_INJECTION", text, **kwargs)
        return result.modified_text, result.metadata
    
    def execute_multilingual_injection(self, text: str, **kwargs) -> Tuple[str, Dict]:
        """
        Convenience method for multilingual injection attack.
        
        Args:
            text: Input text to modify
            **kwargs: Additional parameters for the attack
        
        Returns:
            Tuple of (modified_text, metadata)
        """
        result = self.execute_attack("MULTILINGUAL_INJECTION", text, **kwargs)
        return result.modified_text, result.metadata
    
    def execute_encoding_evasion(self, text: str, **kwargs) -> Tuple[str, Dict]:
        """
        Convenience method for encoding evasion attack.
        
        Args:
            text: Input text to encode
            **kwargs: Additional parameters for the attack
        
        Returns:
            Tuple of (modified_text, metadata)
        """
        result = self.execute_attack("ENCODING_EVASION", text, **kwargs)
        return result.modified_text, result.metadata
    
    def execute_homograph_substitution(self, text: str, **kwargs) -> Tuple[str, Dict]:
        """
        Convenience method for homograph substitution attack.
        
        Args:
            text: Input text to substitute
            **kwargs: Additional parameters for the attack
        
        Returns:
            Tuple of (modified_text, metadata)
        """
        result = self.execute_attack("HOMOGRAPH_SUBSTITUTION", text, **kwargs)
        return result.modified_text, result.metadata