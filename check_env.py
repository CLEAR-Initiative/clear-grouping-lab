#!/usr/bin/env python3
"""Verify .env without revealing it: which API host, whether the key is
accepted, and whether OPENROUTER_API_KEY is set. Prints no secret values.

    python3 check_env.py
"""

from __future__ import annotations

import os

from lab_common import graphql, load_env

load_env()
url = os.environ.get("CLEAR_API_URL") or os.environ.get("CLEAR_API_BASE") or ""
host = url.split("//")[-1].split("/")[0]
print(f"CLEAR_API_URL host: {host or '(unset)'}  {'OK dev' if host == 'dev-api.clearinitiative.io' else 'NOT the dev API'}")
key = os.environ.get("CLEAR_API_KEY", "")
print(f"CLEAR_API_KEY: {'set' if key else 'unset'}, {'looks like an API key (sk_live_…)' if key.startswith('sk_live_') else 'does not start with sk_live_ — the API will reject it'}")
print(f"OPENROUTER_API_KEY: {'set' if os.environ.get('OPENROUTER_API_KEY') else 'unset'}")
try:
    me = graphql("query { me { email role } }")["me"]
    if me:
        print(f"API accepts the key: yes — user {me.get('email')} with role {me.get('role')}")
    else:
        print("API accepts the key: NO — `me` is null. The key is unknown, revoked or expired on this host "
              "(a production key does not work on dev). Use the dev pipeline key from clear-pipeline's dev env.")
except SystemExit as exc:
    print(f"API accepts the key: no — {str(exc)[:160]}")
