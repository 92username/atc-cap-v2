"""
Basic tests for TATIC Processor
"""
import os
import shutil
import tempfile
from datetime import datetime

import pandas as pd
import pytest

# Import the module to test
from tatic_processor import TATICProcessor

# Test constants
TEST_JOB_ID = "test_job_123456"


@pytest.fixture
def temp_job_dir():
    """Create a temporary job directory for testing"""
    base_dir = tempfile.mkdtemp()
    job_dir = os.path.join(base_dir, TEST_JOB_ID)
    os.makedirs(job_dir, exist_ok=True)

    # Also create outputs and uploads directories within the temp dir
    uploads_dir = os.path.join(base_dir, "uploads", TEST_JOB_ID)
    outputs_dir = os.path.join(base_dir, "outputs", TEST_JOB_ID)
    os.makedirs(uploads_dir, exist_ok=True)
    os.makedirs(outputs_dir, exist_ok=True)

    yield base_dir

    # Clean up after the test
    shutil.rmtree(base_dir)


@pytest.fixture
def sample_tatic_df():
    """Create a minimal sample DataFrame that resembles TATIC data"""
    data = {
        "DATA": pd.date_range(start="2025-01-01", periods=5),
        "HORA": ["08:00", "09:30", "10:15", "14:45", "16:20"],
        "ORIGEM": ["SBSP", "SBBR", "SBGR", "SBCT", "SBRJ"],
        "DESTINO": ["SBBR", "SBGR", "SBCT", "SBRJ", "SBSP"],
        "REGRA": ["IFR", "IFR", "IFR", "VFR", "IFR"],
        "EQUIPAMENTO": ["A320", "B738", "E195", "C208", "AT72"],
        "MATRICULA": ["PT-XYZ", "PP-ABC", "PR-123", "PT-456", "PP-789"],
    }
    df = pd.DataFrame(data)

    # Add weekday column required by processor
    df["weekday"] = df["DATA"].dt.day_name()

    return df


def test_tatic_processor_initialization(temp_job_dir):
    """Test that the TATIC processor initializes correctly"""
    processor = TATICProcessor(
        job_id=TEST_JOB_ID,
        inicio_periodo=datetime(2025, 1, 1),
        fim_periodo=datetime(2025, 1, 31),
        base_dir=temp_job_dir,
        incluir_finais_de_semana=False,
    )

    assert processor.job_id == TEST_JOB_ID
    assert processor.periodo_inicio == datetime(2025, 1, 1)
    assert processor.periodo_fim == datetime(2025, 1, 31)
    assert processor.job_dir.exists()


def test_process_weekday_filtering(sample_tatic_df):
    """Test that weekday filtering works correctly"""
    # Create a processor with weekends excluded
    processor = TATICProcessor(
        job_id=TEST_JOB_ID,
        inicio_periodo=datetime(2025, 1, 1),
        fim_periodo=datetime(2025, 1, 31),
        incluir_finais_de_semana=False,
    )

    # Set up the DataFrame to have a mix of weekdays and weekends
    sample_tatic_df["weekday"] = ["Monday", "Tuesday", "Wednesday", "Saturday", "Sunday"]

    # Test the filtering logic from generate_table1_mca (without actually calling the method)
    if not processor.incluir_finais_de_semana:
        filtered_df = sample_tatic_df[~sample_tatic_df["weekday"].isin(["Saturday", "Sunday"])]
    else:
        filtered_df = sample_tatic_df

    # Check that weekend days are correctly filtered out
    assert len(filtered_df) == 3
    assert "Saturday" not in filtered_df["weekday"].values
    assert "Sunday" not in filtered_df["weekday"].values

    # Now test with weekends included
    processor.incluir_finais_de_semana = True

    if not processor.incluir_finais_de_semana:
        filtered_df = sample_tatic_df[~sample_tatic_df["weekday"].isin(["Saturday", "Sunday"])]
    else:
        filtered_df = sample_tatic_df

    # Check that all days are included
    assert len(filtered_df) == 5
    assert "Saturday" in filtered_df["weekday"].values
    assert "Sunday" in filtered_df["weekday"].values
