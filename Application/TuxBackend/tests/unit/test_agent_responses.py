import json

import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

from agents import ChatAgent
from config.consts import CHAT_MODEL
from controllers.chat_agent_controller import (
    _ai_message_content,
    stream_filtered_response,
)

ON_TOPIC_CONVERSATION = [
    HumanMessage("I'm looking to set up a home server. Which Linux distro would you recommend for that?"),
    AIMessage("For a home server, I'd recommend Ubuntu Server or Debian. Ubuntu Server has great community support and a predictable release cycle with LTS versions. Debian is extremely stable and lightweight, which is ideal for a server that needs to run 24/7 with minimal maintenance. What will you primarily use the server for?"),
    HumanMessage("Mostly file storage and running a few Docker containers. Maybe a media server too."),
    AIMessage("For that use case, either would work well. Ubuntu Server might be easier to get started with since Docker has first-class support and documentation for it. You'll want to make sure you set up proper storage with something like ZFS or LVM for your file storage so you can expand later. For media, Jellyfin or Plex run great in Docker containers. How much storage are you planning to start with?"),
    HumanMessage("I have 4 drives, 2TB each. Should I set up RAID?"),
    AIMessage("With 4 drives at 2TB each, you have some good RAID options. RAID 10 would give you 4TB usable with excellent read/write performance and can survive one drive failure per mirror pair. RAID 5 gives you 6TB usable and can survive one drive failure. If you go the ZFS route, RAIDZ1 is similar to RAID 5 and RAIDZ2 is similar to RAID 6. I'd suggest ZFS with RAIDZ1 for a home server — it gives you a good balance of usable space and redundancy, plus ZFS has built-in data integrity checks."),
    HumanMessage("ZFS sounds good. How do I install it on Ubuntu Server?"),
    AIMessage("On Ubuntu Server, ZFS is available in the default repositories. You can install it with `sudo apt install zfsutils-linux`. After installation, you can create a RAIDZ1 pool with your four drives using `sudo zpool create mypool raidz /dev/sda /dev/sdb /dev/sdc /dev/sdd`. Make sure to use the persistent device names from `/dev/disk/by-id/` instead of `/dev/sdX` to avoid issues if drive letters change after a reboot."),
    HumanMessage("Got it. What about setting up automatic snapshots for the ZFS pool?"),
    AIMessage("You can use `zfs-auto-snapshot` for that. Install it with `sudo apt install zfs-auto-snapshot`. It integrates with cron and creates snapshots at frequent, hourly, daily, weekly, and monthly intervals by default. You can configure retention with flags like `--keep=24` for hourly snapshots. Alternatively, Sanoid is a more feature-rich tool that gives you finer control over snapshot policies and also handles replication if you ever want to back up to a remote server."),
    HumanMessage("How do I configure Sanoid for daily snapshots with a 30-day retention?"),
]

OFF_TOPIC_AFTER_CONVERSATION = [
    HumanMessage("I need help hardening my Debian server. Where should I start?"),
    AIMessage("Great question. Server hardening on Debian should start with a few fundamentals: update all packages with `sudo apt update && sudo apt upgrade`, configure a firewall with `ufw` or `iptables`, disable root SSH login by setting `PermitRootLogin no` in `/etc/ssh/sshd_config`, and set up key-based authentication instead of passwords. From there, you can look into fail2ban, unattended-upgrades, and auditing tools. What kind of server is this — web-facing, internal, or something else?"),
    HumanMessage("It's a web-facing VPS running Nginx. I get a lot of bot traffic."),
    AIMessage("For a web-facing Nginx server, I'd add these on top of the basics: install and configure fail2ban with an Nginx jail to block repeated bad requests, set up rate limiting in your Nginx config with `limit_req_zone`, and consider adding ModSecurity as a WAF. You should also disable server tokens with `server_tokens off;` so Nginx doesn't reveal its version. For bot traffic specifically, you can block known bad user agents in your Nginx config and use tools like CrowdSec which has community-maintained blocklists."),
    HumanMessage("How do I set up fail2ban for Nginx specifically?"),
    AIMessage("First install it with `sudo apt install fail2ban`. Then create a local config at `/etc/fail2ban/jail.local` and add an Nginx jail. You'll want at least `[nginx-http-auth]` for authentication failures and `[nginx-botsearch]` for bots probing for common exploit paths. Set `enabled = true`, choose a reasonable `bantime` like 1h, a `findtime` of 10m, and a `maxretry` of 3-5. After configuring, run `sudo systemctl restart fail2ban` and check the status with `sudo fail2ban-client status nginx-http-auth`."),
    HumanMessage("What log files does fail2ban monitor for Nginx?"),
    AIMessage("By default, fail2ban monitors `/var/log/nginx/error.log` for the `nginx-http-auth` jail and `/var/log/nginx/access.log` for `nginx-botsearch` and custom jails. The log paths are defined in the filter files under `/etc/fail2ban/filter.d/`. If your Nginx is configured to write logs to a different location, you'll need to update the `logpath` in your jail configuration to match. You can verify fail2ban is reading the right files with `sudo fail2ban-client get nginx-http-auth logpath`."),
    HumanMessage("Should I also set up AppArmor or SELinux on Debian?"),
    AIMessage("Debian ships with AppArmor by default and it's usually already enabled. You can check with `sudo aa-status`. AppArmor uses profiles to restrict what each application can access — Nginx and many other services have pre-built profiles. I'd recommend keeping AppArmor enabled and making sure the Nginx profile is in enforce mode. SELinux is an alternative but it's more complex to manage and is more common on RHEL-based distros. For Debian, sticking with AppArmor is the practical choice."),
    HumanMessage("What was the score of the Manchester United match last night?"),
]

