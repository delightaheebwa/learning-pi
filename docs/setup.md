# Setup

Setup has two parts: install the pinned pi layer, then start the learner notebook in `state/`. The commands below are idempotent, so re-running them is safe. For the short version, see the [README Quick start](../README.md#quick-start).

All platforms need `git` and `python3`. The setup also needs `deno` for `lpi test`, and `nodejs` plus `npm`, because `lpi update` checks extension versions via `npm view`. Install [mise](https://mise.jdx.dev) for the pinned `pi` binary. The Open WebUI face in `deploy/` is Linux-only and also needs Docker and Compose.

## Start the notebook

The learner state already lives at `state/` with its full history. It was a separate repo until 2026-11-09.

```bash
~/learning-pi/install.sh ~/learning-pi/state
cd ~/learning-pi/state && pi   # approve/trust once, then /review /lesson /teach
```

Run `pi` from `state/` so the relative paths in the skills resolve. Set `LEARNING_SYSTEM_ROOT` to the same path for the scripts that take a state root. Define your track in `state/Learning System/MISSION.md` and `state/Learning System/CURRICULUM.md`, then run `/teach <topic>` or `/lesson`.

`init-state.sh` still builds a separate scaffold repo from a clone. Rewriting it for the single-repo layout is open work, listed in [`docs/README.md`](README.md).

## Omarchy and Arch Linux

```bash
sudo pacman -S --needed git openssh python base-devel curl unzip mise deno nodejs npm openssl
# optional, only for the Linux-only Open WebUI face in deploy/: docker and firewall
sudo pacman -S --needed docker docker-compose ufw
export PATH="$HOME/.local/bin:$HOME/.local/share/mise/shims:$PATH"
mkdir -p ~/.local/bin
[ -d ~/learning-pi ] || git clone https://github.com/delightaheebwa/learning-pi.git ~/learning-pi
ln -sf ~/learning-pi/bin/pi ~/.local/bin/pi
ln -sf ~/learning-pi/bin/lpi ~/.local/bin/lpi
~/.local/bin/pi --version && ~/learning-pi/scripts/learn-check --no-load
# next: see Start the notebook above
```

Optional Omarchy extras: the bar widget and the evening reminder.

```bash
~/learning-pi/omarchy/install.sh
```

## Ubuntu, Debian, and WSL

```bash
sudo apt-get update && sudo apt-get install -y git python3 curl unzip openssl ca-certificates nodejs npm
export PATH="$HOME/.local/bin:$HOME/.local/share/mise/shims:$HOME/.deno/bin:$PATH"
command -v mise >/dev/null || curl -fsSL https://mise.run | sh
command -v deno >/dev/null || curl -fsSL https://deno.land/install.sh | sh
grep -qs 'mise/shims' ~/.bashrc || echo 'export PATH="$HOME/.local/bin:$HOME/.local/share/mise/shims:$HOME/.deno/bin:$PATH"' >> ~/.bashrc
mkdir -p ~/.local/bin
[ -d ~/learning-pi ] || git clone https://github.com/delightaheebwa/learning-pi.git ~/learning-pi
ln -sf ~/learning-pi/bin/pi ~/.local/bin/pi
ln -sf ~/learning-pi/bin/lpi ~/.local/bin/lpi
~/.local/bin/pi --version && ~/learning-pi/scripts/learn-check --no-load
# next: see Start the notebook above
```

## Windows with WSL2

Native Windows (PowerShell or `cmd.exe`) is not supported. Every entrypoint is bash: `install.sh`, `bin/pi`, and `scripts/learn-check`. The `.pi/` overlay uses Unix symlinks, and the deploy path needs systemd, `ufw`, and Linux `docker0` networking. On Windows, run everything inside WSL2.

```powershell
# PowerShell as Administrator (once): enable WSL2 and install Ubuntu. Reboot when prompted. Needs Windows 10 2004+ or 11.
wsl --install
# Then install Docker Desktop, enable "Use the WSL 2 based engine" + WSL integration for the Ubuntu distro
```

```bash
# Inside the Ubuntu/WSL2 distro: enable systemd (needed for pi-bridge.service and the audit timer), then restart the distro
sudo sh -c 'printf "[boot]\nsystemd=true\n" > /etc/wsl.conf'
exit
```

```powershell
wsl --shutdown
```

```bash
# Re-enter the distro and verify systemd + docker, then follow the Ubuntu/Debian block above
systemd-detect-virt >/dev/null; docker run --rm hello-world
sudo apt-get update && sudo apt-get install -y git python3 curl unzip openssl ca-certificates nodejs npm
export PATH="$HOME/.local/bin:$HOME/.local/share/mise/shims:$HOME/.deno/bin:$PATH"
command -v mise >/dev/null || curl -fsSL https://mise.run | sh
command -v deno >/dev/null || curl -fsSL https://deno.land/install.sh | sh
grep -qs 'mise/shims' ~/.bashrc || echo 'export PATH="$HOME/.local/bin:$HOME/.local/share/mise/shims:$HOME/.deno/bin:$PATH"' >> ~/.bashrc
mkdir -p ~/.local/bin
[ -d ~/learning-pi ] || git clone https://github.com/delightaheebwa/learning-pi.git ~/learning-pi
ln -sf ~/learning-pi/bin/pi ~/.local/bin/pi
ln -sf ~/learning-pi/bin/lpi ~/.local/bin/lpi
~/.local/bin/pi --version && ~/learning-pi/scripts/learn-check --no-load
# next: see Start the notebook above
```

Docker Desktop runs on the Windows side. The checkout in WSL is the single working copy. The current Open WebUI face publishes on `http://127.0.0.1:3000`, as described in [`deploy/README.md`](../deploy/README.md). Keep the repo on the Linux filesystem (`~/...`, not `/mnt/c/...`) so symlinks work and performance holds.

## macOS with Homebrew

```bash
command -v brew >/dev/null || /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install git python mise deno node
export PATH="/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin:$HOME/.local/share/mise/shims:$PATH"
mkdir -p ~/.local/bin
[ -d ~/learning-pi ] || git clone https://github.com/delightaheebwa/learning-pi.git ~/learning-pi
ln -sf ~/learning-pi/bin/pi ~/.local/bin/pi
ln -sf ~/learning-pi/bin/lpi ~/.local/bin/lpi
~/.local/bin/pi --version && ~/learning-pi/scripts/learn-check --no-load
# next: see Start the notebook above
```

## Notes

- `pi --version` triggers `mise` to fetch the pinned version from `versions.lock.json` on first run. `learn-check --no-load` verifies the gate without a live `pi` binary or network models.
- If `~/.local/bin` is not on your `PATH`, persist the full export from your platform's block in your shell rc (`~/.bashrc` or `~/.zshrc`). That export covers `~/.local/bin`, the mise shims, and `~/.deno/bin`.
- macOS: Homebrew needs the Xcode Command Line Tools. Run `xcode-select --install`. That also provides `/usr/bin/git` and the system `python3`. macOS ships LibreSSL, whose `openssl` covers the one base-flow use, `openssl rand -hex` for deploy keys.
- The Open WebUI face is optional and Linux-only. It needs systemd, `ufw`, and the `docker0` `172.17.0.1` bridge, which Docker Desktop for Mac or Windows does not provide. After the base setup above, follow the Apply steps in [`deploy/README.md`](../deploy/README.md). macOS and Windows users run the pi CLI path instead.
- Clones use HTTPS, not SSH. The repo is public, so you need no key and no GitHub account. On a network that blocks outbound SSH, the old `git@github.com:` form fails with `ssh: connect to host github.com port 22: Connection timed out` plus git's misleading "Please make sure you have the correct access rights". The blocked port is the cause, not permissions. To push over SSH anyway, register a key and run `git remote set-url origin git@github.com:delightaheebwa/learning-pi.git`. If port 22 is blocked, map `github.com` to `ssh.github.com:443` in `~/.ssh/config`.
