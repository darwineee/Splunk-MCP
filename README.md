# Splunk MCP Server

A Model Context Protocol (MCP) server that provides AI agents with the ability to query and interact with Splunk instances. This server enables natural language interactions with Splunk data through secure API connections.

## Features

- **Splunk Query Execution**: Run SPL (Search Processing Language) queries with customizable time ranges
- **Flexible Authentication**: Support for both token-based and username/password authentication
- **Health Monitoring**: Built-in health check endpoint

## Tools Available

### `run_splunk_query`
Execute Splunk search queries and retrieve results.

**Parameters:**
- `query` (str): The Splunk search query to run
- `earliest_time` (str, optional): The earliest time for the search (default: "-24h")
- `latest_time` (str, optional): The latest time for the search (default: "now")

**Returns:** List of search results including data and any messages/warnings

### `get_indexes`
List all accessible Splunk indexes.

**Returns:** List of index names available to the configured user

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd Splunk-MCP
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root with your Splunk configuration:

### Token-based Authentication (Recommended)
```env
SPLUNK_HOST=your-splunk-host.com
SPLUNK_PORT=8089
SPLUNK_PROTOCOL=https
SPLUNK_TOKEN=your-splunk-token
```

### Username/Password Authentication
```env
SPLUNK_HOST=your-splunk-host.com
SPLUNK_PORT=8089
SPLUNK_PROTOCOL=https
SPLUNK_USERNAME=your-username
SPLUNK_PASSWORD=your-password
```

### Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `SPLUNK_HOST` | Splunk server hostname | `localhost` |
| `SPLUNK_PORT` | Splunk management port | `8089` |
| `SPLUNK_PROTOCOL` | Connection protocol (http/https) | `https` |
| `SPLUNK_TOKEN` | Authentication token (preferred) | None |
| `SPLUNK_USERNAME` | Username for basic auth | None |
| `SPLUNK_PASSWORD` | Password for basic auth | None |

## Usage

### Starting the Server

Run the MCP server:
```bash
python main.py
```

The server will start on `http://0.0.0.0:8081` with Server-Sent Events (SSE) transport.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.