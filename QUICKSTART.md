# ConversationIQ Quick Start Guide

Get up and running with ConversationIQ in 5 minutes!

## Step 1: Installation (1 minute)

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize the system
python conversationiq.py init
```

## Step 2: Create Agents (1 minute)

Generate agents automatically for your use case:

```bash
# For customer support evaluation
python conversationiq.py agent generate "customer support for a SaaS product" --count 5

# List created agents and copy their IDs
python conversationiq.py agent list
```

Copy the agent IDs for later use (you'll need at least 3).

## Step 3: Configure API (1 minute)

Add your chat API configuration:

```bash
python conversationiq.py api add "My Chat API" "https://api.example.com/v1/chat/completions"
# Enter your API key when prompted

# Test the connection
python conversationiq.py api list
# Copy the config ID
```

## Step 4: Create a Test (1 minute)

Use the example questions provided:

```bash
python conversationiq.py test create \
  "My First Test" \
  "Testing customer support responses" \
  "You are a helpful customer support agent. Be friendly and concise." \
  --api-config-id <YOUR_API_CONFIG_ID> \
  --agent-ids <AGENT_ID_1>,<AGENT_ID_2>,<AGENT_ID_3> \
  --questions-file examples/example_questions.json

# List tests and copy the test ID
python conversationiq.py test list
```

## Step 5: Run Test & View Results (1 minute)

```bash
# Run the test
python conversationiq.py test run <YOUR_TEST_ID>

# View results
python conversationiq.py results summary <YOUR_TEST_ID>

# Export detailed report
python conversationiq.py results export <YOUR_TEST_ID> --format report
```

## What's Next?

### Customize Your Agents

Create agents with specific perspectives:

```bash
python conversationiq.py agent create \
  "Skeptical Customer" \
  "A cautious user who questions everything and looks for red flags"
```

### Add More Questions

Create your own questions file:

```json
{
  "questions": [
    {"text": "Your question here", "category": "general", "priority": 1}
  ]
}
```

### Analyze Results

Export in different formats:

```bash
# JSON for programmatic analysis
python conversationiq.py results export <TEST_ID> --format json

# CSV for spreadsheet analysis
python conversationiq.py results export <TEST_ID> --format csv

# Full report for stakeholders
python conversationiq.py results export <TEST_ID> --format report
```

## Common Use Cases

### Customer Support Evaluation
```bash
python conversationiq.py agent generate "customer support" --count 5
# Creates: Angry Customer, Patient Learner, Tech Savvy User, etc.
```

### Technical Documentation Testing
```bash
python conversationiq.py agent generate "technical documentation for developers" --count 4
# Creates: Junior Dev, Senior Architect, DevOps Engineer, etc.
```

### Sales Conversation Analysis
```bash
python conversationiq.py agent generate "sales prospects" --count 5
# Creates: Budget-Conscious CFO, Innovation-Seeking CTO, etc.
```

## Troubleshooting

**Problem**: API test fails
- **Solution**: Check your endpoint URL and API key

**Problem**: Test runs but no evaluations
- **Solution**: Ensure agents were created and IDs are correct

**Problem**: TinyTroupe not available
- **Solution**: `pip install tinytroupe` (optional, will fall back to rule-based evaluation)

## Need Help?

- Check the full [README.md](README.md) for detailed documentation
- Review [examples/](examples/) for sample files
- Open an issue on GitHub

Happy evaluating! 🚀
