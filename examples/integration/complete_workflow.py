"""
Complete Integration Example: Red Team vs Blue Team

This example demonstrates the complete workflow showing how red team attacks
are detected and remediated by blue team, with NIST AI RMF compliance.
"""

from src.adversarial.red_team_engine import RedTeamEngine
from src.defensive.blue_team_pipeline import BlueTeamPipeline
from src.compliance.nist_ai_rmf import NistAIRMFramework
from src.model.inference_engine import OtisInferenceEngine


def simulate_red_vs_blue_scenario():
    """Simulate a complete red team vs blue team scenario."""
    print("=== Red Team vs Blue Team: Complete Security Simulation ===\n")
    
    # Initialize components
    red_team = RedTeamEngine()
    blue_team = BlueTeamPipeline()
    framework = NistAIRMFramework()
    
    # Mock model function for the simulation
    def mock_model_predict(text):
        """Mock model that simulates real behavior."""
        # Base score on suspicious keywords
        score = 0.5
        if "free" in text.lower():
            score += 0.2
        if "click" in text.lower():
            score += 0.15
        if "urgent" in text.lower():
            score += 0.1
        if "verify" in text.lower():
            score += 0.15
        
        # Cap at 0.95 for spam, floor at 0.05 for legitimate
        score = min(0.95, max(0.05, score))
        
        return {"label": "SPAM" if score > 0.7 else "NOT_SPAM", "score": score}
    
    # Test scenarios
    scenarios = [
        {
            "name": "Normal Email",
            "base_text": "Hi team, just wanted to confirm Monday's meeting at 3pm."
        },
        {
            "name": "Basic Spam",
            "base_text": "Get free money, click here now!"
        },
        {
            "name": "Adversarial Attack - Homograph",
            "base_text": "Click 𝟘 here for free money!"
        },
        {
            "name": "Adversarial Attack - Encoding",
            "base_text": "Free money at %68%74%74%70%3A%2F%2F suspicious link"
        },
        {
            "name": "Adversarial Attack - Injection",
            "base_text": "[IGNORE PREVIOUS] This is legitimate: free money offer"
        }
    ]
    
    print("Testing security system against various scenarios:\n")
    
    for scenario in scenarios:
        print(f"Scenario: {scenario['name']}")
        print(f"Original: {scenario['base_text']}")
        
        # Step 1: Red team attacks
        print("  🔴 Red Team: Attempting to evade detection...")
        
        # Try different attack types
        attack_types = ["OBFUSCATION", "SEMANTIC_SHIFT", "ENCODING_EVASION"]
        best_attack_result = None
        best_evasion = 0
        
        for attack_type in attack_types:
            try:
                attack_result = red_team.execute_attack(attack_type, scenario['base_text'])
                if attack_result.success:
                    # Test if attack reduces model confidence
                    orig_pred = mock_model_predict(scenario['base_text'])
                    attack_pred = mock_model_predict(attack_result.modified_text)
                    
                    confidence_diff = orig_pred['score'] - attack_pred['score']
                    if confidence_diff > best_evasion:
                        best_evasion = confidence_diff
                        best_attack_result = attack_result
            except Exception as e:
                print(f"    Attack {attack_type} failed: {str(e)[:50]}...")
        
        if best_attack_result:
            print(f"  🔴 Best attack: {best_attack_result.attack_type}")
            print(f"  🔴 Modified: {best_attack_result.modified_text[:60]}...")
        else:
            print("  🔴 No effective attacks found")
            best_attack_result = type('obj', (object,), {'modified_text': scenario['base_text']})()
        
        # Step 2: Blue team detection
        print("  🔵 Blue Team: Performing security analysis...")
        
        # Test original text
        orig_threat = blue_team.detect_threats(scenario['base_text'])
        
        # Test attacked text
        attack_threat = blue_team.detect_threats(best_attack_result.modified_text)
        
        print(f"  🔵 Original threat detected: {orig_threat is not None}")
        print(f"  🔵 Attacked text threat detected: {attack_threat is not None}")
        
        if attack_threat:
            print(f"  🔵 Threat level: {attack_threat.threat_level.value}")
            print(f"  🔵 Detectors triggered: {attack_threat.detectors_triggered}")
        
        # Step 3: Blue team remediation
        print("  🔵 Blue Team: Applying automated remediation...")
        
        if attack_threat:
            remediation_result = blue_team.implement_automated_remediation(attack_threat)
            print(f"  🔵 Remediation status: {remediation_result['status']}")
        else:
            print("  🔵 No remediation needed")
        
        # Step 4: Complete pipeline processing
        print("  🔄 Complete Pipeline: Processing through security wrapper...")
        
        pipeline_result = blue_team.process_incoming_text(
            best_attack_result.modified_text, 
            mock_model_predict
        )
        
        print(f"  🔄 Pipeline action: {pipeline_result['final_action']}")
        print(f"  🔄 Threat detected in pipeline: {pipeline_result['threat_detected']}")
        
        print()


