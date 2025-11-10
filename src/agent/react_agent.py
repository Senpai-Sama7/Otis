"""ReAct agent implementation with PolicyEngine and Planner/Executor pattern."""

import asyncio
import json
from typing import Any

from src.agent.model import OllamaModel
from src.core.logging import get_logger
from src.models.schemas import AgentRequest, AgentResponse
from src.reasoning.planner import Planner
from src.reasoning.query_router import QueryRouter
from src.security.policy_engine import PolicyDecision, PolicyEngine

logger = get_logger(__name__)


class ReactAgent:
    """
    ReAct (Reasoning + Acting) agent with hard-coded policy enforcement.

    Architecture:
    - PolicyEngine: Hard-coded security rules (no prompt injection possible)
    - Planner: Generates multi-step plans for complex tasks
    - Executor: Executes plan steps with policy validation
    
    Upgraded from 2 iterations to 10-15 for true autonomy.
    """

    def __init__(
        self,
        model: OllamaModel,
        tools: dict[str, Any],
        user: Any,
        request: AgentRequest,
        max_iterations: int = 10,
        max_exec_time: int = 300,
    ):
        self.model = model
        self.tools = tools
        self.user = user
        self.request = request
        self.max_iterations = max_iterations
        self.max_exec_time = max_exec_time
        
        # Hard-coded policy enforcement
        self.policy_engine = PolicyEngine(user=user, request=request)
        
        # Initialize memory system (FIXED - was None)
        from src.memory.memory_system import MemorySystem
        from src.services.chroma import ChromaService
        
        chroma_service = ChromaService()
        self.memory_system = MemorySystem(
            vector_store=chroma_service,
            persistence_path="./data/memory",
            working_memory_capacity=10,
        )
        
        # Planner for multi-step autonomy
        self.planner = Planner(ollama_client=model, available_tools=tools)
        
        # Query router for intelligent strategy selection
        self.query_router = QueryRouter(ollama_client=model)

    async def run(self, request: AgentRequest) -> AgentResponse:
        """
        Execute the ReAct loop with integrated reasoning engine.

        Args:
            request: Agent request with instruction and configuration

        Returns:
            Agent response with summary, steps, proposals, evidence, and confidence
        """
        logger.info(
            "Starting ReAct agent with integrated ReasoningEngine",
            instruction=request.instruction,
            mode=request.mode,
            user_role=self.user.role,
        )

        steps = []
        proposals = []
        evidence = []
        start_time = asyncio.get_event_loop().time()

        try:
            # Initialize memory system
            await self.memory_system.initialize()
            
            # Step 1: Get context from memory
            memory_context = await self.memory_system.get_context_for_reasoning(
                query=request.instruction,
                max_items=10,
            )
            
            # Step 2: Use ReasoningEngine with memory context
            from src.reasoning.reasoning_engine import ReasoningContext, ReasoningEngine
            
            reasoning_engine = ReasoningEngine(
                ollama_client=self.model,
                memory_system=self.memory_system,  # FIXED - was None
            )
            
            # Create context with relevant memories
            context = ReasoningContext(
                query=request.instruction,
                relevant_memories=memory_context.get("relevant_knowledge", []),
            )
            reasoning_result = await reasoning_engine.reason(context)
            
            logger.info(
                "reasoning_engine.completed",
                strategy=reasoning_result.strategy_used.value,
                confidence=reasoning_result.confidence,
            )
            
            # Step 2: If reasoning suggests actions, generate plan
            if reasoning_result.confidence > 0.5:
                plan = await self.planner.create_plan(request.instruction)
                logger.info("planner.plan_generated", steps=len(plan.steps))
            else:
                # Low confidence - return reasoning result directly
                return AgentResponse(
                    summary=reasoning_result.response,
                    steps=[{"reasoning": reasoning_result.response}],
                    proposals=None,
                    evidence=None,
                    confidence=reasoning_result.confidence,
                )

            # Step 3: Execute plan with policy enforcement
            for step_idx, plan_step in enumerate(plan.steps):
                if step_idx >= self.max_iterations:
                    logger.warning("agent.max_iterations_reached")
                    break

                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed > self.max_exec_time:
                    logger.warning("agent.timeout", elapsed=elapsed)
                    break

                tool_name = plan_step.get("tool")
                tool_params = plan_step.get("params", {})
                reasoning = plan_step.get("reasoning", "")

                step = {
                    "iteration": step_idx + 1,
                    "thought": reasoning,
                    "action": tool_name,
                    "action_input": tool_params,
                }

                # POLICY ENFORCEMENT POINT
                decision = self.policy_engine.validate(tool_name, tool_params)
                step["policy_decision"] = decision.value

                observation = await self._execute_with_policy(
                    tool_name, tool_params, decision, proposals, evidence
                )
                
                step["observation"] = observation
                steps.append(step)

            # Generate summary
            summary = self._generate_summary(steps, proposals, evidence)
            confidence = self._calculate_confidence(steps, evidence, proposals)

            # Store interaction in memory
            await self.memory_system.add_interaction(
                query=request.instruction,
                response=summary,
                context={"steps": len(steps), "confidence": confidence},
                metadata={"user_role": self.user.role, "mode": request.mode},
            )
            
            # Save memory to disk
            await self.memory_system.save_persistent_memories()

            logger.info(
                "ReAct agent completed",
                steps_count=len(steps),
                proposals_count=len(proposals),
                confidence=confidence,
            )

            return AgentResponse(
                summary=summary,
                steps=steps,
                proposals=proposals if proposals else None,
                evidence=evidence if evidence else None,
                confidence=confidence,
            )

        except Exception as e:
            logger.error("ReAct agent execution failed", error=str(e))
            return AgentResponse(
                summary=f"Agent execution failed: {str(e)}",
                steps=steps,
                proposals=None,
                evidence=None,
                confidence=0.0,
            )

    async def _execute_with_policy(
        self,
        tool_name: str,
        tool_params: dict[str, Any],
        decision: PolicyDecision,
        proposals: list,
        evidence: list,
    ) -> str:
        """Execute tool with policy enforcement."""
        if decision == PolicyDecision.PERMIT:
            # Policy passes - execute tool
            tool = self.tools.get(tool_name)
            if not tool:
                return f"Tool {tool_name} not found"
            
            observation_data = await tool.execute(**tool_params)
            
            # Collect evidence
            if tool_name in ["scan_environment", "query_threat_intel"]:
                if observation_data.get("success"):
                    evidence.append({"source": tool_name, "data": observation_data})
            
            return json.dumps(observation_data)

        elif decision == PolicyDecision.REQUIRES_APPROVAL:
            # Policy requires approval - force propose_action
            proposal_tool = self.tools.get("propose_action")
            if not proposal_tool:
                return "Approval required but propose_action tool not available"
            
            rationale = f"Policy requires approval for {tool_name} with params {tool_params}"
            
            proposal_data = await proposal_tool.execute(
                code=f"{tool_name}({json.dumps(tool_params)})",
                risk="high",
                rationale=rationale,
            )
            
            proposals.append(proposal_data)
            return f"Action {tool_name} requires human approval. Proposal sent. Awaiting feedback."

        elif decision == PolicyDecision.DENY:
            # Policy denies
            reason = self.policy_engine.get_denial_reason(tool_name, tool_params)
            return f"Action {tool_name} was denied by security policy: {reason}"

        return "Unknown policy decision"

    async def _execute_simple_query(self, query: str) -> str:
        """Execute simple query directly."""
        # For simple queries, use query_threat_intel if available
        tool = self.tools.get("query_threat_intel")
        if tool:
            result = await tool.execute(query=query, k=3)
            return json.dumps(result)
        return "No suitable tool for simple query"

    def _format_tool_descriptions(self) -> str:
        """Format tool descriptions for the prompt."""
        descriptions = []
        for name, tool in self.tools.items():
            params = tool.get_parameters()
            descriptions.append(f"- {name}: {tool.description}")
            descriptions.append(f"  Parameters: {json.dumps(params, indent=2)}")
        return "\n".join(descriptions)

    def _build_prompt(self, instruction: str, mode: str, tool_descriptions: str) -> str:
        """Build the initial ReAct prompt."""
        return f"""You are a cybersecurity AI agent using the ReAct (Reasoning + Acting) framework.

Your task: {instruction}

Mode: {mode} (passive = read-only operations, active = may include network changes)

Available tools:
{tool_descriptions}

IMPORTANT RULES:
1. Always start with passive, low-risk operations (scan_environment, query_threat_intel)
2. For high-risk actions, use propose_action which requires human approval
3. Format your response as:
   Thought: <your reasoning>
   Action: <tool_name>
   Action Input: <valid JSON parameters>

4. If no action needed, just provide:
   Thought: <final reasoning>
   Answer: <final answer>

Begin! Analyze the task and decide on your first action.

Thought:"""

    def _parse_response(self, response: str) -> tuple[str, str | None, dict[str, Any]]:
        """
        Parse model response into thought, action, and action input.

        Returns:
            Tuple of (thought, action_name, action_input_dict)
        """
        thought = ""
        action = None
        action_input = {}

        lines = response.strip().split("\n")
        current_section = None

        for line in lines:
            line = line.strip()
            if line.startswith("Thought:"):
                current_section = "thought"
                thought = line[8:].strip()
            elif line.startswith("Action:"):
                current_section = "action"
                action = line[7:].strip()
            elif line.startswith("Action Input:"):
                current_section = "action_input"
                input_text = line[13:].strip()
                try:
                    action_input = json.loads(input_text)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse action input", input_text=input_text)
                    action_input = {}
            elif line.startswith("Answer:"):
                # Final answer - no action needed
                current_section = "answer"
                action = None
            elif current_section == "thought":
                thought += " " + line
            elif current_section == "action_input":
                try:
                    action_input = json.loads(line)
                except json.JSONDecodeError:
                    pass

        return thought.strip(), action, action_input

    def _generate_summary(
        self, steps: list[dict], proposals: list[dict], evidence: list[dict]
    ) -> str:
        """Generate a summary of the agent execution."""
        summary_parts = [f"Completed {len(steps)} reasoning steps."]

        if evidence:
            summary_parts.append(f"Gathered {len(evidence)} pieces of evidence.")

        if proposals:
            summary_parts.append(f"Generated {len(proposals)} action proposals requiring approval.")

        # Extract key findings from evidence
        findings = []
        for ev in evidence:
            if ev["source"] == "scan_environment":
                data = ev["data"]
                if "findings" in data:
                    findings.append(f"Found {len(data['findings'])} items in scan")

        if findings:
            summary_parts.extend(findings)

        return " ".join(summary_parts)

    def _calculate_confidence(
        self, steps: list[dict], evidence: list[dict], proposals: list[dict]
    ) -> float:
        """
        Calculate confidence score based on execution quality.

        Factors:
        - Completed steps
        - Evidence collected
        - Successful observations
        """
        if not steps:
            return 0.0

        # Base confidence from completed steps
        confidence = min(len(steps) / self.max_iterations, 1.0) * 0.4

        # Bonus for evidence collected
        if evidence:
            confidence += min(len(evidence) / 2, 0.3)

        # Bonus for successful observations
        successful_steps = sum(
            1 for step in steps if step.get("observation", {}).get("success", False)
        )
        confidence += (successful_steps / len(steps)) * 0.3

        return min(confidence, 1.0)


async def run_agent(req: AgentRequest, user: Any) -> AgentResponse:
    """
    Convenience function to run the ReAct agent with PolicyEngine.

    Args:
        req: Agent request with instruction and settings
        user: Authenticated user for policy enforcement

    Returns:
        Agent response with results
    """
    # Import tools dynamically to avoid circular imports
    from src.services.chroma import ChromaService
    from src.services.telegram import TelegramService
    from src.tools.propose_action import ProposeActionTool
    from src.tools.query_threat_intel import QueryThreatIntelTool
    from src.tools.scan_environment import ScanEnvironmentTool

    # Initialize services
    chroma_service = ChromaService()
    telegram_service = TelegramService()

    # Initialize tools
    tools = {
        "scan_environment": ScanEnvironmentTool(),
        "query_threat_intel": QueryThreatIntelTool(chroma_service),
        "propose_action": ProposeActionTool(telegram_service),
    }

    # Create model and agent with user context
    model = OllamaModel()
    agent = ReactAgent(
        model=model,
        tools=tools,
        user=user,
        request=req,
        max_iterations=10,
        max_exec_time=300,
    )

    try:
        return await agent.run(req)
    finally:
        await model.close()
