# test/test_logger_service.py
import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock, mock_open
from fastapi.testclient import TestClient
from datetime import datetime
import json
import uuid

# Import the app and functions
from logger_service.main import app, get_logger, log_to_file, log_info, LogEntry

class TestLoggerService:
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for each test"""
        # Create a temporary directory for logs during testing
        self.temp_dir = tempfile.mkdtemp()
        
        # Patch LOG_DIR to use temp directory
        with patch('logger_service.main.LOG_DIR', self.temp_dir):
            self.client = TestClient(app)
            yield
        
        # Cleanup
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        # Clear service_loggers cache
        from logger_service.main import service_loggers
        service_loggers.clear()

    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    @patch('logger_service.main.LOG_DIR')
    def test_get_logger_new_service(self, mock_log_dir):
        """Test creating a new logger for a service"""
        mock_log_dir.__str__ = lambda: self.temp_dir
        
        with patch('logger_service.main.service_loggers', {}):
            logger = get_logger("test_service")
            assert logger is not None
            assert logger.name == "test_service"
            
            # Test getting the same logger again
            logger2 = get_logger("test_service")
            assert logger is logger2

    @patch('logger_service.main.LOG_DIR')
    def test_get_logger_existing_service(self, mock_log_dir):
        """Test getting an existing logger"""
        mock_log_dir.__str__ = lambda: self.temp_dir
        
        with patch('logger_service.main.service_loggers', {}):
            logger1 = get_logger("existing_service")
            logger2 = get_logger("existing_service")
            assert logger1 is logger2

    @patch('logger_service.main.get_logger')
    def test_log_to_file_info_level(self, mock_get_logger):
        """Test logging INFO level message"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        log_entry = LogEntry(
            service="test_service",
            level="INFO",
            message="Test info message",
            details={"key": "value"}
        )
        
        log_to_file(log_entry)
        
        mock_get_logger.assert_called_once_with("test_service")
        mock_logger.info.assert_called_once_with('Test info message - Details: {"key": "value"}')

    @patch('logger_service.main.get_logger')
    def test_log_to_file_error_level(self, mock_get_logger):
        """Test logging ERROR level message"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        log_entry = LogEntry(
            service="test_service",
            level="ERROR",
            message="Test error message"
        )
        
        log_to_file(log_entry)
        
        mock_logger.error.assert_called_once_with("Test error message")

    @patch('logger_service.main.get_logger')
    def test_log_to_file_warning_level(self, mock_get_logger):
        """Test logging WARNING level message"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        log_entry = LogEntry(
            service="test_service",
            level="WARNING",
            message="Test warning message"
        )
        
        log_to_file(log_entry)
        
        mock_logger.warning.assert_called_once_with("Test warning message")

    @patch('logger_service.main.get_logger')
    def test_log_to_file_debug_level(self, mock_get_logger):
        """Test logging DEBUG level message"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        log_entry = LogEntry(
            service="test_service",
            level="DEBUG",
            message="Test debug message"
        )
        
        log_to_file(log_entry)
        
        mock_logger.debug.assert_called_once_with("Test debug message")

    @patch('logger_service.main.get_logger')
    def test_log_to_file_unknown_level(self, mock_get_logger):
        """Test logging with unknown level (should not call any logger method)"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        log_entry = LogEntry(
            service="test_service",
            level="UNKNOWN",
            message="Test unknown level message"
        )
        
        log_to_file(log_entry)
        
        # None of the logging methods should be called
        mock_logger.info.assert_not_called()
        mock_logger.error.assert_not_called()
        mock_logger.warning.assert_not_called()
        mock_logger.debug.assert_not_called()

    @patch('logger_service.main.get_logger')
    def test_log_info_function(self, mock_get_logger):
        """Test log_info helper function"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        result = log_info("Test message", "test_service")
        
        assert result is True
        mock_get_logger.assert_called_once_with("test_service")
        mock_logger.info.assert_called_once_with("Test message")

    @patch('logger_service.main.log_to_file')
    def test_create_log_endpoint(self, mock_log_to_file):
        """Test POST /log endpoint"""
        log_data = {
            "service": "test_service",
            "level": "INFO",
            "message": "Test log message",
            "details": {"key": "value"}
        }
        
        response = self.client.post("/log", json=log_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    @patch('logger_service.main.log_to_file')
    def test_create_log_endpoint_with_timestamp(self, mock_log_to_file):
        """Test POST /log endpoint with provided timestamp"""
        timestamp = "2023-01-01T10:00:00"
        log_data = {
            "service": "test_service",
            "level": "INFO",
            "message": "Test log message",
            "timestamp": timestamp
        }
        
        response = self.client.post("/log", json=log_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    @patch('logger_service.main.log_to_file')
    def test_create_log_endpoint_without_timestamp(self, mock_log_to_file):
        """Test POST /log endpoint without timestamp (should be auto-generated)"""
        log_data = {
            "service": "test_service",
            "level": "INFO",
            "message": "Test log message"
        }
        
        with patch('logger_service.main.datetime') as mock_datetime:
            mock_now = MagicMock()
            mock_datetime.now.return_value = mock_now
            
            response = self.client.post("/log", json=log_data)
            
            assert response.status_code == 200
            mock_datetime.now.assert_called_once()

    @patch('logger_service.main.log_to_file')
    def test_create_logs_batch_endpoint(self, mock_log_to_file):
        """Test POST /log/batch endpoint"""
        batch_data = {
            "logs": [
                {
                    "service": "service1",
                    "level": "INFO",
                    "message": "Message 1"
                },
                {
                    "service": "service2",
                    "level": "ERROR",
                    "message": "Message 2"
                }
            ]
        }
        
        response = self.client.post("/log/batch", json=batch_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["count"] == 2

    @patch('logger_service.main.log_to_file')
    def test_create_logs_batch_endpoint_auto_timestamp(self, mock_log_to_file):
        """Test POST /log/batch endpoint with auto timestamp generation"""
        batch_data = {
            "logs": [
                {
                    "service": "service1",
                    "level": "INFO",
                    "message": "Message 1"
                }
            ]
        }
        
        with patch('logger_service.main.datetime') as mock_datetime:
            mock_now = MagicMock()
            mock_datetime.now.return_value = mock_now
            
            response = self.client.post("/log/batch", json=batch_data)
            
            assert response.status_code == 200
            mock_datetime.now.assert_called_once()

    @patch('logger_service.main.os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="2023-01-01 10:00:00 - INFO - Test log 1\n2023-01-01 10:01:00 - ERROR - Test log 2\n")
    def test_get_logs_endpoint_success(self, mock_file, mock_exists):
        """Test GET /logs/{service_name} endpoint success case"""
        mock_exists.return_value = True
        
        response = self.client.get("/logs/test_service")
        
        assert response.status_code == 200
        data = response.json()
        assert "logs" in data
        assert "total" in data
        assert len(data["logs"]) == 2

    @patch('logger_service.main.os.path.exists')
    def test_get_logs_endpoint_file_not_exists(self, mock_exists):
        """Test GET /logs/{service_name} endpoint when log file doesn't exist"""
        mock_exists.return_value = False
        
        response = self.client.get("/logs/nonexistent_service")
        
        assert response.status_code == 200
        data = response.json()
        assert data["logs"] == []
        assert data["total"] == 0

    @patch('logger_service.main.os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="2023-01-01 10:00:00 - INFO - Test log 1\n2023-01-01 10:01:00 - ERROR - Test log 2\n2023-01-01 10:02:00 - INFO - Test log 3\n")
    def test_get_logs_endpoint_with_level_filter(self, mock_file, mock_exists):
        """Test GET /logs/{service_name} endpoint with level filter"""
        mock_exists.return_value = True
        
        response = self.client.get("/logs/test_service?level=INFO")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["logs"]) == 2  # Only INFO logs

    @patch('logger_service.main.os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="Log 1\nLog 2\nLog 3\nLog 4\nLog 5\n")
    def test_get_logs_endpoint_with_pagination(self, mock_file, mock_exists):
        """Test GET /logs/{service_name} endpoint with pagination"""
        mock_exists.return_value = True
        
        response = self.client.get("/logs/test_service?limit=2&offset=1")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["logs"]) == 2
        assert data["logs"][0] == "Log 2"
        assert data["logs"][1] == "Log 3"

    @patch('logger_service.main.os.path.exists')
    @patch('builtins.open', side_effect=IOError("File read error"))
    def test_get_logs_endpoint_file_read_error(self, mock_file, mock_exists):
        """Test GET /logs/{service_name} endpoint with file read error"""
        mock_exists.return_value = True
        
        response = self.client.get("/logs/test_service")
        
        assert response.status_code == 500
        data = response.json()
        assert "Error retrieving logs" in data["detail"]

    @patch('logger_service.main.os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="Log line 1\nLog line 2\n")
    def test_get_logs_endpoint_all_parameters(self, mock_file, mock_exists):
        """Test GET /logs/{service_name} endpoint with all parameters"""
        mock_exists.return_value = True
        
        response = self.client.get(
            "/logs/test_service?level=INFO&start_time=2023-01-01T00:00:00&end_time=2023-01-01T23:59:59&limit=10&offset=0"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "logs" in data
        assert "total" in data

    def test_log_entry_model_validation(self):
        """Test LogEntry model validation"""
        # Valid log entry
        log_entry = LogEntry(
            service="test_service",
            level="INFO",
            message="Test message"
        )
        assert log_entry.service == "test_service"
        assert log_entry.level == "INFO"
        assert log_entry.message == "Test message"
        assert log_entry.details is None
        assert log_entry.timestamp is None

    def test_log_entry_model_with_all_fields(self):
        """Test LogEntry model with all fields"""
        timestamp = datetime.now()
        log_entry = LogEntry(
            service="test_service",
            level="ERROR",
            message="Test error",
            details={"error_code": 500},
            timestamp=timestamp
        )
        assert log_entry.service == "test_service"
        assert log_entry.level == "ERROR"
        assert log_entry.message == "Test error"
        assert log_entry.details == {"error_code": 500}
        assert log_entry.timestamp == timestamp

    @patch('logger_service.main.LOG_DIR')
    @patch('logger_service.main.os.makedirs')
    def test_log_directory_creation(self, mock_makedirs, mock_log_dir):
        """Test that log directory is created"""
        # This test ensures the module-level code is covered
        import importlib
        import logger_service.main
        importlib.reload(logger_service.main)
        mock_makedirs.assert_called()

    def test_invalid_log_data(self):
        """Test POST /log with invalid data"""
        invalid_data = {
            "service": "test_service",
            # Missing required 'level' and 'message' fields
        }
        
        response = self.client.post("/log", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_invalid_batch_data(self):
        """Test POST /log/batch with invalid data"""
        invalid_data = {
            "logs": [
                {
                    "service": "test_service",
                    # Missing required fields
                }
            ]
        }
        
        response = self.client.post("/log/batch", json=invalid_data)
        assert response.status_code == 422  # Validation error

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=logger_service", "--cov-report=term-missing"])
