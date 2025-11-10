"""Main orchestration pipeline for blue team threat detection and remediation."""

import hashlib
import logging
from dataclasses import dataclass
from datetime import datetime

from .remediation_engine import AutomatedRemediationEngine
from .threat_detectors import ThreatLevel, run_all_detectors

logger = logging.getLogger(__name__)


@dataclass
class ThreatEvent:
    """Represents a detected threat event."""
    event_id: str
    timestamp: datetime
    text: str
    threat_level: ThreatLevel
    detectors_triggered: list[str]
    detector_details: list[dict]
    confidence_score: float
    original_model_prediction: dict | None = None
    severity_score: float = 0.0


class BlueTeamPipeline:
    """
    Main orchestration pipeline for threat detection and remediation.

    Integrates all detectors and implements automated response actions.
    """

    def __init__(self):
        self.remediation_engine = AutomatedRemediationEngine()
        self.threat_events: list[ThreatEvent] = []

        logger.info("Blue Team Pipeline initialized")

    def detect_threats(self, text: str, model_output: dict | None = None) -> ThreatEvent | None:
        """
        Run all threat detectors on the given text.

        Args:
            text: Text to analyze for threats
            model_output: Optional model output for confidence analysis

        Returns:
            ThreatEvent if threat detected, None otherwise
        """
        logger.info(f"Starting threat detection for text: {text[:100]}...")

        # Run all detectors
        detector_results = run_all_detectors(text, model_output)

        # Collect triggered detectors and details
        triggered_detectors = []
        detector_details = []
        highest_threat_level = ThreatLevel.NONE
        total_confidence = 0.0
        detector_count = 0

        for detector_name, detected, details in detector_results:
            if detected and details:
                triggered_detectors.append(detector_name)

                # Calculate detector-specific threat level
                detector_threat_level = ThreatLevel(details.get('threat_level', 'none'))
                if detector_threat_level.value != 'none':
                    # Use enum comparison to find highest threat
                    threat_values = {'none': 0, 'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
                    if threat_values[detector_threat_level.value] > threat_values[highest_threat_level.value]:
                        highest_threat_level = detector_threat_level

                # Calculate average confidence across detectors
                if 'confidence' in details:
                    total_confidence += details['confidence']
                    detector_count += 1

                details['detector_name'] = detector_name
                detector_details.append(details)

        # Calculate overall severity score
        avg_confidence = total_confidence / detector_count if detector_count > 0 else 0.0
        severity_score = self._calculate_severity_score(triggered_detectors, avg_confidence, detector_details)

        # Determine final threat level (escalate if needed based on multiple triggers)
        final_threat_level = self._escalate_threat_level(highest_threat_level, len(triggered_detectors))

        if final_threat_level != ThreatLevel.NONE:
            # Create threat event ID
            text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
            timestamp_str = datetime.now().strftime('%Y%m%d%H%M%S')
            event_id = f"THREAT_{timestamp_str}_{text_hash}"

            threat_event = ThreatEvent(
                event_id=event_id,
                timestamp=datetime.now(),
                text=text,
                threat_level=final_threat_level,
                detectors_triggered=triggered_detectors,
                detector_details=detector_details,
                confidence_score=avg_confidence,
                original_model_prediction=model_output,
                severity_score=severity_score
            )

            self.threat_events.append(threat_event)

            logger.warning(
                f"THREAT DETECTED: {final_threat_level.value.upper()} - "
                f"Triggers: {len(triggered_detectors)}, "
                f"Detectors: {', '.join(triggered_detectors[:3])}..."
            )

            return threat_event
        else:
            logger.info("No threats detected")
            return None

    def _calculate_severity_score(self, triggered_detectors: list[str], avg_confidence: float, details: list[dict]) -> float:
        """
        Calculate overall severity score based on detectors triggered and confidence.

        Args:
            triggered_detectors: List of detectors that triggered
            avg_confidence: Average confidence across detectors
            details: Details from all detectors

        Returns:
            Severity score (0.0-1.0)
        """
        base_score = 0.0

        # Weight different detectors differently
        detector_weights = {
            'HOMOGRAPH': 0.8,
            'ENCODING_ANOMALY': 0.7,
            'INJECTION_PATTERN': 0.9,
            'CONFIDENCE_ANOMALY': 0.6,
            'SCRIPT_MIXING': 0.7,
            'SUSPICIOUS_LANGUAGE': 0.6
        }

        for detector in triggered_detectors:
            base_score += detector_weights.get(detector, 0.5)

        # Normalize by number of triggers
        if triggered_detectors:
            base_score = min(1.0, base_score / len(triggered_detectors))

        # Incorporate confidence
        final_score = (base_score * 0.7) + (avg_confidence * 0.3)
        return min(1.0, final_score)

    def _escalate_threat_level(self, base_level: ThreatLevel, trigger_count: int) -> ThreatLevel:
        """
        Escalate threat level based on number of detectors triggered.

        Args:
            base_level: Base threat level from individual detectors
            trigger_count: Number of detectors that triggered

        Returns:
            Escalated threat level
        """
        if trigger_count >= 4:
            return ThreatLevel.CRITICAL
        elif trigger_count >= 3:
            if base_level.value != 'critical':
                return ThreatLevel.HIGH
        elif trigger_count >= 2:
            if base_level.value not in ['critical', 'high']:
                return ThreatLevel.MEDIUM

        return base_level

    def implement_automated_remediation(self, threat_event: ThreatEvent) -> dict:
        """
        Implement automated remediation for detected threat.

        Args:
            threat_event: ThreatEvent object with threat information

        Returns:
            Dict with remediation actions taken
        """
        threat_info = {
            'threat_level': threat_event.threat_level.value.upper(),
            'text': threat_event.text,
            'detectors_triggered': threat_event.detectors_triggered,
            'severity_score': threat_event.severity_score,
            'event_id': threat_event.event_id
        }

        logger.info(f"Initiating remediation for {threat_event.event_id}")

        remediation_result = self.remediation_engine.remediate(threat_info)

        logger.info(f"Remediation completed for {threat_event.event_id}: {remediation_result.get('status', 'unknown')}")

        return remediation_result

    def process_incoming_text(self, text: str, model_predict_func) -> dict:
        """
        Complete pipeline: detect threats and implement remediation if needed.

        Args:
            text: Input text to process
            model_predict_func: Function to get model prediction

        Returns:
            Dict with processing results
        """
        logger.info(f"Processing incoming text: {text[:100]}...")

        # Get model prediction
        try:
            model_output = model_predict_func(text)
            model_output['text'] = text  # Add text for context
        except Exception as e:
            logger.error(f"Model prediction failed: {e}")
            model_output = {'score': 0.0, 'label': 'ERROR', 'text': text}

        # Run threat detection
        threat_event = self.detect_threats(text, model_output)

        result = {
            'text': text,
            'model_prediction': model_output,
            'threat_detected': threat_event is not None,
            'threat_event_id': threat_event.event_id if threat_event else None,
            'final_action': 'allow',
            'processing_steps': []
        }

        if threat_event:
            result['processing_steps'].append('threat_detected')

            # Implement remediation
            remediation_result = self.implement_automated_remediation(threat_event)
            result['remediation_result'] = remediation_result

            # Determine final action based on remediation
            status = remediation_result.get('status', 'unknown')
            if 'critical' in status or 'quarantined' in status:
                result['final_action'] = 'quarantine'
            elif 'flagged' in status:
                result['final_action'] = 'flag_for_review'
            elif 'logged' in status:
                result['final_action'] = 'allow'
            else:
                result['final_action'] = 'allow'
        else:
            result['processing_steps'].append('no_threat_detected')

        logger.info(f"Processing completed: action={result['final_action']}")
        return result

    def get_threat_statistics(self) -> dict:
        """Get statistics about detected threats."""
        if not self.threat_events:
            return {
                'total_events': 0,
                'threat_level_breakdown': {
                    'critical': 0,
                    'high': 0,
                    'medium': 0,
                    'low': 0,
                    'none': 0
                },
                'detector_trigger_frequency': {}
            }

        # Count threat levels
        threat_counts = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'none': 0
        }

        # Count detector triggers
        detector_counts = {}

        for event in self.threat_events:
            threat_counts[event.threat_level.value] += 1

            for detector in event.detectors_triggered:
                detector_counts[detector] = detector_counts.get(detector, 0) + 1

        return {
            'total_events': len(self.threat_events),
            'threat_level_breakdown': threat_counts,
            'detector_trigger_frequency': detector_counts,
            'average_severity_score': sum(e.severity_score for e in self.threat_events) / len(self.threat_events),
            'most_common_threat': max(threat_counts.items(), key=lambda x: x[1])[0]
        }

    def classify_threat_severity(self, threat_event: ThreatEvent) -> str:
        """
        Classify overall threat severity based on multiple factors.

        Args:
            threat_event: ThreatEvent to classify

        Returns:
            Threat severity string (CRITICAL/HIGH/MEDIUM/LOW)
        """
        # Base on threat level from detectors
        base_severity = threat_event.threat_level.value.upper()

        # Consider number of detectors triggered
        detector_count = len(threat_event.detectors_triggered)

        # Consider severity score
        severity_score = threat_event.severity_score

        # Adjust classification based on multiple factors
        if detector_count >= 4 or severity_score >= 0.8:
            return "CRITICAL"
        elif detector_count >= 3 or severity_score >= 0.6:
            return "HIGH"
        elif detector_count >= 2 or severity_score >= 0.4:
            return "MEDIUM"
        else:
            return base_severity

    def batch_process_texts(self, texts: list[str], model_predict_func) -> list[dict]:
        """
        Process multiple texts in batch.

        Args:
            texts: List of texts to process
            model_predict_func: Function to get model predictions

        Returns:
            List of processing results for each text
        """
        results = []

        for i, text in enumerate(texts):
            logger.info(f"Processing batch item {i+1}/{len(texts)}")
            result = self.process_incoming_text(text, model_predict_func)
            results.append(result)

        return results

    def get_recent_threats(self, hours: int = 24) -> list[ThreatEvent]:
        """
        Get threats detected in the last specified hours.

        Args:
            hours: Number of hours to look back

        Returns:
            List of recent ThreatEvents
        """
        import datetime as dt

        time_threshold = datetime.now() - dt.timedelta(hours=hours)
        recent_threats = [t for t in self.threat_events if t.timestamp > time_threshold]

        # Sort by timestamp, most recent first
        recent_threats.sort(key=lambda x: x.timestamp, reverse=True)

        return recent_threats

    def clear_old_threats(self, days: int = 30) -> int:
        """
        Clear threat events older than specified days.

        Args:
            days: Number of days to retain events

        Returns:
            Number of events removed
        """
        import datetime as dt

        time_threshold = datetime.now() - dt.timedelta(days=days)
        old_events = [t for t in self.threat_events if t.timestamp < time_threshold]

        # Remove old events
        self.threat_events = [t for t in self.threat_events if t.timestamp >= time_threshold]

        logger.info(f"Removed {len(old_events)} events older than {days} days")
        return len(old_events)
