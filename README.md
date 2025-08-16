# Local Agent System 🤖

A production-ready, autonomous multi-agent AI system for code operations using local LLMs via Ollama.

## Overview

Local Agent System enables you to deploy multiple specialized AI agents that can autonomously analyze, write, modify, and test code. All processing happens locally using Ollama models, ensuring privacy, cost-effectiveness, and offline capability.

### Key Features

- **Multi-Agent Pipelines**: Chain specialized agents for complex workflows
- **Local Execution**: Run everything on your machine with Ollama
- **Autonomous Operation**: Agents can execute real code and make decisions
- **Extensible Architecture**: Easy to add new agent types and capabilities
- **Production Ready**: Comprehensive testing, logging, and error handling

## Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **Ollama** installed and running ([Download Ollama](https://ollama.ai))
3. At least one Ollama model pulled:
   ```bash
   ollama pull qwen2.5-coder:14b-instruct-q4_K_M
   ```

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/local-agent.git
   cd local-agent
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements-minimal.txt  # For basic functionality
   # OR
   pip install -r requirements.txt  # For all features including dev tools
   ```

### Basic Usage

#### Single Agent Execution

```python
from agent_system import LocalAgent

# Create an agent
agent = LocalAgent()

# Run a task
result = agent.run("Write a Python function to calculate fibonacci numbers")

if result["success"]:
    print(result["output"])
```

#### Multi-Agent Pipeline

```python
from multi_agent import MultiAgentSystem

# Create the system
system = MultiAgentSystem()

# Define a pipeline
pipeline = [
    {
        "agent": "analyzer",
        "role": "code analyzer",
        "task": "Find all Python files lacking docstrings"
    },
    {
        "agent": "documenter",
        "role": "documentation writer",
        "task": "Add docstrings to the first file found",
        "use_previous": True  # Use output from analyzer
    },
    {
        "agent": "tester",
        "role": "test writer",
        "task": "Write tests for the documented file",
        "use_previous": True
    }
]

# Execute pipeline
results = system.run_pipeline(pipeline)

# Save results
import json
with open("pipeline_results.json", "w") as f:
    json.dump(results, f, indent=2)
```

## Architecture

### Component Overview

```
local-agent/
├── agent_system.py       # Single agent implementation
├── multi_agent.py        # Multi-agent orchestration
├── agents/
│   └── base_agent.py    # Base agent class (WIP)
├── tests/               # Comprehensive test suite
├── docs/                # Documentation
└── config.yaml          # Configuration (coming soon)
```

### Agent Types (Planned)

- **CodeAnalyzer**: Analyzes code structure, finds issues
- **Documenter**: Adds documentation and comments
- **TestWriter**: Generates unit and integration tests
- **BugFixer**: Identifies and fixes bugs
- **Refactorer**: Improves code structure and performance
- **Migrator**: Converts code between frameworks/languages

## Advanced Usage

### Custom Model Selection

```python
# Use a specific model for an agent
agent = LocalAgent(model="ollama/deepseek-coder:33b")

# Different models for different agents
system = MultiAgentSystem()
system.model = "ollama/qwen2.5-coder:32b"  # For coding tasks
```

### Error Handling

```python
result = agent.run("complex task")

if not result["success"]:
    print(f"Error: {result['error']}")
    # Implement retry logic or fallback
```

### Pipeline with Error Recovery

```python
pipeline = [
    {
        "agent": "risky_agent",
        "task": "potentially failing task",
        "continue_on_error": True  # Continue pipeline even if this fails
    },
    {
        "agent": "cleanup_agent",
        "task": "cleanup and recovery"
    }
]
```

## Development

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
pytest tests/test_agent_system.py -v

# Run only unit tests
pytest -m unit
```

### Code Quality

```bash
# Format code
make format

# Run linters
make lint

# Clean build artifacts
make clean
```

### Project Structure

- `requirements.txt` - All dependencies
- `requirements-minimal.txt` - Core dependencies only
- `requirements-dev.txt` - Development tools
- `pytest.ini` - Test configuration
- `Makefile` - Common development commands

## Configuration (Coming Soon)

Future versions will support configuration via `config.yaml`:

```yaml
models:
  default: "ollama/qwen2.5-coder:14b"
  reasoning: "ollama/deepseek-r1:8b"
  
agents:
  analyzer:
    model: "${models.reasoning}"
    timeout: 120
    retry_attempts: 3
```

## Roadmap

- [x] Basic agent implementation
- [x] Multi-agent pipelines
- [x] Comprehensive testing
- [ ] Configuration management
- [ ] Async task execution
- [ ] REST API endpoints
- [ ] Web UI dashboard
- [ ] Agent marketplace
- [ ] Distributed execution

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Ensure all tests pass (`make test`)
5. Format your code (`make format`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Security Considerations

- **Local Execution**: All LLM processing happens on your machine
- **No Data Transmission**: No code or data is sent to external services
- **Sandboxing**: Agents execute in controlled environments (planned)
- **Input Validation**: All inputs are validated before execution (coming soon)

## Troubleshooting

### Common Issues

1. **Ollama Connection Error**
   ```bash
   # Ensure Ollama is running
   ollama serve
   ```

2. **Model Not Found**
   ```bash
   # Pull the required model
   ollama pull qwen2.5-coder:14b-instruct-q4_K_M
   ```

3. **Import Errors**
   ```bash
   # Ensure you're in the virtual environment
   source venv/bin/activate
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Built with [Open Interpreter](https://github.com/KillianLucas/open-interpreter)
- Powered by [Ollama](https://ollama.ai)
- Inspired by AutoGPT and LangChain

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/local-agent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/local-agent/discussions)
- **Documentation**: [Full Docs](./docs/)

---

**Note**: This project is under active development. APIs may change between versions.