# Copilot Instructions for ATC-CAP-V2

## Overview
This project is a web application for processing and analyzing TATIC data. It uses Streamlit for the user interface, Python (with Pandas) for data processing, and Docker for deployment. The application supports uploading Excel files, processing large datasets, and generating categorized reports in ZIP format.

## Architecture
- **Frontend**: Streamlit-based web interface.
- **Backend**: Python scripts for data processing (`tatic_processor.py`).
- **Data Flow**: Excel (.xlsx) files are uploaded, processed into CSV, and output as ZIP reports.
- **Deployment**: Dockerized for production with `docker-compose.yml`.

## Key Files and Directories
- `app.py`: Main entry point for the Streamlit application.
- `tatic_processor.py`: Core data processing logic.
- `requirements.txt`: Python dependencies.
- `assets/`: Contains static files like category tables and example data.
- `uploads/`: Directory for user-uploaded files.
- `outputs/`: Directory for generated reports.

## Developer Workflows
### Local Development
1. Clone the repository:
   ```bash
   git clone https://github.com/92username/atc-cap-v2
   cd atc-cap-v2
   ```
2. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   streamlit run app.py
   ```

### Testing
- Use `pytest` for running tests.
- Ensure code quality with `Black` and `Ruff` linters.

### Docker Deployment
- Build and run the application using Docker:
  ```bash
  docker-compose up --build
  ```

## Project-Specific Conventions
- **File Naming**: Reports follow the format `relatorio_NNNN_DDMMYYYY_MODO.zip`.
  - `MODO` can be `STD` (standard) or `H` (helicopter).
- **Data Validation**: Uploaded files are validated for required columns (e.g., `H.Evento`, `Indicativo`, `Evento`).
- **Modes**: The application supports two modes:
  - **Standard (A-E)**: Traditional wake turbulence categories.
  - **Helicopter (H)**: Special category for helicopters.

## Integration Points
- **Streamlit**: Handles the user interface and file uploads.
- **Pandas**: Processes and validates data.
- **OpenPyXL**: Reads Excel files.
- **Docker**: Ensures consistent deployment environments.

## CI/CD Pipeline
- **Linting**: Black and Ruff.
- **Testing**: Pytest.
- **Build & Deploy**: Docker and GitHub Actions.

## Examples
### Adding a New Report Type
1. Update `tatic_processor.py` to include the new report logic.
2. Modify `app.py` to add the new report to the UI.
3. Test locally and ensure the report is generated correctly.

### Debugging
- Logs are displayed in real-time during data processing in the Streamlit interface.
- Check the `outputs/` directory for generated files.

## Helpful URLs
- Development: [http://localhost:8502](http://localhost:8502)
- Production: [http://localhost](http://localhost)