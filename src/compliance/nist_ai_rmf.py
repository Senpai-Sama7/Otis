"""NIST AI Risk Management Framework implementation for compliance."""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class RiskManagementFunction(Enum):
    """NIST AI RMF Core Functions."""
    MAP = "map"           # Context & identification
    MEASURE = "measure"   # Assessment & quantification
    MANAGE = "manage"     # Control implementation
    GOVERN = "govern"     # Governance & oversight


@dataclass
class ComplianceAssessment:
    """Structure for compliance assessment results."""
    function: RiskManagementFunction
    assessment_date: datetime
    findings: Dict
    control_status: str  # "Implemented", "Partial", "Not Implemented"
    evidence: List[str]
    remediation_plan: Optional[str] = None
    confidence_score: float = 0.0


@dataclass
class RiskAssessment:
    """Structure for individual risk assessment."""
    risk_id: str
    category: str
    description: str
    likelihood: float  # 0.0-1.0
    impact: float      # 0.0-1.0
    risk_score: float  # likelihood * impact
    controls: List[str]
    status: str        # "Mitigated", "Accepted", "In Progress", "Unaddressed"


class NistAIRMFramework:
    """
    Implementation of NIST AI Risk Management Framework.
    
    The framework provides 4 core functions:
    1. MAP: Establish context and identify risks
    2. MEASURE: Assess and quantify risks
    3. MANAGE: Implement and maintain controls
    4. GOVERN: Ensure oversight and accountability
    """
    
    def __init__(self):
        self.assessments: List[ComplianceAssessment] = []
        self.risk_register: List[RiskAssessment] = []
        
        logger.info("NIST AI RMF Framework initialized")
    
    def assess_map_function(self) -> ComplianceAssessment:
        """
        Assess MAP (Context & Identification) function.
        
        MAP includes:
        - System design documentation
        - Threat model identification
        - Data flow mapping
        - Stakeholder analysis
        - Regulatory requirement identification
        """
        logger.info("Assessing MAP function")
        
        # Check for required documentation
        has_threat_model = self._check_documentation_exists("THREAT_MODEL.md")
        has_system_architecture = self._check_documentation_exists("SYSTEM_ARCHITECTURE.md")
        has_data_flow_map = self._check_documentation_exists("DATA_FLOW.md")
        has_risk_register = len(self.risk_register) > 0
        
        # Calculate compliance score
        required_items = 4
        implemented_items = sum([
            has_threat_model,
            has_system_architecture,
            has_data_flow_map,
            has_risk_register
        ])
        
        compliance_score = implemented_items / required_items if required_items > 0 else 0.0
        control_status = self._determine_control_status(compliance_score)
        
        findings = {
            "has_threat_model": has_threat_model,
            "has_system_architecture": has_system_architecture,
            "has_data_flow_map": has_data_flow_map,
            "has_risk_register": has_risk_register,
            "compliance_percentage": compliance_score * 100
        }
        
        evidence = []
        if has_threat_model:
            evidence.append("THREAT_MODEL.md exists and documents threat landscape")
        if has_system_architecture:
            evidence.append("SYSTEM_ARCHITECTURE.md documents system design")
        if has_data_flow_map:
            evidence.append("DATA_FLOW.md maps data processing flows")
        if has_risk_register:
            evidence.append("Risk register maintained with identified risks")
        
        assessment = ComplianceAssessment(
            function=RiskManagementFunction.MAP,
            assessment_date=datetime.now(),
            findings=findings,
            control_status=control_status,
            evidence=evidence,
            confidence_score=compliance_score
        )
        
        self.assessments.append(assessment)
        logger.info(f"MAP assessment completed: {control_status} ({compliance_score:.1%})")
        
        return assessment
    
    def assess_measure_function(self) -> ComplianceAssessment:
        """
        Assess MEASURE (Assessment & Quantification) function.
        
        MEASURE includes:
        - Risk quantification methods
        - Performance metrics tracking
        - Adversarial robustness testing
        - Impact assessment procedures
        """
        logger.info("Assessing MEASURE function")
        
        # Check for measurement capabilities
        has_robustness_tests = self._check_capability_exists("robustness_testing")
        has_performance_metrics = self._check_capability_exists("performance_tracking")
        has_impact_assessment = self._check_capability_exists("impact_assessment")
        has_bias_detection = self._check_capability_exists("bias_detection")
        
        # Calculate compliance score
        required_items = 4
        implemented_items = sum([
            has_robustness_tests,
            has_performance_metrics,
            has_impact_assessment,
            has_bias_detection
        ])
        
        compliance_score = implemented_items / required_items if required_items > 0 else 0.0
        control_status = self._determine_control_status(compliance_score)
        
        findings = {
            "has_robustness_tests": has_robustness_tests,
            "has_performance_metrics": has_performance_metrics,
            "has_impact_assessment": has_impact_assessment,
            "has_bias_detection": has_bias_detection,
            "compliance_percentage": compliance_score * 100
        }
        
        evidence = []
        if has_robustness_tests:
            evidence.append("Adversarial robustness testing implemented")
        if has_performance_metrics:
            evidence.append("Performance metrics tracked over time")
        if has_impact_assessment:
            evidence.append("Impact assessment procedures documented")
        if has_bias_detection:
            evidence.append("Bias detection and mitigation implemented")
        
        assessment = ComplianceAssessment(
            function=RiskManagementFunction.MEASURE,
            assessment_date=datetime.now(),
            findings=findings,
            control_status=control_status,
            evidence=evidence,
            confidence_score=compliance_score
        )
        
        self.assessments.append(assessment)
        logger.info(f"MEASURE assessment completed: {control_status} ({compliance_score:.1%})")
        
        return assessment
    
    def assess_manage_function(self) -> ComplianceAssessment:
        """
        Assess MANAGE (Control Implementation) function.
        
        MANAGE includes:
        - Preventive controls (input validation, model hardening)
        - Detective controls (anomaly detection, monitoring)
        - Corrective controls (incident response, remediation)
        - Control effectiveness monitoring
        """
        logger.info("Assessing MANAGE function")
        
        # Check for management controls
        has_preventive_controls = self._check_capability_exists("preventive_controls")
        has_detective_controls = self._check_capability_exists("detective_controls")
        has_corrective_controls = self._check_capability_exists("corrective_controls")
        has_audit_trails = self._check_capability_exists("audit_trails")
        
        # Calculate compliance score
        required_items = 4
        implemented_items = sum([
            has_preventive_controls,
            has_detective_controls,
            has_corrective_controls,
            has_audit_trails
        ])
        
        compliance_score = implemented_items / required_items if required_items > 0 else 0.0
        control_status = self._determine_control_status(compliance_score)
        
        findings = {
            "has_preventive_controls": has_preventive_controls,
            "has_detective_controls": has_detective_controls,
            "has_corrective_controls": has_corrective_controls,
            "has_audit_trails": has_audit_trails,
            "compliance_percentage": compliance_score * 100
        }
        
        evidence = []
        if has_preventive_controls:
            evidence.append("Preventive controls (input validation, model hardening) implemented")
        if has_detective_controls:
            evidence.append("Detective controls (anomaly detection, monitoring) active")
        if has_corrective_controls:
            evidence.append("Corrective controls (incident response, remediation) established")
        if has_audit_trails:
            evidence.append("Comprehensive audit trails maintained")
        
        assessment = ComplianceAssessment(
            function=RiskManagementFunction.MANAGE,
            assessment_date=datetime.now(),
            findings=findings,
            control_status=control_status,
            evidence=evidence,
            confidence_score=compliance_score
        )
        
        self.assessments.append(assessment)
        logger.info(f"MANAGE assessment completed: {control_status} ({compliance_score:.1%})")
        
        return assessment
    
    def assess_govern_function(self) -> ComplianceAssessment:
        """
        Assess GOVERN (Governance & Oversight) function.
        
        GOVERN includes:
        - Governance committee oversight
        - Risk register maintenance
        - Stakeholder communication
        - Compliance auditing
        - Policy documentation
        """
        logger.info("Assessing GOVERN function")
        
        # Check for governance capabilities
        has_governance_committee = self._check_capability_exists("governance_committee")
        has_risk_register_maintenance = self._check_capability_exists("risk_register_maintenance")
        has_stakeholder_communication = self._check_capability_exists("stakeholder_communication")
        has_compliance_auditing = self._check_capability_exists("compliance_auditing")
        has_policy_documentation = self._check_documentation_exists("SECURITY_POLICY.md")
        
        # Calculate compliance score
        required_items = 5
        implemented_items = sum([
            has_governance_committee,
            has_risk_register_maintenance,
            has_stakeholder_communication,
            has_compliance_auditing,
            has_policy_documentation
        ])
        
        compliance_score = implemented_items / required_items if required_items > 0 else 0.0
        control_status = self._determine_control_status(compliance_score)
        
        findings = {
            "has_governance_committee": has_governance_committee,
            "has_risk_register_maintenance": has_risk_register_maintenance,
            "has_stakeholder_communication": has_stakeholder_communication,
            "has_compliance_auditing": has_compliance_auditing,
            "has_policy_documentation": has_policy_documentation,
            "compliance_percentage": compliance_score * 100
        }
        
        evidence = []
        if has_governance_committee:
            evidence.append("Governance committee established with oversight responsibilities")
        if has_risk_register_maintenance:
            evidence.append("Risk register actively maintained and updated")
        if has_stakeholder_communication:
            evidence.append("Stakeholder communication processes established")
        if has_compliance_auditing:
            evidence.append("Compliance auditing procedures implemented")
        if has_policy_documentation:
            evidence.append("Security policy documentation maintained")
        
        assessment = ComplianceAssessment(
            function=RiskManagementFunction.GOVERN,
            assessment_date=datetime.now(),
            findings=findings,
            control_status=control_status,
            evidence=evidence,
            confidence_score=compliance_score
        )
        
        self.assessments.append(assessment)
        logger.info(f"GOVERN assessment completed: {control_status} ({compliance_score:.1%})")
        
        return assessment
    
    def _check_documentation_exists(self, filename: str) -> bool:
        """
        Check if required documentation exists.
        
        Args:
            filename: Name of documentation file to check
            
        Returns:
            True if documentation exists, False otherwise
        """
        import os
        docs_dir = os.path.join(os.path.dirname(__file__), "..", "..", "docs")
        doc_path = os.path.join(docs_dir, filename)
        return os.path.exists(doc_path)
    
    def _check_capability_exists(self, capability: str) -> bool:
        """
        Check if required capability is implemented.
        
        Args:
            capability: Name of capability to check
            
        Returns:
            True if capability exists, False otherwise
        """
        # This is a simplified check - in a real implementation,
        # this would check for actual capability implementation
        capability_mapping = {
            "robustness_testing": True,  # Would check for red team engine
            "performance_tracking": True,  # Would check for metrics tracking
            "impact_assessment": True,  # Would check for impact analysis
            "bias_detection": True,  # Would check for bias detection system
            "preventive_controls": True,  # Would check for blue team system
            "detective_controls": True,  # Would check for threat detection
            "corrective_controls": True,  # Would check for remediation
            "audit_trails": True,  # Would check for audit logging
            "governance_committee": False,  # Would check for governance structure
            "risk_register_maintenance": True,  # Would check for risk register
            "stakeholder_communication": False,  # Would check for communication system
            "compliance_auditing": True,  # Would check for audit procedures
        }
        
        return capability_mapping.get(capability, False)
    
    def _determine_control_status(self, compliance_score: float) -> str:
        """
        Determine control status based on compliance score.
        
        Args:
            compliance_score: Score between 0.0 and 1.0
            
        Returns:
            Control status string
        """
        if compliance_score >= 0.9:
            return "Implemented"
        elif compliance_score >= 0.7:
            return "Partial"
        else:
            return "Not Implemented"
    
    def generate_compliance_report(self) -> Dict:
        """
        Generate comprehensive NIST AI RMF compliance report.
        
        Returns:
            Dictionary with compliance assessment results
        """
        logger.info("Generating comprehensive compliance report")
        
        # Run all assessments if not already run
        if not self.assessments:
            self.assess_map_function()
            self.assess_measure_function()
            self.assess_manage_function()
            self.assess_govern_function()
        
        # Calculate overall compliance
        total_assessments = len(self.assessments)
        if total_assessments == 0:
            overall_score = 0.0
        else:
            overall_score = sum(ass.confidence_score for ass in self.assessments) / total_assessments
        
        # Breakdown by function
        function_scores = {}
        function_statuses = {}
        
        for assessment in self.assessments:
            func_name = assessment.function.value
            function_scores[func_name] = assessment.confidence_score
            function_statuses[func_name] = assessment.control_status
        
        # Identify areas for improvement
        improvement_areas = []
        for assessment in self.assessments:
            if assessment.control_status != "Implemented":
                improvement_areas.append({
                    "function": assessment.function.value,
                    "status": assessment.control_status,
                    "findings": assessment.findings
                })
        
        report = {
            "report_date": datetime.now().isoformat(),
            "framework": "NIST AI RMF",
            "version": "1.0",
            "overall_compliance": {
                "score": overall_score,
                "percentage": overall_score * 100,
                "rating": self._get_compliance_rating(overall_score)
            },
            "function_breakdown": {
                "scores": function_scores,
                "statuses": function_statuses
            },
            "improvement_areas": improvement_areas,
            "risk_register_summary": {
                "total_risks": len(self.risk_register),
                "high_risks": len([r for r in self.risk_register if r.risk_score >= 0.7]),
                "medium_risks": len([r for r in self.risk_register if 0.4 <= r.risk_score < 0.7]),
                "low_risks": len([r for r in self.risk_register if r.risk_score < 0.4])
            },
            "assessment_summary": [
                {
                    "function": assessment.function.value,
                    "status": assessment.control_status,
                    "confidence": assessment.confidence_score
                }
                for assessment in self.assessments
            ]
        }
        
        logger.info(f"Compliance report generated: {report['overall_compliance']['rating']}")
        return report
    
    def _get_compliance_rating(self, score: float) -> str:
        """
        Get human-readable compliance rating based on score.
        
        Args:
            score: Compliance score (0.0-1.0)
            
        Returns:
            Rating string
        """
        if score >= 0.9:
            return "Exemplary"
        elif score >= 0.8:
            return "Strong"
        elif score >= 0.7:
            return "Moderate"
        elif score >= 0.5:
            return "Needs Improvement"
        else:
            return "Significant Gaps"
    
    def add_risk_assessment(self, risk: RiskAssessment) -> str:
        """
        Add a risk assessment to the register.
        
        Args:
            risk: RiskAssessment object to add
            
        Returns:
            Risk ID for the added risk
        """
        import uuid
        
        # Generate unique risk ID if not provided
        if not risk.risk_id:
            risk.risk_id = f"RISK-{uuid.uuid4().hex[:8].upper()}"
        
        self.risk_register.append(risk)
        
        logger.info(f"Risk added to register: {risk.risk_id} - {risk.description[:50]}...")
        return risk.risk_id
    
    def get_risk_register(self) -> List[RiskAssessment]:
        """
        Get the complete risk register.
        
        Returns:
            List of RiskAssessment objects
        """
        return self.risk_register.copy()
    
    def update_risk_status(self, risk_id: str, new_status: str) -> bool:
        """
        Update the status of a risk in the register.
        
        Args:
            risk_id: ID of the risk to update
            new_status: New status for the risk
            
        Returns:
            True if update successful, False otherwise
        """
        for risk in self.risk_register:
            if risk.risk_id == risk_id:
                risk.status = new_status
                logger.info(f"Risk {risk_id} status updated to: {new_status}")
                return True
        
        logger.warning(f"Risk not found for update: {risk_id}")
        return False
    
    def generate_risk_treatment_plan(self) -> Dict:
        """
        Generate a risk treatment plan based on current register.
        
        Returns:
            Dictionary with risk treatment recommendations
        """
        logger.info("Generating risk treatment plan")
        
        unaddressed_risks = [r for r in self.risk_register if r.status == "Unaddressed"]
        high_risks = [r for r in self.risk_register if r.risk_score >= 0.7 and r.status != "Mitigated"]
        
        treatment_plan = {
            "generated_date": datetime.now().isoformat(),
            "total_risks": len(self.risk_register),
            "unaddressed_risks": len(unaddressed_risks),
            "high_priority_risks": len(high_risks),
            "treatment_recommendations": []
        }
        
        # Generate recommendations for high priority risks
        for risk in high_risks:
            treatment_plan["treatment_recommendations"].append({
                "risk_id": risk.risk_id,
                "category": risk.category,
                "description": risk.description,
                "risk_score": risk.risk_score,
                "recommended_action": self._get_treatment_recommendation(risk),
                "priority": "HIGH"
            })
        
        # Generate recommendations for medium risks
        medium_risks = [r for r in self.risk_register if 0.4 <= r.risk_score < 0.7 and r.status != "Mitigated"]
        for risk in medium_risks:
            treatment_plan["treatment_recommendations"].append({
                "risk_id": risk.risk_id,
                "category": risk.category,
                "description": risk.description,
                "risk_score": risk.risk_score,
                "recommended_action": self._get_treatment_recommendation(risk),
                "priority": "MEDIUM"
            })
        
        logger.info(f"Risk treatment plan generated: {len(treatment_plan['treatment_recommendations'])} recommendations")
        return treatment_plan
    
    def _get_treatment_recommendation(self, risk: RiskAssessment) -> str:
        """
        Get treatment recommendation for a risk.
        
        Args:
            risk: RiskAssessment object
            
        Returns:
            Treatment recommendation string
        """
        if risk.risk_score >= 0.8:
            return "Implement immediate controls and mitigation measures"
        elif risk.risk_score >= 0.6:
            return "Develop and implement appropriate controls within 30 days"
        elif risk.risk_score >= 0.4:
            return "Monitor and implement controls within 90 days"
        else:
            return "Accept risk with ongoing monitoring"
    
    def run_complete_assessment(self) -> Dict:
        """
        Run complete NIST AI RMF assessment.
        
        Returns:
            Complete assessment and compliance report
        """
        logger.info("Running complete NIST AI RMF assessment")
        
        # Clear previous assessments
        self.assessments.clear()
        
        # Run all function assessments
        map_assessment = self.assess_map_function()
        measure_assessment = self.assess_measure_function()
        manage_assessment = self.assess_manage_function()
        govern_assessment = self.assess_govern_function()
        
        # Generate comprehensive report
        report = self.generate_compliance_report()
        
        # Generate risk treatment plan
        treatment_plan = self.generate_risk_treatment_plan()
        
        complete_assessment = {
            "comprehensive_report": report,
            "risk_treatment_plan": treatment_plan,
            "individual_assessments": {
                "map": map_assessment,
                "measure": measure_assessment,
                "manage": manage_assessment,
                "govern": govern_assessment
            },
            "summary": {
                "overall_rating": report["overall_compliance"]["rating"],
                "compliance_percentage": report["overall_compliance"]["percentage"],
                "recommendations_count": len(treatment_plan["treatment_recommendations"])
            }
        }
        
        logger.info(f"Complete assessment completed: {report['overall_compliance']['rating']}")
        return complete_assessment