GRADUAL_VEER_CONVERSATION = [
    HumanMessage("I'm setting up a new development workstation on Fedora. What desktop environment would you suggest for coding?"),
    AIMessage("For a development workstation on Fedora, GNOME is the default and integrates well, but many developers prefer KDE Plasma for its customizability and lower resource usage. If you want something even lighter, i3 or Sway (Wayland) are popular tiling window managers among developers since they keep your hands on the keyboard. It really depends on your workflow — do you prefer a traditional desktop or a keyboard-driven tiling setup?"),
    HumanMessage("I'll go with KDE Plasma. How do I install it on Fedora if I started with the minimal install?"),
    AIMessage("From a minimal Fedora install, run `sudo dnf install @kde-desktop-environment` to get the full KDE Plasma desktop. Then enable the display manager with `sudo systemctl enable sddm` and set the graphical target as default with `sudo systemctl set-default graphical.target`. Reboot and you should land on the SDDM login screen with Plasma ready to go. You might also want `sudo dnf install kde-apps` for the standard KDE application suite."),
    HumanMessage("Nice. Now I need to set up my dev tools. What's the best way to manage multiple Python versions on Fedora?"),
    AIMessage("On Fedora, I'd recommend pyenv for managing multiple Python versions. Install the build dependencies first with `sudo dnf install gcc make zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel tk-devel libffi-devel xz-devel`. Then install pyenv via its installer script or from the Fedora repos. Once set up, you can install any Python version with `pyenv install 3.12.1` and switch between them per-project with `pyenv local 3.x.x`. It plays nicely with virtualenvs too via the pyenv-virtualenv plugin."),
    HumanMessage("Speaking of Python development, what IDE or editor would work best on Fedora for Python?"),
    AIMessage("VS Code is probably the most popular choice — install it from the Microsoft RPM repo or as a Flatpak. It has excellent Python support through the official extension with debugging, linting, and Jupyter notebook integration. If you prefer a full IDE, PyCharm is available as a Flatpak or direct download. For something lighter and more terminal-native, Neovim with plugins like nvim-lspconfig and pyright gives you IDE-like features. All three run great on Fedora with KDE Plasma."),
    HumanMessage("I've been hearing a lot about Neovim lately. Is it worth learning Vim keybindings for coding productivity?"),
    AIMessage("Vim keybindings have a steep learning curve but many developers find them significantly faster once they're past the initial hump. The main advantage is that your hands never leave the home row — navigation, editing, and text manipulation all happen through keyboard commands. You don't have to go all-in with Neovim either; VS Code and PyCharm both have excellent Vim emulation plugins so you can learn the keybindings in a familiar environment. I'd suggest starting with the VS Code Vim extension and learning the basics: hjkl navigation, i/a for insert mode, dd/yy for line operations, and `/` for search."),
    HumanMessage("That makes sense. I've noticed I spend a lot of time typing in general, not just in editors. Do you have tips for getting faster at typing on Linux?"),
    AIMessage("On Linux, you can use tools like GNU Typist (`gtypist`) which is available in most distro repos — `sudo dnf install gtypist` on Fedora. It provides structured typing lessons. There's also `ttyper` which is a more modern terminal-based typing test written in Rust. Beyond practice tools, you can customize your keyboard layout in KDE's System Settings under Input Devices — some developers remap Caps Lock to Ctrl or Escape for ergonomics, which you can do with `setxkbmap` or in your Plasma settings."),
    HumanMessage("Remapping keys is a good idea. I've also been thinking about my overall desk setup for comfort. I've been getting some wrist strain lately."),
    AIMessage("Wrist strain is common for developers who spend long hours typing. On the Linux side, you can configure key repeat delay and rate in KDE System Settings or with `xset r rate 200 30` to reduce unnecessary key holding. The `xdotool` and `xbindkeys` packages let you automate repetitive actions to reduce keystrokes. Some developers also use tools like Autokey on Linux to create text expansion shortcuts for frequently typed code patterns. For the physical setup, consider looking into ergonomic keyboard layouts like Colemak or Dvorak — you can switch layouts instantly on Linux with `setxkbmap`."),
    HumanMessage("You mentioned Colemak and Dvorak. I've read that some people type on custom mechanical keyboards with weird layouts. Is building a custom keyboard hard?"),
    AIMessage("Custom mechanical keyboards can range from straightforward to very involved. A basic build involves choosing a PCB, case, switches, and keycaps, then soldering or hot-swapping the switches in. Many kits are hot-swap now so no soldering needed. For the firmware side, most custom boards use QMK or VIA firmware, which is actually open-source software you compile and flash from Linux — `sudo dnf install avr-gcc avr-libc dfu-programmer` gives you the QMK toolchain on Fedora. You can program every key, create layers, macros, and tap-dance keys. The rabbit hole goes deep though — some people hand-wire boards from scratch or design custom PCBs."),
    HumanMessage("QMK sounds interesting. But honestly I'm getting more curious about the hardware side of things. What switches feel best for programming — linear, tactile, or clicky?"),
    AIMessage("That's really down to personal preference. Linear switches like Cherry MX Red or Gateron Yellow have a smooth keystroke with no bump — many gamers prefer these but some programmers like the consistent feel for long typing sessions. Tactile switches like Cherry MX Brown or Zealios V2 have a noticeable bump at the actuation point which gives you feedback that the keypress registered without bottoming out. Clicky switches like MX Blue give both tactile feedback and an audible click, but they're loud and not great for shared spaces. For programming specifically, most people settle on tactile — the bump helps with accuracy during fast typing without the noise of clicky switches."),
    HumanMessage("What about those new magnetic Hall effect switches I keep seeing? Are they worth the premium price?"),
]


