#!/usr/bin/env python3
"""
FastAPI Request Logger

A reusable middleware component for logging API requests with detailed information.
"""

import time
import logging
from typing import Callable, Optional
from datetime import datetime
import json
import os
from pathlib import Path

from fastapi import Request, Response
from fastapi.responses import JSONResponse
import uvicorn


class APILogger:
    """API logger for tracking and recording HTTP requests."""
    
    def __init__(
        self,
        log_level: int = logging.INFO,
        log_file: Optional[str] = None,
        log_format: str = "json"
    ):
        """
        Initialize the API logger.
        
        Args:
            log_level: Logging level (default: INFO)
            log_file: Optional file path to save logs
            log_format: Format for logs - "json" or "text"
        """
        self.log_format = log_format
        
        # Create logger
        self.logger = logging.getLogger("api_logger")
        self.logger.setLevel(log_level)
        self.logger.propagate = False  # Prevent duplicate logs
        
        # Avoid adding multiple handlers
        if not self.logger.handlers:
            # Create formatter
            if log_format == "json":
                formatter = logging.Formatter('%(message)s')
            else:
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            
            # File handler (if specified)
            if log_file:
                # Create directory if it doesn't exist
                log_path = Path(log_file)
                log_path.parent.mkdir(parents=True, exist_ok=True)
                
                file_handler = logging.FileHandler(log_file)
                file_handler.setLevel(log_level)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
    
    def _format_log_entry(self, log_data: dict) -> str:
        """
        Format log entry based on configured format.
        
        Args:
            log_data: Dictionary containing log information
            
        Returns:
            Formatted log string
        """
        if self.log_format == "json":
            return json.dumps(log_data, separators=(',', ':'))
        else:
            return (
                f"method={log_data['method']} "
                f"path={log_data['path']} "
                f"status={log_data['status']} "
                f"duration={log_data['duration_ms']:.2f}ms "
                f"timestamp={log_data['timestamp']}"
            )
    
    async def log_request(
        self,
        request: Request,
        response: Response,
        start_time: float
    ) -> None:
        """
        Log request details.
        
        Args:
            request: FastAPI Request object
            response: FastAPI Response object
            start_time: Time when request started processing
        """
        try:
            duration = time.time() - start_time
            duration_ms = duration * 1000
            
            log_data = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params) if request.query_params else None,
                "status": response.status_code,
                "duration_ms": round(duration_ms, 2),
                "client_host": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            }
            
            # Remove None values
            log_data = {k: v for k, v in log_data.items() if v is not None}
            
            log_entry = self._format_log_entry(log_data)
            
            # Log at different levels based on status code
            if 500 <= response.status_code < 600:
                self.logger.error(log_entry)
            elif 400 <= response.status_code < 500:
                self.logger.warning(log_entry)
            else:
                self.logger.info(log_entry)
                
        except Exception as e:
            self.logger.error(f"Failed to log request: {str(e)}")


def create_logging_middleware(logger: APILogger) -> Callable:
    """
    Create middleware for logging API requests.
    
    Args:
        logger: APILogger instance to use for logging
        
    Returns:
        Middleware function for FastAPI
    """
    async def logging_middleware(request: Request, call_next):
        """
        Middleware function that logs request information.
        
        Args:
            request: Incoming request
            call_next: Next middleware/function in chain
            
        Returns:
            Response from the endpoint
        """
        start_time = time.time()
        
        try:
            response = await call_next(request)
        except Exception as e:
            # Log internal server errors
            response = JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )
            logger.logger.error(f"Unhandled exception: {str(e)}")
        
        # Log the request
        await logger.log_request(request, response, start_time)
        
        return response
    
    return logging_middleware


# Example integration
def example_app():
    """
    Example FastAPI application demonstrating logger integration.
    """
    from fastapi import FastAPI, HTTPException
    
    # Create FastAPI app
    app = FastAPI(title="Example API", version="1.0.0")
    
    # Create logger
    logger = APILogger(
        log_level=logging.INFO,
        log_file="logs/api.log",
        log_format="json"
    )
    
    # Add middleware
    app.middleware("http")(create_logging_middleware(logger))
    
    # Example endpoints
    @app.get("/")
    async def root():
        return {"message": "Hello World"}
    
    @app.get("/items/{item_id}")
    async def read_item(item_id: int):
        if item_id < 0:
            raise HTTPException(status_code=400, detail="Item ID must be positive")
        return {"item_id": item_id, "name": f"Item {item_id}"}
    
    @app.get("/error")
    async def trigger_error():
        raise HTTPException(status_code=500, detail="Internal server error example")
    
    return app


if __name__ == "__main__":
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    # Run example app
    app = example_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)