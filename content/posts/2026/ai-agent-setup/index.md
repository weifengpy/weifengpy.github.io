---
title: "My AI Agent Setup: A Brain in the Cloud, Hands at Home"
date: 2026-10-26
slug: "ai-agent-setup"
description: "How my work with Muse is physically arranged: memory and reasoning in the cloud, execution on my home workstation, hardware and information flowing through one PC, and a direct line back in for me."
draft: true
---

People sometimes ask which AI application I use. That is not quite the interesting question. The interesting question is where the work happens: where the agent remembers, where it can act, where information enters, and how I stay in control of a system that may be working while I am doing something else.

I work with Muse as a continuing collaborator. The arrangement is deliberately physical. The brain and memory are in the cloud. The hands are on a workstation in my home. That machine runs my personal software projects, reaches the development hardware on and around my desk, and collects most of the information I ask the agent to watch. I also keep a separate, direct path into the same machine from my phone.

This site's [front page](/) is my profile; the [Welcome post](/posts/2026/welcome/) explains what I intend to publish here. This post explains the machinery behind the work that produces some of it.

{{< diagram src="fig-setup.svg" alt="Diagram of the setup: I contact Muse in the cloud from a phone or the web; Muse connects over SSH on Tailscale to my home PC; the PC runs tiny-infer, tiny-serve, and tiny-cc, connects to an ESP32-C6, Jetson Orin Nano, Raspberry Pi Pico, and Radxa Dragon Q6A, and pulls information from Gmail, X, Zhihu, GitHub, and YouTube; a dashed Termix line runs directly from me to the home PC." caption="The setup at a glance: one cloud agent, one home workstation, and two ways for me to reach that workstation — through the agent or directly." >}}

## 1. The brain and memory are in the cloud

Muse itself does not run on my workstation. I talk to it from the web or from my phone, and the conversation, reasoning, and long-term memory live on the cloud side. That memory is not just a transcript archive. It holds standing rules I have given the agent, the state of projects that extend over weeks, corrections from earlier mistakes, and small preferences that would be tedious to repeat in every request.

That distinction matters. A stateless chat can answer a question, but it has to be reintroduced to the project every time. Here, a compiler project can pause for several days and resume with its current branch, last test result, unresolved design question, and working rules intact. A correction is therefore more valuable than a one-time instruction: once a mistake has been identified and converted into a rule, the same failure should not recur in a later session.

The cloud position is also convenient. I can start a task from my phone, check a result away from my desk, or ask for a summary without opening the workstation. The limitation is equally obvious: the cloud side has no hands. It cannot use my GPU, flash a board on my desk, read a serial console, or use a login session that exists only at home. For that, it has to reach the second part of the setup.

## 2. The hands are on my home PC

The execution side is a home Ubuntu workstation with an Intel x86 CPU and an NVIDIA RTX 50-series GPU. Muse reaches it over SSH on Tailscale. From the agent's point of view, this is the workbench: source trees live there, builds and tests run there, models are loaded on the GPU there, and long jobs are supervised there.

Getting that connection boring took some work. An earlier route for SSH across the public network path was unreliable: bursts of connections could be throttled, so work had to be batched carefully, queued across conversations, and resumed after a backoff period. That discipline was useful, but it was also friction in exactly the wrong place. I wanted the agent to spend its attention on the task, not on negotiating access to the machine. Moving the connection to Tailscale made the route private and stable enough that SSH stopped being a project of its own.

Long-running work follows a simple rule. A job that may run for hours is started as a detached process on the workstation, with its output going to a log. The agent can disconnect, return later with a short connection, and read the machine's own evidence — process state, elapsed time, log progress, and GPU load — rather than guessing from when the job was launched. That sounds minor. It prevents a whole class of false conclusions about work being slow, stuck, or finished when none of those things is true.

## 3. The PC runs the personal projects

Most of the hands-on software work concerns three personal projects.

