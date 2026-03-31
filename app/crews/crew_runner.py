"""
Crew Runner — orchestrates the sequential execution of marketing agents.
Mirrors Cassian's crew_runner.py pattern: agents run in sequence, each receiving
the outputs of all prior agents as context.

Execution order (default full run):
  1. Intake Analyst
  2. Behavioral Scientist  }  Phase 2: Research (could run in parallel later)
  3. Psychometrics Expert   }
  4. Competitive Intelligence  }  Phase 3: Audit (could run in parallel later)
  5. Social Strategist         }
  6. Chief Strategist       — Phase 4: Strategy synthesis
  7. Creative Director      — Phase 5: Creative execution
  8. Stakeholder Agent      — Optional, can run standalone

Agents 2+3 and 4+5 are logically parallel but run sequentially for simplicity.
Can be parallelized later with asyncio if needed.
"""
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models import (
    CrewRun, AgentRun, AgentName, RunStatus, Project
)
from app.crews.agents.research_agent import ResearchAgent
from app.crews.agents.intake_analyst import IntakeAnalystAgent
from app.crews.agents.behavioral_scientist import BehavioralScientistAgent
from app.crews.agents.psychometrics_expert import PsychometricsExpertAgent
from app.crews.agents.competitive_intelligence import CompetitiveIntelligenceAgent
from app.crews.agents.social_strategist import SocialStrategistAgent
from app.crews.agents.chief_strategist import ChiefStrategistAgent
from app.crews.agents.creative_director import CreativeDirectorAgent
from app.crews.agents.stakeholder_agent import StakeholderAgent

logger = logging.getLogger("idideration.crew_runner")

# Default full pipeline order
DEFAULT_AGENT_ORDER = [
    AgentName.RESEARCH_AGENT,
    AgentName.INTAKE_ANALYST,
    AgentName.BEHAVIORAL_SCIENTIST,
    AgentName.PSYCHOMETRICS_EXPERT,
    AgentName.COMPETITIVE_INTELLIGENCE,
    AgentName.SOCIAL_STRATEGIST,
    AgentName.CHIEF_STRATEGIST,
    AgentName.CREATIVE_DIRECTOR,
]

AGENT_CLASS_MAP = {
    AgentName.RESEARCH_AGENT: ResearchAgent,
    AgentName.INTAKE_ANALYST: IntakeAnalystAgent,
    AgentName.BEHAVIORAL_SCIENTIST: BehavioralScientistAgent,
    AgentName.PSYCHOMETRICS_EXPERT: PsychometricsExpertAgent,
    AgentName.COMPETITIVE_INTELLIGENCE: CompetitiveIntelligenceAgent,
    AgentName.SOCIAL_STRATEGIST: SocialStrategistAgent,
    AgentName.CHIEF_STRATEGIST: ChiefStrategistAgent,
    AgentName.CREATIVE_DIRECTOR: CreativeDirectorAgent,
    AgentName.STAKEHOLDER_AGENT: StakeholderAgent,
}


def create_crew_run(db: Session, project_id: int, agents: list[AgentName] = None) -> CrewRun:
    """Create a new crew run with agent run records."""
    if agents is None:
        agents = DEFAULT_AGENT_ORDER

    crew_run = CrewRun(
        project_id=project_id,
        status=RunStatus.PENDING,
        agents_to_run=[a.value for a in agents],
    )
    db.add(crew_run)
    db.flush()

    for i, agent_name in enumerate(agents):
        agent_run = AgentRun(
            crew_run_id=crew_run.id,
            agent_name=agent_name,
            sequence_order=i,
            status=RunStatus.PENDING,
        )
        db.add(agent_run)

    db.commit()
    db.refresh(crew_run)
    return crew_run


