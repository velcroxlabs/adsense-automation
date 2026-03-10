#!/usr/bin/env python3
"""
Minimal Google Ads API connectivity test.

Checks:
- required environment variables are present
- OAuth refresh flow can initialize a client
- accessible customers can be listed
"""

from __future__ import annotations

import os
import sys
from typing import Any, Dict

from env_utils import load_project_env

load_project_env()


REQUIRED_ENV_VARS = [
    "GOOGLE_ADS_DEVELOPER_TOKEN",
    "GOOGLE_ADS_CLIENT_ID",
    "GOOGLE_ADS_CLIENT_SECRET",
    "GOOGLE_ADS_REFRESH_TOKEN",
]


def build_google_ads_config() -> Dict[str, Any]:
    missing = [name for name in REQUIRED_ENV_VARS if not os.getenv(name)]
    if missing:
        print("Missing required environment variables:")
        for name in missing:
            print(f"  - {name}")
        raise SystemExit(1)

    config: Dict[str, Any] = {
        "developer_token": os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"],
        "client_id": os.environ["GOOGLE_ADS_CLIENT_ID"],
        "client_secret": os.environ["GOOGLE_ADS_CLIENT_SECRET"],
        "refresh_token": os.environ["GOOGLE_ADS_REFRESH_TOKEN"],
        "use_proto_plus": True,
    }

    login_customer_id = os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "").strip()
    if login_customer_id:
        config["login_customer_id"] = login_customer_id.replace("-", "")

    return config


def main() -> None:
    try:
        from google.ads.googleads.client import GoogleAdsClient
    except ImportError:
        print("google-ads is not installed.")
        print("Run: pip install google-ads")
        raise SystemExit(1)

    config = build_google_ads_config()

    print("Initializing Google Ads client...")

    try:
        client = GoogleAdsClient.load_from_dict(config)
        customer_service = client.get_service("CustomerService")
        response = customer_service.list_accessible_customers()
    except Exception as exc:
        print(f"Google Ads connection failed: {exc}")
        raise SystemExit(1)

    resources = list(response.resource_names)

    print("Connection successful.")
    print(f"Accessible customers: {len(resources)}")

    if not resources:
        print("No accessible customers returned.")
        return

    for resource_name in resources:
        print(f"  - {resource_name}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
