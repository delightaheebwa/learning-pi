<!-- provenance: status=verified | source=https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/00-setup-and-tooling/10-terminal-and-shell/docs/en.md ; https://man7.org/linux/man-pages/man1/tmux.1.html | verified-by=fact-check-agent | date=2026-10-26 -->

# AI Engineering — Terminal & Shell

> The terminal is where AI engineers live. Get comfortable here. Every AI workflow touches the shell: training runs, GPU monitoring, log tailing, remote SSH sessions, environment management.

## Core Concepts

### 1. Shell Basics

The shell (bash, zsh) is the program that interprets your commands. Key operations:

| Operation | Command/Shortcut |
| --- | --- |
| Navigate | `cd`, `pwd`, `ls -la` |
| History search | `Ctrl+R` then type (cycle with `Ctrl+R` again) |
| Clear terminal | `clear` or `Ctrl+L` |
| Cancel command | `Ctrl+C` |
| Suspend command | `Ctrl+Z` (resume with `fg`) |

### 2. Piping & Redirection

Piping (`|`) connects commands — send output of one as input to the next. Essential for log processing.

| Symbol | What it does |
| --- | --- |
| `>` | Write stdout to file (overwrite) |
| `>>` | Append stdout to file |
| `2>` | Write stderr to file |
| `2>&1` | Send stderr to same place as stdout |
| `|` | Pipe stdout of one command as stdin to the next |

**Common patterns:**

```bash
# Filter logs
tail -f train.log | grep --line-buffered "loss"

# Extract values
grep "loss:" train.log | awk '{print $NF}' > losses.txt

# Redirect both stdout and stderr
python train.py > train_full.log 2>&1

# Log everything and still see it on screen
python train.py 2>&1 | tee train.log
```

### 3. Background Processes & Process Management

Training runs take hours. Use these for managing long-running processes:

| Method | Survives terminal close? | Can reattach? |
| --- | --- | --- |
| `command &` | No | No |
| `nohup command &` | Yes | No (check log file) |
| `tmux` | Yes | Yes |

Key commands: `jobs`, `fg %1`, `kill %1` / `kill $(pgrep -f "train.py")`, `ps aux | grep train.py`

**Rule of thumb:** For anything longer than a few minutes, use tmux.

### 4. tmux (Terminal Multiplexer)

Creates persistent terminal sessions with multiple panes. The single most useful tool for managing training runs.

| Action | Command |
| --- | --- |
| Start named session | `tmux new -s training` |
| Split horizontally | `Ctrl+B` then `"` |
| Split vertically | `Ctrl+B` then `%` |
| Navigate panes | `Ctrl+B` then arrow keys |
| Detach (keep running) | `Ctrl+B` then `d` |
| Reattach | `tmux attach -t training` |
| List sessions | `tmux ls` |
| Kill session | `tmux kill-session -t training` |

**Typical AI workflow:** One pane running training, another monitoring GPU with `watch -n1 nvidia-smi`, a third tailing logs. Detach, leave, SSH back later and reattach.

### 5. System & GPU Monitoring

| Tool | Purpose |
| --- | --- |
| `htop` | System processes, memory usage, CPU. Sort by memory with `F6` to find leaks. Tree view with `F5`. |
| `nvtop` | GPU processes (NVIDIA). Install: `apt install nvtop` or `brew install nvtop` |
| `nvidia-smi` | Quick GPU check. `watch -n1 nvidia-smi` for live updates. |
| `watch` | Run any command repeatedly. `watch -n1 <cmd>` updates every 1 second. |

### 6. SSH & Remote File Transfer

For connecting to cloud GPU boxes (Lambda, RunPod, Vast.ai):

```bash
# Connect
ssh -i ~/.ssh/my_gpu_key user@gpu-box-ip

# Copy files
scp model.pt user@gpu-box-ip:~/models/
rsync -avz ./data/ user@gpu-box-ip:~/data/

# Port forward (access remote Jupyter/TensorBoard locally)
ssh -L 8888:localhost:8888 user@gpu-box-ip
```

**SSH config** (`~/.ssh/config`) lets you alias servers:

```markdown
Host gpu
    HostName 192.168.1.100
    User ubuntu
    IdentityFile ~/.ssh/gpu_key
```

Then just `ssh gpu`.

### 7. AI Shell Aliases & Patterns

**Useful aliases** (add to `~/.bashrc` or `~/.zshrc`):

- `alias gpu='nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total,temperature.gpu --format=csv,noheader'`
- `alias killtraining='pkill -f "python.*train"'`
- `alias ae='source .venv/bin/activate'`
- `alias watchloss='tail -f logs/*.log | grep --line-buffered "loss"'`

**Common terminal patterns for AI work:**

- Compare experiment logs: `diff <(grep "accuracy" exp1.log) <(grep "accuracy" exp2.log)`
- Find largest model files: `find . -name "*.pt" -o -name "*.safetensors" | xargs du -h | sort -rh | head -20`
- Check disk space: `df -h` / `du -sh ./data/*`
- Verify environment: `env | grep -i cuda` / `env | grep -i torch`
- Count project size: `find . -name "*.py" | xargs wc -l | tail -1`

## Sources

- [ai-engineering-from-scratch Phase 0, Lesson 10](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/00-setup-and-tooling/10-terminal-and-shell/docs/en.md)
- Source saved at: `Knowledge Wiki/raw/sources/2026-06-25 - terminal-and-shell-ai-engineering.md`

## Related

- [[AI Engineering - Dev Environment Stack]]
- [[GPU Computing]]
- [[Editor and Remote Dev Setup]]