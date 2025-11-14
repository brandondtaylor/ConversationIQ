# ConversationIQ

> AI-powered chat response evaluation platform using Microsoft TinyTroupe virtual agents

ConversationIQ allows you to evaluate chat API responses from multiple perspectives using virtual agent personas. Each agent provides qualitative feedback on responses, helping you understand how different user types perceive your chat AI.

## Features

- 🤖 **Virtual Agent Management**: Create and manage diverse agent personas with unique backgrounds and perspectives
- 🔌 **Chat API Integration**: Connect to any chat API endpoint for evaluation
- 📊 **Multi-Agent Evaluation**: Get feedback from multiple personas on each response
- 🎯 **Three Evaluation Modes**: Single-Agent, Focus Group (with discussion), or Both
- 👥 **Focus Group Analysis**: AI agents discuss responses in real-time with detailed insights
- 📁 **Flexible Question Loading**: Import questions from JSON, CSV, or text files, or use the visual editor
- 📈 **Comprehensive Reporting**: Aggregate feedback, identify patterns, export results
- 🎭 **TinyTroupe Integration**: Leverage Microsoft's TinyTroupe for sophisticated persona simulation
- 💻 **CLI Interface**: Easy-to-use command-line interface for all operations
- 🌐 **Full-Stack Web UI**: Modern React interface with real-time monitoring and analytics
- 📊 **Real-time Charts**: Live monitoring of test execution with interactive visualizations
- 🔄 **WebSocket Support**: Real-time updates during test execution with automatic reconnection

## Installation

### Prerequisites

- Python 3.10 or higher
- pip

### Setup

1. **Clone the repository**:
```bash
git clone <repository-url>
cd ConversationIQ
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Initialize the database**:
```bash
python conversationiq.py init
```

This will create the database and necessary data directories.

## Quick Start

**New to ConversationIQ?** Try the **Web UI** for a modern, intuitive experience!

```bash
# Start the Web UI (see WEB_UI_README.md for details)
./start-backend.sh    # Terminal 1
./start-frontend.sh   # Terminal 2
# Then visit http://localhost:5173
```

**Prefer the CLI?** Continue with the steps below:

### 1. Create Virtual Agents

You can create agents manually or generate them automatically.

**Manual creation**:
```bash
python conversationiq.py agent create "Tech Expert" "A software engineer who values technical accuracy"
```

**Auto-generate agents for a task**:
```bash
python conversationiq.py agent generate "customer support for a SaaS product" --count 5
```

**List all agents**:
```bash
python conversationiq.py agent list
```

### 2. Configure Chat API

Add your chat API endpoint and key:

```bash
python conversationiq.py api add "My Chat API" "https://api.example.com/chat"
# You'll be prompted to enter the API key securely
```

Test the connection:
```bash
python conversationiq.py api test <config-id>
```

### 3. Prepare Questions

Create a questions file in JSON, CSV, or plain text format.

**Example JSON format** (`questions.json`):
```json
{
  "questions": [
    {
      "text": "How do I reset my password?",
      "category": "account",
      "priority": 1
    },
    {
      "text": "What are your business hours?",
      "category": "general",
      "priority": 2
    }
  ]
}
```

**Example CSV format** (`questions.csv`):
```csv
text,category,priority
How do I reset my password?,account,1
What are your business hours?,general,2
```

**Example text format** (`questions.txt`):
```
How do I reset my password?

What are your business hours?

Can I get a refund?
```

### 4. Create and Run a Test

**Create a test**:
```bash
python conversationiq.py test create \
  "Customer Support Evaluation" \
  "Evaluate customer support responses" \
  "You are a helpful customer support agent for our SaaS platform" \
  --api-config-id <api-config-id> \
  --agent-ids <agent-id-1>,<agent-id-2>,<agent-id-3> \
  --questions-file questions.json
```

**List tests**:
```bash
python conversationiq.py test list
```

**Run the test**:
```bash
python conversationiq.py test run <test-id>
```

The test will:
1. Send each question to your chat API
2. Have each agent evaluate the response
3. Store all evaluations in the database

### 5. View Results

**Show summary**:
```bash
python conversationiq.py results summary <test-id>
```

**Export results**:
```bash
# Export as JSON
python conversationiq.py results export <test-id> --format json

# Export as CSV
python conversationiq.py results export <test-id> --format csv

