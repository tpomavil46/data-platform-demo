# Data Platform Demo

A portfolio demonstration project showcasing a custom data engineering stack and streaming data pipeline architecture.

## Overview

This project demonstrates a homegrown data engineering stack built for real-time event processing and analytics. It is designed as a portfolio piece to showcase architectural patterns and engineering capabilities.

**Important**: This project uses a custom-built data engineering infrastructure and is not intended to be cloned and run as-is. The documentation below describes the architecture, components, and implementation approach for demonstration purposes.

## Technology Stack

This demonstration leverages the following technologies in a custom integration:

- **Apache Kafka**: Event streaming platform for real-time data ingestion
- **PostgreSQL**: Relational database for persistent storage and analytics
- **Apache Airflow**: Workflow orchestration engine for scheduling and monitoring dbt transformations
- **Trino**: Distributed SQL query engine for high-performance analytics across data sources
- **dbt (Data Build Tool)**: SQL-based data transformation framework
- **Apache Superset**: Modern business intelligence and data visualization platform
- **Python**: Custom stream processing and orchestration
- **Homegrown Infrastructure**: Custom deployment and configuration management

## Architecture Overview

The platform implements a complete streaming data pipeline with the following components:

```
[Kafka Producer] -> [Kafka] -> [Flink Consumer Service] -> [PostgreSQL]
                                                           |
                                                           v
                                      [Airflow] -> [dbt Models] <- [Trino] <- [Superset]
                                      (1 min)           |              ^
                                                        v              |
                                                  [Analytics Tables] --+
```

### Components

1. **Kafka Producer** (`kafka_producer/`): Generates synthetic user event data and publishes to Kafka topics
2. **Stream Consumer** (`flink_jobs/`): Consumes events from Kafka and performs real-time aggregations into PostgreSQL
3. **Apache Airflow**: Orchestrates dbt transformations on a 1-minute schedule, ensuring near-real-time analytics updates
4. **dbt Analytics** (`dbt_project/`): Transforms raw streaming data into analytics-ready models
5. **Trino**: Provides high-performance SQL query interface for interactive analytics and ad-hoc exploration
6. **Apache Superset**: Business intelligence platform for creating dashboards and visualizations connected to both PostgreSQL and Trino

## Prerequisites

- Python 3.12+
- Apache Kafka 2.x+ (running on localhost:9092)
- PostgreSQL 12+ (with a database and schema configured)
- Apache Airflow 2.x+ (configured with DAGs for dbt orchestration)
- Trino (configured with PostgreSQL connector)
- Apache Superset (configured with PostgreSQL and Trino database connections)
- pip and virtualenv

## Project Structure

```
data-platform-demo/
├── kafka_producer/          # Event generation and publishing
│   └── producer.py          # Main producer script
├── flink_jobs/              # Stream processing consumers
│   ├── consumer.py          # Production consumer with environment variables
│   └── simple_consumer.py  # Basic consumer example
├── dbt_project/             # Data transformation layer
│   ├── models/
│   │   ├── analytics/       # Business logic models
│   │   └── example/         # Example dbt models
│   ├── dbt_project.yml      # dbt project configuration
│   └── profiles.yml         # Database connection profiles
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd data-platform-demo
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
POSTGRES_HOST=localhost
POSTGRES_DB=your_database
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
```

### 5. Set Up Kafka

Ensure Kafka is running locally on port 9092:

```bash
# Start Zookeeper
bin/zookeeper-server-start.sh config/zookeeper.properties

# Start Kafka Server
bin/kafka-server-start.sh config/server.properties

# Create the required topic
bin/kafka-topics.sh --create --topic user_events --bootstrap-server localhost:9092
```

### 6. Initialize PostgreSQL Schema

Connect to your PostgreSQL database and create the streaming schema:

```sql
CREATE SCHEMA IF NOT EXISTS streaming;
```

The consumer will automatically create the required tables on first run.

## Usage

### Starting the Pipeline

#### 1. Start the Kafka Producer

```bash
python kafka_producer/producer.py
```

This will generate synthetic user events with the following structure:
- `user_id`: Random user identifier (1-100)
- `event_type`: One of ['click', 'view', 'purchase']
- `timestamp`: ISO format timestamp
- `value`: Random value (1-100)

#### 2. Start the Consumer

```bash
python flink_jobs/consumer.py
```

The consumer will:
- Read events from the `user_events` Kafka topic
- Aggregate event counts by user and event type
- Upsert records into `streaming.user_events` table in PostgreSQL

#### 3. Run dbt Transformations

