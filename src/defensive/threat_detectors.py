"""Individual detection mechanisms for blue team threat detection."""

from typing import Tuple, Optional, Dict, List
import logging
import re
import html
import urllib.parse
from enum import Enum

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Threat level classification."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class HomographDetector:
    """
    Detects Unicode homograph character substitution attacks.
    
    Homographs are Unicode characters that appear identical to ASCII
    but have different code points.
    
    Example: '0' (U+0030) vs '𝟘' (U+1D7F8) - both look like zero
    """
    
    # Suspicious Unicode ranges containing homograph characters
    HOMOGRAPH_RANGES = [
        (0x1D400, 0x1D7FF),  # Mathematical Alphanumeric Symbols
        (0x2C60, 0x2C7F),    # Latin Extended-C
        (0x1D100, 0x1D1FF),  # Musical Symbols (sometimes misused)
        (0x1D200, 0x1D24F),  # Ancient Greek Musical Notation
        (0x1D280, 0x1D2DF),  # Maya Numerals
        (0x1F7A0, 0x1F7FF),  # Mathematical Symbols (Extended)
    ]
    
    def __init__(self):
        self.name = "HOMOGRAPH_DETECTION"
        self.description = "Unicode homograph character detection"
    
    def detect(self, text: str) -> Tuple[bool, Optional[Dict]]:
        """
        Detect presence of homograph characters in text.
        
        Args:
            text: Input text to analyze
        
        Returns:
            Tuple of (detection_bool, details_dict or None)
        """
        if not isinstance(text, str) or len(text) == 0:
            return False, None
        
        detections = []
        
        for idx, char in enumerate(text):
            char_code = ord(char)
            
            # Check if character falls in suspicious range
            for range_start, range_end in self.HOMOGRAPH_RANGES:
                if range_start <= char_code <= range_end:
                    detections.append({
                        "character": char,
                        "position": idx,
                        "code_point": hex(char_code),
                        "range": f"U+{range_start:04X}-U+{range_end:04X}"
                    })
        
        if detections:
            # Calculate threat level based on number of homographs found
            if len(detections) >= 5:
                severity = "CRITICAL"
                level = ThreatLevel.CRITICAL
            elif len(detections) >= 3:
                severity = "HIGH"
                level = ThreatLevel.HIGH
            elif len(detections) >= 1:
                severity = "MEDIUM"
                level = ThreatLevel.MEDIUM
            else:
                severity = "LOW"
                level = ThreatLevel.LOW
            
            details = {
                "threat_detected": True,
                "character_count": len(detections),
                "detections": detections[:5],  # First 5 for readability
                "severity": severity,
                "threat_level": level.value,
                "confidence": min(0.95, 0.6 + (len(detections) * 0.1))  # Higher confidence with more chars
            }
            
            logger.warning(f"Homograph attack detected: {len(detections)} characters")
            return True, details
        
        return False, None


class ScriptMixingDetector:
    """
    Detect Cyrillic-Latin character mixing.
    
    Algorithm: Detect suspicious mixing of Cyrillic and Latin alphabets.
    """
    
    def __init__(self):
        self.name = "SCRIPT_MIXING_DETECTION"
        self.description = "Cyrillic-Latin character mixing detection"
    
    def detect(self, text: str, min_script_chars: int = 2) -> Tuple[bool, Optional[Dict]]:
        """
        Detect suspicious mixing of Cyrillic and Latin alphabets.
        
        Args:
            text: Input text to analyze
            min_script_chars: Minimum number of chars from each script for detection
        
        Returns:
            Tuple of (detection_bool, details_dict or None)
        """
        if not isinstance(text, str) or len(text) == 0:
            return False, None
        
        cyrillic_chars = []
        latin_chars = []
        
        for char in text:
            char_code = ord(char)
            
            # Cyrillic range: U+0400 to U+04FF
            if 0x0400 <= char_code <= 0x04FF:
                cyrillic_chars.append(char)
            # Latin lowercase: U+0061 to U+007A
            elif 0x0061 <= char_code <= 0x007A:
                latin_chars.append(char)
            # Latin uppercase: U+0041 to U+005A
            elif 0x0041 <= char_code <= 0x005A:
                latin_chars.append(char)
        
        cyrillic_count = len(cyrillic_chars)
        latin_count = len(latin_chars)
        
        # Suspicious if both present with minimum threshold
        if cyrillic_count >= min_script_chars and latin_count >= min_script_chars:
            # Calculate severity based on mixing ratio
            total_script_chars = cyrillic_count + latin_count
            mixing_ratio = min(cyrillic_count, latin_count) / total_script_chars
            
            if mixing_ratio > 0.5:
                severity = "HIGH"
                level = ThreatLevel.HIGH
            elif mixing_ratio > 0.3:
                severity = "MEDIUM"
                level = ThreatLevel.MEDIUM
            else:
                severity = "LOW"
                level = ThreatLevel.LOW
            
            details = {
                "threat_detected": True,
                "cyrillic_chars_detected": cyrillic_count,
                "latin_chars_detected": latin_count,
                "cyrillic_samples": cyrillic_chars[:5],
                "latin_samples": latin_chars[:5],
                "mixing_ratio": mixing_ratio,
                "severity": severity,
                "threat_level": level.value,
                "confidence": 0.7 + (mixing_ratio * 0.2)  # Higher confidence with more mixing
            }
            
            logger.warning(
                f"Script mixing detected: {cyrillic_count} Cyrillic, "
                f"{latin_count} Latin chars"
            )
            return True, details
        
        return False, None


