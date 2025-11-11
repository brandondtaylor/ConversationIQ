"""
Command-line interface for ConversationIQ.
"""
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
from pathlib import Path
from typing import Optional, List
import json

from ..storage.database import init_database
from ..storage.schemas import (
    AgentCreate, APIConfigCreate, TestConfigCreate,
    QuestionCreate, TestStatus
)
from ..agents.manager import AgentManager
from ..agents.generator import AgentGenerator
from ..agents.personas import PersonaFactory
from ..api.config import APIConfigManager
from ..tests.config import TestConfigManager
from ..tests.questions import QuestionLoader
from ..tests.executor import TestExecutor
from ..evaluation.evaluator import EvaluationAnalyzer

app = typer.Typer(help="ConversationIQ - AI Chat Response Evaluation Platform")
console = Console()


# ============================================================================
# INITIALIZATION
# ============================================================================

@app.command()
def init(
    db_path: str = typer.Option(
        "./data/conversationiq.db",
        help="Database file path"
    )
):
    """Initialize the database and create required directories."""
    console.print("[bold blue]Initializing ConversationIQ...[/bold blue]")

    try:
        # Initialize database
        init_database(f"sqlite:///{db_path}")
        console.print(f"✓ Database initialized at {db_path}", style="green")

        # Create directories
        Path("data/agents").mkdir(parents=True, exist_ok=True)
        Path("data/tests").mkdir(parents=True, exist_ok=True)
        Path("data/results").mkdir(parents=True, exist_ok=True)
        console.print("✓ Data directories created", style="green")

        console.print("\n[bold green]Initialization complete![/bold green]")
        console.print("Run 'conversationiq --help' to see available commands.")

    except Exception as e:
        console.print(f"[bold red]Error during initialization: {e}[/bold red]")
        raise typer.Exit(1)


# ============================================================================
# AGENT MANAGEMENT
# ============================================================================

agent_app = typer.Typer(help="Manage virtual agents")
app.add_typer(agent_app, name="agent")


@agent_app.command("create")
def create_agent(
    name: str = typer.Argument(..., help="Agent name"),
    description: str = typer.Argument(..., help="Agent description"),
    interactive: bool = typer.Option(True, help="Interactive mode for additional details")
):
    """Create a new virtual agent."""
    console.print(f"[bold blue]Creating agent: {name}[/bold blue]")

    demographics = {}
    personality_traits = []
    expertise_areas = []

    if interactive:
        # Gather additional details interactively
        demographics["age"] = typer.prompt("Age", type=int, default=35)
        demographics["occupation"] = typer.prompt("Occupation", default="Professional")
        demographics["education"] = typer.prompt("Education level", default="Bachelor's")

        traits_input = typer.prompt(
            "Personality traits (comma-separated)",
            default="Analytical, Thorough"
        )
        personality_traits = [t.strip() for t in traits_input.split(",")]

        expertise_input = typer.prompt(
            "Expertise areas (comma-separated)",
            default="General"
        )
        expertise_areas = [e.strip() for e in expertise_input.split(",")]

    agent = AgentCreate(
        name=name,
        description=description,
        demographics=demographics,
        personality_traits=personality_traits,
        expertise_areas=expertise_areas
    )

    with AgentManager() as manager:
        created_agent = manager.create(agent)
        console.print(f"✓ Agent created with ID: {created_agent.id}", style="green")


@agent_app.command("list")
def list_agents():
    """List all agents."""
    with AgentManager() as manager:
        agents = manager.list()

        if not agents:
            console.print("No agents found. Create one with 'conversationiq agent create'")
            return

        table = Table(title="Virtual Agents")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Occupation", style="green")
        table.add_column("Expertise", style="yellow")

        for agent in agents:
            occupation = agent.demographics.get("occupation", "N/A")
            expertise = ", ".join(agent.expertise_areas[:2]) if agent.expertise_areas else "N/A"
            table.add_row(agent.id[:8], agent.name, occupation, expertise)

        console.print(table)


@agent_app.command("generate")
def generate_agents(
    task: str = typer.Argument(..., help="Task description"),
    count: int = typer.Option(3, help="Number of agents to generate")
):
    """Generate agents for a specific task using templates."""
    console.print(f"[bold blue]Generating {count} agents for task: {task}[/bold blue]")

    generator = AgentGenerator()
    agents = generator.generate_agents_for_task(task, num_agents=count)

    with AgentManager() as manager:
        created_ids = []
        for agent in agents:
            created_agent = manager.create(agent)
            created_ids.append(created_agent.id)
            console.print(f"✓ Created agent: {created_agent.name}", style="green")

        console.print(f"\n[bold green]Generated {len(created_ids)} agents[/bold green]")


@agent_app.command("delete")
def delete_agent(agent_id: str = typer.Argument(..., help="Agent ID")):
    """Delete an agent."""
    with AgentManager() as manager:
        if manager.delete(agent_id):
            console.print(f"✓ Agent {agent_id} deleted", style="green")
        else:
            console.print(f"Agent {agent_id} not found", style="red")


# ============================================================================
# API CONFIGURATION
# ============================================================================

api_app = typer.Typer(help="Manage chat API configurations")
app.add_typer(api_app, name="api")


@api_app.command("add")
def add_api_config(
    name: str = typer.Argument(..., help="Configuration name"),
    endpoint: str = typer.Argument(..., help="API endpoint URL"),
    api_key: str = typer.Option(..., prompt=True, hide_input=True, help="API key")
):
    """Add a new API configuration."""
    console.print(f"[bold blue]Adding API configuration: {name}[/bold blue]")

    config = APIConfigCreate(
        name=name,
        endpoint=endpoint,
        api_key=api_key
    )

    with APIConfigManager() as manager:
        created_config = manager.create(config)
        console.print(f"✓ API configuration created with ID: {created_config.id}", style="green")

        # Test connection
        console.print("Testing connection...")
        success, message = manager.test_config(created_config.id)

        if success:
            console.print(f"✓ {message}", style="green")
        else:
            console.print(f"⚠ Connection test failed: {message}", style="yellow")


