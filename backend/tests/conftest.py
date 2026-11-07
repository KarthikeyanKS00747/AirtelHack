"""Pytest test configuration and fixtures for Udyam Digital backend."""
import pytest
import os
import sys

# Ensure backend root is in python path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app
from app.services.recommendation_engine import RecommendationEngine, BusinessProfile
from app.services.kyc_service import get_gstin_registry, get_udyam_registry


@pytest.fixture(scope="session")
def engine_instance():
    return RecommendationEngine()


@pytest.fixture(scope="session")
def gstin_reg():
    return get_gstin_registry()


@pytest.fixture(scope="session")
def udyam_reg():
    return get_udyam_registry()


@pytest.fixture(scope="module")
def test_client():
    client = TestClient(app)
    return client
