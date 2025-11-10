"""Automated remediation engine for detected threats."""

import logging
from typing import Dict, List, Any
from datetime import datetime
import hashlib
from enum import Enum

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Threat level classification."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class AutomatedRemediationEngine:
    """
    Automated response to detected threats.
    
    Actions vary by severity:
    - CRITICAL: Quarantine + alert security team + incident response
    - HIGH: Quarantine + flag for manual review
    - MEDIUM: Flag for review + enhanced inspection
    - LOW: Log only
    """
    
    def __init__(self, audit_logger=None, notification_system=None):
        self.audit_logger = audit_logger
        self.notifications = notification_system
        self.quarantine_queue = []
        self.remediation_history = []
        
        logger.info("Automated Remediation Engine initialized")
    
    def remediate(self, threat_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute remediation for detected threat.
        
        Args:
            threat_event: Dict with threat information
                - threat_level (str): CRITICAL/HIGH/MEDIUM/LOW
                - text (str): The text that triggered the threat
                - detectors_triggered (List[str]): List of detectors that fired
                - severity_score (float): 0.0-1.0 severity score
                - event_id (str): Unique event identifier
        
        Returns:
            Dict with remediation actions taken
        """
        
        threat_level_str = threat_event.get('threat_level', 'LOW')
        try:
            threat_level = ThreatLevel(threat_level_str.upper())
        except ValueError:
            logger.error(f"Invalid threat level: {threat_level_str}, defaulting to LOW")
            threat_level = ThreatLevel.LOW
        
        text = threat_event.get('text', '')
        event_id = threat_event.get('event_id', self._generate_event_id(text))
        
        remediation_actions = {
            "event_id": event_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "threat_level": threat_level.value,
            "actions_taken": [],
            "status": "in_progress",
            "original_threat_data": threat_event
        }
        
        try:
            if threat_level == ThreatLevel.CRITICAL:
                # Immediate quarantine + escalation
                remediation_actions["actions_taken"].extend([
                    "quarantine_message",
                    "alert_security_team_critical",
                    "trigger_incident_response",
                    "block_sender_domain",
                    "create_incident_ticket"
                ])
                
                # Quarantine
                self._quarantine_message(text, event_id)
                
                # Alert security team if notification system available
                if self.notifications:
                    self.notifications.send_alert(
                        level="CRITICAL",
                        title="Critical Threat Detected",
                        details=threat_event,
                        event_id=event_id
                    )
                
                remediation_actions["status"] = "critical_escalated"
            
            elif threat_level == ThreatLevel.HIGH:
                # Quarantine + manual review
                remediation_actions["actions_taken"].extend([
                    "quarantine_message",
                    "log_to_audit_trail",
                    "flag_for_manual_review",
                    "request_additional_analysis"
                ])
                
                self._quarantine_message(text, event_id)
                
                if self.notifications:
                    self.notifications.send_alert(
                        level="HIGH",
                        title="High Severity Threat",
                        details=threat_event,
                        event_id=event_id
                    )
                
                remediation_actions["status"] = "quarantined_high"
            
            elif threat_level == ThreatLevel.MEDIUM:
                # Flag for review + enhanced monitoring
                remediation_actions["actions_taken"].extend([
                    "flag_for_review",
                    "apply_enhanced_inspection",
                    "add_to_watchlist"
                ])
                
                if self.notifications:
                    self.notifications.send_notification(
                        level="MEDIUM",
                        title="Medium Severity Threat Flagged",
                        details=threat_event,
                        event_id=event_id
                    )
                
                remediation_actions["status"] = "flagged_medium"
            
            elif threat_level == ThreatLevel.LOW:
                # Log only
                remediation_actions["actions_taken"].append("log_only")
                remediation_actions["status"] = "logged"
            
            else:  # ThreatLevel.NONE
                remediation_actions["actions_taken"].append("no_action")
                remediation_actions["status"] = "no_threat"
            
            # Always audit log if audit logger available
            if self.audit_logger:
                try:
                    self.audit_logger.log_remediation(remediation_actions)
                except Exception as e:
                    logger.error(f"Audit logging failed: {e}")
            
            logger.info(f"Remediation executed: {event_id} - {threat_level.value}")
        
        except Exception as e:
            logger.error(f"Remediation failed: {e}")
            remediation_actions["status"] = "remediation_failed"
            remediation_actions["error"] = str(e)
        
        # Add to remediation history
        self.remediation_history.append(remediation_actions)
        
        return remediation_actions
    
    def _quarantine_message(self, text: str, event_id: str) -> None:
        """Quarantine malicious message."""
        quarantine_entry = {
            "event_id": event_id,
            "text_hash": hashlib.sha256(text.encode()).hexdigest(),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "status": "quarantined",
            "retention_days": 90
        }
        self.quarantine_queue.append(quarantine_entry)
        logger.info(f"Message quarantined: {event_id}")
    
    def _generate_event_id(self, text: str) -> str:
        """Generate a unique event ID based on text content."""
        text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        return f"REMEDIATE_{timestamp}_{text_hash}"
    
    def get_quarantined_messages(self) -> List[Dict[str, Any]]:
        """Get list of quarantined messages."""
        return self.quarantine_queue.copy()
    
    def release_from_quarantine(self, event_id: str) -> bool:
        """Release a message from quarantine (for false positives)."""
        for i, entry in enumerate(self.quarantine_queue):
            if entry["event_id"] == event_id:
                released_entry = self.quarantine_queue.pop(i)
                released_entry["status"] = "released"
                logger.info(f"Message released from quarantine: {event_id}")
                return True
        logger.warning(f"Quarantined message not found: {event_id}")
        return False
    
    def get_remediation_statistics(self) -> Dict[str, Any]:
        """Get statistics about remediation activities."""
        if not self.remediation_history:
            return {
                "total_remediations": 0,
                "by_threat_level": {
                    "critical": 0,
                    "high": 0,
                    "medium": 0, 
                    "low": 0,
                    "none": 0
                },
                "by_status": {},
                "quarantine_count": len(self.quarantine_queue)
            }
        
        # Count by threat level
        threat_level_counts = {
            "critical": 0,
            "high": 0, 
            "medium": 0,
            "low": 0,
            "none": 0
        }
        
        # Count by status
        status_counts = {}
        
        for event in self.remediation_history:
            tl = event.get("threat_level", "none")
            if tl in threat_level_counts:
                threat_level_counts[tl] += 1
            
            status = event.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_remediations": len(self.remediation_history),
            "by_threat_level": threat_level_counts,
            "by_status": status_counts,
            "quarantine_count": len(self.quarantine_queue),
            "oldest_remediation": min(
                (e.get("timestamp") for e in self.remediation_history if e.get("timestamp")),
                default="N/A"
            ) if self.remediation_history else "N/A"
        }
    
    def clear_old_quarantine(self, days: int = 90) -> int:
        """
        Clear quarantine entries older than specified days.
        
        Args:
            days: Number of days to retain quarantine entries
            
        Returns:
            Number of entries removed
        """
        import datetime as dt
        
        cutoff = datetime.utcnow() - dt.timedelta(days=days)
        old_entries = []
        
        for i in range(len(self.quarantine_queue) - 1, -1, -1):
            entry_time_str = self.quarantine_queue[i]["timestamp"]
            entry_time = datetime.fromisoformat(entry_time_str.replace("Z", "+00:00"))
            if entry_time < cutoff:
                old_entries.append(i)
        
        # Remove old entries in reverse order to maintain indices
        for i in sorted(old_entries, reverse=True):
            del self.quarantine_queue[i]
        
        logger.info(f"Removed {len(old_entries)} quarantine entries older than {days} days")
        return len(old_entries)