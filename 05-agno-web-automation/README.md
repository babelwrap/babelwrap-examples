# Agno Web Automation — Every Interaction Type

An Agno-powered agent demonstrates BabelWrap's full interaction capabilities: login with authentication, hover to reveal hidden content, keyboard presses, form filling, checkbox toggling, and file upload — all on the-internet.herokuapp.com.

## Setup

```bash
pip install -r requirements.txt
```

Set your API keys:

```bash
export BABELWRAP_API_KEY="your-babelwrap-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

## Run

```bash
python web_automation.py
```

Or pass a custom task:

```bash
python web_automation.py "Go to the-internet.herokuapp.com/login and log in with tomsmith / SuperSecretPassword!"
```

## What It Demonstrates

The agent visits the-internet.herokuapp.com and exercises every BabelWrap interaction type:

1. **Authentication** — Log in with credentials on `/login`, verify success
2. **Hover** — Hover over user avatars on `/hovers` to reveal hidden profile links
3. **Keyboard** — Press Enter, Tab, and Escape on `/key_presses`
4. **Checkboxes** — Toggle checkboxes on `/checkboxes`
5. **File Upload** — Upload a test file on `/upload`
6. **Dropdown** — Select an option from a dropdown on `/dropdown`