@api_app.command("list")
def list_api_configs():
    """List all API configurations."""
    with APIConfigManager() as manager:
        configs = manager.list()

        if not configs:
            console.print("No API configurations found.")
            return

        table = Table(title="API Configurations")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Endpoint", style="green")

        for config in configs:
            table.add_row(config.id[:8], config.name, config.endpoint[:50])

        console.print(table)


@api_app.command("test")
def test_api_config(config_id: str = typer.Argument(..., help="Configuration ID")):
    """Test an API configuration."""
    with APIConfigManager() as manager:
        console.print("Testing API connection...")
        success, message = manager.test_config(config_id)

        if success:
            console.print(f"✓ {message}", style="green")
        else:
            console.print(f"✗ {message}", style="red")


# ============================================================================
# TEST MANAGEMENT
# ============================================================================

test_app = typer.Typer(help="Manage and run tests")
app.add_typer(test_app, name="test")


@test_app.command("create")
def create_test(
    name: str = typer.Argument(..., help="Test name"),
    description: str = typer.Argument(..., help="Test description"),
    task_context: str = typer.Argument(..., help="Task context for agents"),
    api_config_id: str = typer.Option(..., help="API configuration ID"),
    agent_ids: str = typer.Option(..., help="Comma-separated agent IDs"),
    questions_file: Optional[str] = typer.Option(None, help="Questions file (JSON/CSV)")
):
    """Create a new test configuration."""
    console.print(f"[bold blue]Creating test: {name}[/bold blue]")

    agent_id_list = [aid.strip() for aid in agent_ids.split(",")]

    # Load questions if file provided
    questions = []
    if questions_file:
        console.print(f"Loading questions from {questions_file}...")
        questions = QuestionLoader.auto_detect_format(questions_file)
        console.print(f"✓ Loaded {len(questions)} questions", style="green")

    test_config = TestConfigCreate(
        name=name,
        description=description,
        task_context=task_context,
        api_config_id=api_config_id,
        agent_ids=agent_id_list,
        questions=questions
    )

    with TestConfigManager() as manager:
        created_test = manager.create(test_config)
        console.print(f"✓ Test created with ID: {created_test.id}", style="green")
        console.print(f"Status: {created_test.status.value}")


@test_app.command("list")
def list_tests(
    status: Optional[str] = typer.Option(None, help="Filter by status")
):
    """List all tests."""
    with TestConfigManager() as manager:
        test_status = TestStatus(status) if status else None
        tests = manager.list(status=test_status)

        if not tests:
            console.print("No tests found.")
            return

        table = Table(title="Tests")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Status", style="green")
        table.add_column("Agents", style="yellow")
        table.add_column("Created", style="blue")

        for test in tests:
            table.add_row(
                test.id[:8],
                test.name,
                test.status.value,
                str(len(test.agent_ids)),
                test.created_at.strftime("%Y-%m-%d")
            )

        console.print(table)


@test_app.command("run")
def run_test(test_id: str = typer.Argument(..., help="Test ID")):
    """Run a test."""
    console.print(f"[bold blue]Running test: {test_id}[/bold blue]\n")

    executor = TestExecutor()

    def progress_callback(message: str):
        console.print(f"  {message}")

    try:
        result = executor.run_test(test_id, progress_callback=progress_callback)

        console.print("\n[bold green]Test completed successfully![/bold green]")
        console.print(f"Questions processed: {result['questions_processed']}")
        console.print(f"Total evaluations: {result['total_evaluations']}")

    except Exception as e:
        console.print(f"\n[bold red]Test failed: {e}[/bold red]")
        raise typer.Exit(1)


@test_app.command("add-questions")
def add_questions_to_test(
    test_id: str = typer.Argument(..., help="Test ID"),
    questions_file: str = typer.Argument(..., help="Questions file (JSON/CSV/TXT)")
):
    """Add questions to an existing test."""
    console.print(f"Loading questions from {questions_file}...")

    questions = QuestionLoader.auto_detect_format(questions_file)
    console.print(f"✓ Loaded {len(questions)} questions", style="green")

    with TestConfigManager() as manager:
        if manager.add_questions(test_id, questions):
            console.print(f"✓ Added {len(questions)} questions to test", style="green")
        else:
            console.print("Test not found", style="red")


# ============================================================================
# RESULTS & ANALYSIS
# ============================================================================

results_app = typer.Typer(help="View and analyze test results")
app.add_typer(results_app, name="results")


@results_app.command("summary")
def show_summary(test_id: str = typer.Argument(..., help="Test ID")):
    """Show test results summary."""
    analyzer = EvaluationAnalyzer()
    summary = analyzer.get_summary(test_id)

    console.print(Panel(summary, title="Test Results Summary", border_style="blue"))


@results_app.command("export")
def export_results(
    test_id: str = typer.Argument(..., help="Test ID"),
    format: str = typer.Option("json", help="Format: json, csv, txt, report"),
    output: Optional[str] = typer.Option(None, help="Output file path")
):
    """Export test results."""
    analyzer = EvaluationAnalyzer()

    console.print(f"Exporting results as {format}...")

    try:
        output_file = analyzer.export_results(test_id, format, output)
        console.print(f"✓ Results exported to: {output_file}", style="green")
    except Exception as e:
        console.print(f"Export failed: {e}", style="red")
        raise typer.Exit(1)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main CLI entry point."""
    app()


if __name__ == "__main__":
    main()
