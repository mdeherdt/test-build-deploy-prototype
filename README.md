# Microservices Template Project

This is a template project with two Python microservices that communicate with each other and with a database.

## Project Structure

```
.
├── service_a/                  # Service A - API + DB
│   ├── app/                    # Application code
│   │   ├── __init__.py
│   │   ├── db.py               # Database setup
│   │   ├── main.py             # FastAPI app
│   │   ├── models.py           # SQLAlchemy models
│   │   └── schemas.py          # Pydantic schemas
│   ├── tests/                  # Tests
│   │   ├── __init__.py
│   │   └── test_items.py       # Tests for CRUD operations
│   ├── Dockerfile              # Docker configuration
│   └── requirements.txt        # Python dependencies
│
├── service_b/                  # Service B - Client/Aggregator
│   ├── app/                    # Application code
│   │   ├── __init__.py
│   │   ├── client.py           # HTTP client to Service A
│   │   └── main.py             # FastAPI app
│   ├── tests/                  # Tests
│   │   ├── __init__.py
│   │   └── test_proxy.py       # Tests for proxy endpoint
│   ├── Dockerfile              # Docker configuration
│   └── requirements.txt        # Python dependencies
│
├── k8s/                        # Kubernetes manifests
│   ├── service-a-deployment.yaml
│   ├── service-a-service.yaml
│   ├── service-b-deployment.yaml
│   └── service-b-service.yaml
│
└── .github/
    └── workflows/
        └── ci-cd.yml           # GitHub Actions workflow
```

## Services Overview

### Service A

Service A is a simple CRUD API that stores items in a SQLite database. It exposes the following endpoints:

- `POST /items` - Create a new item
- `GET /items` - List all items
- `GET /items/{id}` - Get a specific item
- `DELETE /items/{id}` - Delete an item
- `GET /health` - Health check endpoint

### Service B

Service B is a proxy service that calls Service A and transforms the response. It exposes the following endpoints:

- `GET /proxy-items` - Calls Service A's `/items` endpoint, transforms the data, and returns it
- `GET /health` - Health check endpoint

## Running Locally

### Prerequisites

- Python 3.9+
- pip

### Service A

```bash
# Navigate to Service A directory
cd service_a

# Install dependencies
pip install -r requirements.txt

# Run the service
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000. You can access the Swagger UI at http://localhost:8000/docs.

### Service B

```bash
# Navigate to Service B directory
cd service_b

# Install dependencies
pip install -r requirements.txt

# Run the service (make sure Service A is running)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

The API will be available at http://localhost:8001. You can access the Swagger UI at http://localhost:8001/docs.

## Running with Docker

### Prerequisites

- Docker

### Building the Images

```bash
# Build Service A
docker build -t service-a:latest ./service_a

# Build Service B
docker build -t service-b:latest ./service_b
```

### Running the Containers

```bash
# Create a Docker network
docker network create microservices

# Run Service A
docker run -d --name service-a --network microservices -p 8000:8000 service-a:latest

# Run Service B (pointing to Service A)
docker run -d --name service-b --network microservices -p 8001:8001 -e SERVICE_A_BASE_URL=http://service-a:8000 service-b:latest
```

## Running with Docker Compose

Docker Compose provides an easier way to run both services together with a single command.

### Prerequisites

- Docker
- Docker Compose

### Running the Services

```bash
# Start both services
docker-compose up -d

# Check the status of the services
docker-compose ps

# View logs
docker-compose logs -f

# Stop the services
docker-compose down
```

The services will be available at:
- Service A: http://localhost:8000 (Swagger UI: http://localhost:8000/docs)
- Service B: http://localhost:8001 (Swagger UI: http://localhost:8001/docs)

### Persistent Data

The SQLite database for Service A is stored in a Docker volume named `service_a_data`, ensuring that your data persists even when containers are stopped or removed.

## Running Tests

### Service A

```bash
cd service_a
pytest
```

### Service B

```bash
cd service_b
pytest
```

## Deploying to Kubernetes

### Prerequisites

- kubectl configured to connect to your Kubernetes cluster
- A container registry (e.g., GitHub Container Registry)

### Deployment Steps

1. **Push Docker images to a container registry**

   ```bash
   # Tag images
   docker tag service-a:latest ghcr.io/your-username/service-a:latest
   docker tag service-b:latest ghcr.io/your-username/service-b:latest

   # Push images
   docker push ghcr.io/your-username/service-a:latest
   docker push ghcr.io/your-username/service-b:latest
   ```

2. **Update Kubernetes manifests**

   Update the image references in the Kubernetes manifests to point to your container registry:

   ```bash
   # Replace placeholders in Kubernetes manifests
   find k8s -type f -name "*.yaml" -exec sed -i "s|\${CONTAINER_REGISTRY}|ghcr.io/your-username|g" {} \;
   find k8s -type f -name "*.yaml" -exec sed -i "s|\${IMAGE_TAG}|latest|g" {} \;
   ```

3. **Apply Kubernetes manifests**

   ```bash
   kubectl apply -f k8s/
   ```

4. **Verify deployment**

   ```bash
   kubectl rollout status deployment/service-a
   kubectl rollout status deployment/service-b
   ```

5. **Access the services**

   Service A is only accessible within the cluster. Service B is exposed via NodePort:

   ```bash
   # Get the NodePort for Service B
   kubectl get svc service-b
   ```

   You can access Service B at `http://<node-ip>:<node-port>`.

## CI/CD with GitHub Actions

This project includes a GitHub Actions workflow that:

1. Runs tests for both services
2. Builds and pushes Docker images to GitHub Container Registry
3. Deploys to Kubernetes

To use this workflow, you need to:

1. Create a GitHub repository and push this code to it
2. Set up the following secrets in your GitHub repository:
   - `GITHUB_TOKEN` - GitHub token with permissions to push to the container registry
   - `KUBE_CONFIG` - Base64-encoded kubeconfig file for your Kubernetes cluster

The workflow will run automatically on pushes to the `main` branch.

## Customization

- **Container Registry**: Update the `CONTAINER_REGISTRY` environment variable in the GitHub Actions workflow to use a different container registry.
- **Kubernetes Namespace**: The manifests don't specify a namespace. You can add a namespace to the manifests or use `kubectl -n <namespace>` to deploy to a specific namespace.
- **Database**: Service A uses SQLite for simplicity. For production, you might want to use a more robust database like PostgreSQL.
