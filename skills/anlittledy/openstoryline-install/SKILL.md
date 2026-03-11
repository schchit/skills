---
name: openstoryline-install
description: Use this skill when the user asks to install, set up, start, verify, repair, or troubleshoot OpenStoryline on the current machine. This includes requests such as "install OpenStoryline", "set up OpenStoryline", "start OpenStoryline", "fix my OpenStoryline installation", as well as Chinese requests like “安装 OpenStoryline”, “配置 OpenStoryline”, “启动 OpenStoryline”, “把 OpenStoryline 跑起来”, “修复 OpenStoryline 安装问题”, or “排查 OpenStoryline 启动失败”.
---

# OpenStoryline Installation Skill

You help the user install, configure, start, verify, and repair OpenStoryline on the current machine.

Your goal is not to describe the project in general terms. Your goal is to get the user to a working state where OpenStoryline can actually run and complete a minimal first task.

## Goal

A successful outcome means most of the following are true:

1. The official OpenStoryline repository is present locally.
2. The required environment has been created.
3. Resources and Python dependencies have been installed.
4. `config.toml` has been configured as needed.
5. the MCP server can start.
6. the CLI or Web interface can start.
7. the user can perform a minimal first-run verification.

## When to use this skill

Use this skill when the user wants to:

- install OpenStoryline
- set up OpenStoryline on this machine
- start OpenStoryline for the first time
- verify whether OpenStoryline is installed correctly
- fix an OpenStoryline installation or startup issue
- use the Docker-based setup instead of source installation

## When not to use this skill

Do not use this skill when:

- the user only wants a general introduction to OpenStoryline
- OpenStoryline is already installed and the user wants to edit a video
- the task is about using OpenStoryline rather than installing it
- the user is asking about editing workflows, prompts, or media preparation

In those cases, prefer the usage skill instead.

## Core rules

- Always prefer the official repository and official README flow.
- Do not invent new installation paths when the README already provides one.
- Detect the environment first, then choose the installation path.
- Validate each major step before moving on.
- If OpenStoryline already appears to be installed, do not reinstall it blindly.
- If a step fails, stop and fix that exact issue before continuing.
- Prefer local-only startup by default.
- Do not expose the service to the local network unless the user explicitly wants mobile/LAN access.
- If the user mainly wants the fastest trial path, Docker is a valid alternative.


## Installation flow

### 1. Get the source code

First, ask the user which directory they want to install OpenStoryline in.
If the repository is not present locally, clone the official repository:
```bash
git clone https://github.com/FireRedTeam/FireRed-OpenStoryline.git
cd FireRed-OpenStoryline
```

- 后续命令中的 `<repo-root>` 指向 OpenStoryline 仓库根目录，例如：

  ```bash
  /Users/yourname/Desktop/code/Openstoryline/FireRed-Openstoryline
  ```

  所有命令都默认在这个目录下执行

### 2. Create and activate the environment

Prefer Conda and Python 3.11.

If a usable environment already exists, verify it before creating a new one.

```bash
conda create -n storyline python=3.11
conda activate storyline
```

### 3. Install dependencies

Choose the path based on platform:

- macOS / Linux: prefer the automatic installation path first

```
sh build_env.sh
```

If the automatic path fails or is unavailable, fall back to the manual resource-download path described in the official README.

- Windows: follow the manual resource-download path
  - Step 1: Create a new directory under the project root directory `.storyline`。

  - Step 2: Download and Extract:
    *   [Download Models (models.zip)](https://image-url-2-feature-1251524319.cos.ap-shanghai.myqcloud.com/openstoryline/models.zip) -> Extract to the `.storyline` directory.

    *   [Download Resources (resource.zip)](https://image-url-2-feature-1251524319.cos.ap-shanghai.myqcloud.com/openstoryline/resource.zip) -> Extract to the `resource` directory.
  - Step 3:  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

### 4. Configure `config.toml`

#### Required configuration
Before you begin editing, the following 6 fields must have values; otherwise, the model call will fail. You must first ask the user for the specific values ​​of these fields, and then modify them using a script:

- `[llm].model`
- `[llm].base_url`
- `[llm].api_key`
- `[vlm].model`
- `[vlm].base_url`
- `[vlm].api_key`

Directly available commands (executed in the repository root directory, using .venv as an example):

```bash
cd <repo-root> && source .venv/bin/activate && python scripts/update_config.py --config ./config.toml --set llm.model=REPLACE_WITH_REAL_MODEL
cd <repo-root> && source .venv/bin/activate && python scripts/update_config.py --config ./config.toml --set llm.base_url=REPLACE_WITH_REAL_URL
cd <repo-root> && source .venv/bin/activate && python scripts/update_config.py --config ./config.toml --set llm.api_key=sk-REPLACE_WITH_REAL_KEY

cd <repo-root> && source .venv/bin/activate && python scripts/update_config.py --config ./config.toml --set vlm.model=REPLACE_WITH_REAL_MODEL
cd <repo-root> && source .venv/bin/activate && python scripts/update_config.py --config ./config.toml --set vlm.base_url=REPLACE_WITH_REAL_URL
cd <repo-root> && source .venv/bin/activate && python scripts/update_config.py --config ./config.toml --set vlm.api_key=sk-REPLACE_WITH_REAL_KEY
```

### 5. Start the MCP server

#### MacOS or Linux

```bash
PYTHONPATH=src python -m open_storyline.mcp.server
MCP_PID=$!
```

#### Windows
```
$env:PYTHONPATH="src"; python -m open_storyline.mcp.server
```

This may take some time. When you see the following content, it means that the server has started successfully.
```
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
```

### 6. Start an interaction interface in another terminal

In the new terminal, first go to the repository root and activate the same environment again.

- Method 1: Command Line Interface

  ```bash
  python cli.py
  ```

  When you see the following content, it means that OpenStoryline has started successfully.
  ```
  Smart Editing Agent v 1.0.0
  Please describe your editing needs, type /exit to exit.
  You:
  ```

- Method 2: Web Interface

  ```bash
  uvicorn agent_fastapi:app --host 127.0.0.1 --port 8005
  ```

  When you see the following content, it means that OpenStoryline has started successfully.
  ```
  INFO:     Started server process [PID]
  INFO:     Waiting for application startup.
  INFO:     Application startup complete.
  INFO:     Uvicorn running on http://127.0.0.1:8005 (Press CTRL+C to quit)
  ```

If the user explicitly wants phone access over the local network, explain that LAN exposure has security implications and should only be used on trusted networks.

### 7. Verify success

Do not stop at “the install command finished”.

A real success state should include most of the following:

- the MCP server starts without an immediate fatal error
- the CLI or Web interface starts successfully
- a minimal first-run check can be performed

## Failure handling

When something fails:

1. identify exactly which step failed
2. summarize the meaning of the error in plain language
3. fix only the current blocker first
4. resume from the nearest valid checkpoint

Do not stack multiple speculative fixes at once unless the failure is obviously multi-causal.

## Completion behavior

After installation succeeds:

- tell the user what is now available
- tell the user how to launch OpenStoryline again later
- give the user one minimal next step
- if the user wants to actually make or edit a video, transition to the usage skill