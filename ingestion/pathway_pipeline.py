import sys
import time
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
from ingestion.openaq_client import OpenAQClient

load_dotenv()

# Pathway engine compatibility check for Windows / Python 3.13
try:
    import pathway as pw
    if not hasattr(pw, "Schema"):
        raise AttributeError("Pathway stub package detected on Windows / unsupported platform.")
    IS_REAL_PATHWAY = True
except (ImportError, AttributeError):
    IS_REAL_PATHWAY = False
    print("Notice: Real Pathway engine binary wheels are unavailable on Windows native Python. Using compatibility fallback layer.")

    class MockColumnDefinition:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class MockSchema:
        pass

    class MockConnectorSubject:
        def __init__(self):
            self._buffer = []

        def next(self, **kwargs):
            self._buffer.append(kwargs)

        def run(self):
            pass

    class MockTable:
        def __init__(self, subject, schema):
            self.subject = subject
            self.schema = schema

    class MockPython:
        ConnectorSubject = MockConnectorSubject
        
        @staticmethod
        def read(subject, schema=None):
            return MockTable(subject, schema)

    class MockDebug:
        @staticmethod
        def compute_and_print(table):
            print("--- Pathway Stream Table Output (Compatibility Mode) ---")
            if hasattr(table, "subject"):
                if not table.subject._buffer and hasattr(table.subject, "poll_once"):
                    table.subject.poll_once()
                for i, row in enumerate(table.subject._buffer):
                    print(f"Row {i+1}: {row}")

    class MockPW:
        Schema = MockSchema
        python = MockPython
        debug = MockDebug

        @staticmethod
        def column_definition(**kwargs):
            return MockColumnDefinition(**kwargs)

        @staticmethod
        def run():
            print("Pathway pipeline completed in compatibility mode.")

    pw = MockPW()

# 1. Define the Schema for incoming air quality records
class AirQualitySchema(pw.Schema):
    location_id: int = pw.column_definition(primary_key=True)
    city: str
    parameter: str
    value: float
    unit: str
    timestamp: str

# 2. Implement the Custom Connector Subject for OpenAQ
class OpenAQConnectorSubject(pw.python.ConnectorSubject):
    def __init__(self, poll_interval: int = 60, location_ids: list = None):
        super().__init__()
        self.poll_interval = poll_interval
        self.location_ids = location_ids or [8118]  # Default example location ID (e.g., New Delhi)
        self.client = OpenAQClient()

    def poll_once(self):
        for loc_id in self.location_ids:
            try:
                measurements = self.client.get_latest_measurements(loc_id)
                for m in measurements:
                    self.next(
                        location_id=m["location_id"],
                        city=m["city"],
                        parameter=m["parameter"] or "unknown",
                        value=float(m["value"] or 0.0),
                        unit=m["unit"] or "",
                        timestamp=m["last_updated"] or time.strftime("%Y-%m-%d %H:%M:%S")
                    )
            except Exception as e:
                print(f"Exception during OpenAQ polling: {e}")

    def run(self):
        if not IS_REAL_PATHWAY:
            self.poll_once()
            return
        while True:
            self.poll_once()
            time.sleep(self.poll_interval)

# 3. Stream Setup Function
def create_air_quality_stream():
    subject = OpenAQConnectorSubject(poll_interval=60, location_ids=[8118])
    stream_table = pw.python.read(subject, schema=AirQualitySchema)
    return stream_table

if __name__ == "__main__":
    table = create_air_quality_stream()
    # Debug output to verify stream data in terminal
    pw.debug.compute_and_print(table)
    pw.run()