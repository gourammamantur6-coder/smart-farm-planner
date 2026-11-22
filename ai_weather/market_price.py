
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

# Load API key from the main project folder
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

BASE_URL = "https://api.ceda.ashoka.edu.in/v1/agmarknet"


def get_commodities():
    """Fetch the available agricultural commodities from CEDA."""

    api_key = os.getenv("CEDA_API_KEY")

    if not api_key:
        return {"error": "CEDA API key not found"}

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    try:
        response = requests.get(
            f"{BASE_URL}/commodities",
            headers=headers,
            timeout=30
        )

        response.raise_for_status()
        result = response.json()

        commodities = result.get("output", {}).get("data", [])

        return {
            "status": "success",
            "total_commodities": len(commodities),
            "commodities": commodities
        }

    except requests.RequestException as error:
        return {"error": f"CEDA API request failed: {error}"}
    except ValueError:
        return {"error": "Invalid JSON response from CEDA"}
