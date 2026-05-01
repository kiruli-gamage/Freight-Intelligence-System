# Freight-Intelligence-System

# Freight Intelligence System (FIS)
### Autonomous Logistics Agent v1.0

---

## Overview

The Freight Intelligence System (FIS) is an autonomous AI agent designed to monitor, 
analyze, and report on global freight container operations in real time. Built as part of 
a Data Science Applications and AI assignment, FIS demonstrates the integration of 
large language models, autonomous tool use, memory, and reasoning into a practical 
enterprise-level application.

The agent manages 15 cargo containers across 7 major global terminals operated by 
real-world shipping lines including Maersk, COSCO, MSC, Evergreen, Hapag-Lloyd, 
CMA CGM, and ONE.

---

## Problem Statement

Global freight operations generate enormous volumes of data across thousands of 
containers, terminals, and shipping routes. Human operators struggle to monitor 
capacity utilization, forecast stockouts, assess risk, and ensure inspection compliance 
simultaneously. Delayed action on critical containers can result in millions of dollars 
in losses.

FIS solves this by providing an intelligent, conversational interface that autonomously 
scans, forecasts, prioritizes, and assesses freight data — giving operators instant, 
actionable intelligence.

---

## Key Features

- **Autonomous Agent** — Powered by LangChain ReAct agent with Groq LLaMA 3
- **6 Intelligent Tools** — Each tool performs a specific logistics operation
- **Risk Scoring** — Calculates risk scores (0-10) based on utilization, inspection dates, priority and cargo category
- **Capacity Forecasting** — Predicts days until containers reach full capacity
- **Fleet Efficiency Analysis** — Tracks total freight value, utilization rates and inspection compliance
- **Inspection Alerts** — Flags containers overdue for inspection
- **Conversation Memory** — Remembers context across the session using ConversationBufferMemory
- **Professional UI** — Built with Streamlit featuring live metrics dashboard and collapsible fleet panel
- **Direct Tool Routing** — Common queries bypass the LLM for instant responses

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.11 |
| AI Framework | LangChain 0.2.16 |
| LLM | Groq LLaMA 3.1 8B Instant |
| Agent Type | ReAct (Reasoning + Acting) |
| Memory | ConversationBufferMemory |
| Frontend | Streamlit |
| Data | Pandas |
| API | Groq API (Free Tier) |

---

## Project Structure
