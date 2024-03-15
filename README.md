[![hello-world](https://github.com/dimamushalapugin/credit_project_learn_python/actions/workflows/hello-world.yml/badge.svg)](https://github.com/dimamushalapugin/credit_project_learn_python/actions/workflows/hello-world.yml)

# Financial Analytics Platform

Welcome to the Financial Analytics Platform! This project is designed for financial companies to analyze credit data, create risk assessments (scoring models), and generate automated reports. The platform uses Python, Flask, PostgreSQL, MongoDB, and Gunicorn to provide a robust and scalable solution.

## Features

- **Credit Data Analysis**: Visualize and analyze credit data using interactive charts and graphs.
- **Risk Assessment**: Create risk assessment models to evaluate creditworthiness and generate scoring reports.
- **Automated Reporting**: Generate customized reports automatically based on predefined criteria and parameters.
- **Data Storage**: Utilize PostgreSQL and MongoDB for efficient data storage and retrieval.
- **Scalability**: Deploy the platform using Gunicorn for scalability and performance optimization.

## Technologies Used

- **Python**: Backend development and data processing.
- **Flask**: Web framework for building the API endpoints and handling requests.
- **PostgreSQL**: Relational database for structured data storage.
- **MongoDB**: NoSQL database for storing unstructured and semi-structured data.
- **Gunicorn**: WSGI HTTP server for deploying Flask applications.

## Getting Started

### Prerequisites

- Python 3.12
- Pip
- PostgreSQL
- MongoDB
- Flask

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/dimamushalapugin/credit_project_learn_python.git

## Configuration

Before running the application, make sure to configure the environment variables:

1. Create a `.env` file in the root directory of the project.
2. Add the necessary environment variables to the `.env` file, such as database connection strings and API keys.

## Database Setup

To set up the databases for the platform, follow these steps:

### PostgreSQL

1. Create a PostgreSQL database for the application.
2. Update the PostgreSQL connection string in the `.env` file with the appropriate credentials.

### MongoDB

1. Start the MongoDB service on your local machine.
2. Update the MongoDB connection string in the `.env` file with the appropriate URI.

Once you have completed these steps, you can proceed to run the application.

