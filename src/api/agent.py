"""Agent routes for AI operations."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.dependencies import get_current_user, require_analyst
from src.core.logging import get_logger
from src.database import get_db
from src.models.database import User
from src.models.schemas import (
    AgentActionRequest,
    AgentActionResponse,
    AgentRequest,
    AgentResponse,
    ScanRequest,
    ScanResponse,
    ThreatQueryRequest,
    ThreatQueryResponse,
)
from src.services import ChromaService, DockerSandboxService, OllamaService
from src.tools import ProposeActionTool, QueryThreatIntelTool, ScanEnvironmentTool

router = APIRouter(prefix="/agent", tags=["Agent"])
logger = get_logger(__name__)


@router.post("/run", response_model=AgentResponse)
async def run_agent(
    request: AgentRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Run the ReAct agent with the given instruction.

    This is the main endpoint for autonomous agent execution.
    The agent will:
    1. Use ReAct loop to reason about the task
    2. Execute appropriate tools (scan_environment, query_threat_intel, propose_action)
    3. Return summary, steps, proposals, evidence, and confidence score

    Args:
        request: Agent request with instruction, scan_duration, and mode

    Returns:
        Agent response with execution results
    """
    logger.info(
        "Agent run requested",
        user=current_user.username,
        instruction=request.instruction[:100],
        mode=request.mode,
    )

    try:
        # Import agent module
        from src.agent.react_agent import run_agent as execute_agent

        # Execute the agent
        result = await execute_agent(request)

        logger.info(
            "Agent execution completed",
            user=current_user.username,
            steps=len(result.steps),
            confidence=result.confidence,
        )

        return result

    except Exception as e:
        logger.error("Agent execution failed", user=current_user.username, error=str(e))
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")


@router.post("/scan", response_model=ScanResponse, dependencies=[Depends(require_analyst)])
async def scan_environment(
    scan_request: ScanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Scan the environment for security issues."""
    logger.info("Scan requested", user=current_user.username, scan_type=scan_request.scan_type)

    tool = ScanEnvironmentTool()
    result = await tool.execute(
        scan_type=scan_request.scan_type,
        target=scan_request.target,
        **scan_request.options,
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Scan failed"))

    # Store scan result in database
    from src.database.repository import BaseRepository
    from src.models.database import EnvironmentScan

    repo = BaseRepository(EnvironmentScan, db)
    scan_record = repo.create(
        scan_type=scan_request.scan_type,
        target=scan_request.target,
        findings=str(result.get("findings", [])),
        vulnerabilities_count=result.get("vulnerabilities_count", 0),
        risk_score=result.get("risk_score"),
    )

    return scan_record


@router.post("/threat-intel", response_model=ThreatQueryResponse)
async def query_threat_intelligence(
    query_request: ThreatQueryRequest,
    current_user: User = Depends(get_current_user),
):
    """Query threat intelligence database."""
    logger.info("Threat intel query", user=current_user.username, query=query_request.query)

    chroma_service = ChromaService()
    tool = QueryThreatIntelTool(chroma_service)

    result = await tool.execute(
        query=query_request.query,
        sources=query_request.sources,
        limit=query_request.limit,
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Query failed"))

    return result


@router.post(
    "/propose-action", response_model=AgentActionResponse, dependencies=[Depends(require_analyst)]
)
async def propose_action(
    action_request: AgentActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Propose an action for approval."""
    logger.info(
        "Action proposed",
        user=current_user.username,
        action_type=action_request.action_type,
    )

    from src.services import TelegramService

    telegram_service = TelegramService()
    tool = ProposeActionTool(telegram_service)

    result = await tool.execute(
        db=db,
        action_type=action_request.action_type,
        description=action_request.description,
        proposed_code=action_request.proposed_code,
        reasoning=action_request.reasoning,
        risk_level=action_request.risk_level,
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to propose action"))

    # Get the created action
    from src.database.repository import BaseRepository
    from src.models.database import AgentAction

    repo = BaseRepository(AgentAction, db)
    action = repo.get(result["action_id"])

    return action


@router.post("/execute-code", dependencies=[Depends(require_analyst)])
async def execute_code(
    code: str,
    language: str = "python",
    current_user: User = Depends(get_current_user),
):
    """Execute code in a sandboxed environment."""
    logger.info("Code execution requested", user=current_user.username, language=language)

    sandbox = DockerSandboxService()
    result = await sandbox.execute_code(code=code, language=language)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Execution failed"))

    return result


@router.post("/analyze")
async def analyze_with_llm(
    prompt: str,
    context: str = "",
    current_user: User = Depends(get_current_user),
):
    """Analyze a security issue using the LLM."""
    logger.info("LLM analysis requested", user=current_user.username)

    ollama_service = OllamaService()

    system_prompt = """You are Otis, an advanced cybersecurity AI agent. Your role is to:
1. Analyze security threats and vulnerabilities
2. Provide actionable recommendations
3. Reference MITRE ATT&CK, NIST, and OWASP best practices
4. Think step-by-step using the ReAct framework
5. Always prioritize security and safety

When analyzing, follow this pattern:
- Thought: Understand the problem
- Action: What tool or analysis to use
- Observation: What you learned
- Answer: Your recommendation
"""

    full_prompt = f"{context}\n\n{prompt}" if context else prompt

    response = await ollama_service.generate(
        prompt=full_prompt,
        system=system_prompt,
        temperature=0.7,
    )

    return {"analysis": response}


@router.get("/tools/propose_action/status")
async def get_proposal_status(
    current_user: User = Depends(get_current_user),
):
    """Get status of pending high-risk action proposals."""
    logger.info("Proposal status requested", user=current_user.username)

    from src.security.policy import ApprovalGate

    approval_gate = ApprovalGate()
    pending = approval_gate.list_pending()

    # Filter for high-risk proposals
    high_risk_pending = [p for p in pending if p.get("risk_level") in ["high", "critical"]]

    return {
        "pending_count": len(pending),
        "high_risk_count": len(high_risk_pending),
        "proposals": high_risk_pending,
    }