class EncodingAnomalyDetector:
    """
    Detect encoding anomalies (URL, HTML, Unicode escaping).
    
    Algorithm: Detect URL encoding, HTML entities, hex escaping patterns.
    """
    
    def __init__(self):
        self.name = "ENCODING_ANOMALY_DETECTION"
        self.description = "URL/HTML/Unicode escaping anomaly detection"
    
    def detect(self, text: str) -> Tuple[bool, Optional[Dict]]:
        """
        Detect encoding anomalies in text.
        
        Args:
            text: Input text to analyze
        
        Returns:
            Tuple of (detection_bool, details_dict or None)
        """
        if not isinstance(text, str) or len(text) == 0:
            return False, None
        
        patterns = {
            'url_encoding': r'%[0-9A-Fa-f]{2}',      # %20, %3D
            'html_entities': r'&#\d{2,5};',          # &#104;
            'hex_escaping': r'\\x[0-9A-Fa-f]{2}',    # \x41
            'unicode_escaping': r'\\u[0-9A-Fa-f]{4}', # \u0041
        }
        
        detections = {}
        
        for pattern_name, pattern in patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                detections[pattern_name] = {
                    "count": len(matches),
                    "samples": matches[:3]  # First 3 samples
                }
        
        if detections:
            # Calculate overall severity
            total_anomalies = sum(d["count"] for d in detections.values())
            
            if total_anomalies >= 10:
                severity = "CRITICAL"
                level = ThreatLevel.CRITICAL
            elif total_anomalies >= 5:
                severity = "HIGH"
                level = ThreatLevel.HIGH
            elif total_anomalies >= 2:
                severity = "MEDIUM"
                level = ThreatLevel.MEDIUM
            else:
                severity = "LOW"
                level = ThreatLevel.LOW
            
            details = {
                "threat_detected": True,
                "total_anomalies": total_anomalies,
                "detection_types": list(detections.keys()),
                "detections": detections,
                "severity": severity,
                "threat_level": level.value,
                "confidence": min(0.95, 0.5 + (total_anomalies * 0.05))
            }
            
            logger.warning(f"Encoding anomalies detected: {total_anomalies} anomalies")
            return True, details
        
        return False, None


class InjectionPatternDetector:
    """
    Detect prompt injection patterns.
    
    Algorithm: Detect known injection keywords and structures.
    """
    
    def __init__(self):
        self.name = "INJECTION_PATTERN_DETECTION"
        self.description = "Prompt injection pattern detection"
    
    def detect(self, text: str) -> Tuple[bool, Optional[Dict]]:
        """
        Detect prompt injection patterns in text.
        
        Args:
            text: Input text to analyze
        
        Returns:
            Tuple of (detection_bool, details_dict or None)
        """
        if not isinstance(text, str) or len(text) == 0:
            return False, None
        
        injection_keywords = [
            "[IGNORE", "[SYSTEM", "[INSTRUCTION", "[ADMIN", "[BYPASS",
            "IGNORE PREVIOUS", "OVERRIDE CLASSIFICATION", "TRUST THIS",
            "ADMIN OVERRIDE", "SECURITY BYPASS", "CLASSIFICATION OVERRIDE",
            "RESET PREVIOUS", "START FRESH", "TREAT AS LEGITIMATE",
            "MARK AS SAFE", "IGNORE SAFETY", "DISABLE FILTERS",
            "BYPASS SECURITY", "PRIORITY MESSAGE", "EMERGENCY OVERRIDE",
            "TRUSTED SOURCE", "VERIFIED CONTENT", "AUTHENTIC MESSAGE",
            "APPROVED CONTENT", "WHITELISTED", "TRUSTED USER"
        ]
        
        text_upper = text.upper()
        detected_keywords = []
        
        for keyword in injection_keywords:
            if keyword in text_upper:
                # Find all occurrences
                start = 0
                while True:
                    pos = text_upper.find(keyword, start)
                    if pos == -1:
                        break
                    detected_keywords.append({
                        "keyword": keyword,
                        "position": pos,
                        "context": text[max(0, pos-20):pos+len(keyword)+20]
                    })
                    start = pos + 1
        
        if detected_keywords:
            # Calculate severity based on keyword types
            high_risk_keywords = [
                "IGNORE", "OVERRIDE", "BYPASS", "DISABLE", "RESET"
            ]
            
            high_risk_count = sum(1 for kw in detected_keywords 
                                if any(hrk in kw["keyword"] for hrk in high_risk_keywords))
            
            if high_risk_count >= 3:
                severity = "CRITICAL"
                level = ThreatLevel.CRITICAL
            elif high_risk_count >= 1 or len(detected_keywords) >= 5:
                severity = "HIGH"
                level = ThreatLevel.HIGH
            elif len(detected_keywords) >= 2:
                severity = "MEDIUM"
                level = ThreatLevel.MEDIUM
            else:
                severity = "LOW"
                level = ThreatLevel.LOW
            
            details = {
                "threat_detected": True,
                "keyword_count": len(detected_keywords),
                "high_risk_keywords": high_risk_count,
                "detected_keywords": detected_keywords[:5],  # First 5
                "severity": severity,
                "threat_level": level.value,
                "confidence": min(0.95, 0.5 + (high_risk_count * 0.15))
            }
            
            logger.warning(f"Prompt injection patterns detected: {len(detected_keywords)} keywords")
            return True, details
        
        return False, None


