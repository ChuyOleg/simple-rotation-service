## Installation.

### Python 3.12.3 is used.

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd token-rotation-service
   ```

2. **Create virtual environment**:
   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install dependencies**:
   ```bash
    uvicorn app:app --reload --port=8080
   ```