def execute_crew_run(db: Session, crew_run_id: int):
    """Execute a crew run — runs all agents in sequence, passing outputs forward."""
    crew_run = db.query(CrewRun).filter(CrewRun.id == crew_run_id).first()
    if not crew_run:
        raise ValueError(f"CrewRun {crew_run_id} not found")

    crew_run.status = RunStatus.RUNNING
    crew_run.started_at = datetime.now(timezone.utc)
    db.commit()

    project = db.query(Project).filter(Project.id == crew_run.project_id).first()
    prior_outputs: dict[str, dict] = {}

    try:
        for agent_run in crew_run.agent_runs:
            agent_name = agent_run.agent_name
            agent_class = AGENT_CLASS_MAP.get(agent_name)

            if not agent_class:
                logger.error(f"No agent class for {agent_name}")
                agent_run.status = RunStatus.FAILED
                agent_run.error_message = f"No agent class registered for {agent_name.value}"
                db.commit()
                continue

            logger.info(f"Running agent: {agent_name.value} (#{agent_run.sequence_order + 1})")

            agent = agent_class(
                db=db,
                project_id=crew_run.project_id,
                agent_run=agent_run,
            )

            output = agent.run(prior_outputs)
            prior_outputs[agent_name.value] = output

            logger.info(
                f"Agent {agent_name.value} completed. "
                f"Tokens: {agent_run.total_tokens}, Cost: ${agent_run.cost_usd:.4f}"
            )

        crew_run.status = RunStatus.COMPLETED
        crew_run.completed_at = datetime.now(timezone.utc)
        db.commit()

        logger.info(f"Crew run {crew_run_id} completed successfully.")
        return prior_outputs

    except Exception as e:
        logger.error(f"Crew run {crew_run_id} failed: {e}")
        crew_run.status = RunStatus.FAILED
        crew_run.error_message = str(e)
        crew_run.completed_at = datetime.now(timezone.utc)
        db.commit()
        raise


def rerun_single_agent(db: Session, crew_run_id: int, agent_name: AgentName, guidance: str | None = None):
    """Re-execute a single agent within an existing crew run."""
    crew_run = db.query(CrewRun).filter(CrewRun.id == crew_run_id).first()
    if not crew_run:
        raise ValueError(f"CrewRun {crew_run_id} not found")

    # Find the target agent run
    target = None
    for ar in crew_run.agent_runs:
        if ar.agent_name == agent_name:
            target = ar
            break
    if not target:
        raise ValueError(f"Agent {agent_name.value} not found in CrewRun {crew_run_id}")

    # Reset the agent run
    target.status = RunStatus.PENDING
    target.output_json = None
    target.output_raw = None
    target.error_message = None
    target.input_prompt = None
    target.input_tokens = 0
    target.output_tokens = 0
    target.total_tokens = 0
    target.cost_usd = 0.0
    target.started_at = None
    target.completed_at = None
    target.model_used = None
    target.rerun_guidance = guidance  # Store one-time guidance (cleared on next rerun)

    crew_run.status = RunStatus.RUNNING
    db.commit()

    # Build prior_outputs from earlier completed agents in this run
    prior_outputs: dict[str, dict] = {}
    for ar in crew_run.agent_runs:
        if ar.sequence_order < target.sequence_order and ar.status == RunStatus.COMPLETED and ar.output_json:
            prior_outputs[ar.agent_name.value] = ar.output_json

    try:
        agent_class = AGENT_CLASS_MAP.get(agent_name)
        if not agent_class:
            raise ValueError(f"No agent class registered for {agent_name.value}")

        logger.info(f"Rerunning agent: {agent_name.value}" + (f" with guidance" if guidance else ""))
        agent = agent_class(db=db, project_id=crew_run.project_id, agent_run=target)
        agent.run(prior_outputs)
        logger.info(f"Agent {agent_name.value} rerun completed. Tokens: {target.total_tokens}, Cost: ${target.cost_usd:.4f}")

    except Exception as e:
        logger.error(f"Agent {agent_name.value} rerun failed: {e}")

    # Reconcile crew run status
    all_statuses = [ar.status for ar in crew_run.agent_runs]
    if any(s == RunStatus.FAILED for s in all_statuses):
        crew_run.status = RunStatus.FAILED
    elif any(s == RunStatus.PENDING for s in all_statuses):
        # Downstream agents still pending — don't mark completed
        crew_run.status = RunStatus.FAILED
        crew_run.error_message = "Pipeline incomplete — use Continue Pipeline to run remaining agents"
    else:
        crew_run.status = RunStatus.COMPLETED
    crew_run.completed_at = datetime.now(timezone.utc)
    db.commit()


