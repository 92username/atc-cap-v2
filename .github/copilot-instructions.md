# Copilot Instructions for ATC-CAP-V2

## Overview
This project is a web application for processing and analyzing TATIC (air traffic control) data according to MCA 100-26-2 specifications. It uses Streamlit for the user interface, Python with Pandas for data processing, and Docker for deployment. The application processes Excel files containing flight movement data, categorizes aircraft by wake turbulence, and generates statistical reports in ZIP format.

## Architecture
- **Frontend**: Single-page Streamlit application with expandable sidebar instructions
- **Processing**: Async job-based data processing with real-time logging via callback functions
- **Data Flow**: Excel (.xlsx) → CSV conversion → Data validation/normalization → Statistical analysis → ZIP report generation
- **Storage**: Job-specific directories for uploads (`uploads/job_id/`) and outputs (`outputs/job_id/`)
- **Deployment**: Dockerized with persistent volumes for data retention

## Key Files and Directories
- `app.py`: Main Streamlit application with UI, file upload handling, and session state management
- `tatic_processor.py`: Core processing engine with async Excel conversion, data validation, and report generation
- `requirements.txt`: Python dependencies (Streamlit 1.24+, Pandas 2.0+, OpenPyXL 3.1+)
- `assets/categorias-A-E.csv`: Aircraft category mapping table (A-E wake turbulence categories)
- `assets/DataGrid-sbjr.xlsx`: Sample TATIC data file for testing
- `uploads/`: Job-specific uploaded Excel files (auto-cleaned)
- `outputs/`: Generated ZIP reports with incremental naming

## Developer Workflows
### Local Development
```bash
git clone https://github.com/92username/atc-cap-v2
cd atc-cap-v2
python -m venv venv && source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
streamlit run app.py  # Runs on http://localhost:8506
```

### Testing
```bash
pytest tests/  # Run test suite
black . && ruff check .  # Code quality checks
```

### Docker Deployment
```bash
docker-compose up --build  # Build and run with persistent volumes
# Access at configured APP_PORT (default 8506)
```

## Project-Specific Conventions

### Report Naming and Numbering
Reports use incremental numbering with format: `relatorio_NNNN_DDMMYYYY_MODO.zip`
- `NNNN`: Zero-padded sequential number (scans existing files for next available)
- `DDMMYYYY`: Current date
- `MODO`: "STD" (standard A-E categories) or "H" (helicopter category enabled)

Example: `relatorio_0001_15102025_H.zip`

### Data Processing Patterns
- **Column Normalization**: Maps Portuguese column names to English (`"h.evento"` → `"timestamp_utc"`, `"equipamento"` → `"equipamento"`)
- **Timestamp Parsing**: Vectorized parsing of Portuguese date formats (`2025-janeiro-15 14:30:00` → UTC datetime)
- **Event Filtering**:
  - Runway statistics: `{"ARR", "DEP", "TGL"}`
  - ATC totals: `{"ARR", "DEP", "TGL", "QAY", "QAF", "ABA", "ABD", "ACD", "ATN", "LOW", "QRF", "QSO"}`
- **Helicopter Classification**: Hardcoded list of 47+ models (R22, S76, A109, EC135, etc.) when H-mode enabled

### Job-Based Processing
- Each upload creates unique job ID: `job_YYYYMMDDHHMMSS_UUID`
- Separate directories for uploads and outputs with same job ID
- Async processing with `asyncio.to_thread()` for Excel conversion
- Real-time logging via callback functions passed to processor

Example job directory structure:
```
outputs/job_20251015143022_a1b2c3d4/
├── tabela1_movimento_percentual_categoria.csv
├── tabela2_resultado_mix_categoria.csv
├── tabela3_movimento_mensal_pista.csv
├── tabela4_percentual_utilizacao_pistas.csv
├── resumo.txt
└── charts_data.json
```

### Category Loading with Fallbacks
Aircraft categories loaded from multiple possible paths:
1. `TATIC_CATEGORIAS_CSV` environment variable
2. `categorias-A-E.csv` in module/assets directories
3. Falls back to basic classification if file not found

### Portuguese Date Format Handling
```python
# Vectorized month replacement in tatic_processor.py
meses_map = {
    'janeiro': '01', 'fevereiro': '02', 'março': '03', 'abril': '04',
    'maio': '05', 'junho': '06', 'julho': '07', 'agosto': '08',
    'setembro': '09', 'outubro': '10', 'novembro': '11', 'dezembro': '12'
}
# Converts: "2025-janeiro-15 14:30:00" → "2025-01-15 14:30:00"
```

## Integration Points
- **Streamlit**: UI, file uploads, session state, real-time progress display
- **Pandas**: DataFrame operations, vectorized timestamp parsing, Excel reading
- **OpenPyXL**: Excel file processing with encoding detection
- **AsyncIO**: Non-blocking Excel conversion and processing
- **Docker Volumes**: Persistent storage for uploads/outputs across container restarts

## CI/CD Pipeline
- **Linting**: Black code formatting, Ruff linting
- **Testing**: Pytest with fixtures for temporary directories
- **Build**: Docker image build and push to GHCR
- **Deploy**: Automated deployment to VPS with SSH

## Common Development Tasks

### Adding New Aircraft Categories
1. Update `assets/categorias-A-E.csv` with new aircraft models
2. Test category loading fallback in `tatic_processor.py`
3. Verify classification in generated reports

### Modifying Report Tables
1. Update table generation logic in `tatic_processor.py` methods like `generate_table1_mca()`
2. Modify UI options in `app.py` if new parameters needed
3. Test with sample data and verify ZIP contents

### Debugging Data Processing
- Check real-time logs in Streamlit interface during processing
- Examine intermediate CSV files in job output directories
- Use `pandas.read_excel()` directly for Excel parsing issues
- Verify column normalization with `normalize_columns()` method

### Adding New Processing Options
When adding features like helicopter mode or weekend inclusion:
1. Add parameter to `TATICProcessor.__init__()`
2. Pass from `app.py` radio buttons to processor instantiation
3. Update table generation methods (e.g., `generate_table1_mca()`) to respect the flag
4. Update report naming logic in `gerar_nome_relatorio()`

## Performance Considerations
- Vectorized timestamp parsing for large datasets (155k+ records in ~70 seconds)
- Async Excel conversion to prevent UI blocking
- Job-based isolation prevents file conflicts
- Memory-efficient DataFrame operations with Pandas

## URLs
- Development: http://localhost:8506
- Production: Configurable via APP_PORT environment variable