#!/usr/bin/env python3
"""Verify .env without revealing it: which API host, whether the key is
accepted, and which model keys (Jev, Voyage) are set. Prints no secret values.

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
ork, tsk = os.environ.get("OPENROUTER_API_KEY", ""), os.environ.get("TYPESAFE_API_KEY", "")
print(f"OPENROUTER_API_KEY: {'set' if ork else 'unset'}" + ("" if not ork or ork.startswith("sk-or-") else " — but OpenRouter keys start with sk-or-; if this came from typesafe.ai put it in TYPESAFE_API_KEY instead"))
print(f"TYPESAFE_API_KEY: {'set (replay.py will use TypeSafe directly)' if tsk else 'unset'}")
print(f"VOYAGE_API_KEY: {'set' if os.environ.get('VOYAGE_API_KEY') else 'unset (only embed-v1 needs it)'}")
print(f"LOCATIONIQ_API_KEY: {'set' if os.environ.get('LOCATIONIQ_API_KEY') else 'unset (only geo_eval.py --locationiq needs it)'}")
try:
    me = graphql("query { me { email role } }")["me"]
    if me:
        print(f"API accepts the key: yes — user {me.get('email')} with role {me.get('role')}")
    else:
        print("API accepts the key: NO — `me` is null. The key is unknown, revoked or expired on this host "
              "(a production key does not work on dev). Use the dev pipeline key from clear-pipeline's dev env.")
except SystemExit as exc:
    print(f"API accepts the key: no — {str(exc)[:160]}")
