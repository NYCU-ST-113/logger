# Logger Service

This repository contains the Logger Service, a microservice designed to handle centralized logging operations for the classroom booking system.

## Overview

The Logger Service provides a reliable way to record and retrieve logs from various microservices in a centralized location. It's built with FastAPI and designed to work as part of a microservices architecture, making it easier to debug, monitor, and analyze application behavior across services.

## Getting Started

Follow these steps to set up and run the Logger Service on your local machine.

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- SMTP server access (for sending emails)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd logger
   ```

2. **Create and activate a virtual environment**
   ```bash
   # Create a virtual environment
   python3 -m venv logger_env
   
   # Activate the virtual environment
   # On Linux/Mac:
   source logger_env/bin/activate
   
   # On Windows:
   # logger_env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create necessary directories**
   ```bash
   mkdir -p logs csv_exports
   ```

### Running the Service

Start the Logger Service with:

```bash
uvicorn logger_service.main:app --reload --port 7000
```

The service will be available at `http://localhost:7000`.

## API Documentation

Once the service is running, you can access the API documentation at:
- Swagger UI: `http://localhost:7000/docs`
- ReDoc: `http://localhost:7000/redoc`

## Features

- Centralized logging for multiple microservices
- Support for different log levels (INFO, ERROR, WARNING, DEBUG)
- Structured logging with message and detailed context

## Testing

Run the tests with:

```bash
python3 -m pytest test/test_logger.py -v
```

For coverage report:
```bash
python3 -m pytest --cov=logger_service --cov-report=term-missing test/
```

## Project Structure

```
mailer/
├── common_utils/      
│   ├── common_utils
│   │   ├── logger
│   │       ├── __init__.py
│   │       ├── client.py # client api for calling logger micro-service
│   ├── setup.py               
├── logger_service/       # Main package
│   ├── __init__.py
│   ├── main.py           # FastAPI application
├── tests/                # Test package
│   ├── __init__.py
│   └── test_logger.py    # Tests for logger service
├── .gitignore            # Git ignore file
├── requirements.txt      # Project dependencies
└── README.md             # This file
```

## Notes

- This service was originally part of a larger microservices architecture including Payment Service and Mailer Service, which have been removed to make this a standalone service.
- When integrating with other services, you may need to adjust configurations accordingly.

## License


## Contact
