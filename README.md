# Energy Usage Web Application

A Python web application that displays instantaneous power usage data. The application authenticates users and shows real-time power data that refreshes every 10 seconds.

## Features

- User authentication using the NET2GRID Customer Engagement API
- Display of instantaneous power data for electricity and gas
- Auto-refresh of power data every 10 seconds
- Responsive design for desktop and mobile devices
- Docker containerization for easy deployment

## Prerequisites

- Docker and Docker Compose
- NET2GRID API credentials (client_id and client_secret)

## Setup

1. Clone this repository:
   ```
   git clone <repository-url>
   cd energyUsage
   ```

2. Create a `.env` file in the project root with your API credentials:
   ```
   # API Configuration
   CLIENT_ID=your_client_id
   CLIENT_SECRET=your_client_secret
   API_BASE_URL=https://api.n2g-ynni.net

   # Flask Configuration
   SECRET_KEY=your_secret_key_for_flask_sessions
   PORT=5000
   ```

   Replace `your_client_id`, `your_client_secret`, and `your_secret_key_for_flask_sessions` with your actual values.

## Running the Application

### Using Docker

1. Build the Docker image:
   ```
   docker build -t energy-usage-app .
   ```

2. Run the container:
   ```
   docker run -p 5000:5000 --env-file .env energy-usage-app
   ```

3. Access the application at http://localhost:5000

### Without Docker

1. Install dependencies:
   ```
   pip install pip-tools
   pip-compile pyproject.toml --output-file=requirements.txt
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python app.py
   ```

3. Access the application at http://localhost:5000

## Usage

1. Open the application in your web browser
2. Log in with your NET2GRID credentials
3. View your instantaneous power data on the dashboard
4. The data will automatically refresh every 10 seconds

## Project Structure

```
energyUsage/
├── app.py                 # Main Flask application
├── templates/             # HTML templates
│   ├── login.html         # Login page
│   └── dashboard.html     # Dashboard page
├── static/                # Static files
│   └── css/
│       └── style.css      # CSS styles
├── .env                   # Environment variables
├── pyproject.toml         # Project dependencies
├── Dockerfile             # Docker configuration
└── .dockerignore          # Docker ignore file
```

## API Documentation

The application uses the NET2GRID Customer Engagement API. The OpenAPI specification can be found in the `docs/` directory.

## License

[MIT License](LICENSE)