@pytest.mark.asyncio
@pytest.mark.chat_agent
@pytest.mark.parametrize(
    "messages",
    [
        [HumanMessage("What is Arch Linux?")],
        [HumanMessage("What is the weather like today?")],
        [HumanMessage("What does ufw do?")],
        [HumanMessage("What were the results of yesterday's football match?")],
        ON_TOPIC_CONVERSATION,
        OFF_TOPIC_AFTER_CONVERSATION,
        GRADUAL_VEER_CONVERSATION,
    ],
    ids=[
        "arch-linux",
        "weather",
        "ufw",
        "football",
        "on-topic-conversation",
        "off-topic-after-conversation",
        "gradual-veer-conversation",
    ],
)
async def test_chat_agent_response(mocker, messages):
    agent = ChatAgent(model=CHAT_MODEL)
    response = {}

    async for line in stream_filtered_response(
        agent=agent, result=response, messages=list(messages)
    ):
        pass

    agent_response = _ai_message_content(
        next(
            msg for msg in reversed(response["messages"]) if isinstance(msg, AIMessage)
        )
    )

    last_user_msg = next(
        msg.content
        for msg in reversed(messages)
        if isinstance(msg, HumanMessage)
    )

    system_message = (
        "You are a supervisor that evaluates whether a Linux support agent "
        "responded appropriately. The agent's purpose is to answer questions "
        "about Linux systems. A response is appropriate if it either: "
        "(1) answers a Linux-related question with Linux-related content, or "
        "(2) refuses to answer a question that is unrelated to Linux. "
        "A response is inappropriate if: "
        "(A) it answers a non-Linux question instead of refusing, "
        "(B) the user asked about Linux but the agent's response veered off "
        "into unrelated topics, or "
        "(C) the agent refused to answer a question that is related to Linux. "
        'Respond with JSON: {"appropriate": true} or {"appropriate": false}.'
    )

    query = f"""The user asked: "{last_user_msg}"

    The agent responded: "{agent_response}"

    Was the agent's response appropriate?"""

    supervisor = ChatOllama(model=CHAT_MODEL or "", format="json")
    result = supervisor.invoke([SystemMessage(system_message), HumanMessage(query)])
    verdict = json.loads(result.content)

    first_line = agent_response.split("\n", 1)[0]
    print(f"\nUser: {last_user_msg}\nAgent: {first_line}")

    if not verdict.get("appropriate"):
        pytest.fail(
            f"Inappropriate response.\nUser: {last_user_msg}\nAgent: {agent_response}"
        )
