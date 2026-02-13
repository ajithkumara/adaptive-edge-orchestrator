# System Architecture

The Adaptive Orchestrator dynamically balances processing workloads between Edge nodes and the Cloud based on real-time metrics, cost models, and anomaly detection.

```mermaid
graph TD
    subgraph "Edge Layer"
        EN[Edge Node] --> |"Telemetry/Logs"| PE[Processing Engine]
        PE --> |"Decision Request"| EN
    end

    subgraph "Orchestration Layer"
        EN --> |"GRPC/REST"| ORC[Orchestrator Controller]
        ORC --> |"Evaluate"| DE[Decision Engine]
        DE --> |"Lookup"| DL[Domain Logic]
        ORC --> |"Store"| SS[State Store]
    end

    subgraph "Cloud Layer"
        ORC --> |"Forwarding"| CI[Cloud Ingestion]
        CI --> |"Stream"| SA[Spark Analytics]
        SA --> |"Store"| DW[Delta Lake]
    end

    subgraph "Domain Layer"
        DL --> AN[Anomaly Rules]
        DL --> CM[Cost Models]
        DL --> PL[Policies]
    end

    EN -.-> |"Adaptive Redirect"| CI
```

## Responsibility Boundaries

- **Edge Layer**: Local ingestion, validation, and near-real-time inference.
- **Orchestration Layer**: Coordination of processing modes and centralized state management.
- **Cloud Layer**: Long-term storage, complex analytics, and global model training.
- **Domain Layer**: Pure business rules isolated from infrastructure concerns.
