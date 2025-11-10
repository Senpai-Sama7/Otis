"""Tests for NIST AI Risk Management Framework compliance."""

import pytest
from src.compliance.nist_ai_rmf import NistAIRMFramework, RiskAssessment
from datetime import datetime


@pytest.fixture
def compliance_framework():
    return NistAIRMFramework()


def test_map_function_assessment():
    """Test MAP function assessment."""
    framework = NistAIRMFramework()
    assessment = framework.assess_map_function()
    
    assert assessment.function.value == 'map'
    assert assessment.assessment_date <= datetime.now()
    assert isinstance(assessment.findings, dict)
    assert assessment.control_status in ['Implemented', 'Partial', 'Not Implemented']
    assert isinstance(assessment.evidence, list)
    assert 0.0 <= assessment.confidence_score <= 1.0


def test_measure_function_assessment():
    """Test MEASURE function assessment."""
    framework = NistAIRMFramework()
    assessment = framework.assess_measure_function()
    
    assert assessment.function.value == 'measure'
    assert assessment.assessment_date <= datetime.now()
    assert isinstance(assessment.findings, dict)
    assert assessment.control_status in ['Implemented', 'Partial', 'Not Implemented']


def test_manage_function_assessment():
    """Test MANAGE function assessment."""
    framework = NistAIRMFramework()
    assessment = framework.assess_manage_function()
    
    assert assessment.function.value == 'manage'
    assert isinstance(assessment.findings, dict)
    assert assessment.control_status in ['Implemented', 'Partial', 'Not Implemented']


def test_govern_function_assessment():
    """Test GOVERN function assessment."""
    framework = NistAIRMFramework()
    assessment = framework.assess_govern_function()
    
    assert assessment.function.value == 'govern'
    assert isinstance(assessment.findings, dict)
    assert assessment.control_status in ['Implemented', 'Partial', 'Not Implemented']


def test_complete_nist_assessment():
    """Test complete NIST AI RMF assessment."""
    framework = NistAIRMFramework()
    complete_assessment = framework.run_complete_assessment()
    
    assert 'comprehensive_report' in complete_assessment
    assert 'risk_treatment_plan' in complete_assessment
    assert 'individual_assessments' in complete_assessment
    assert 'summary' in complete_assessment
    
    report = complete_assessment['comprehensive_report']
    assert 'overall_compliance' in report
    assert 'function_breakdown' in report
    assert 'improvement_areas' in report
    
    summary = complete_assessment['summary']
    assert 'overall_rating' in summary
    assert 'compliance_percentage' in summary


def test_generate_compliance_report():
    """Test compliance report generation."""
    framework = NistAIRMFramework()
    report = framework.generate_compliance_report()
    
    assert 'report_date' in report
    assert 'overall_compliance' in report
    assert 'function_breakdown' in report
    assert 'improvement_areas' in report
    assert 'risk_register_summary' in report
    assert 'assessment_summary' in report
    
    overall = report['overall_compliance']
    assert 'score' in overall
    assert 'percentage' in overall
    assert 'rating' in overall
    assert 0.0 <= overall['score'] <= 1.0


def test_risk_assessment_management():
    """Test risk assessment registration and management."""
    framework = NistAIRMFramework()
    
    # Add a risk
    risk = RiskAssessment(
        risk_id="",
        category="model_bias",
        description="Potential bias in spam classification",
        likelihood=0.6,
        impact=0.7,
        risk_score=0.42,  # 0.6 * 0.7
        controls=["fairness_metrics", "bias_testing"],
        status="In Progress"
    )
    
    risk_id = framework.add_risk_assessment(risk)
    assert risk_id.startswith("RISK-")
    
    # Get risk register
    register = framework.get_risk_register()
    assert len(register) >= 1
    
    # Find our risk
    our_risk = None
    for r in register:
        if r.risk_id == risk_id:
            our_risk = r
            break
    
    assert our_risk is not None
    assert our_risk.category == "model_bias"
    assert our_risk.status == "In Progress"


def test_risk_status_updates():
    """Test updating risk status."""
    framework = NistAIRMFramework()
    
    risk = RiskAssessment(
        risk_id="",
        category="adversarial_attack",
        description="Model vulnerable to character obfuscation",
        likelihood=0.8,
        impact=0.9,
        risk_score=0.72,
        controls=["input_validation"],
        status="Unaddressed"
    )
    
    risk_id = framework.add_risk_assessment(risk)
    
    # Update status
    success = framework.update_risk_status(risk_id, "Mitigated")
    assert success
    
    # Verify update
    register = framework.get_risk_register()
    updated_risk = None
    for r in register:
        if r.risk_id == risk_id:
            updated_risk = r
            break
    
    assert updated_risk is not None
    assert updated_risk.status == "Mitigated"


