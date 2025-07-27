import os
from fastmcp import FastMCP
from dotenv import load_dotenv
import asyncio
from starlette.requests import Request
from starlette.responses import JSONResponse
from splunklib import client, results

splunk_mcp = FastMCP(
    name="Splunk MCP server",
    instructions="""
    This is a Splunk MCP server that allows an AI agent to run Splunk queries and retrieve results.
    Use the `run_splunk_query` tool to execute Splunk queries.
    Use the `get_indexes` tool to list all accessible Splunk indexes.
    """,
)

@splunk_mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request):
    return JSONResponse({"status": "healthy"})

# Do not directly use this variable. Use `get_splunk_service()` instead.
splunk_service_instance: client.Service = None

SPLUNK_HOST = os.getenv("SPLUNK_HOST", "localhost")
SPLUNK_PORT = int(os.getenv("SPLUNK_PORT", 8089))
SPLUNK_PROTOCOL = os.getenv("SPLUNK_PROTOCOL", "https")

SPLUNK_TOKEN = os.getenv("SPLUNK_TOKEN")

def get_splunk_service() -> client.Service:
    """Get a Splunk service instance, creating it if it doesn't already exist."""
    global splunk_service_instance
    if not isinstance(splunk_service_instance, client.Service):
        if SPLUNK_TOKEN:
            splunk_service_instance = client.connect(
                host=SPLUNK_HOST,
                port=SPLUNK_PORT,
                token=SPLUNK_TOKEN,
                scheme=SPLUNK_PROTOCOL,
                verify=SHOULD_USE_SSL,
            )
        else:
            SPLUNK_USERNAME = os.getenv("SPLUNK_USERNAME")
            SPLUNK_PASSWORD = os.getenv("SPLUNK_PASSWORD")
            SHOULD_USE_SSL = SPLUNK_PROTOCOL.lower() == "https"
            if not SPLUNK_USERNAME or not SPLUNK_PASSWORD:
                raise ValueError("SPLUNK_USERNAME and SPLUNK_PASSWORD must be set if SPLUNK_TOKEN is not provided.")
            splunk_service_instance = client.connect(
                host=SPLUNK_HOST,
                port=SPLUNK_PORT,
                username=SPLUNK_USERNAME,
                password=SPLUNK_PASSWORD,
                scheme=SPLUNK_PROTOCOL,
                verify=SHOULD_USE_SSL,
            )
    return splunk_service_instance

@splunk_mcp.tool
def run_splunk_query(query: str, earliest_time: str = "-24h", latest_time: str = "now") -> list:
    """
    Run a Splunk query and return the results.
    
    Args:
        query (str): The Splunk search query to run.
        earliest_time (str): The earliest time for the search (default: -24h).
        latest_time (str): The latest time for the search (default: now).

    Returns:
        list: A list of results from the Splunk search. It may include dictionaries for each result or messages for warnings/errors.
    """
    if not query.strip():
        raise ValueError("Query cannot be empty.")

    service = get_splunk_service()
    kwargs = {
        "earliest_time": earliest_time,
        "latest_time": latest_time,
        "output_mode": "json",
    }
    search_result = service.jobs.oneshot(query, **kwargs)
    reader = results.JSONResultsReader(search_result)
    results_list = []
    for result in reader:
        if isinstance(result, dict):
            results_list.append(result)
        elif isinstance(result, results.Message):
            # Handle messages (warnings, errors) from Splunk
            results_list.append({"message": result.message.value,})

    return results_list

@splunk_mcp.tool
def get_indexes() -> list:
    """
    Lists all accessible Splunk indexes.

    Returns:
        list: A list of index names.
    """
    service = get_splunk_service()
    indexes = service.indexes.list()
    return [index.name for index in indexes]

async def setup():
    load_dotenv()
    await splunk_mcp.run_async(
        transport="sse",
        host="0.0.0.0",
        port=8081,
    )

if __name__ == "__main__":
    asyncio.run(setup())
    splunk_mcp.http_app()