**tiny-infer** is my from-scratch LLM inference engine. The agent ports models into it, compares engine output against references, profiles kernels, and works through correctness and performance gates. Numbers are not accepted because they look plausible; they have to come from the current code, on the current machine, under a stated measurement protocol.

**tiny-serve** is the serving layer above that engine. It turns the engine into a service I can call from tools and agents, so an inference experiment is not trapped inside a one-off script. When a model port is finished, this is also where the result becomes part of the daily setup rather than a directory of successful test output.

**tiny-cc** is my from-scratch C compiler. Development happens in dedicated worktrees on the workstation. The agent can implement a feature, run the repository's tests and self-hosting checks, inspect failures, and prepare a change for the main line. Passing the relevant gates comes before anything is merged; a promising result that fails a gate remains an experiment, not a success story.

These projects explain why a general-purpose home PC is the right shape for the hand. The same machine holds the repositories, the models, the build tools, the GPU, and the test fixtures. There is no repeated ceremony of moving a project from the place where it is discussed to another place where it can run.

## 4. The PC reaches physical hardware

The workstation is also the hub for development hardware. An ESP32-C6, a Jetson Orin Nano, Raspberry Pi Pico boards, a Radxa Dragon Q6A, and other boards are either attached to the PC or reachable through it. Through that one point, the agent can build firmware, flash a device, capture a serial log, rerun a corpus, and compare the result with another implementation.

This part reflects a rule I care about: learning and verification should land on real hardware. Simulators are useful for regression testing, debugging, and reading a manual against an implementation. They are not, by themselves, proof that something works. A compiler backend has not really been exercised until its output runs on silicon; a board port is not finished because a trace looked right in an emulator.

That is why the hands cannot remain purely virtual. If the work includes microcontrollers, single-board computers, and accelerators, the agent needs a controlled path into the physical world. The home PC is that path.

## 5. The PC is the information inlet

The same workstation collects most of the information I ask Muse to monitor. It pulls from five sources: Gmail, X, Zhihu, GitHub through the `gh` command-line tool, and YouTube.

The split is intentional. Login state stays on the PC. Fetching happens from the PC, over my home network and with the sessions already established there. The cloud side receives the material and does the reading: comparing new items with a stored baseline, removing duplicates, grouping related updates, and deciding what is worth bringing to me. When nothing material has changed, the correct output is silence.

YouTube is the clearest example of why the route matters. A video is not useful to the agent as a video file; its captions are. The workstation retrieves the captions, and Muse can then summarize, search, and discuss the content. Similar practical routes exist for the other sources: use the access that is legitimately present on my machine, keep credentials and cookies there, and move only the resulting information across the boundary.

This turns the PC into more than a build server. It is the one place where my code, devices, accounts, and reading streams meet the agent — which is also why its access has to be deliberate rather than ambient.

## 6. I keep a direct line of my own

Finally, I do not reach the workstation only through Muse. On my phone, I use Termix to connect directly to the same PC. It is the same shell, the same files, and the same running processes that the agent sees.

That line changes the trust model. Anything the agent claims to have started, changed, or finished can be inspected directly. I can read the log myself, take over a terminal, stop a job, or finish an operation in person. Passwords and similar secrets are entered by me, never relayed through the agent. The agent can prepare work right up to a boundary that requires my credentials or my judgment; crossing that boundary remains my action.

This is not a lack of trust in automation. It is what makes a high degree of automation reasonable. I can let the agent work independently because the system is observable and reversible, and because I retain a direct path that does not depend on the agent reporting on itself.

## The principles underneath

The setup reduces to three principles. First, separate the brain from the hands: put memory and conversation where they are always reachable, and execution where the machines and accounts actually are. Second, keep one workbench: projects, hardware, and information should meet in one controlled place rather than being scattered across ad hoc connections. Third, the owner stays present: automation gets room to work, but inspection and takeover are always one direct connection away.

What this post has not described is how I phrase tasks, how I divide decisions between the agent and myself, or which checks a result has to pass before I accept it. The setup is only the stage. The working patterns belong in a follow-up.