def test_risk_treatment_plan():
    """Test risk treatment plan generation."""
    framework = NistAIRMFramework()
    
    # Add some risks
    high_risk = RiskAssessment(
        risk_id="",
        category="security",
        description="Adversarial attack vulnerability",
        likelihood=0.9,
        impact=0.9,
        risk_score=0.81,
        controls=[],
        status="Unaddressed"
    )
    framework.add_risk_assessment(high_risk)
    
    medium_risk = RiskAssessment(
        risk_id="",
        category="fairness",
        description="Model bias issue",
        likelihood=0.5,
        impact=0.6,
        risk_score=0.3,
        controls=[],
        status="Unaddressed"
    )
    framework.add_risk_assessment(medium_risk)
    
    # Generate treatment plan
    plan = framework.generate_risk_treatment_plan()
    
    assert 'generated_date' in plan
    assert 'total_risks' in plan
    assert 'treatment_recommendations' in plan
    assert plan['total_risks'] >= 2
    
    # Should have recommendations for high priority risks
    high_priority_recs = [r for r in plan['treatment_recommendations'] 
                         if r['priority'] == 'HIGH']
    assert len(high_priority_recs) >= 1


def test_compliance_rating_system():
    """Test compliance rating system."""
    framework = NistAIRMFramework()
    
    # Test rating calculation
    rating1 = framework._get_compliance_rating(0.95)
    assert rating1 == "Exemplary"
    
    rating2 = framework._get_compliance_rating(0.85)
    assert rating2 == "Strong"
    
    rating3 = framework._get_compliance_rating(0.75)
    assert rating3 == "Moderate"
    
    rating4 = framework._get_compliance_rating(0.6)
    assert rating4 == "Needs Improvement"
    
    rating5 = framework._get_compliance_rating(0.3)
    assert rating5 == "Significant Gaps"


def test_control_status_determination():
    """Test control status determination."""
    framework = NistAIRMFramework()
    
    status1 = framework._determine_control_status(0.95)
    assert status1 == "Implemented"
    
    status2 = framework._determine_control_status(0.75)
    assert status2 == "Partial"
    
    status3 = framework._determine_control_status(0.4)
    assert status3 == "Not Implemented"


def test_documentation_checking():
    """Test documentation checking functionality."""
    framework = NistAIRMFramework()
    
    # This will return False since files likely don't exist in test environment
    has_doc = framework._check_documentation_exists("SECURITY_POLICY.md")
    # The result doesn't matter, just that it doesn't crash
    assert isinstance(has_doc, bool)


def test_capability_checking():
    """Test capability checking functionality."""
    framework = NistAIRMFramework()
    
    has_capability = framework._check_capability_exists("robustness_testing")
    # The result depends on the internal mapping, but should be boolean
    assert isinstance(has_capability, bool)


def test_empty_framework():
    """Test framework with no assessments."""
    framework = NistAIRMFramework()
    
    # Generate report with no assessments
    report = framework.generate_compliance_report()
    
    assert 'overall_compliance' in report
    overall = report['overall_compliance']
    assert overall['score'] == 0.0
    assert overall['percentage'] == 0.0
    assert len(report['function_breakdown']['scores']) == 0


def test_single_function_assessment():
    """Test individual function assessments."""
    framework = NistAIRMFramework()
    
    # Test each function individually
    map_result = framework.assess_map_function()
    assert map_result.function == framework.__class__.__dict__['MAP']
    
    measure_result = framework.assess_measure_function()
    assert measure_result.function == framework.__class__.__dict__['MEASURE']
    
    manage_result = framework.assess_manage_function()
    assert manage_result.function == framework.__class__.__dict__['MANAGE']
    
    govern_result = framework.assess_govern_function()
    assert govern_result.function == framework.__class__.__dict__['GOVERN']


def test_risk_register_persistence():
    """Test that risk register persists between operations."""
    framework = NistAIRMFramework()
    
    # Add risk
    risk = RiskAssessment(
        risk_id="",
        category="test",
        description="Test risk",
        likelihood=0.5,
        impact=0.5,
        risk_score=0.25,
        controls=[],
        status="Unaddressed"
    )
    risk_id = framework.add_risk_assessment(risk)
    
    # Verify risk exists
    register = framework.get_risk_register()
    assert len(register) == 1
    assert register[0].risk_id == risk_id
    
    # Add another risk
    risk2 = RiskAssessment(
        risk_id="",
        category="test2", 
        description="Test risk 2",
        likelihood=0.3,
        impact=0.4,
        risk_score=0.12,
        controls=[],
        status="Mitigated"
    )
    framework.add_risk_assessment(risk2)
    
    # Verify both risks exist
    register = framework.get_risk_register()
    assert len(register) == 2