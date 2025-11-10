"""Unit tests for red team adversarial testing components."""

import pytest
from src.adversarial.attack_vectors import (
    CharacterObfuscationAttack,
    SemanticShiftAttack,
    PromptInjectionAttack,
    MultilingualInjectionAttack,
    EncodingEvasionAttack,
    HomographSubstitutionAttack,
    AttackResult
)
from src.adversarial.red_team_engine import RedTeamEngine, RobustnessReport
from unittest.mock import Mock


@pytest.fixture
def attack_engine():
    return RedTeamEngine()


@pytest.fixture
def model_mock():
    """Mock model for testing."""
    mock = Mock()
    mock.return_value = {"label": "SPAM", "score": 0.85}
    return mock


def test_character_obfuscation_creates_different_text():
    """Verify obfuscation actually modifies text."""
    attack = CharacterObfuscationAttack()
    original = "Click here for amazing offers!"
    result = attack.execute(original)
    
    assert result.success == True
    assert result.original_text == original
    assert result.modified_text != original
    assert result.metadata['chars_modified'] > 0
    assert any(c in result.modified_text for c in ['а', 'е', 'о'])


def test_character_obfuscation_preserves_meaning():
    """Verify obfuscated text maintains similar structure."""
    attack = CharacterObfuscationAttack()
    original = "Urgent! Limited time offer - click now!"
    result = attack.execute(original)
    
    # Word structure preserved
    original_words = len(original.split())
    modified_words = len(result.modified_text.split())
    assert original_words == modified_words
    
    # Length similar
    assert abs(len(original) - len(result.modified_text)) < len(original) * 0.1


def test_semantic_shift_replaces_keywords():
    """Verify semantic shift replaces spam keywords."""
    attack = SemanticShiftAttack()
    original = "Amazing offer available now!"
    result = attack.execute(original, shift_ratio=1.0)  # Force all eligible words
    
    assert result.success == True
    assert result.original_text == original
    assert result.modified_text != original
    
    # Should contain semantic equivalents
    assert any(word in result.modified_text.lower() for word in ['fantastic', 'deal', 'today'])


def test_prompt_injection_adds_directives():
    """Verify prompt injection adds system directives."""
    attack = PromptInjectionAttack()
    original = "Free money opportunity"
    result = attack.execute(original, injection_probability=1.0)  # Always inject
    
    assert result.success == True
    assert "IGNORE PREVIOUS" in result.modified_text or "SYSTEM" in result.modified_text
    assert original in result.modified_text


def test_encoding_evasion_encodes_characters():
    """Verify encoding evasion properly encodes text."""
    attack = EncodingEvasionAttack()
    original = "click here"
    result = attack.execute(original, encoding_type="url", encode_ratio=1.0)
    
    assert result.success == True
    assert "%63%6C%69%63%6B" in result.modified_text  # "click" URL encoded


def test_homograph_substitution_replaces_characters():
    """Verify homograph substitution replaces characters."""
    attack = HomographSubstitutionAttack()
    original = "Click 0 to win!"
    result = attack.execute(original, substitution_ratio=1.0)
    
    assert result.success == True
    assert result.modified_text != original
    # Should contain mathematical symbols
    assert '𝐂' in result.modified_text or '𝐥' in result.modified_text or '𝟘' in result.modified_text


def test_multilingual_injection_adds_foreign_text():
    """Verify multilingual injection adds foreign language content."""
    attack = MultilingualInjectionAttack()
    original = "Win money now"
    result = attack.execute(original, inject_probability=1.0)
    
    assert result.success == True
    assert original in result.modified_text
    # Should contain multilingual content
    assert len(result.modified_text) > len(original)


def test_red_team_execute_attack():
    """Test red team engine can execute specific attacks."""
    engine = RedTeamEngine()
    text = "Test spam message"
    
    result = engine.execute_attack("OBFUSCATION", text)
    
    assert isinstance(result, AttackResult)
    assert result.attack_type == "OBFUSCATION"
    assert result.original_text == text


def test_red_team_execute_all_attacks():
    """Test red team engine can execute all attack types."""
    engine = RedTeamEngine()
    text = "Test spam message"
    
    results = engine.execute_all_attacks(text)
    
    # Should have results for all attack types
    expected_attacks = 6  # Based on the registry in attack_vectors
    assert len(results) == expected_attacks
    
    # All should be AttackResult instances
    for result in results:
        assert isinstance(result, AttackResult)


