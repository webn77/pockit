# pockit

**Production-Ready LLM Agent Engine with Deterministic Gates & Automated Evaluation**

`pockit` is an open-source starter kit and architectural framework designed to safely bridge the gap between Proof of Concept (PoC) and Production for LLM agents operating in high-stakes, regulated domains (such as fintech, healthcare, and legal services).

Rather than trusting LLMs with autonomous critical decisions, `pockit` orchestrates agent behaviors using **LangGraph**, forces contextual retrieval, evaluates queries with deterministic **Rule-Based Access Control (RBAC)** & **Threshold Gates**, and tests agent stability with a built-in **Quantitative Evaluation Harness**.

---

## 1. Why pockit? (The Governance Gap)

Most enterprise LLM agent initiatives stall at the PoC stage. According to Gartner and McKinsey analysis, the primary failure point is not the LLM's capability, but the **Governance Gap**:
* **Black-box reasoning**: Lack of an auditable trail for safety compliance.
* **Stochastic decision making**: Risk of execution errors due to hallucinated tool calling.
* **JIT RBAC integration**: Lack of dynamic role-based access control inside agent states.

`pockit` solves this by decoupling *natural language understanding* from *execution control*.

```
   [User Request]
         │
         ▼
 ┌───────────────┐
 │ RAG Retrieval │ ◄── Forced retrieval of authoritative policies/guidelines
 └───────┬───────┘
         ▼
 ┌───────────────┐
 │   LLM Agent   │ ◄── Parses intent and arguments, but CANNOT execute sensitive tools
 └───────┬───────┘
         ▼
 ┌───────────────┐
 │ Deterministic │
 │  Safety Gate  │ ◄── Pure Python validation (RBAC, Threshold checks)
 └───────┬───────┘
         │
         ├─► [ALLOW] ──► Execute Tool
         ├─► [REVIEW] ─► Interrupt Graph for Human Approval (HITL)
         └─► [BLOCK] ──► Terminate execution with explanation
```

---

## 2. Core Features & Architecture

The framework is architected using a clean **Core / Adapter** pattern, allowing you to easily swap the domain-specific logic while keeping the control flow logic intact.

### Core Engine (Reusable & Zero-Modification)
* **LangGraph Orchestrator**: Manages state, execution paths, and human-in-the-loop interrupts.
* **Forced RAG Pipeline**: Ensures contextual domain knowledge is retrieved *before* the agent responds.
* **Three-Tier Gate Engine (`risk_gate`)**: Processes tool calls through strict policies, categorizing outcomes into `ALLOW`, `REVIEW` (HITL Interrupt), or `BLOCK`.
* **Evaluation Harness**: Automatically measures agent accuracy, tool selection, and RAG faithfulness against a customizable golden evaluation dataset.
* **MCP (Model Context Protocol) Wrapper**: Exposes validated tools securely via standard MCP interfaces.

### Adapters (Swap these 4 elements to port to any domain)
1. **Tool Interface**: Target API functions (e.g., payment, prescription lookup, contract editing).
2. **Policy Knowledge Base**: Text documents for RAG (e.g., refund rules, medical guidelines, standard NDAs).
3. **Deterministic Gate Rules**: Code-based constraints (e.g., transaction limits, role clearances).
4. **Golden Evaluation Dataset**: Benchmark dataset containing real-world test cases.

---

## 3. High-Stakes Domain Mapping

| Domain | Policy/RAG Adapter | Tool Adapter | Safety Gate Rules (Deterministic) |
|---|---|---|---|
| **Fintech / Payment** *(Current bundle)* | Refund & Settlement Policy | Core Ledger & Payment APIs | - Over $1,000: `REVIEW` (HITL)<br>- Over $1,500: `BLOCK`<br>- Unverified account: `BLOCK` |
| **Healthcare** | Medical Guidelines & Drug DB | Patient Record / Prescriber API | - Narcotic prescription: `BLOCK`<br>- Off-label drug: `REVIEW`<br>- Non-specialist prescriber: `BLOCK` |
| **Legaltech** | Contract Templates & Case Law | PDF Generator, Document Signer | - Settlement > $100k: `REVIEW`<br>- Modifying standard NDA: `REVIEW` |

---

## 4. Getting Started (Instantiation #1: Payment PoC)

This repository includes a pre-packaged **Payment Agent** instantiation as a reference implementation.

### Prerequisites

* Python 3.10+
* An active Anthropic Claude subscription (or set `ANTHROPIC_API_KEY` in environment)

### Setup

```bash
# Clone the repository
git clone https://github.com/your-username/pockit.git
cd pockit

# Set up virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Create .env and configure keys
cp .env.example .env
```

### Run Indexing & Demo

```bash
# 1. Index payment policies into Chroma DB
python -m src.rag.retriever

# 2. Run the E2E Demo showing ALLOW, REVIEW, and BLOCK paths
python -m src.run_demo
```

### Run Evaluation Suite

```bash
# Run the quantitative evaluation harness
python -m src.eval.run_eval
```

---

## 5. Quantitative Evaluation Results

The evaluation harness measures deterministic metrics separately from stochastic (LLM-based) metrics to guarantee true reproducibility.

| Dimension | Metric | Score | Note / Context |
|---|---|---|---|
| **Deterministic** | `risk_gate` Unit Test | **9/9** | Validates boundary value rules (e.g., $1,000 limit, RBAC checks) |
| **Deterministic** | `retrieval_precision@3` | **80%** | Measures if the correct policy section is within the top 3 RAG results |
| **Stochastic** | `tool_selection_accuracy` | **100%** | Measures LLM's accuracy in choosing the correct tool and parameters |

---

## 6. Project Directory Structure

```
.
├── src/
│   ├── gate/          # Core: deterministic threshold and RBAC evaluation
│   ├── rag/           # Core: policy indexing & forced retrieval logic
│   ├── eval/          # Core: golden dataset runner & evaluator
│   ├── tools/         # Adapter: domain-specific API interfaces
│   ├── graph.py       # Core: LangGraph configuration & interrupts
│   └── mcp_server.py  # Core: MCP wrapper exposing validated interfaces
├── data/              # Adapter: synthesis files and transaction records
└── docs/              # Research documentation & Korean translation
```

---

## 7. Documentation & Contributions

* For the Korean version of the documentation, please refer to [docs/README_ko.md](file:///Users/idong-won/projects/work/poc-payment-agent/docs/README_ko.md).
* For detailed market analysis and design decisions, see the files under [docs/benchmarking/](file:///Users/idong-won/projects/work/poc-payment-agent/docs/benchmarking/).
