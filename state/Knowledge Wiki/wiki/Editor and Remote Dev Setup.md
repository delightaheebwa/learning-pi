<!-- provenance: status=verified | source=legacy | verified-by=fact-check-agent | date=2026-10-26 -->

# Editor & Remote Dev Setup

> Your editor is your co-pilot. Configure it once to stay out of your way.

## The Five-Layer Editor Stack

```
5. Remote Development — SSH into GPU boxes, cloud VMs
4. Terminal Integration — Run scripts, debug, monitor GPU
3. AI-Specific Settings — Auto-format, type checking, rulers
2. Extensions — Python, Jupyter, Pylance, GitLens, Remote SSH
1. Base Editor — VS Code (free, extensible, universal)
```

## Essential VS Code Extensions for AI

| Extension | Why |
|-----------|-----|
| Python | Language support, virtual env detection, run/debug |
| Pylance | Fast type checking, autocomplete, import resolution |
| Jupyter | Run notebooks inside VS Code, variable explorer |
| GitLens | Inline git blame, see who changed what |
| Remote SSH | Open remote GPU box folder as if it were local |
| Debugpy | Step-through Python debugging |
| Black Formatter | Auto-format on save |
| Ruff | Fast linting, catches common mistakes |

## Critical Settings

```jsonc
{
    "python.analysis.typeCheckingMode": "basic",   // catch wrong types before running
    "editor.formatOnSave": true,                     // never think about formatting
    "editor.rulers": [88, 120],                      // Black wraps at 88
    "notebook.output.scrolling": true,                // training loops = thousands of lines
    "files.autoSave": "afterDelay"                    // avoid stale code runs
}
```

## Remote SSH Setup

The most important extension for AI: edit/debug code on remote GPU boxes as if they were local.

For passwordless access:
```bash
ssh-keygen -t ed25519 -C "your-email@example.com"
ssh-copy-id user@your-gpu-box-ip
```

Add to `~/.ssh/config`:
```
Host gpu-box
    HostName 203.0.113.50
    User ubuntu
    IdentityFile ~/.ssh/id_ed25519
```

## Key Terms

| Term | Meaning |
|------|---------|
| **LSP** | Language Server Protocol: standard for editors to get type info, completions, and diagnostics |
| **Pylance** | Microsoft's Python LSP using Pyright for type checking and IntelliSense |
| **Remote SSH** | VS Code extension that runs a server on a remote machine and streams UI to your local editor |
| **Format on save** | Editor runs a formatter (Black, Ruff) every time you save |

## Sources

- VS Code docs — Remote SSH: https://code.visualstudio.com/docs/remote/ssh
- Black formatter: https://black.readthedocs.io/
- Ruff: https://docs.astral.sh/ruff/

## Related
- [[AI Engineering - Dev Environment Stack]]
- [[Jupyter Notebook Workflow]]