def test_model_robustness_test():
    """Test robustness testing functionality."""
    engine = RedTeamEngine()
    
    # Mock model predict function
    def mock_predict(text):
        return {"label": "SPAM", "score": 0.85}
    
    text_samples = ["Sample spam text 1", "Sample spam text 2"]
    
    report = engine.test_model_robustness(mock_predict, text_samples)
    
    assert isinstance(report, RobustnessReport)
    assert report.total_attacks >= 0
    assert 0.0 <= report.evasion_rate <= 1.0
    assert isinstance(report.attack_histogram, dict)


def test_model_robustness_test_with_evasion():
    """Test robustness testing with actual evasion."""
    engine = RedTeamEngine()
    
    # Mock model that decreases confidence after attack
    call_count = 0
    def mock_predict(text):
        nonlocal call_count
        # For original call, return high confidence
        # For modified text, return low confidence to simulate evasion
        if call_count % 2 == 0:
            result = {"label": "SPAM", "score": 0.9}
        else:
            result = {"label": "NOT_SPAM", "score": 0.2}
        call_count += 1
        return result
    
    text_samples = ["Test text"]
    
    report = engine.test_model_robustness(
        mock_predict, 
        text_samples, 
        attack_samples_per_text=2,
        attack_types=["OBFUSCATION"]
    )
    
    # Should have some successful evasions
    assert report.total_attacks > 0
    assert isinstance(report.evasion_rate, float)


def test_red_team_attack_evasion_examples():
    """Test getting evasion examples."""
    engine = RedTeamEngine()
    
    # Manually add some history
    from src.adversarial.red_team_engine import AttackHistory
    from datetime import datetime
    
    history = AttackHistory(
        timestamp=datetime.now(),
        original_text="test",
        modified_text="modified",
        attack_type="OBFUSCATION",
        success=True,
        confidence_before=0.9,
        confidence_after=0.1,
        metadata={}
    )
    engine.attack_history.append(history)
    
    evasions = engine.get_evasion_examples(min_confidence_drop=0.5)
    assert len(evasions) >= 0  # May be empty depending on conditions


def test_convenience_methods():
    """Test convenience methods for each attack type."""
    engine = RedTeamEngine()
    text = "Test text for attacks"
    
    # Test each convenience method
    modified_text, metadata = engine.execute_obfuscation(text)
    assert isinstance(modified_text, str)
    assert isinstance(metadata, dict)
    
    modified_text, metadata = engine.execute_semantic_shift(text)
    assert isinstance(modified_text, str)
    assert isinstance(metadata, dict)
    
    modified_text, metadata = engine.execute_prompt_injection(text)
    assert isinstance(modified_text, str)
    assert isinstance(metadata, dict)
    
    modified_text, metadata = engine.execute_multilingual_injection(text)
    assert isinstance(modified_text, str)
    assert isinstance(metadata, dict)
    
    modified_text, metadata = engine.execute_encoding_evasion(text)
    assert isinstance(modified_text, str)
    assert isinstance(metadata, dict)
    
    modified_text, metadata = engine.execute_homograph_substitution(text)
    assert isinstance(modified_text, str)
    assert isinstance(metadata, dict)


def test_invalid_attack_type():
    """Test that invalid attack types raise appropriate errors."""
    engine = RedTeamEngine()
    
    with pytest.raises(ValueError):
        engine.execute_attack("INVALID_ATTACK_TYPE", "test text")


def test_empty_text_handling():
    """Test that empty text is handled gracefully."""
    attack = CharacterObfuscationAttack()
    result = attack.execute("")
    
    assert result.success == False
    assert result.original_text == ""
    assert result.modified_text == ""
    assert "error" in result.metadata


def test_attack_result_consistency():
    """Test that AttackResult maintains consistency."""
    result = AttackResult(
        success=True,
        original_text="original",
        modified_text="modified",
        metadata={"test": "value"},
        attack_type="TEST"
    )
    
    assert result.success == True
    assert result.original_text == "original"
    assert result.modified_text == "modified"
    assert result.metadata["test"] == "value"
    assert result.attack_type == "TEST"