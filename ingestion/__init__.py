"""Ingestion package for fetching and streaming air quality data."""

from .openaq_client import OpenAQClient
from .pathway_pipeline import AirQualitySchema, OpenAQConnectorSubject, create_air_quality_stream

__all__ = [
    "OpenAQClient",
    "AirQualitySchema",
    "OpenAQConnectorSubject",
    "create_air_quality_stream",
]