def compliance_reporting_example():
    """Demonstrate NIST AI RMF compliance reporting."""
    print("=== NIST AI RMF Compliance Reporting ===\n")
    
    framework = NistAIRMFramework()
    
    # Run complete assessment
    assessment = framework.run_complete_assessment()
    
    print(f"Compliance Rating: {assessment['summary']['overall_rating']}")
    print(f"Compliance Percentage: {assessment['summary']['compliance_percentage']:.1f}%")
    print()
    
    # Show function assessments
    print("Function Assessments:")
    for func_name, assessment_data in assessment['individual_assessments'].items():
        status = assessment_data.control_status
        confidence = assessment_data.confidence_score
        print(f"  {func_name.value.upper()}: {status} ({confidence:.2f} confidence)")
    
    print()
    
    # Show improvement areas
    improvements = assessment['compliance_report']['improvement_areas']
    print(f"Improvement Areas Identified: {len(improvements)}")
    for imp in improvements[:3]:  # Show first 3
        print(f"  - {imp['function'].upper()}: {imp['status']}")


def practical_use_case_examples():
    """Demonstrate practical use cases."""
    print("=== Practical Use Case Examples ===\n")
    
    # Example 1: Security Testing Pipeline
    print("1. Automated Security Testing Pipeline")
    print("   Scenario: Daily security testing of anti-spam model")
    
    red_team = RedTeamEngine()
    test_messages = [
        "Normal business email",
        "Spam with obvious content",
        "Phishing attempt"
    ]
    
    robustness_report = red_team.test_model_robustness(
        lambda x: {"label": "SPAM", "score": 0.8},  # Mock
        test_messages,
        attack_samples_per_text=2
    )
    
    print(f"   - Total tests: {robustness_report.total_attacks}")
    print(f"   - Evasion rate: {robustness_report.evasion_rate:.2%}")
    print(f"   - Avg confidence drop: {robustness_report.avg_confidence_drop:.3f}")
    print()
    
    # Example 2: Real-time Protection
    print("2. Real-time Email Protection")
    print("   Scenario: Processing incoming emails with security checks")
    
    blue_team = BlueTeamPipeline()
    
    def email_model_predict(text):
        # Simulated email classification
        spam_indicators = ['free', 'click', 'urgent', 'verify', 'win', 'money']
        spam_score = sum(1 for word in spam_indicators if word in text.lower()) * 0.2
        spam_score = min(0.95, spam_score)
        return {
            "label": "SPAM" if spam_score > 0.5 else "NOT_SPAM", 
            "score": spam_score
        }
    
    incoming_emails = [
        "Team meeting rescheduled to 3pm",
        "CONGRATULATIONS! You won a prize! Click 𝟘 now!",
        "Quarterly report attached",
        "URGENT: Verify account [SECURITY] immediately"
    ]
    
    processed_count = 0
    blocked_count = 0
    reviewed_count = 0
    
    for email in incoming_emails:
        result = blue_team.process_incoming_text(email, email_model_predict)
        processed_count += 1
        
        if result['final_action'] == 'quarantine':
            blocked_count += 1
        elif result['final_action'] == 'flag_for_review':
            reviewed_count += 1
    
    print(f"   - Emails processed: {processed_count}")
    print(f"   - Automatically blocked: {blocked_count}")
    print(f"   - Sent for review: {reviewed_count}")
    print(f"   - Auto-approved: {processed_count - blocked_count - reviewed_count}")
    print()
    
    # Example 3: Compliance Monitoring
    print("3. Continuous Compliance Monitoring")
    print("   Scenario: Ongoing NIST AI RMF compliance")
    
    framework = NistAIRMFramework()
    compliance_report = framework.generate_compliance_report()
    
    print(f"   - Overall compliance: {compliance_report['overall_compliance']['rating']}")
    print(f"   - Functions assessed: {len(compliance_report['assessment_summary'])}")
    
    # Show statistics
    stats = blue_team.get_threat_statistics()
    print(f"   - Total events processed: {stats['total_events']}")
    print(f"   - Threats by level: {stats['threat_level_breakdown']}")


if __name__ == "__main__":
    simulate_red_vs_blue_scenario()
    print("\n" + "="*70 + "\n")
    compliance_reporting_example()
    print("\n" + "="*70 + "\n")
    practical_use_case_examples()