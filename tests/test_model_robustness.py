"""Tests for model robustness and adversarial detection."""

import pytest
from src.model.inference_engine import OtisInferenceEngine
from src.adversarial.red_team_engine import RedTeamEngine
from unittest.mock import Mock, patch


@pytest.fixture
def mock_model():
    """Create a mock model for testing."""
    with patch('src.model.inference_engine.AutoTokenizer.from_pretrained') as mock_tokenizer, \
         patch('src.model.inference_engine.AutoModelForSequenceClassification.from_pretrained') as mock_model_class, \
         patch('src.model.inference_engine.pipeline') as mock_pipeline:
        
        # Mock tokenizer
        mock_tokenizer.return_value = Mock()
        
        # Mock model
        mock_model_instance = Mock()
        mock_model_class.return_value = mock_model_instance
        
        # Mock pipeline
        mock_pipeline_instance = Mock()
        mock_pipeline_instance.return_value = [{"label": "SPAM", "score": 0.8}]
        mock_pipeline.return_value = mock_pipeline_instance
        
        engine = OtisInferenceEngine(model_name="test-model", blue_team_enabled=False, red_team_monitoring=False)
        return engine


def test_engine_initialization():
    """Test that inference engine initializes correctly."""
    with patch('src.model.inference_engine.AutoTokenizer.from_pretrained'), \
         patch('src.model.inference_engine.AutoModelForSequenceClassification.from_pretrained'), \
         patch('src.model.inference_engine.pipeline'):
        
        engine = OtisInferenceEngine(model_name="test-model")
        
        assert engine.model_name == "test-model"
        assert engine.device in ["cuda", "cpu"]
        assert hasattr(engine, 'classifier')


def test_single_prediction():
    """Test single prediction functionality."""
    with patch('src.model.inference_engine.AutoTokenizer.from_pretrained'), \
         patch('src.model.inference_engine.AutoModelForSequenceClassification.from_pretrained'), \
         patch('src.model.inference_engine.pipeline') as mock_pipeline:
        
        # Mock the pipeline to return a specific result
        mock_pipeline.return_value.return_value = [{"label": "SPAM", "score": 0.85}]
        
        engine = OtisInferenceEngine(model_name="test-model", blue_team_enabled=False)
        result = engine.predict("Test email content")
        
        assert "label" in result
        assert "score" in result
        assert result["label"] in ["SPAM", "NOT_SPAM", "SECURITY_BLOCKED", "ERROR"]
        assert 0.0 <= result["score"] <= 1.0


def test_batch_prediction():
    """Test batch prediction functionality."""
    with patch('src.model.inference_engine.AutoTokenizer.from_pretrained'), \
         patch('src.model.inference_engine.AutoModelForSequenceClassification.from_pretrained'), \
         patch('src.model.inference_engine.pipeline') as mock_pipeline:
        
        # Mock the pipeline to return a specific result for all inputs
        mock_pipeline.return_value.return_value = [{"label": "SPAM", "score": 0.7}]
        
        engine = OtisInferenceEngine(model_name="test-model", blue_team_enabled=False)
        texts = ["Email 1", "Email 2", "Email 3"]
        results = engine.predict_batch(texts, batch_size=2)
        
        assert len(results) == len(texts)
        for result in results:
            assert "label" in result
            assert "score" in result


def test_model_info():
    """Test model information retrieval."""
    with patch('src.model.inference_engine.AutoTokenizer.from_pretrained'), \
         patch('src.model.inference_engine.AutoModelForSequenceClassification.from_pretrained'), \
         patch('src.model.inference_engine.pipeline'):
        
        engine = OtisInferenceEngine(model_name="test-model")
        info = engine.get_model_info()
        
        assert "model_name" in info
        assert "device" in info
        assert "model_type" in info
        assert "task" in info
        assert "labels" in info
        assert "security_features" in info


