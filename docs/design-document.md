# Design Document: OEC Event Processing Service

## 1. Project Overview

### 1.1 Purpose
Create a scalable service to process Opsgenie events via OEC integration, with easily extendable event handlers.

### 1.2 Key Features
- Event processing from Opsgenie OEC integration
- Pluggable handler architecture
- Docker-based deployment
- Easy handler registration system
- Reusable services for external systems integration

## 2. System Architecture

### 2.1 High-Level Components

1. **Infrastructure Layer**
   - Docker containers
   - OEC Integration
   - Configuration files
   - Environment management

2. **Core Service Layer**
   - Event Router: Responsible for routing incoming events to appropriate handlers
   - Handler Registry: Manages registration and discovery of event handlers
   - Configuration Manager: Handles service configuration and environment variables

3. **Service Layer**
   - Kubernetes Service: Manages K8s cluster operations
     * Pod management
     * Deployment control
     * Service operations
     * Custom resource handling
   - AWS Service: Handles AWS infrastructure operations
     * EC2 management
     * S3 operations
     * Lambda functions
     * CloudWatch integration
   - ClickHouse Service: Database operations
     * Query execution
     * Data management
     * Schema operations
   - GitHub Service: Repository and code management
     * PR operations
     * Repository management
     * Issue tracking
     * Workflow management
   - Service Factory: Creates service instances with proper configuration

4. **Handler Layer**
   - Base Handler Interface: Common interface for all handlers
   - Specific Event Handlers: Individual handlers for different event types
   - Handler Factory: Creates handler instances based on event types

### 2.2 Component Details

#### 2.2.1 Core Service Structure
```
src/
├── core/
│   ├── __init__.py
│   ├── router.py          # Event routing logic
│   ├── registry.py        # Handler registration
│   └── config.py          # Configuration management
├── services/
│   ├── __init__.py
│   ├── base.py           # Base service interface
│   ├── kubernetes/
│   │   ├── __init__.py
│   │   ├── service.py    # K8s service implementation
│   │   └── types.py      # K8s related type definitions
│   ├── aws/
│   │   ├── __init__.py
│   │   ├── service.py    # AWS service implementation
│   │   └── types.py      # AWS related type definitions
│   ├── clickhouse/
│   │   ├── __init__.py
│   │   ├── service.py    # ClickHouse service implementation
│   │   └── types.py      # ClickHouse related type definitions
│   └── github/
│       ├── __init__.py
│       ├── service.py    # GitHub service implementation
│       └── types.py      # GitHub related type definitions
├── handlers/
│   ├── __init__.py
│   ├── base.py           # Base handler interface
│   ├── alert_handler.py  # Alert event handler
│   └── incident_handler.py # Incident event handler
├── utils/
│   ├── __init__.py
│   └── exceptions.py     # Custom exceptions
└── main.py              # Application entry point
```

## 3. Implementation Plan

### 3.1 Phase 1: Project Setup
1. Initialize project structure
2. Set up Docker and docker-compose
3. Configure dependency management
4. Set up service configurations

### 3.2 Phase 2: Service Layer Implementation
1. Implement base service interface
2. Create service factory
3. Implement individual services
   - Kubernetes service
   - AWS service
   - ClickHouse service
   - GitHub service
4. Add service tests

### 3.3 Phase 3: Core Implementation
1. Implement base handler interface
2. Create handler registry with service injection
3. Implement event router
4. Set up configuration management

### 3.4 Phase 4: Handler Implementation
1. Implement initial handlers using services
2. Create handler tests
3. Document handler creation process

### 3.5 Phase 5: Infrastructure
1. Configure networking
2. Create deployment scripts

## 4. Docker Configuration

### 4.1 Services
```yaml
# docker-compose.yml structure
services:
  app:
    build: .
    volumes:
      - ./src:/app/src
```


1. Set up initial project structure
2. Create Docker environment
3. Implement core components
4. Add initial handlers
5. Set up basic OEC integration

