"""Model inference engine with security wrapping for Otis anti-spam model."""

import logging
from typing import Dict, List, Optional, Callable, Any

logger = logging.getLogger(__name__)


class OtisInferenceEngine:
    """
    Load and run the Otis anti-spam model with security wrapping.
    
    This engine integrates the Otis model with blue team security checks
    and provides a secure inference interface.
    """
    
    def __init__(
        self, 
        model_name: str = "Titeiiko/OTIS-Official-Spam-Model",
        device: Optional[str] = None,
        blue_team_enabled: bool = True,
        red_team_monitoring: bool = False
    ):
        """
        Initialize the Otis inference engine.
        
        Args:
            model_name: Name of the HuggingFace model to load
            device: Device to run model on ('cuda', 'cpu', or None for auto)
            blue_team_enabled: Whether to enable blue team security checks
            red_team_monitoring: Whether to monitor for adversarial patterns
        """
        try:
            import torch
            from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
        except ImportError:
            logger.error("Transformers library not installed. Please install with: pip install transformers torch")
            raise ImportError("Transformers library is required for OtisInferenceEngine. Install with: pip install transformers torch")
        
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        
        # Initialize model components
        try:
            logger.info(f"Loading model '{model_name}' on {self.device}")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name).to(self.device)
            self.classifier = pipeline(
                "text-classification",
                model=model_name,
                device=0 if torch.cuda.is_available() else -1,
                tokenizer=self.tokenizer
            )
        except Exception as e:
            logger.error(f"Failed to load model '{model_name}': {e}")
            raise
        
        # Initialize security components
        self.blue_team_enabled = blue_team_enabled
        self.red_team_monitoring = red_team_monitoring
        
        if blue_team_enabled:
            from ..defensive.blue_team_pipeline import BlueTeamPipeline
            self.blue_team = BlueTeamPipeline()
        else:
            self.blue_team = None
        
        if red_team_monitoring:
            from ..adversarial.red_team_engine import RedTeamEngine
            self.red_team = RedTeamEngine()
        else:
            self.red_team = None
        
        logger.info(f"Otis Inference Engine initialized on {self.device}")
    
    def predict(self, text: str) -> Dict[str, Any]:
        """
        Single prediction with optional security wrapping.
        
        Args:
            text: Text to classify as spam or not spam
            
        Returns:
            Dictionary with classification results
        """
        logger.info(f"Processing prediction for text: {text[:100]}...")
        
        # Pre-inference security check (blue team)
        if self.blue_team and self.blue_team_enabled:
            threat_event = self.blue_team.detect_threats(text)
            if threat_event and threat_event.threat_level.value in ['critical', 'high']:
                logger.warning(f"High threat detected, returning security blocked response")
                return {
                    "label": "SECURITY_BLOCKED",
                    "score": 1.0,
                    "text": text,
                    "security_event_id": threat_event.event_id,
                    "threat_level": threat_event.threat_level.value
                }
        
        # Run inference
        try:
            result = self.classifier(text)[0]
            confidence = result["score"]
            
            # Map labels if needed (HuggingFace models often use LABEL_0/LABEL_1)
            label = result["label"]
            if label == "LABEL_1":
                label = "SPAM"
            elif label == "LABEL_0":
                label = "NOT_SPAM"
            
            prediction_result = {
                "label": label,
                "score": confidence,
                "text": text
            }
            
            logger.info(f"Prediction: {label} (confidence: {confidence:.3f})")
            
        except Exception as e:
            logger.error(f"Model inference failed: {e}")
            return {
                "label": "ERROR",
                "score": 0.0,
                "text": text,
                "error": str(e)
            }
        
        # Post-inference security check
        if self.blue_team and self.blue_team_enabled:
            # Run threat detection on the model output
            model_output_with_text = prediction_result.copy()
            threat_event = self.blue_team.detect_threats(text, model_output_with_text)
            
            if threat_event:
                logger.warning(f"Post-inference threat detected: {threat_event.threat_level.value}")
                prediction_result["security_event_id"] = threat_event.event_id
                prediction_result["post_inference_threat"] = threat_event.threat_level.value
        
        return prediction_result
    
    def predict_batch(self, texts: List[str], batch_size: int = 32) -> List[Dict[str, Any]]:
        """
        Batch predictions for efficiency with optional security wrapping.
        
        Args:
            texts: List of texts to classify
            batch_size: Size of batches for processing
            
        Returns:
            List of prediction results
        """
        logger.info(f"Processing batch of {len(texts)} texts")
        
        results = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            batch_results = []
            
            for text in batch:
                result = self.predict_single_with_security(text)
                batch_results.append(result)
            
            results.extend(batch_results)
        
        logger.info(f"Batch processing completed for {len(results)} texts")
        return results
    
    def predict_single_with_security(self, text: str) -> Dict[str, Any]:
        """
        Single prediction with comprehensive security checking.
        
        Args:
            text: Text to classify
            
        Returns:
            Dictionary with classification and security information
        """
        # This is a more comprehensive version of predict that includes 
        # additional security checks and logging
        overall_result = self.predict(text)
        
        # If red team monitoring is enabled, analyze for adversarial patterns
        if self.red_team and self.red_team_monitoring:
            try:
                # Run robustness test to see if this text might be adversarial
                robustness_report = self.red_team.test_model_robustness(
                    self._get_predict_func(),
                    [text],
                    attack_samples_per_text=1,
                    attack_types=["OBFUSCATION", "SEMANTIC_SHIFT", "ENCODING_EVASION"]
                )
                
                # Check if the text was vulnerable to any attacks in the report
                if robustness_report.total_attacks > 0:
                    avg_confidence_drop = robustness_report.avg_confidence_drop
                    overall_result["is_potential_adversarial"] = avg_confidence_drop > 0.1
                    overall_result["robustness_metrics"] = {
                        "evasion_rate": robustness_report.evasion_rate,
                        "avg_confidence_drop": avg_confidence_drop
                    }
            except Exception as e:
                logger.warning(f"Red team analysis failed: {e}")
        
        return overall_result
    
    def _get_predict_func(self) -> Callable:
        """Return a function that can be used for predictions."""
        def predict_func(text: str) -> Dict[str, Any]:
            return self.predict(text)
        return predict_func
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model.
        
        Returns:
            Dictionary with model information
        """
        return {
            "model_name": self.model_name,
            "device": self.device,
            "model_type": "transformer_binary_classifier",
            "task": "spam_classification",
            "labels": ["SPAM", "NOT_SPAM"],
            "security_features": {
                "blue_team_enabled": self.blue_team_enabled,
                "red_team_monitoring": self.red_team_monitoring,
                "pre_inference_check": self.blue_team_enabled,
                "post_inference_check": self.blue_team_enabled
            }
        }
    
    def test_adversarial_robustness(
        self,
        test_texts: List[str],
        attack_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Test model's robustness against adversarial attacks.
        
        Args:
            test_texts: List of texts to test
            attack_types: List of attack types to use for testing
            
        Returns:
            Dictionary with robustness metrics
        """
        if not self.red_team:
            logger.warning("Red team not initialized for robustness testing")
            return {"error": "Red team not available"}
        
        logger.info(f"Testing adversarial robustness on {len(test_texts)} texts")
        
        try:
            report = self.red_team.test_model_robustness(
                self._get_predict_func(),
                test_texts,
                attack_samples_per_text=3,
                attack_types=attack_types
            )
            
            robustness_metrics = {
                "total_attacks": report.total_attacks,
                "successful_evasions": report.successful_evasions,
                "evasion_rate": report.evasion_rate,
                "avg_confidence_drop": report.avg_confidence_drop,
                "attack_histogram": report.attack_histogram,
                "recommendations": []
            }
            
            # Generate recommendations based on results
            if report.evasion_rate > 0.3:
                robustness_metrics["recommendations"].append(
                    "Model shows high vulnerability to adversarial attacks. "
                    "Consider implementing additional defensive measures."
                )
            elif report.evasion_rate > 0.1:
                robustness_metrics["recommendations"].append(
                    "Moderate vulnerability detected. "
                    "Some defensive measures may be beneficial."
                )
            else:
                robustness_metrics["recommendations"].append(
                    "Model shows good robustness against tested attacks."
                )
            
            return robustness_metrics
            
        except Exception as e:
            logger.error(f"Robustness testing failed: {e}")
            return {"error": str(e)}
    
    def update_security_settings(
        self,
        blue_team_enabled: Optional[bool] = None,
        red_team_monitoring: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Update security settings at runtime.
        
        Args:
            blue_team_enabled: Whether to enable/disable blue team checks
            red_team_monitoring: Whether to enable/disable red team monitoring
            
        Returns:
            Dictionary with updated settings
        """
        if blue_team_enabled is not None:
            self.blue_team_enabled = blue_team_enabled
            if blue_team_enabled and not self.blue_team:
                self.blue_team = BlueTeamPipeline()
            logger.info(f"Blue team enabled: {blue_team_enabled}")
        
        if red_team_monitoring is not None:
            self.red_team_monitoring = red_team_monitoring
            if red_team_monitoring and not self.red_team:
                self.red_team = RedTeamEngine()
            logger.info(f"Red team monitoring: {red_team_monitoring}")
        
        return {
            "blue_team_enabled": self.blue_team_enabled,
            "red_team_monitoring": self.red_team_monitoring
        }
    
    def get_security_status(self) -> Dict[str, Any]:
        """
        Get current security status and statistics.
        
        Returns:
            Dictionary with security status information
        """
        status = {
            "timestamp": str(datetime.now()),
            "blue_team_enabled": self.blue_team_enabled,
            "red_team_monitoring": self.red_team_monitoring
        }
        
        if self.blue_team:
            try:
                threat_stats = self.blue_team.get_threat_statistics()
                status["threat_statistics"] = threat_stats
            except Exception as e:
                logger.warning(f"Could not get threat statistics: {e}")
                status["threat_statistics"] = {"error": str(e)}
        
        if self.red_team:
            try:
                # We don't have access to the mdp_orchestrator directly in red_team_engine
                # but we can get basic info
                status["red_team_status"] = "initialized"
            except Exception as e:
                logger.warning(f"Could not get red team status: {e}")
                status["red_team_status"] = {"error": str(e)}
        
        return status


# Import datetime for the method that uses it
from datetime import datetime


# Example usage function (can be called to test)
def create_otis_engine(model_name: str = "Titeiiko/OTIS-Official-Spam-Model") -> OtisInferenceEngine:
    """
    Convenience function to create an Otis inference engine.
    
    Args:
        model_name: Name of the model to load
        
    Returns:
        Initialized OtisInferenceEngine
    """
    return OtisInferenceEngine(model_name=model_name)