# Export detailed report
python conversationiq.py results export <test-id> --format report
```

## Architecture

```
conversationiq/
├── src/
│   ├── api/              # Chat API integration
│   ├── agents/           # Agent management & TinyTroupe
│   ├── tests/            # Test configuration & execution
│   ├── evaluation/       # Results aggregation & formatting
│   ├── storage/          # Database models & schemas
│   └── ui/               # CLI interface
├── data/
│   ├── agents/           # Saved agent configurations
│   ├── tests/            # Test configurations
│   └── results/          # Exported results
└── conversationiq.py     # Main entry point
```

## Key Concepts

### Virtual Agents

Virtual agents are personas that evaluate chat responses from specific perspectives. Each agent has:
- **Demographics**: Age, occupation, education level
- **Personality Traits**: Analytical, skeptical, creative, etc.
- **Expertise Areas**: Technology, business, education, etc.
- **Evaluation Criteria**: Weights for different aspects (accuracy, clarity, tone)

### Task Context

The task context provides agents with background information about what the chat AI should accomplish. This helps agents evaluate responses appropriately.

### Evaluations

Each evaluation includes:
- **Likes**: What the agent appreciated about the response
- **Dislikes**: Concerns or issues identified
- **Suggestions**: Recommendations for improvement
- **Rating**: Numeric score (1-10)
- **Agent Perspective**: The agent's unique viewpoint

### TinyTroupe Integration

When TinyTroupe is available, agents use sophisticated persona simulation for evaluation. Otherwise, the system falls back to rule-based evaluation.

## Advanced Usage

### Adding Questions to Existing Test

```bash
python conversationiq.py test add-questions <test-id> new-questions.json
```

### Filtering Tests by Status

```bash
python conversationiq.py test list --status completed
```

### Custom Agent Creation

For more control, create agents programmatically:

```python
from src.agents.manager import AgentManager
from src.storage.schemas import AgentCreate

agent = AgentCreate(
    name="Senior Developer",
    description="A senior software engineer with 10 years of experience",
    demographics={
        "age": 38,
        "occupation": "Senior Software Engineer",
        "education": "Master's in Computer Science"
    },
    personality_traits=["Detail-oriented", "Direct", "Efficient"],
    expertise_areas=["Software Engineering", "API Design", "Documentation"],
    evaluation_criteria_weights={
        "technical_accuracy": 0.35,
        "clarity": 0.25,
        "completeness": 0.25,
        "code_quality": 0.15
    }
)

with AgentManager() as manager:
    created_agent = manager.create(agent)
    print(f"Created agent: {created_agent.id}")
```

### Programmatic Test Execution

```python
from src.tests.executor import TestExecutor
from src.evaluation.evaluator import EvaluationAnalyzer

# Run test
executor = TestExecutor()
result = executor.run_test(test_id)

# Analyze results
analyzer = EvaluationAnalyzer()
analysis = analyzer.analyze_test(test_id)

print(f"Average rating: {analysis['overall']['rating_stats']['average']}")
```

## API Configuration Examples

### OpenAI-compatible API

```bash
python conversationiq.py api add "OpenAI GPT-4" "https://api.openai.com/v1/chat/completions"
```

### Anthropic Claude API

```bash
python conversationiq.py api add "Claude" "https://api.anthropic.com/v1/messages"
```

### Custom API

For custom APIs, ensure your endpoint accepts requests in this format:
```json
{
  "messages": [
    {"role": "system", "content": "context"},
    {"role": "user", "content": "question"}
  ]
}
```

And returns responses that include the text in a standard field like `content`, `text`, or `response`.

## Question File Formats

### JSON

```json
{
  "questions": [
    {
      "text": "Question text",
      "category": "optional category",
      "priority": 1,
      "expected_tone": "friendly",
      "metadata": {
        "custom_field": "value"
      }
    }
  ]
}
```

### CSV

Minimum required column: `text` or `question`

Optional columns: `category`, `priority`, `expected_tone`

### Plain Text

Questions separated by double newlines:

```
First question here

Second question here

Third question here
```

## Database Migration

If you're upgrading from a previous version, run the migration script to update your database schema:

```bash
python scripts/migrate_database.py
```

The migration script handles:
- Renaming `metadata` to `meta_data` column (avoids SQLAlchemy conflicts)
- Adding `response_time` column to evaluations
- Adding `evaluation_mode` column to test configs
- Creating any missing tables

For a custom database URL:
```bash
python scripts/migrate_database.py postgresql://user:pass@localhost/dbname
```

## Troubleshooting

### TinyTroupe Not Available

If TinyTroupe is not installed, the system will use rule-based evaluation. To use full TinyTroupe features:

```bash
pip install tinytroupe
```

### API Connection Failures

- Verify your endpoint URL is correct
- Check that your API key is valid
- Ensure your API returns responses in a compatible format

### Database Issues

Reset the database:
```bash
rm data/conversationiq.db
python conversationiq.py init
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/
flake8 src/
```

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Add your license here]

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

Built with ❤️ using Microsoft TinyTroupe and modern Python tooling
