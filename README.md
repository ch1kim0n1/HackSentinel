# MindCore · Sentinel

> **Find the bugs before they find you.**

MindCore · Sentinel is a CLI-first, deterministic, AI-powered bug discovery tool that simulates a real user interacting with your project and produces **engineer-grade bug reports** in under two minutes.

Sentinel does not debug your code.  
It finds where and how your software breaks — before judges, users, or demo-time chaos do.

---

## Why Sentinel Exists

Hackathon teams waste massive time:
- Manually clicking through unfinished apps
- Missing obvious crashes during demos
- Discovering bugs under pressure instead of fixing them
- Writing poor or incomplete bug reports

Sentinel replaces ad-hoc testing with a **fast, repeatable, autonomous user simulation**.

---

## Core Principles

- **Hackathon-first**
- **User-centric bug discovery**
- **Deterministic output**
- **Local-only execution**
- **No authentication**
- **Strict time limits**
- **Honest failure reporting**

Sentinel never hallucinates bugs.

---

## What Sentinel Is

- A CLI tool
- An autonomous “user-zero”
- A bug discovery engine
- A structured report generator

## What Sentinel Is NOT

- A security scanner
- A performance tester
- A load-testing tool
- A replacement for QA teams
- A debugger
- A CI pipeline tool

---

## Supported Use Case

**When to use Sentinel:**
- Mid-hackathon before feature freeze
- Before demos or judging
- After major changes
- When something “feels unstable”

**When not to use Sentinel:**
- For security audits
- For performance benchmarking
- For production-grade QA
- When code does not run at all

---

## Input Contract

Sentinel operates on a **local repository**.

### Required Input
```bash
sentinel /path/to/repo
