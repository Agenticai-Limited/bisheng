# Bisheng Platform - Architecture & Handover Document

**Version**: 2.4.0-beta1
**Date**: March 17, 2026
**Repository**: Forked from [dataelement/bisheng](https://github.com/dataelement/bisheng)
**Active Branch**: `feature/dev` (development), `main` (production)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture Overview](#2-system-architecture-overview)
3. [Git Repository & Branch Strategy](#3-git-repository--branch-strategy)
4. [Directory Structure](#4-directory-structure)
5. [Backend Architecture](#5-backend-architecture)
6. [Frontend Architecture](#6-frontend-architecture)
7. [Database Schema](#7-database-schema)
8. [API Architecture](#8-api-architecture)
9. [Workflow Engine](#9-workflow-engine)
10. [LLM Management System](#10-llm-management-system)
11. [Knowledge Base & RAG System](#11-knowledge-base--rag-system)
12. [LinSight Agent System](#12-linsight-agent-system)
13. [Tool & MCP Management](#13-tool--mcp-management)
14. [Chat & Session Management](#14-chat--session-management)
15. [Celery Task Queue](#15-celery-task-queue)
16. [Configuration System](#16-configuration-system)
17. [Docker Deployment](#17-docker-deployment)
18. [CI/CD Pipeline](#18-cicd-pipeline)
19. [Security & Access Control](#19-security--access-control)
20. [Custom Modifications (feature/dev)](#20-custom-modifications-featuredev)
21. [Development Guide](#21-development-guide)
22. [Key Metrics](#22-key-metrics)
23. [Known Limitations & Future Considerations](#23-known-limitations--future-considerations)

---

## 1. Executive Summary

**Bisheng** is an open-source LLM application DevOps platform designed for enterprise scenarios. It provides a complete solution for building, deploying, and managing intelligent applications with support for:

- **Workflows**: Visual graph-based workflow builder (LangGraph-based)
- **Agents**: Expert-level AI agents via LinSight (AGL framework)
- **RAG**: Knowledge base with dual vector store (Milvus + Elasticsearch)
- **Multi-Model Orchestration**: 11+ LLM provider integrations
- **MCP Protocol**: Model Context Protocol tool management

Our fork adds **AWS Bedrock LLM integration** and **local Docker build configuration** on the `feature/dev` branch.

---

## 2. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend (React 18 + Vite)                   │
│                    Nginx Reverse Proxy (:3001)                  │
│  ┌─────────────────────┐  ┌──────────────────────────────────┐  │
│  │  Platform UI         │  │  Client (iframe components)      │  │
│  │  - Workflow Builder  │  │  - Embedded chat                 │  │
│  │  - Chat Interface    │  │  - Public endpoints              │  │
│  │  - Knowledge Mgmt    │  │                                  │  │
│  │  - Model Config      │  │                                  │  │
│  │  - Admin Panel       │  │                                  │  │
│  └─────────────────────┘  └──────────────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────────┘
                               │ HTTP / WebSocket
┌──────────────────────────────▼──────────────────────────────────┐
│                  FastAPI Backend (:7860)                         │
│                  Uvicorn ASGI, 8 workers                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────────┐  │
│  │ REST API │ │WebSocket │ │ Services │ │ Workflow Engine   │  │
│  │ v1       │ │ Streams  │ │ Layer    │ │ (LangGraph)       │  │
│  └──────────┘ └──────────┘ └──────────┘ └───────────────────┘  │
└───────┬──────────┬──────────┬──────────┬───────────────────────┘
        │          │          │          │
   ┌────▼───┐ ┌───▼────┐ ┌──▼───┐ ┌───▼──────────┐
   │ MySQL  │ │ Redis  │ │Celery│ │ LLM Providers│
   │ (3306) │ │ (6379) │ │Workers│ │ OpenAI, etc. │
   └────────┘ └────────┘ └──┬───┘ └──────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼─────────┐  ┌─────▼──────┐  ┌──────────▼──┐
   │ Milvus       │  │Elasticsearch│  │ MinIO       │
   │ Vector DB    │  │ Full-Text   │  │ Object Store│
   │ (19530)      │  │ (9200)      │  │ (9000/9001) │
   └──────┬───────┘  └────────────┘  └─────────────┘
          │
   ┌──────▼───────┐
   │ etcd         │
   │ Coordination │
   │ (2379)       │
   └──────────────┘
```

### Service Communication

| From | To | Protocol | Purpose |
|------|----|----------|---------|
| Browser | Nginx | HTTPS | Static assets, reverse proxy |
| Nginx | Backend | HTTP :7860 | API routing |
| Browser | Backend | WebSocket | Real-time chat streaming |
| Backend | MySQL | TCP :3306 | Persistent data storage |
| Backend | Redis | TCP :6379 | Cache, Celery broker, pub/sub |
| Backend | Milvus | gRPC :19530 | Vector similarity search |
| Backend | Elasticsearch | HTTP :9200 | Full-text search |
| Backend | MinIO | HTTP :9000 | File/object storage |
| Celery Workers | Redis | TCP :6379 | Task queue broker |
| Celery Workers | MySQL | TCP :3306 | Task result storage |
| Milvus | etcd | TCP :2379 | Metadata coordination |
| Milvus | MinIO | TCP :9000 | Vector data storage |

---

## 3. Git Repository & Branch Strategy

### Branch Architecture

```
main (production)
 └── feature/dev (active development)
```

- **`main`**: Production branch, tracks upstream `dataelement/bisheng` releases
- **`feature/dev`**: Our development branch with custom modifications

### Key Commits on `feature/dev` (ahead of main)

| Commit | Description |
|--------|-------------|
| `feat: add Bedrock embeddings support` | AWS Bedrock embedding client |
| `feat: Normalize Bedrock content blocks` | Streaming response normalization |
| `fix: Filter unsupported parameters for Bedrock` | Parameter compatibility |
| `feat: Simplify Bedrock LLM configuration` | Direct AWS credential passing |
| `build: Configure docker-compose local builds` | Local image building |
| `chore: update dependencies` | Backend dependency updates |

### Syncing with Upstream

```bash
# Add upstream remote (if not already added)
git remote add upstream https://github.com/dataelement/bisheng.git

# Fetch upstream changes
git fetch upstream

# Merge upstream main into our main
git checkout main
git merge upstream/main

# Rebase feature/dev on updated main
git checkout feature/dev
git rebase main
```

---

## 4. Directory Structure

```
bisheng/
├── docker/                              # Deployment configuration
│   ├── docker-compose.yml              # Main compose (updated for local builds)
│   ├── docker-compose-ft.yml           # Fine-tuning variant
│   ├── docker-compose-uns.yml          # Unstructured data variant
│   ├── docker-compose-office.yml       # Office document variant
│   ├── .env                            # Environment variables
│   ├── bisheng/
│   │   ├── config/config.yaml          # Main app configuration
│   │   └── entrypoint.sh              # Multi-mode startup script
│   ├── nginx/                          # Nginx reverse proxy config
│   ├── mysql/                          # MySQL init & data
│   ├── redis/                          # Redis config
│   └── data/                           # Persistent volumes
│
├── src/
│   ├── backend/                        # Python backend (~86K lines)
│   │   ├── bisheng/                   # Main application package
│   │   │   ├── main.py               # FastAPI app entry point
│   │   │   ├── api/                   # REST API layer
│   │   │   │   ├── v1/               # API version 1 routers
│   │   │   │   ├── services/         # Business logic services
│   │   │   │   └── utils/            # API utilities
│   │   │   ├── core/                  # Core infrastructure
│   │   │   │   ├── ai/               # LLM integrations
│   │   │   │   ├── cache/            # Redis client
│   │   │   │   ├── database/         # DB connections & Alembic migrations
│   │   │   │   ├── search/           # Search functionality
│   │   │   │   ├── storage/          # MinIO storage client
│   │   │   │   └── vectorstore/      # Vector DB integrations
│   │   │   ├── database/             # SQLAlchemy ORM
│   │   │   │   └── models/           # 25 database model files
│   │   │   ├── workflow/              # Workflow execution engine
│   │   │   │   ├── graph/            # LangGraph state machine
│   │   │   │   ├── nodes/            # 11+ node type implementations
│   │   │   │   ├── edges/            # Edge definitions
│   │   │   │   └── callback/         # Event callbacks
│   │   │   ├── llm/                   # LLM management
│   │   │   │   ├── domain/           # LLM domain models
│   │   │   │   └── api/              # LLM API endpoints
│   │   │   ├── knowledge/            # RAG / Knowledge base
│   │   │   │   ├── api/              # Knowledge API
│   │   │   │   ├── domain/           # RAG domain logic
│   │   │   │   └── rag/              # RAG implementations
│   │   │   ├── linsight/             # Agent system (AGL-based)
│   │   │   │   ├── api/              # Agent APIs
│   │   │   │   ├── domain/           # Agent domain logic
│   │   │   │   └── worker.py         # Async task execution
│   │   │   ├── mcp_manage/           # MCP protocol support
│   │   │   ├── tool/                  # Tool/function management
│   │   │   ├── user/                  # User & auth management
│   │   │   ├── chat/                  # Chat session management
│   │   │   ├── worker/               # Celery task definitions
│   │   │   ├── services/             # Shared business services
│   │   │   ├── interface/            # Component interfaces
│   │   │   └── common/               # Shared utilities
│   │   ├── pyproject.toml            # Python dependencies (uv)
│   │   ├── Dockerfile                # Backend container build
│   │   └── entrypoint.sh            # Container startup
│   │
│   └── frontend/                      # React frontend (614 TS/TSX files)
│       ├── platform/                  # Main platform UI
│       │   ├── src/
│       │   │   ├── pages/            # Page components
│       │   │   │   ├── BuildPage/    # Workflow builder
│       │   │   │   ├── ChatAppPage/  # Chat interfaces
│       │   │   │   ├── KnowledgePage/# Knowledge base UI
│       │   │   │   ├── ModelPage/    # Model configuration
│       │   │   │   ├── Dashboard/    # Dashboard
│       │   │   │   ├── SystemPage/   # System settings
│       │   │   │   └── EvaluationPage/# Evaluation UI
│       │   │   ├── components/       # Reusable UI components
│       │   │   ├── CustomNodes/      # Custom flow node renderers
│       │   │   ├── controllers/      # API client controllers
│       │   │   ├── store/            # Zustand state stores
│       │   │   ├── types/            # TypeScript type definitions
│       │   │   └── routes/           # React Router config
│       │   ├── package.json          # NPM dependencies
│       │   └── Dockerfile            # Frontend container build
│       └── client/                    # Embedded iframe client
│
├── .github/workflows/                 # GitHub Actions CI/CD
│   ├── base_ci.yml                   # Base image build (ARM/AMD)
│   ├── ci.yml                        # Main CI pipeline
│   └── release.yml                   # Release workflow
└── .drone.yml                         # Legacy Drone CI config
```

---

## 5. Backend Architecture

### Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | FastAPI | 0.120.4+ |
| ASGI Server | Uvicorn | latest |
| Language | Python | 3.10+ |
| ORM | SQLAlchemy / SQLModel | latest |
| Task Queue | Celery | 5.5.3+ |
| LLM Framework | LangChain | 0.3.23+ |
| Agent Framework | LangGraph | 0.3.27+ |
| RAG Framework | LlamaIndex | 0.12.52+ |
| Vector DB Client | pymilvus | 2.5.10+ |
| OpenAI Client | openai | 1.68.2+ |
| Web Scraping | Playwright | 1.57.0 |
| Package Manager | uv | latest |
| Logging | loguru | latest |

### Application Entry Point

**File**: `src/backend/bisheng/main.py`

The FastAPI application initializes with:
1. CORS middleware configuration
2. Request/response logging middleware
3. Exception handlers
4. Router registration (16+ routers)
5. Static file serving
6. Database connection pool
7. Redis connection

### Backend Layered Architecture

```
┌─────────────────────────────────┐
│         API Layer (FastAPI)      │  ← HTTP/WebSocket handlers
│         src/backend/bisheng/api/ │
├─────────────────────────────────┤
│        Service Layer             │  ← Business logic
│        api/services/             │
├─────────────────────────────────┤
│        Domain Layer              │  ← Domain models & rules
│        llm/domain/, knowledge/   │
│        domain/, linsight/domain/ │
├─────────────────────────────────┤
│        Data Layer                │  ← ORM models & repositories
│        database/models/          │
├─────────────────────────────────┤
│        Core Infrastructure       │  ← DB, cache, storage, vector
│        core/                     │
└─────────────────────────────────┘
```

---

## 6. Frontend Architecture

### Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | React | 18.3.1 |
| Build Tool | Vite | 5.3.1 |
| Language | TypeScript | 5.4.5 |
| Styling | TailwindCSS | 3.4.4 |
| UI Components | Radix UI | latest |
| State Management | Zustand | 4.5.2 |
| HTTP Client | Axios | 1.7.2 |
| Graph/Flow Editor | @xyflow/react | 12.8.4 |
| Code Editor | React Ace | latest |
| Internationalization | i18next | 23.12.1 |
| Charts | Recharts | 2.12.7 |
| Icons | Lucide React | latest |

### Page Structure

| Page | Path | Purpose |
|------|------|---------|
| BuildPage | `/build` | Visual workflow/flow builder with drag-and-drop nodes |
| ChatAppPage | `/chat` | Chat interface for testing and using apps |
| KnowledgePage | `/knowledge` | Knowledge base upload, chunking, management |
| ModelPage | `/model` | LLM provider & model configuration |
| Dashboard | `/dashboard` | Overview, statistics, recent activity |
| SystemPage | `/system` | Admin: users, roles, groups, RBAC |
| EvaluationPage | `/evaluation` | Model evaluation and benchmarking |
| DataSetPage | `/dataset` | Dataset management |
| LogPage | `/log` | Activity and audit log viewer |
| DiffFlowPage | `/diff` | Workflow version comparison |

### State Management Pattern

```
Zustand Store (global)
├── User auth state
├── Theme/UI preferences
├── Alert notifications
└── Active workspace context

React Query (server state)
├── API data caching
├── Optimistic updates
└── Background refetching

Component Local State
├── Form inputs
├── Modal visibility
└── Drag-and-drop state
```

---

## 7. Database Schema

### Core Tables (25 models)

Located in `src/backend/bisheng/database/models/`:

#### User & Access Control

| Table | File | Purpose |
|-------|------|---------|
| `user` | `user.py` | User accounts (name, email, password hash) |
| `role` | `role.py` | Role definitions (admin, user, custom) |
| `role_access` | `role_access.py` | Permission matrix (role → resource → access type) |
| `group` | `group.py` | User groups |
| `group_resource` | `group_resource.py` | Group-level resource permissions |
| `user_group` | `user_group.py` | User-group membership |
| `user_link` | `user_link.py` | User federation/linking |

#### Application & Workflow

| Table | File | Purpose |
|-------|------|---------|
| `flow` | `flow.py` | Workflows, chats, apps (polymorphic via `flow_type`) |
| `flowversion` | `flow_version.py` | Version history for flows (JSON `data` column) |
| `assistant` | `assistant.py` | AI assistant configurations |
| `component` | `component.py` | Custom component definitions |

#### Chat & Messages

| Table | File | Purpose |
|-------|------|---------|
| `session` | `session.py` | Chat sessions/conversations |
| `message` | `message.py` | Individual messages with metadata |
| `recall_chunk` | `recall_chunk.py` | Retrieved knowledge chunks per message |

#### Knowledge Base

| Table | File | Purpose |
|-------|------|---------|
| `dataset` | `dataset.py` | Knowledge base collections |

#### Evaluation & Analytics

| Table | File | Purpose |
|-------|------|---------|
| `evaluation` | `evaluation.py` | Model evaluation records |
| `audit_log` | `audit_log.py` | Access audit trail |
| `report` | `report.py` | Generated reports |
| `tag` | `tag.py` | Tag/classification system |

#### Task Management

| Table | File | Purpose |
|-------|------|---------|
| `mark_task` | `mark_task.py` | Task definitions |
| `mark_record` | `mark_record.py` | Task execution records |
| `mark_app_user` | `mark_app_user.py` | Task-app-user mappings |

#### Configuration

| Table | File | Purpose |
|-------|------|---------|
| `template` | `template.py` | Reusable templates |
| `variable_value` | `variable_value.py` | Dynamic variable storage |
| `invite_code` | `invite_code.py` | User invitation codes |

### Migration System

- **Tool**: Alembic
- **Location**: `src/backend/bisheng/core/database/alembic/`
- **Latest Migration**: `v2_3_0_beta1` (revision `9ba42685e830`)
- **Sensitive Fields**: Database URLs encrypted with Fernet

### Key Schema: `flowversion`

This is the most important table for workflow development:

```sql
CREATE TABLE flowversion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    flow_id VARCHAR(64) NOT NULL,     -- References flow.id
    name VARCHAR(64),                  -- Version label (v0, v1, v2, ...)
    data JSON,                         -- Full workflow definition (nodes, edges, params)
    -- ... timestamps
);
```

The `data` JSON column contains the entire workflow graph:
```json
{
  "edges": [...],       // Connections between nodes
  "nodes": [            // Node definitions
    {
      "id": "code_xxxxx",
      "type": "flowNode",
      "data": {
        "group_params": [
          {
            "params": [
              {"key": "code", "value": "def main(...): ..."},
              {"key": "code_input", "value": [...]},
              {"key": "code_output", "value": [...]}
            ]
          }
        ]
      }
    }
  ],
  "viewport": {...}
}
```

---

## 8. API Architecture

### REST API Endpoints

**Base URL**: `/api/v1/` (routed via Nginx to backend :7860)

| Router | Path | Purpose |
|--------|------|---------|
| chat | `/api/v1/chat` | Chat operations, message management, streaming |
| workflow | `/api/v1/workflow` | Workflow CRUD & execution |
| assistant | `/api/v1/assistant` | AI assistant management |
| flows | `/api/v1/flows` | Flow/app CRUD |
| component | `/api/v1/component` | Component registry & templates |
| endpoints | `/api/v1/endpoints` | Public endpoint management |
| validate | `/api/v1/validate` | Flow validation |
| skillcenter | `/api/v1/skillcenter` | Skill/preset management |
| user | `/api/v1/user` | User profile & authentication |
| variable | `/api/v1/variable` | Variable management |
| audit | `/api/v1/audit` | Audit log retrieval |
| evaluation | `/api/v1/evaluation` | Evaluation features |
| usergroup | `/api/v1/usergroup` | User group management |
| tool | `/api/v1/tool` | Tool/function management |
| tag | `/api/v1/tag` | Tagging system |
| report | `/api/v1/report` | Report generation |

### WebSocket Endpoints

- **Chat Streaming**: `/api/v1/chat/run_stream` — real-time LLM response streaming
- **Workflow Callbacks**: Event-driven progress updates

### Response Format

All API responses follow a consistent structure:

```json
{
  "status_code": 200,
  "status_message": "Success",
  "data": { ... }
}
```

### Authentication

- **Method**: JWT bearer tokens in `Authorization` header
- **User Injection**: `UserPayload.get_login_user` via FastAPI `Depends()`
- **First User**: Automatically assigned admin role on registration

### Interactive API Docs

FastAPI auto-generates OpenAPI documentation:
- Swagger UI: `http://localhost:7860/docs`
- ReDoc: `http://localhost:7860/redoc`

---

## 9. Workflow Engine

### Architecture

The workflow engine is built on **LangGraph** (`StateGraph`) and provides visual, graph-based workflow execution.

**Location**: `src/backend/bisheng/workflow/`

```
workflow/
├── graph/
│   ├── graph_engine.py      # Main engine: builds & executes LangGraph
│   ├── graph_state.py       # State container for execution context
│   └── edge_manage.py       # Edge routing & dependency tracking
├── nodes/                    # Node type implementations
│   ├── start/               # Workflow entry point
│   ├── output/              # Result output (supports interrupts)
│   ├── code/                # Python code execution (sandboxed)
│   ├── llm/                 # LLM inference nodes
│   ├── agent/               # Agentic reasoning nodes
│   ├── rag/                 # RAG/knowledge retrieval
│   ├── input/               # User input handling
│   ├── knowledge_retriever/ # Knowledge base query
│   └── condition/           # Conditional branching
├── edges/                    # Edge definitions
└── callback/                 # Event streaming callbacks
```

### Execution Flow

```
1. User triggers workflow (via chat or API)
         │
2. GraphEngine loads workflow definition from flowversion.data
         │
3. Nodes assembled into LangGraph StateGraph
         │
4. Edges wired based on workflow connections
         │
5. Execution begins at Start node
         │
6. State flows through nodes (fan-in/fan-out supported)
         │
7. LLM/Code/RAG nodes process data
         │
8. Output node returns result (streamed via WebSocket)
         │
9. Messages saved to database
```

### Node Types

| Node | Purpose | Key Features |
|------|---------|-------------|
| Start | Entry point | Defines initial variables |
| Input | User input | Form fields with validation |
| LLM | LLM inference | Multi-provider, prompt templates |
| Code | Python execution | Custom logic, API calls |
| Agent | Agentic reasoning | Tool use, multi-step reasoning |
| RAG | Knowledge retrieval | Vector search + reranking |
| Knowledge Retriever | KB query | Direct knowledge base access |
| Condition | Branching | Expression-based routing |
| Output | Result output | Streaming, formatted responses |

### Key Configuration

- **Recursion Limit**: 50 steps (configurable)
- **Async Support**: Both sync and async execution paths
- **Interrupts**: Human-in-the-loop via fake output nodes
- **Fan-in/Fan-out**: Parallel execution with state merging

---

## 10. LLM Management System

### Supported Providers

**Location**: `src/backend/bisheng/llm/domain/llm/llm.py`

| # | Provider | Class | Notes |
|---|----------|-------|-------|
| 1 | OpenAI | `ChatOpenAI` | GPT-4, GPT-3.5, etc. |
| 2 | Azure OpenAI | `AzureChatOpenAI` | Enterprise Azure deployment |
| 3 | Ollama | `ChatOllama` | Local models |
| 4 | Anthropic | `ChatAnthropic` | Claude models |
| 5 | Google GenAI | `ChatGoogleGenerativeAI` | Gemini models |
| 6 | Deepseek | `CustomChatDeepSeek` | Deepseek models |
| 7 | Tongyi (Alibaba) | `CustomChatTongYi` | Qwen models |
| 8 | Moonshot | `CustomMoonshot` | Kimi models |
| 9 | ZhipuAI | `ChatZhipuAI` | GLM models |
| 10 | MiniMax | `MiniMaxChat` | MiniMax models |
| 11 | **AWS Bedrock** | `CustomChatBedrock` | **NEW in feature/dev** |

### Configuration Priority

```
Runtime Parameters (user-provided)
    ↓ overrides
Advanced Parameters (model-level config)
    ↓ overrides
Model Configuration (admin-set defaults)
    ↓ overrides
Server Configuration (provider base URL, API keys)
```

### Bedrock Integration (Custom, feature/dev)

**New files**:
- `src/backend/bisheng/core/ai/llm/custom_chat_bedrock.py`

**Features**:
- AWS Bedrock Converse model support
- Direct AWS credential passing (access key + secret key)
- Bedrock embeddings client
- Parameter filtering for unsupported Converse options
- Content block normalization for streaming responses

### Embedding Providers

Multiple embedding backends for vector search:
- OpenAI embeddings
- AWS Bedrock embeddings (NEW)
- Ollama embeddings
- Custom embedding implementations

---

## 11. Knowledge Base & RAG System

### Architecture

**Location**: `src/backend/bisheng/knowledge/`

```
Knowledge Base
├── Document Upload (MinIO storage)
│   └── Supported: pdf, docx, pptx, xlsx, txt, md,
│                   html, csv, jpg, png, bmp, tiff
├── Document Processing (Celery async)
│   ├── Text extraction
│   ├── Chunking (configurable size + overlap)
│   └── Metadata preservation
├── Vector Store (dual)
│   ├── Milvus (semantic similarity search)
│   └── Elasticsearch (full-text + hybrid search)
└── RAG Pipeline
    ├── Query embedding
    ├── Vector similarity retrieval
    ├── Reranking (cross-encoder)
    └── Context injection into LLM prompt
```

### Vector Store Configuration

**Milvus**:
```yaml
vector_stores:
  milvus:
    connection_args: '{"host":"milvus","port":"19530"}'
    is_partition: true
    partition_suffix: '1'
```

**Elasticsearch**:
```yaml
vector_stores:
  elasticsearch:
    url: 'http://elasticsearch:9200'
    # Optional: ssl, auth
```

---

## 12. LinSight Agent System

### Overview

**Location**: `src/backend/bisheng/linsight/`

LinSight provides expert-level AI agents using the **Agent Guidance Language (AGL)** framework.

| Component | File | Purpose |
|-----------|------|---------|
| SOP Management | `domain/services/sop_manage.py` | Standard Operating Procedure definitions |
| Task Execution | `domain/task_exec.py` | Agent task orchestration |
| Session Versions | `domain/models/linsight_session_version.py` | Session state tracking |
| Worker | `worker.py` | Async background execution |

### Configuration

- **Max Workers**: 4 processes
- **Max Concurrent Tasks**: 5
- **Execution Mode**: Independent worker process or thread pool
- **Progress**: Callback-based real-time streaming

---

## 13. Tool & MCP Management

### Tool System

**Location**: `src/backend/bisheng/tool/`

- Import external APIs via OpenAPI spec
- Define custom Python tools
- Function calling integration with LLMs
- Error handling and retry logic

### MCP (Model Context Protocol) Support

**Location**: `src/backend/bisheng/mcp_manage/`

| Feature | Description |
|---------|-------------|
| Stdio connections | Process-based MCP servers |
| SSE streaming | Server-Sent Events for real-time data |
| Tool registration | Dynamic tool discovery from MCP servers |
| Async client | Non-blocking MCP communication |

---

## 14. Chat & Session Management

### Components

**Location**: `src/backend/bisheng/chat/` + `src/backend/bisheng/chat_session/`

### Chat Manager

Central orchestration for all chat interactions:
- Session lifecycle management
- Message routing (workflow vs. assistant vs. direct)
- WebSocket stream management
- History persistence

### Message Model

```
Message
├── id (UUID)
├── session_id (FK → session)
├── message_type (user / assistant / system)
├── content (text)
├── metadata (JSON)
│   ├── source (workflow node, tool, etc.)
│   ├── tokens_used
│   └── model_name
├── feedback (like / dislike / null)
├── is_sensitive (boolean)
└── created_at (timestamp)
```

---

## 15. Celery Task Queue

### Queue Architecture

**Location**: `src/backend/bisheng/worker/`

```
Redis (Broker)
    │
    ├── knowledge_celery    → Document processing (20 threads)
    ├── workflow_celery      → Workflow execution (100 threads, single process!)
    ├── celery (default)     → Telemetry, misc tasks (100 threads)
    └── beat                 → Scheduled/periodic tasks
```

### Key Constraints

- **Workflow workers MUST run single process** (LangGraph limitation)
- **Knowledge workers**: 20 concurrent threads for file processing
- **Beat scheduler**: One instance only (no duplicates)

### Task Categories

| Queue | Tasks | Concurrency |
|-------|-------|-------------|
| knowledge_celery | PDF parsing, OCR, chunking, embedding | 20 threads |
| workflow_celery | Long-running workflow execution | 100 threads (1 process) |
| celery | Telemetry aggregation, cleanup | 100 threads |
| beat | Periodic maintenance, statistics | 1 (scheduler) |

---

## 16. Configuration System

### Main Config File

**Path**: `docker/bisheng/config/config.yaml`

```yaml
# ===== Database =====
database_url: "mysql+pymysql://root:ENCRYPTED_PASSWORD@mysql:3306/bisheng"
# Note: Password is Fernet-encrypted

# ===== Cache & Message Queue =====
redis_url: "redis://redis:6379/1"
celery_redis_url: "redis://redis:6379/2"

# ===== Vector Stores =====
vector_stores:
  milvus:
    connection_args: '{"host":"milvus","port":"19530"}'
    is_partition: true
    partition_suffix: '1'
  elasticsearch:
    url: 'http://elasticsearch:9200'

# ===== Object Storage (MinIO) =====
object_storage:
  type: minio
  minio:
    endpoint: 'minio:9000'
    access_key: 'minioadmin'
    secret_key: 'minioadmin'
    public_bucket: 'bisheng'
    tmp_bucket: 'tmp-dir'

# ===== Logging =====
logger_conf:
  level: DEBUG
  handlers:
    - sink: "/app/data/bisheng.log"
      level: INFO
      rotation: "00:00"
      retention: "3 Days"
```

### Environment Variables (`.env`)

| Variable | Purpose |
|----------|---------|
| `DOCKER_VOLUME_DIRECTORY` | Base path for Docker volumes |
| `OPENAI_API_KEY` | OpenAI API credentials |
| `ANTHROPIC_API_KEY` | Anthropic API credentials |
| `AWS_ACCESS_KEY_ID` | AWS credentials (for Bedrock) |
| `AWS_SECRET_ACCESS_KEY` | AWS credentials (for Bedrock) |

---

## 17. Docker Deployment

### Services Overview

| Service | Port(s) | Image | Health Check |
|---------|---------|-------|-------------|
| **mysql** | 3306 | mysql:8.0 | `mysqladmin ping` |
| **redis** | 6379 | redis:7.0.4 | `redis-cli ping` |
| **backend** | 7860 | bisheng-backend:mu (local build) | `GET /health` |
| **backend_worker** | — | bisheng-backend:mu (local build) | — |
| **frontend** | 3001 | bisheng-frontend:mu (local build) | — |
| **elasticsearch** | 9200, 9300 | elasticsearch:8.12.0 | — |
| **milvus** | 19530, 9091 | milvus:v2.5.10 | — |
| **etcd** | 2379 | etcd:3.5.18 | — |
| **minio** | 9000, 9001 | minio:latest | `curl /minio/health/live` |

### Build Configuration (feature/dev)

Changed from pulling pre-built images to **local builds**:

```yaml
# docker-compose.yml (feature/dev changes)
backend:
  build:
    context: ../src/backend
    dockerfile: Dockerfile
  image: bisheng-backend:mu

frontend:
  build:
    context: ../src/frontend
    dockerfile: platform/Dockerfile
  image: bisheng-frontend:mu
```

### Startup Commands

```bash
# Start entire stack
cd docker
docker compose -f docker-compose.yml -p bisheng up -d

# Rebuild after code changes
docker compose -f docker-compose.yml -p bisheng up -d --build

# View logs
docker compose -p bisheng logs -f backend
docker compose -p bisheng logs -f backend_worker

# Stop
docker compose -p bisheng down
```

### Startup Modes (entrypoint.sh)

The backend container supports multiple startup modes:

| Mode | Command | Purpose |
|------|---------|---------|
| `api` (default) | `uvicorn ... --workers 8` | FastAPI server |
| `worker` | All workers combined | Celery workers + beat |
| `knowledge` | Knowledge queue only | Document processing |
| `workflow` | Workflow queue only | Workflow execution |
| `beat` | Beat scheduler only | Periodic tasks |
| `linsight` | Agent worker only | Agent execution |

---

## 18. CI/CD Pipeline

### GitHub Actions

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `base_ci.yml` | Tag `base.v*` | Build base Docker image (ARM64 + AMD64) |
| `ci.yml` | Push/PR | Build & test backend, worker, frontend |
| `release.yml` | Release tag | Publish release images |

### Build Matrix

- **Platforms**: Linux ARM64 + AMD64
- **Registry**: Docker Hub (`dataelement/bisheng-*`)
- **Notifications**: Feishu webhook on completion

### Local Development Build

```bash
# Backend
cd src/backend
docker build -t bisheng-backend:mu .

# Frontend
cd src/frontend
docker build -f platform/Dockerfile -t bisheng-frontend:mu .
```

---

## 19. Security & Access Control

### Authentication

- **JWT Tokens**: Configurable expiry
- **First User**: Auto-assigned admin role
- **Captcha**: Optional for registration
- **Password Storage**: Hashed (not plaintext)

### Authorization (RBAC)

| Access Type | Scope |
|-------------|-------|
| `FLOW_READ` / `FLOW_WRITE` | Workflow/flow access |
| `ASSISTANT_READ` / `ASSISTANT_WRITE` | Assistant management |
| `WORKFLOW_READ` / `WORKFLOW_WRITE` | Workflow execution |
| `DATASET_READ` / `DATASET_WRITE` | Knowledge base access |
| `GROUP_READ` / `GROUP_WRITE` | Group management |

### Data Security

| Measure | Implementation |
|---------|---------------|
| Config encryption | Fernet-encrypted database URLs and secrets |
| SSL/TLS | Configurable for Elasticsearch, external APIs |
| Audit logging | User action tracking in `audit_log` table |
| API key storage | Environment variables, not in code |

---

## 20. Custom Modifications (feature/dev)

### 1. AWS Bedrock Integration

**Files added/modified**:

| File | Change |
|------|--------|
| `src/backend/bisheng/core/ai/llm/custom_chat_bedrock.py` | **NEW** — Bedrock Converse model client |
| `src/backend/bisheng/llm/domain/llm/llm.py` | Bedrock parameter handling & initialization |
| `src/backend/bisheng/llm/domain/llm/embedding.py` | Bedrock embeddings client |
| `src/backend/bisheng/llm/domain/const.py` | Bedrock model type constant |
| `src/frontend/platform/public/models/data.json` | Bedrock model definitions (36+ lines) |
| `src/frontend/platform/src/pages/ModelPage/manage/CustomForm.tsx` | Bedrock form fields (26+ lines) |
| `src/frontend/platform/src/util/advancedParamsTemplates.ts` | Bedrock advanced parameters |

**Key implementation details**:
- Direct AWS credential passing (no IAM role required)
- Parameter filtering for unsupported Converse model options
- Content block normalization for streaming responses
- Frontend model selection and parameter configuration UI

### 2. Docker Compose Local Build

Changed from pulling pre-built images (`dataelement/bisheng-*`) to building locally from source:
- Enables faster development iteration
- Custom image tags (`bisheng-backend:mu`, `bisheng-frontend:mu`)
- No dependency on upstream Docker Hub releases

### 3. Dependency Updates

- Backend `pyproject.toml` updated with new dependencies
- Project configuration version bumped to 2.4.0-beta1

---

## 21. Development Guide

### Prerequisites

| Requirement | Minimum |
|-------------|---------|
| Docker & Docker Compose | 1.25.1+ |
| CPU | 4+ cores |
| RAM | 16+ GB |
| Python | 3.10+ (for local backend dev) |
| Node.js | 18+ (for local frontend dev) |

### Quick Start (Docker)

```bash
# Clone the repo
git clone <your-fork-url>
cd bisheng

# Switch to dev branch
git checkout feature/dev

# Start all services
cd docker
docker compose -f docker-compose.yml -p bisheng up -d

# Wait for health checks to pass (~60s)
docker compose -p bisheng ps

# Access
# Frontend: http://localhost:3001
# Backend API: http://localhost:7860
# API Docs: http://localhost:7860/docs
# MinIO Console: http://localhost:9001
```

### Local Backend Development

```bash
cd src/backend

# Install dependencies
pip install uv
uv pip install -e .

# Set environment
export BISHENG_CONFIG_PATH=/path/to/config.yaml

# Run with auto-reload
PYTHONPATH=. uvicorn bisheng.main:app --reload --port 7860
```

### Local Frontend Development

```bash
cd src/frontend/platform

# Install dependencies
npm install --registry=https://registry.npmmirror.com

# Start dev server (Vite, port 5173)
npm run dev
```

### Key Files to Modify

| Task | Files |
|------|-------|
| Add new workflow node | `src/backend/bisheng/workflow/nodes/` |
| Add new LLM provider | `src/backend/bisheng/llm/domain/llm/llm.py` |
| Add new API endpoint | `src/backend/bisheng/api/v1/` |
| Add database table | `src/backend/bisheng/database/models/` |
| Modify frontend page | `src/frontend/platform/src/pages/` |
| Add UI component | `src/frontend/platform/src/components/` |
| Change configuration | `docker/bisheng/config/config.yaml` |

### Modifying Workflow Code Nodes via Database

Workflow code is stored in the `flowversion` table as JSON. To update code nodes programmatically:

```python
import json
import subprocess

# 1. Export workflow data
# mysql -h HOST -u root -pPASS bisheng -N --raw \
#   -e "SELECT data FROM flowversion WHERE id=N;" > workflow.json

# 2. Parse and modify
with open('workflow.json') as f:
    data = json.load(f)

for node in data['nodes']:
    if node['id'] == 'code_XXXXX':
        for group in node['data']['group_params']:
            for param in group['params']:
                if param['key'] == 'code':
                    param['value'] = new_code_string

# 3. Write back (be careful with escaping!)
# Note: Bisheng UI may cache old data. Close and reopen
# the workflow editor after DB updates.
```

> **Warning**: Bisheng UI caches workflow data in browser memory. After direct database updates, you must close and reopen the workflow editor to see changes.

### Health Checks

```bash
# Backend API
curl http://localhost:7860/health

# MySQL
docker exec bisheng-mysql-1 mysqladmin ping -u root -p

# Redis
docker exec bisheng-redis-1 redis-cli ping

# Elasticsearch
curl http://localhost:9200/_cluster/health

# MinIO
curl http://localhost:9000/minio/health/live
```

---

## 22. Key Metrics

| Metric | Value |
|--------|-------|
| Backend code | ~86,000 lines Python |
| Frontend code | 614 TypeScript/TSX files |
| Database models | 25 core tables |
| API routers | 16+ |
| Workflow node types | 11+ |
| LLM providers | 11 (including Bedrock) |
| Frontend pages | 10+ |
| Docker services | 9 |
| Supported file types | 19 document formats |
| Platform version | 2.4.0-beta1 |

---

## 23. Known Limitations & Future Considerations

### Current Limitations

| Issue | Impact | Mitigation |
|-------|--------|------------|
| Single MySQL instance | SPOF for data layer | Needs replication/clustering for HA |
| Single Redis instance | SPOF for cache/queue | Needs Sentinel or cluster |
| Workflow workers: single process only | Limits workflow throughput | LangGraph constraint |
| ibm-db not supported on ARM64 | CI build workaround | Filtered in CI pipeline |
| Bisheng UI caches workflow data | DB-direct edits may not reflect | Close/reopen workflow editor |

### Production Hardening Checklist

- [ ] MySQL replication or Galera cluster
- [ ] Redis Sentinel or cluster mode
- [ ] Load balancer (HAProxy/ALB) in front of backend instances
- [ ] SSL/TLS certificates for all services
- [ ] CDN for static frontend assets
- [ ] Database backup and disaster recovery plan
- [ ] Monitoring stack (Prometheus + Grafana)
- [ ] Log aggregation (ELK or similar)
- [ ] Rate limiting and DDoS protection
- [ ] Secrets management (Vault or AWS Secrets Manager)

### Extension Points

| Extension | How To |
|-----------|--------|
| New LLM provider | Implement in `llm/domain/llm/llm.py`, add frontend config in `models/data.json` |
| New workflow node | Create directory in `workflow/nodes/`, extend `BaseNode` |
| New vector store | Implement adapter in `core/vectorstore/` |
| New tool type | Define in `tool/`, register via API |
| Custom UI component | Add to `frontend/platform/src/components/` |

---

## Appendix: Useful Commands

```bash
# View all running containers
docker compose -p bisheng ps

# Rebuild specific service
docker compose -p bisheng up -d --build backend

# Database shell
docker exec -it bisheng-mysql-1 mysql -u root -p bisheng

# Redis shell
docker exec -it bisheng-redis-1 redis-cli

# Backend logs (follow)
docker compose -p bisheng logs -f backend backend_worker

# Check Milvus collections
docker exec -it bisheng-milvus-standalone-1 /bin/bash

# Export workflow from database
mysql -h HOST -u root -pPASS bisheng -N --raw \
  -e "SELECT data FROM flowversion WHERE flow_id='XXX' AND name='v6';" > workflow.json
```

---

## 24. AWS Dev Environment

The development environment is deployed on AWS:

| Item | Value |
|------|-------|
| **AWS Account** | `432629721957` |
| **EC2 Instance** | `i-01f9fb0c0a9b6992c` |
| **IP Address** | `3.104.109.160` |
| **URL** | http://3.104.109.160:3001/ |
| **Login Email** | `mike.pang@agenticai.nz` |
| **Login Password** | `euyRty@12` |

---

## 25. Pending Items

1. **Rebrand Bisheng to Nova** — Replace the logo and name with our own branding (e.g., login page, sidebar logo, browser tab title). Config and logo images have been prepared on the `feature/dev` branch but the frontend Docker image needs to be rebuilt.
2. **Configure a dedicated domain for client testing** — Currently accessed via raw IP (`3.104.109.160:3001`). A proper domain name needs to be set up.
3. **Integrate PH0006 (Fraternal Bond) API** — 8 of 9 required Phoenix APIs are integrated. PH0006 is pending — Scott has not yet created the backend service. Once available, integrate it into the `code_phoenixApi.py` workflow node.
4. **Optimise login session management** — The current session handling needs improvement. Implement a globally maintained session with proper timeout, refresh, and state management across the workflow.

---

*Document generated: March 17, 2026 | Updated: March 25, 2026*
*For questions, contact the development team.*
