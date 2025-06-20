# Metatesters 🧪

A LangGraph multi-agent system designed to **jailbreak and analyze other LangGraph systems** through automated testing and vulnerability assessment.

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.4.5+-green.svg)](https://github.com/langchain-ai/langgraph)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🎯 Overview

Metatesters is an innovative security testing framework that uses AI agents to automatically analyze, test, and find vulnerabilities in LangGraph-based agentic systems. It employs a multi-stage approach:

1. **Static Graph Analysis** - Analyzes the structure and components of target LangGraph systems
2. **Dynamic Testing Team Generation** - Creates specialized AI tester personas based on the analysis
3. **Automated Test Case Generation** - Generates comprehensive test cases including edge cases and fault injection
4. **Vulnerability Assessment** - Executes tests and identifies potential security issues and bugs

## 🏗️ Architecture

### Core Components

- **Graph Analysis Agent** (`app/agents/graph_analysis/`) - Performs static analysis of target LangGraph systems
- **Testing Team Agent** (`app/agents/testing_team/`) - Generates specialized AI testers and test cases
- **Arithmetic Sample Agent** (`app/agents/arithmetic_sample/`) - Example target system for demonstration
- **Web UI** (`app/ui/`) - Gradio-based interface for interacting with the system
- **Database Service** (`app/service/`) - SQLite-based storage for test results and tester profiles

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- OpenAI API key or Azure OpenAI access
- UV package manager (recommended) or pip

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/marcos-rg/metatesters.git
   cd metatesters
   ```

2. **Install dependencies:**
   ```bash
   # Using UV (recommended)
   uv sync
   
   # Or using pip
   pip install -e .
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Run the application:**
   ```bash
   # Start the web interface
   python main.py
   
   # Or run LangGraph development server
   make test
   ```

## 🖥️ Usage

### Web Interface

1. **Launch the application:**
   ```bash
   python main.py
   ```

2. **Step 1: Analyze Graph**
   - The system will analyze a sample arithmetic LangGraph system
   - View the generated graph visualization and structure analysis

3. **Step 2: Generate Testing Team**
   - Provide feedback to guide tester creation
   - The system generates specialized AI tester personas
   - Each tester focuses on specific vulnerability types

4. **Step 3: Review Test Results**
   - View generated test cases
   - Analyze identified vulnerabilities
   - Export results for further analysis

### API Usage

```python
from app.agents import graph_analysis_app, testing_team_app

# Analyze a target graph
result = graph_analysis_app.invoke({
    "user_description": "Description of target system",
    "valid_input": {"messages": [...]},
    "graph_before_compile": target_graph
})

# Generate testing team
testers = testing_team_app.invoke({
    "graph_description": result["graph_description"],
    "graph_history_sample": result["history_to_show"],
    "human_analyst_feedback": "Focus on security vulnerabilities",
    "max_analysts": 3,
    "min_test_cases": 6
})
```

## 🧪 Testing Capabilities

### Automated Tester Personas

The system generates specialized AI testers, including:

- **Security Tester** - Focuses on authentication, authorization, and data leakage
- **Edge Case Tester** - Tests boundary conditions and unusual inputs
- **Fault Injection Tester** - Simulates system failures and error conditions
- **Performance Tester** - Identifies scalability and performance issues
- **Logic Tester** - Tests business logic and workflow correctness

## 📁 Project Structure

```
metatesters/
├── app/
│   ├── agents/                 # Multi-agent system components
│   │   ├── arithmetic_sample/  # Example target system
│   │   ├── graph_analysis/     # Static graph analysis agent
│   │   ├── testing_team/       # Test generation agent
│   │   ├── config/            # Configuration management
│   │   └── utils/             # Shared utilities
│   ├── config/                # Application configuration
│   ├── service/               # Database and external services
│   └── ui/                    # Gradio web interface
├── main.py                    # Application entry point
├── langgraph.json            # LangGraph configuration
├── pyproject.toml            # Project dependencies
└── Makefile                  # Development commands
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Azure OpenAI Configuration (alternative)
AZURE_OPENAI_API_KEY=your_azure_key
AZURE_OPENAI_ENDPOINT=your_azure_endpoint

# Database
SQLITE_PATH=./metatesters.db

# Logging
LOG_LEVEL=INFO
```

### Model Configuration

Configure models in `app/agents/config/graph_config.py`:

```python
# Supported models
- azure_openai/gpt-4.1
- openai/gpt-4
- openai/gpt-3.5-turbo
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

1. **Fork and clone the repository**
2. **Create a virtual environment:**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. **Install development dependencies:**
   ```bash
   uv sync --dev
   ```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- [LangGraph](https://github.com/langchain-ai/langgraph) - Framework for building stateful, multi-actor applications
- [LangChain](https://github.com/langchain-ai/langchain) - Building applications with LLMs
- [Gradio](https://github.com/gradio-app/gradio) - Web UI framework

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/marcos-rg/metatesters/issues)
- **Discussions**: [GitHub Discussions](https://github.com/marcos-rg/metatesters/discussions)
- **Email**: marcosreyesgarces@gmail.com

## 🙏 Acknowledgments

- LangChain team for the amazing LangGraph framework
- The open-source community for inspiration and tools
- Security researchers working on AI safety

---

**⚠️ Disclaimer**: This tool is designed for legitimate security testing and research purposes. Users are responsible for ensuring they have proper authorization before testing any systems they do not own.