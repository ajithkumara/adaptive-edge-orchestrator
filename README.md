# Adaptive Edge Orchestrator

A policy-driven adaptive edge–cloud orchestration engine that dynamically optimizes execution placement based on anomaly severity, cost models, and network conditions.

---

## 🚀 Overview

Adaptive Edge Orchestrator is a distributed control system designed to intelligently switch computation between edge and cloud environments in real time.

It enables:

- Autonomous execution mode switching
- Connectivity-aware failover
- Cost-aware compute placement
- Policy-driven anomaly response
- Resilient monitoring during network disruption

The system is built around a clean separation between:

- **Domain intelligence (pure decision logic)**
- **Edge execution layer**
- **Cloud analytics layer**
- **Orchestration control plane**

---

## 🧠 Core Concept

Traditional edge–cloud systems rely on static deployment strategies.  
This system introduces dynamic orchestration driven by:

- Anomaly scoring
- Severity classification
- Cost estimation models
- Budget constraints
- Network state awareness
- Policy-based mode transitions

The orchestrator continuously evaluates operational signals and determines whether workloads should execute:

- Fully at the edge
- Fully in the cloud
- In hybrid mode
- In degraded fail-safe mode

---

## 🏗 Architecture

The project is structured around strict architectural boundaries:

### `domain/`
Pure business logic:
- Anomaly scoring and severity rules
- Cost modeling and budgeting
- Policy validation and state transitions

No infrastructure dependencies.

### `edge/`
- Local inference
- Data buffering and replay
- Resource monitoring
- Connectivity handling

### `cloud/`
- Streaming ingestion
- Storage and analytics
- Governance and schema validation
- Explainability modules

### `orchestrator/`
- Decision engine
- Mode manager
- State coordination
- Policy enforcement

### `tests/`
- Unit tests (domain & orchestrator)
- Integration tests
- End-to-end scenarios

---

## 📊 Key Capabilities

- Adaptive anomaly-driven mode switching
- Replay-on-reconnect buffering strategy
- Cost-aware decision modeling
- Explicit state transition enforcement
- Monitoring-ready (Prometheus + Grafana)
- Benchmark simulation framework

---

## 🧪 Benchmarking & Experiments

The `experiments/` directory contains:

- Adaptive vs static baseline benchmarks
- Edge-only vs cloud-only comparisons
- Cost simulations
- Latency analysis notebooks

---

## 🛠 Local Development

### Start Edge
```bash
./scripts/start_edge.sh