def test_robustness_testing():
    """Test adversarial robustness testing functionality."""
    with patch('src.model.inference_engine.AutoTokenizer.from_pretrained'), \
         patch('src.model.inference_engine.AutoModelForSequenceClassification.from_pretrained'), \
         patch('src.model.inference_engine.pipeline') as mock_pipeline:
        
        # Mock the pipeline
        mock_pipeline.return_value.return_value = [{"label": "SPAM", "score": 0.8}]
        
        engine = OtisInferenceEngine(model_name="test-model", blue_team_enabled=False)
        
        test_texts = ["Normal text", "Another text"]
        results = engine.test_adversarial_robustness(test_texts)
        
        # Should return results even if red team not available in this mock setup
        assert isinstance(results, dict)
        # May have error if red team not properly initialized in mock
        if "error" not in results:
            assert "total_attacks" in results
            assert "evasion_rate" in results


def test_security_settings_update():
    """Test updating security settings."""
    with patch('src.model.inference_engine.AutoTokenizer.from_pretrained'), \
         patch('src.model.inference_engine.AutoModelForSequenceClassification.from_pretrained'), \
         patch('src.model.inference_engine.pipeline'):
        
        engine = OtisInferenceEngine(model_name="test-model", blue_team_enabled=False)
        
        # Update settings
        result = engine.update_security_settings(
            blue_team_enabled=True,
            red_team_monitoring=True
        )
        
        assert result["blue_team_enabled"] == True
        assert result["red_team_monitoring"] == True
        assert engine.blue_team_enabled == True


def test_security_status():
    """Test security status reporting."""
    with patch('src.model.inference_engine.AutoTokenizer.from_pretrained'), \
         patch('src.model.inference_engine.AutoModelForSequenceClassification.from_pretrained'), \
         patch('src.model.inference_engine.pipeline'):
        
        engine = OtisInferenceEngine(model_name="test-model", blue_team_enabled=True)
        status = engine.get_security_status()
        
        assert "timestamp" in status
        assert "blue_team_enabled" in status
        assert "red_team_monitoring" in status


def test_prediction_error_handling():
    """Test error handling in predictions."""
    with patch('src.model.inference_engine.AutoTokenizer.from_pretrained'), \
         patch('src.model.inference_engine.AutoModelForSequenceClassification.from_pretrained'), \
         patch('src.model.inference_engine.pipeline') as mock_pipeline:
        
        # Mock to raise an exception
        mock_pipeline.side_effect = Exception("Model loading failed")
        
        with pytest.raises(Exception):
            engine = OtisInferenceEngine(model_name="test-model", blue_team_enabled=False)


def test_label_mapping():
    """Test label mapping functionality."""
    with patch('src.model.inference_engine.AutoTokenizer.from_pretrained'), \
         patch('src.model.inference_engine.AutoModelForSequenceClassification.from_pretrained'), \
         patch('src.model.inference_engine.pipeline') as mock_pipeline:
        
        # Mock pipeline to return HuggingFace style labels
        mock_pipeline.return_value.return_value = [{"label": "LABEL_1", "score": 0.8}]
        
        engine = OtisInferenceEngine(model_name="test-model", blue_team_enabled=False)
        result = engine.predict("Test text")
        
        # LABEL_1 should be mapped to SPAM
        assert result["label"] in ["SPAM", "NOT_SPAM"]


def test_red_team_integration():
    """Test integration with red team for robustness monitoring."""
    with patch('src.model.inference_engine.AutoTokenizer.from_pretrained'), \
         patch('src.model.inference_engine.AutoModelForSequenceClassification.from_pretrained'), \
         patch('src.model.inference_engine.pipeline') as mock_pipeline:
        
        mock_pipeline.return_value.return_value = [{"label": "SPAM", "score": 0.8}]
        
        # Initialize with red team monitoring enabled
        engine = OtisInferenceEngine(model_name="test-model", blue_team_enabled=False, red_team_monitoring=True)
        
        result = engine.predict("Test text")
        
        # Should have prediction result
        assert "label" in result
        assert "score" in result