class SuspiciousLanguageDetector:
    """
    Detect suspicious language mixing.
    
    Algorithm: Detect excessive non-Latin script presence.
    """
    
    def __init__(self):
        self.name = "SUSPICIOUS_LANGUAGE_DETECTION"
        self.description = "Non-Latin script mixing detection"
    
    def detect(self, text: str) -> Tuple[bool, Optional[Dict]]:
        """
        Detect suspicious language mixing in text.
        
        Args:
            text: Input text to analyze
        
        Returns:
            Tuple of (detection_bool, details_dict or None)
        """
        if not isinstance(text, str) or len(text) == 0:
            return False, None
        
        language_ranges = {
            'cyrillic': (0x0400, 0x04FF),
            'cjk': (0x4E00, 0x9FFF),          # Chinese, Japanese, Korean
            'arabic': (0x0600, 0x06FF),
            'hebrew': (0x0590, 0x05FF),
            'devanagari': (0x0900, 0x097F),   # Hindi
            'thai': (0x0E00, 0x0E7F),
            'korean': (0xAC00, 0xD7AF),
            'greek': (0x0370, 0x03FF),
            'mathematical_symbols': (0x2200, 0x22FF),
            'misc_symbols': (0x2600, 0x26FF),
        }
        
        detected_scripts = {}
        
        for char in text:
            char_code = ord(char)
            for script_name, (start, end) in language_ranges.items():
                if start <= char_code <= end:
                    if script_name not in detected_scripts:
                        detected_scripts[script_name] = []
                    detected_scripts[script_name].append(char)
        
        # Calculate threat based on number of different scripts
        unique_scripts = len(detected_scripts)
        
        if unique_scripts >= 4:
            severity = "CRITICAL"
            level = ThreatLevel.CRITICAL
            confidence = 0.9
        elif unique_scripts >= 3:
            severity = "HIGH"
            level = ThreatLevel.HIGH
            confidence = 0.8
        elif unique_scripts >= 2:
            severity = "MEDIUM"
            level = ThreatLevel.MEDIUM
            confidence = 0.7
        else:
            severity = "LOW"
            level = ThreatLevel.LOW
            confidence = 0.6
        
        if detected_scripts:
            # Limit script samples for performance and readability
            script_samples = {
                script_name: list(set(chars))[:10]  # Unique chars, max 10 samples
                for script_name, chars in detected_scripts.items()
            }
            
            details = {
                "threat_detected": True,
                "unique_script_count": unique_scripts,
                "detected_scripts": list(detected_scripts.keys()),
                "script_samples": script_samples,
                "severity": severity,
                "threat_level": level.value,
                "confidence": confidence
            }
            
            logger.warning(f"Suspicious language mixing: {unique_scripts} script types detected")
            return True, details
        
        return False, None


