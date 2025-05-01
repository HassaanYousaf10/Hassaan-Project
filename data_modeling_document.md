# SmartField Inc. - Modern Data Lakehouse Architecture (Azure + Databricks)

This document explains how the provided architecture diagram fulfills the project deliverables for SmartField Inc., which aims to build a robust, ML-ready, governed data platform using Azure services and Databricks.

---

## 1. Architecture Diagram

### Modern Lakehouse Design on Cloud
The architecture is built on **Microsoft Azure** and **Databricks** as the core compute & lakehouse engine. It integrates structured, semi-structured, and unstructured data from various systems and pushes it through a well-defined layered storage (medallion) model. 

The overall components used include:

- Azure Data Factory (batch ingestion)
- Azure Event Hub (stream ingestion)
- Databricks AutoLoader (file-based streaming)
- Delta Lake (for all Bronze/Silver/Gold layers)
- Azure ML, Unity Catalog, Azure Purview, Azure Blob Storage, and MLflow for governance and AI workflows

### Data Flow: From Source to Consumption

Here’s how data moves:

- **Source Systems**:
    - SQL Server on Azure VM (Operational DB)
    - Azure IoT Hub (sensor telemetry)
    - Technician Mobile App (images, notes, GPS)
    - CRM (Dynamics 365)
    - Customer Support (ServiceNow/Zendesk)

- **Ingestion**:
    - **Batch**: Azure Data Factory ingests data from CRM, SQL, Ticketing
    - **Stream**: Azure Event Hub handles IoT
    - **File Streams**: Databricks Autoloader for mobile app data

- **Raw/Bronze Layer**:
    - Data stored in Delta Lake as-is for auditability and recovery

- **Cleansed/Silver Layer**:
    - dbt handles SQL transformation, deduplication, schema standardization
    - Organizes by business themes (telemetry, customers, work orders)

- **Business/Gold Layer**:
    - Final models are curated for business use cases and AI model consumption

- **Unstructured data** like equipment images and service notes are processed separately and fed into downstream AI workflows (CV & LLM)

### Medallion Architecture (Bronze → Silver → Gold)

This pattern is at the heart of the platform:

- **Bronze**: Raw data, minimally processed, good for traceability.
- **Silver**: Cleaned, validated, enriched; source of truth for analytics.
- **Gold**: Business-level data models, usually joined and aggregated, feeding dashboards and ML.

### Batch + Streaming Paths

- **Batch**: Legacy systems or slowly-changing data are pulled in using Azure Data Factory (e.g., CRM, ticketing, SQL work orders)
- **Streaming**: Real-time telemetry from IoT flows via Event Hub into Bronze layer; mobile app events stream into AutoLoader.

---

## 2. Data Modeling Document

### Key Data Models

**Silver Layer Models:**
- `CleanedWorkOrders`
- `CleanedTelemetryData`
- `CleanedCustomerProfiles`
- `CleanedMobileData`

**Gold Layer Models:**
- `Customer360`: Full view on customer interactions (CRM + Support + App)
- `EquipmentMaintenanceFeatures`: Feature set for predictive ML
- `TechnicianRoutingFeatures`: Used by routing optimization engine
- `CustomerChurnFeatures`: For churn prediction model

### Entity Structure Examples

#### a. `CleanedWorkOrders`
```sql
work_order_id STRING,
customer_id STRING,
status STRING,
technician_id STRING,
opened_ts TIMESTAMP,
closed_ts TIMESTAMP,
equipment_id STRING
```

#### b. `Customer360`
```sql
customer_id STRING,
name STRING,
email STRING,
total_support_tickets INT,
last_purchase_date DATE,
last_service_date DATE,
churn_score DOUBLE
```

#### c. `EquipmentMaintenanceFeatures`
```sql
equipment_id STRING,
avg_temp_last_30days DOUBLE,
pressure_variance DOUBLE,
failure_count INT,
last_maintenance_date DATE,
label_failure BOOLEAN
```

### Partitioning & Optimization

- Time-based partitioning on ingestion timestamps
- Z-Ordering on high-cardinality fields like `customer_id`, `equipment_id`
- OPTIMIZE + VACUUM run on schedule (esp. on Silver/Gold tables)
- Delta Lake for versioning, ACID, schema evolution

---

## 3. Data Governance Strategy

### Metadata & Lineage Tracking

- **Azure Purview**: Automatically crawls and catalogs data from all sources
- **Unity Catalog**: Manages metadata, access policies, and table lineage in Databricks
- **Lineage** is mapped from raw to gold and linked to ML assets via MLflow

### Data Quality Enforcement

- **dbt tests** (e.g., `unique`, `not_null`, `relationships`)
- **Great Expectations or Deequ** used optionally for deeper validations
- Quality checks are tied into deployment pipelines

### Sensitive Data Governance

- PII fields (email, phone, address) are masked or encrypted
- RBAC (via Unity Catalog) restricts access to sensitive tables
- Access logs audited periodically
- Tags in Purview help identify and classify sensitive info

### Monitoring & Alerting

- Pipelines monitored via ADF triggers, Event Hub metrics
- Data freshness tracked via dashboards
- Alerts triggered on test failures or pipeline crashes (integrated with Azure Monitor / Log Analytics)

---

## 4. ML / AI Data Serving Strategy

### Feature Preparation

- Silver tables are the primary source
- Features are joined and transformed in Gold layer
- Stored in **Databricks Feature Store** for consistency and reuse

### ML Models & Pipelines

- **Predictive Maintenance Model**: Uses telemetry + service history
- **Customer Churn Prediction**: Based on CRM + Ticketing + App activity
- **Technician Routing Optimizer**: Combines GPS + WO + calendar data
- **CV Model**: Trained on equipment images using Azure ML
- **LLM Assistant**: Text embeddings from notes + CRM + support tickets

### Unstructured + Structured Handling

- **Unstructured**:
    - Equipment images ingested into Blob Storage, then used by CV models
    - Service notes turned into embeddings and fed into the LLM
- **Structured**:
    - Stored in Delta Tables (Gold)
    - Served to ML models through Feature Store and directly from Delta

---

## Summary

This architecture meets SmartField Inc.'s vision for a smart, scalable, ML-first data platform. It combines modern lakehouse patterns with strong governance and flexible AI/ML integrations – while still being cost-aware and modular enough to evolve over time.