```bash
cd dbt_project
dbt run
```

This will create analytics models including:
- `user_event_summary`: Aggregated view of user events with totals per event type

### Viewing Results

Connect to PostgreSQL to query the transformed data:

```sql
-- View raw streaming data
SELECT * FROM streaming.user_events ORDER BY created_at DESC LIMIT 10;

-- View analytics summary
SELECT * FROM analytics.user_event_summary ORDER BY total_events DESC;
```

## Data Models

### Source: streaming.user_events

Raw event data aggregated from Kafka:

| Column | Type | Description |
|--------|------|-------------|
| user_id | INT | Unique user identifier |
| event_type | VARCHAR(50) | Type of event (click/view/purchase) |
| event_count | INT | Cumulative count of events |
| created_at | TIMESTAMP | Record creation timestamp |

Primary Key: `(user_id, event_type)`

### Analytics: user_event_summary

Pivoted summary of user activity:

| Column | Type | Description |
|--------|------|-------------|
| user_id | INT | Unique user identifier |
| total_clicks | INT | Total click events |
| total_views | INT | Total view events |
| total_purchases | INT | Total purchase events |
| total_events | INT | Sum of all events |

## Development

### Testing dbt Models

```bash
cd dbt_project
dbt test
```

### Debugging

Enable debug logging for the consumer:

```bash
# Debug messages are already included in consumer.py
# Check console output for "DEBUG:" prefixed messages
```

### Adding New Models

1. Create SQL files in `dbt_project/models/analytics/`
2. Define sources in `dbt_project/models/analytics/sources.yml`
3. Run `dbt run` to materialize the models

## Configuration

### dbt Configuration

Edit `dbt_project/profiles.yml` to configure database connections:

```yaml
dbt_project:
  outputs:
    dev:
      type: postgres
      host: localhost
      user: your_user
      password: your_password
      port: 5432
      dbname: your_database
      schema: analytics
  target: dev
```

### Kafka Configuration

Modify bootstrap servers in producer/consumer scripts:

```python
bootstrap_servers=['localhost:9092']  # Update as needed
```

## Deployment Considerations

### Scalability
- Consumer can be scaled horizontally using Kafka consumer groups
- PostgreSQL can be replicated for read-heavy workloads
- dbt models can be incrementalized for large datasets

### Reliability
- Kafka provides message durability and replay capabilities
- PostgreSQL UPSERT pattern ensures idempotent writes
- dbt provides data quality testing framework

### Security
- Use `.env` files for sensitive credentials (never commit to version control)
- Implement SSL/TLS for Kafka connections in production
- Use connection pooling for PostgreSQL in high-throughput scenarios

### Monitoring
- Monitor Kafka consumer lag
- Track PostgreSQL connection pool metrics
- Set up dbt Cloud or custom alerting for model failures

## Troubleshooting

### Kafka Connection Issues

```bash
# Verify Kafka is running
nc -vz localhost 9092

# List topics
kafka-topics.sh --list --bootstrap-server localhost:9092
```

### PostgreSQL Connection Issues

```bash
# Test connection
psql -h localhost -U your_user -d your_database

# Verify schema exists
\dn
```

### Consumer Not Processing Messages

- Check consumer group offset: Consumer may have already processed all messages
- Verify topic exists and has messages
- Check PostgreSQL credentials in `.env` file
- Review console output for error messages

## Dependencies

Core dependencies managed in `requirements.txt`:

- **kafka-python**: Kafka client for Python
- **dbt-core**: Data transformation framework
- **dbt-postgres**: PostgreSQL adapter for dbt
- **psycopg2-binary**: PostgreSQL driver for Python
- **python-dotenv**: Environment variable management

## Contributing

When contributing to this project:

1. Follow SOLID principles and DRY methodology
2. Use Google-style docstrings for all functions and classes
3. Write tests for new functionality (TDD approach)
4. Maintain loose coupling between components
5. Consider the "ilities": scalability, reliability, maintainability, etc.

## License

[Specify your license here]

## Future Enhancements

- [ ] Add Apache Flink for more complex stream processing
- [ ] Implement Terraform for infrastructure as code
- [ ] Add monitoring with Prometheus and Grafana
- [ ] Implement data quality checks with Great Expectations
- [ ] Add CI/CD pipeline for dbt models
- [ ] Containerize with Docker and orchestrate with Kubernetes
- [ ] Add schema registry for Avro/Protobuf support
- [ ] Implement CDC (Change Data Capture) patterns

## Contact

[Add your contact information or team details]
