# Caliper v2 Installation Guide

This guide provides detailed instructions for installing Caliper v2 on different operating systems.

## System Requirements

- **Python**: 3.11-3.13 (3.11 recommended)
- **Operating System**: Windows, macOS, or Linux
- **Disk Space**: At least 1GB for the repository and dependencies
- **Memory**: At least 4GB RAM recommended

## Installation Steps

### 1. Install Python

#### Windows

1. Download Python 3.11 from the [official website](https://www.python.org/downloads/)
2. Run the installer and check "Add Python to PATH"
3. Verify installation by opening a PowerShell window and running:
   ```powershell
   py -3.11 --version
   ```

#### macOS

1. Install Python 3.11 using Homebrew:
   ```bash
   brew install python@3.11
   ```
2. Verify installation:
   ```bash
   python3.11 --version
   ```

#### Linux

1. Install Python 3.11 using your distribution's package manager:
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3.11 python3.11-venv python3.11-dev
   
   # Fedora
   sudo dnf install python3.11 python3.11-devel
   ```
2. Verify installation:
   ```bash
   python3.11 --version
   ```

### 2. Install pipx

pipx is used to install Poetry in an isolated environment.

#### Windows (PowerShell)

```powershell
py -3.11 -m pip install --user pipx
py -3.11 -m pipx ensurepath
# Close and reopen PowerShell
```

#### macOS/Linux

```bash
python3.11 -m pip install --user pipx
pipx ensurepath
exec "$SHELL" -l
```

### 3. Install Poetry

Poetry is used for dependency management and packaging.

```bash
pipx install poetry
```

Verify installation:

```bash
poetry --version
```

### 4. Clone the Repository

#### Using Git

```bash
git clone https://github.com/jasonfescivil/caliper_v2.git
cd caliper_v2
```

#### Without Git

1. Download the repository as a ZIP file
2. Extract the ZIP file
3. Navigate to the extracted directory

### 5. Set Up the Project Environment

#### Create a Virtual Environment

```bash
poetry env use 3.11
```

#### Install Dependencies

```bash
poetry install --with llamaindex
```

This will install all required dependencies, including the LlamaIndex ecosystem.

### 6. Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your API keys:
   - `LLAMA_CLOUD_API_KEY`: Required for cloud retrieval
   - `COHERE_API_KEY`: Optional, for reranking
   - Provider keys as needed:
     - `OPENAI_API_KEY`
     - `ANTHROPIC_API_KEY`
     - `GEMINI_API_KEY`
     - `XAI_API_KEY`

3. For cloud retrieval, also set these index IDs:
   - `FEDERAL_BASE_ID`, `FEDERAL_SUMMARY_ID`
   - `STATE_BASE_ID`, `STATE_SUMMARY_ID`
   - `DESIGN_BASE_ID`, `DESIGN_SUMMARY_ID`

### 7. Verify Installation

Run the doctor command to check your environment:

```bash
poetry run caliper_v2 doctor
```

## Optional: Install Pre-commit Hooks

If you plan to contribute to the project, you can install pre-commit hooks:

```bash
pipx install pre-commit
pre-commit install
```

## Troubleshooting

### Poetry Installation Issues

If you encounter issues with Poetry:

1. Ensure you have the correct Python version:
   ```bash
   python --version
   ```

2. Try reinstalling Poetry:
   ```bash
   pipx uninstall poetry
   pipx install poetry
   ```

### Dependency Installation Issues

If you encounter issues installing dependencies:

1. Update Poetry:
   ```bash
   pipx upgrade poetry
   ```

2. Clear Poetry's cache:
   ```bash
   poetry cache clear --all pypi
   ```

3. Try installing with verbose output:
   ```bash
   poetry install -v --with llamaindex
   ```

### API Key Issues

If you encounter issues with API keys:

1. Ensure your `.env` file is in the correct location (project root)
2. Check that the API keys are correctly formatted (no extra spaces or quotes)
3. Run the doctor command to verify:
   ```bash
   poetry run caliper_v2 doctor
   ```

## Next Steps

After installation, refer to the [Quick Start Guide](quick-start-guide.md) to begin using Caliper v2.