def continue_crew_run(db: Session, crew_run_id: int):
    """Resume a crew run from the first pending agent, using existing completed outputs."""
    crew_run = db.query(CrewRun).filter(CrewRun.id == crew_run_id).first()
    if not crew_run:
        raise ValueError(f"CrewRun {crew_run_id} not found")

    crew_run.status = RunStatus.RUNNING
    crew_run.error_message = None
    crew_run.completed_at = None
    db.commit()

    # Build prior_outputs from all completed agents so far
    prior_outputs: dict[str, dict] = {}
    for ar in sorted(crew_run.agent_runs, key=lambda x: x.sequence_order):
        if ar.status == RunStatus.COMPLETED and ar.output_json:
            prior_outputs[ar.agent_name.value] = ar.output_json

    try:
        for ar in sorted(crew_run.agent_runs, key=lambda x: x.sequence_order):
            if ar.status != RunStatus.PENDING:
                continue  # Skip completed/failed agents

            agent_class = AGENT_CLASS_MAP.get(ar.agent_name)
            if not agent_class:
                logger.error(f"No agent class for {ar.agent_name}")
                ar.status = RunStatus.FAILED
                ar.error_message = f"No agent class registered for {ar.agent_name.value}"
                db.commit()
                continue

            logger.info(f"Continuing from agent: {ar.agent_name.value} (#{ar.sequence_order + 1})")
            agent = agent_class(db=db, project_id=crew_run.project_id, agent_run=ar)
            output = agent.run(prior_outputs)
            prior_outputs[ar.agent_name.value] = output
            logger.info(f"Agent {ar.agent_name.value} completed. Tokens: {ar.total_tokens}, Cost: ${ar.cost_usd:.4f}")

        crew_run.status = RunStatus.COMPLETED
        crew_run.completed_at = datetime.now(timezone.utc)
        db.commit()
        logger.info(f"Crew run {crew_run_id} continued and completed.")

    except Exception as e:
        logger.error(f"Crew run {crew_run_id} continue failed: {e}")
        crew_run.status = RunStatus.FAILED
        crew_run.error_message = str(e)
        crew_run.completed_at = datetime.now(timezone.utc)
        db.commit()
        raise


def get_crew_run_status(db: Session, crew_run_id: int) -> dict:
    """Get current status of a crew run and all its agent runs."""
    crew_run = db.query(CrewRun).filter(CrewRun.id == crew_run_id).first()
    if not crew_run:
        return None

    total_cost = sum(ar.cost_usd or 0 for ar in crew_run.agent_runs)
    total_tokens = sum(ar.total_tokens or 0 for ar in crew_run.agent_runs)

    return {
        "id": crew_run.id,
        "status": crew_run.status.value,
        "started_at": crew_run.started_at.isoformat() if crew_run.started_at else None,
        "completed_at": crew_run.completed_at.isoformat() if crew_run.completed_at else None,
        "error_message": crew_run.error_message,
        "total_cost_usd": round(total_cost, 4),
        "total_tokens": total_tokens,
        "agents": [
            {
                "name": ar.agent_name.value,
                "sequence": ar.sequence_order,
                "status": ar.status.value,
                "model": ar.model_used,
                "tokens": ar.total_tokens or 0,
                "cost_usd": ar.cost_usd or 0,
                "started_at": ar.started_at.isoformat() if ar.started_at else None,
                "completed_at": ar.completed_at.isoformat() if ar.completed_at else None,
                "error": ar.error_message,
            }
            for ar in crew_run.agent_runs
        ],
    }