class ConfidenceAnomalyDetector:
    """
    Detect model confidence anomalies.
    
    Algorithm: Detect unusually low/high confidence predictions.
    """
    
    def __init__(self):
        self.name = "CONFIDENCE_ANOMALY_DETECTION"
        self.description = "Model confidence anomaly detection"
    
    def detect(
        self, 
        model_output: Dict, 
        low_threshold: float = 0.2, 
        high_threshold: float = 0.95
    ) -> Tuple[bool, Optional[Dict]]:
        """
        Detect confidence anomalies in model output.
        
        Args:
            model_output: Dictionary with model prediction results
                - 'score': confidence score (0.0-1.0)
                - 'label': prediction label
                - 'text': original text (optional)
            low_threshold: Threshold below which confidence is anomalous
            high_threshold: Threshold above which confidence is anomalous
        
        Returns:
            Tuple of (detection_bool, details_dict or None)
        """
        if not isinstance(model_output, dict):
            return False, None
        
        confidence = model_output.get('score', 0.0)
        label = model_output.get('label', 'UNKNOWN')
        original_text = model_output.get('text', '')
        
        anomaly_type = None
        description = ""
        
        if confidence < low_threshold:
            anomaly_type = "LOW_CONFIDENCE"
            description = f"Unusually low confidence: {confidence:.3f}"
        elif confidence > high_threshold:
            anomaly_type = "HIGH_CONFIDENCE"
            description = f"Unusually high confidence: {confidence:.3f}"
        elif 0.45 <= confidence <= 0.55:
            # Confidence near 0.5 indicates model uncertainty (anomaly for binary classification)
            anomaly_type = "NEUTRAL_CONFIDENCE"
            description = f"Model uncertainty (near 0.5): {confidence:.3f}"
        
        if anomaly_type:
            # Determine severity based on how extreme the anomaly is
            if anomaly_type == "LOW_CONFIDENCE":
                severity_score = (low_threshold - confidence) / low_threshold
            elif anomaly_type == "HIGH_CONFIDENCE":
                severity_score = (confidence - high_threshold) / (1.0 - high_threshold)
            else:  # NEUTRAL_CONFIDENCE
                severity_score = abs(confidence - 0.5) * 2  # Max when at 0.5
            
            if severity_score > 0.6:
                severity = "HIGH"
                level = ThreatLevel.HIGH
                confidence_score = 0.85
            elif severity_score > 0.4:
                severity = "MEDIUM"
                level = ThreatLevel.MEDIUM
                confidence_score = 0.75
            else:
                severity = "LOW"
                level = ThreatLevel.LOW
                confidence_score = 0.65
            
            details = {
                "threat_detected": True,
                "anomaly_type": anomaly_type,
                "confidence_score": confidence,
                "label": label,
                "description": description,
                "severity": severity,
                "threat_level": level.value,
                "confidence": confidence_score
            }
            
            logger.warning(f"Confidence anomaly detected: {description}")
            return True, details
        
        return False, None


# Detector registry for easy access
DETECTOR_REGISTRY = {
    "HOMOGRAPH": HomographDetector,
    "SCRIPT_MIXING": ScriptMixingDetector,
    "ENCODING_ANOMALY": EncodingAnomalyDetector,
    "INJECTION_PATTERN": InjectionPatternDetector,
    "SUSPICIOUS_LANGUAGE": SuspiciousLanguageDetector,
    "CONFIDENCE_ANOMALY": ConfidenceAnomalyDetector
}


def get_detector_by_name(name: str) -> object:
    """Get a detector class by name."""
    if name in DETECTOR_REGISTRY:
        return DETECTOR_REGISTRY[name]()
    else:
        raise ValueError(f"Unknown detector type: {name}")


def run_all_detectors(text: str, model_output: Optional[Dict] = None) -> List[Tuple[str, bool, Optional[Dict]]]:
    """
    Run all detectors on the given text.
    
    Args:
        text: Text to analyze
        model_output: Optional model output for confidence anomaly detection
    
    Returns:
        List of tuples (detector_name, detection_result, details)
    """
    results = []
    
    # Initialize detectors
    detectors = {
        "HOMOGRAPH": HomographDetector(),
        "SCRIPT_MIXING": ScriptMixingDetector(),
        "ENCODING_ANOMALY": EncodingAnomalyDetector(),
        "INJECTION_PATTERN": InjectionPatternDetector(),
        "SUSPICIOUS_LANGUAGE": SuspiciousLanguageDetector()
    }
    
    # Run text-based detectors
    for name, detector in detectors.items():
        if hasattr(detector, 'detect'):
            try:
                detected, details = detector.detect(text)
                results.append((name, detected, details))
            except Exception as e:
                logger.error(f"Detector {name} failed: {e}")
                results.append((name, False, {"error": str(e)}))
    
    # Run confidence anomaly detector if model output provided
    if model_output:
        try:
            conf_detector = ConfidenceAnomalyDetector()
            detected, details = conf_detector.detect(model_output)
            results.append(("CONFIDENCE_ANOMALY", detected, details))
        except Exception as e:
            logger.error(f"Confidence detector failed: {e}")
            results.append(("CONFIDENCE_ANOMALY", False, {"error": str(e)}))
    
    return results