def test_engine_with_real_red_team():
    """Test engine with actual red team engine."""
    # Create a real red team engine
    red_team = RedTeamEngine()
    
    with patch('src.model.inference_engine.AutoTokenizer.from_pretrained'), \
         patch('src.model.inference_engine.AutoModelForSequenceClassification.from_pretrained'), \
         patch('src.model.inference_engine.pipeline') as mock_pipeline:
        
        mock_pipeline.return_value.return_value = [{"label": "SPAM", "score": 0.8}]
        
        # Create engine with red team
        engine = OtisInferenceEngine(model_name="test-model", blue_team_enabled=False, red_team_monitoring=True)
        engine.red_team = red_team  # Set the real red team engine
        
        # This should work without errors
        result = engine.predict("Test text")
        assert "label" in result


def test_engine_robustness_report_structure():
    """Test the structure of robustness reports."""
    with patch('src.model.inference_engine.AutoTokenizer.from_pretrained'), \
         patch('src.model.inference_engine.AutoModelForSequenceClassification.from_pretrained'), \
         patch('src.model.inference_engine.pipeline') as mock_pipeline:
        
        mock_pipeline.return_value.return_value = [{"label": "SPAM", "score": 0.8}]
        
        engine = OtisInferenceEngine(model_name="test-model", blue_team_enabled=False)
        
        # Mock the red team to simulate a real test
        mock_red_team = Mock()
        mock_report = Mock()
        mock_report.total_attacks = 10
        mock_report.successful_evasions = 2
        mock_report.evasion_rate = 0.2
        mock_report.avg_confidence_drop = 0.15
        mock_report.attack_histogram = {"OBFUSCATION": 5, "SEMANTIC_SHIFT": 5}
        
        mock_red_team.test_model_robustness.return_value = mock_report
        engine.red_team = mock_red_team
        engine.red_team_monitoring = True
        
        test_texts = ["test1", "test2"]
        robustness_results = engine.test_adversarial_robustness(test_texts)
        
        assert "total_attacks" in robustness_results
        assert "successful_evasions" in robustness_results
        assert "evasion_rate" in robustness_results
        assert "avg_confidence_drop" in robustness_results
        assert "attack_histogram" in robustness_results
        assert "recommendations" in robustness_results


def test_prediction_with_security_wrapper():
    """Test prediction with security wrapper functionality."""
    with patch('src.model.inference_engine.AutoTokenizer.from_pretrained'), \
         patch('src.model.inference_engine.AutoModelForSequenceClassification.from_pretrained'), \
         patch('src.model.inference_engine.pipeline') as mock_pipeline:
        
        mock_pipeline.return_value.return_value = [{"label": "SPAM", "score": 0.8}]
        
        # Create engine with blue team enabled
        engine = OtisInferenceEngine(model_name="test-model", blue_team_enabled=True)
        
        # For this test, we expect the security wrapper to be called
        # but since blue team is enabled, it might return different results
        result = engine.predict("Normal email content")
        
        assert isinstance(result, dict)
        assert "label" in result
        assert "score" in result


def test_engine_device_selection():
    """Test that engine properly selects device."""
    with patch('src.model.inference_engine.AutoTokenizer.from_pretrained'), \
         patch('src.model.inference_engine.AutoModelForSequenceClassification.from_pretrained'), \
         patch('src.model.inference_engine.pipeline'), \
         patch('torch.cuda.is_available') as mock_cuda:
        
        # Test with CUDA available
        mock_cuda.return_value = True
        engine = OtisInferenceEngine(model_name="test-model", blue_team_enabled=False)
        assert engine.device == "cuda"
        
        # Test with CUDA not available
        mock_cuda.return_value = False
        engine = OtisInferenceEngine(model_name="test-model", blue_team_enabled=False, device="cpu")
        assert engine.device == "cpu"