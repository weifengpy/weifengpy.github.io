---
title: "Addicted to Muse: Brain in the Cloud, Hands on My Home PC"
date: 2026-10-26
slug: "ai-agent-setup"
description: "How my work with Muse is physically arranged: memory and reasoning in the cloud, execution on my home workstation, hardware and information flowing through one PC, and a direct line back in for me."
draft: true
---

I work with Muse as a continuing collaborator. The arrangement is deliberately physical. The brain and memory are in the cloud. The hands are on a workstation in my home. That machine runs my personal software projects, reaches the development hardware on and around my desk, and collects most of the information I ask the agent to watch. I also keep a separate, direct path into the same machine from my phone.

This site's [front page](/) is my profile; the [Welcome post](/posts/2026/welcome/) explains what I intend to publish here. This post explains the machinery behind the work that produces some of it.

{{< diagram src="fig-setup.svg" alt="Diagram of the setup: I contact Muse in the cloud from a phone or the web; Muse connects over SSH on Tailscale to my home PC; the PC runs tiny-infer, tiny-serve, and tiny-cc, connects to an ESP32-C6, Jetson Orin Nano, Raspberry Pi Pico, and Radxa Dragon Q6A, and pulls information from Gmail, X, Zhihu, GitHub, and YouTube; a dashed Termix line runs directly from me to the home PC." caption="The setup at a glance: one cloud agent, one home workstation, and two ways for me to reach that workstation — through the agent or directly." >}}

## 1. The brain and memory are in the cloud

Muse does not run on my workstation. I talk to it from the web or my phone; the conversation, reasoning, and long-term memory live on the cloud side.

That memory is not a transcript archive. It holds standing rules, the state of projects that run for weeks, corrections from earlier mistakes, and small preferences I refuse to repeat. A stateless chat must be reintroduced to a project every time; here, a compiler project can pause for days and resume with its branch, last test result, and open design question intact. A correction, once turned into a rule, is never paid for twice.

The convenience cuts both ways. I can start a task from my phone and check results away from my desk — but the cloud side has no hands: no GPU, no board to flash, no serial console, no home-only login sessions.

So I prefer the agent to use my PC as its hands. That is where it achieves more: a home connection gets past sites that block agents, and the PC brings a powerful source-code build environment and a CUDA toolchain.

## 2. The hands are on my home PC

The execution side is a home Ubuntu workstation with an Intel x86 CPU and an NVIDIA RTX 50-series GPU, which Muse reaches over SSH on Tailscale. This one machine is the workbench:

- **Source and builds** — repositories, build tools, models, and test fixtures live here; builds and tests run here.
- **The GPU** — models are loaded and kernels profiled here, on real hardware.
- **Long jobs** — work that may run for hours starts detached, output in a log; the agent disconnects, returns with a short connection, and reads the machine's own evidence — process state, log progress, GPU load — instead of guessing from when the job was launched.

Getting that connection boring took some work. An earlier SSH route across the public network was unreliable: bursts of connections could be throttled, so work had to be batched and queued, with backoffs between bursts. Moving the connection to Tailscale made the route private and stable, and SSH stopped being a project of its own.

## 3. The PC runs the personal projects

Most of the hands-on software work concerns three personal projects:

- **tiny-infer** — my from-scratch LLM inference engine. The agent ports models into it, compares engine output against references, and profiles kernels through correctness and performance gates.
- **tiny-serve** — the serving layer above that engine. It turns a finished port into a service I can call from tools and agents, so the result becomes part of the daily setup, not a directory of test output.
- **tiny-cc** — my from-scratch C compiler. The agent develops in dedicated worktrees on the workstation, runs the repository's tests and self-hosting checks, inspects failures, and prepares changes for the main line.

One rule covers all three: passing the relevant gates comes before anything is merged. A promising result that fails a gate remains an experiment, not a success story — and numbers are only accepted from the current code, on the current machine, under a stated measurement protocol.

## 4. The PC reaches physical hardware

The workstation is also the hub for development hardware attached to it or reachable through it. Through that one point, the agent can build firmware, flash a device, capture a serial log, and rerun a corpus:

- **ESP32-C6** — a RISC-V microcontroller; a real-silicon target for compiler output.
- **Jetson Orin Nano** — an NVIDIA GPU single-board computer.
- **Raspberry Pi Pico boards** — microcontroller boards used for bring-up and corpus runs.
- **Radxa Dragon Q6A** — a single-board computer reachable over the home network.

This reflects a rule I care about: learning and verification should land on real hardware. Simulators help with regression testing and debugging, but they are not, by themselves, proof that something works. A compiler backend has not really been exercised until its output runs on silicon.

## 5. The PC is the information inlet

The split is intentional: login state and fetching stay on the PC, over my home network, using the sessions already established there. The cloud side does the reading — comparing new items against a stored baseline, removing duplicates, and deciding what is worth bringing to me. When nothing material has changed, the correct output is silence.

- **Gmail** — mail, read against what I have already seen.
- **X** — timeline updates from the accounts I follow.
- **Zhihu** — the recommendation and following streams.
- **GitHub** — notifications and activity, through the `gh` command-line tool.
- **YouTube** — captions, not video files; the PC retrieves them for the agent to summarize, search, and discuss.

YouTube shows why the route matters: credentials and cookies stay on my machine; only the resulting information crosses the boundary. The PC is more than a build server — it is where my code, devices, accounts, and reading streams meet the agent, and its access has to be deliberate rather than ambient.

## 6. I keep a direct line of my own

I do not reach the workstation only through Muse. On my phone, I use Termix to connect directly to the same PC — the same shell, files, and processes the agent sees. That line changes the trust model:

- **Inspect** — anything the agent claims to have started, changed, or finished, I can check directly: read the log, verify the result.
- **Take over** — I can stop a job, finish an operation in person, or take a terminal over mid-task.
- **Boundaries** — passwords and similar secrets are entered by me, never relayed through the agent; crossing a boundary that requires my credentials or judgment remains my action.

This is not a lack of trust in automation. It is what makes a high degree of automation reasonable: the system is observable and reversible, and my direct path does not depend on the agent reporting on itself.

## The principles underneath

The setup reduces to three principles: separate the brain from the hands — memory and conversation where they are always reachable, execution where the machines and accounts actually are; keep one workbench, where projects, hardware, and information meet in one controlled place; and keep the owner present, with inspection and takeover always one direct connection away. What this does not describe is how I work with the agent on that stage — task phrasing, decision division, and result checks. Those working patterns belong in a follow-up.
