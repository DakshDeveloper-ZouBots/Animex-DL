# Animex GraphQL & REST Scraper[span_0](start_span)[span_0](end_span)
from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Any, Literal
from curl_cffi import requests

logger = logging.getLogger("animex_scraper")

GRAPHQL_URL = "https://graphql.animex.one/graphql"
SERVERS_URL = "https://pp.animex.one/rest/api/servers"
SOURCES_URL = "https://pp.animex.one/rest/api/sources"

FAST_SEARCH_QUERY = """
query FastSearch($query: String, $limit: Int) {
  catalogAnime(filter: { query: $query }, limit: $limit) {
    items { id titleRomaji titleEnglish coverImage episodeCount seasonYear format status }
  }
}
"""

@dataclass
class AnimexClient:
    session: requests.Session | None = None
    timeout: float = 15.0

    def __post_init__(self) -> None:
        if self.session is None:
            self.session = requests.Session(impersonate="chrome")

    def _get(self, url: str, params: dict[str, Any] | None = None) -> Any:
        resp = self.session.get(url, params=params, timeout=self.timeout, impersonate="chrome")
        resp.raise_for_status()
        return resp.json()

    def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        payload = {"query": FAST_SEARCH_QUERY, "variables": {"query": query, "limit": limit}}
        resp = self.session.post(GRAPHQL_URL, json=payload, timeout=self.timeout, impersonate="chrome")
        return resp.json().get("data", {}).get("catalogAnime", {}).get("items", [])

    def get_all_sources(
        self,
        anime_id: str,
        ep_num: int,
        type_: Literal["sub", "dub"] = "sub",
    ) -> list[dict[str, Any]]:
        servers = self._get(SERVERS_URL, params={"id": anime_id, "epNum": ep_num})
        providers = servers.get(f"{type_}Providers") or []
        if not providers:
            return []
        prov_id = providers[0]["id"]
        sources_data = self._get(
            SOURCES_URL,
            params={"id": anime_id, "epNum": ep_num, "type": type_, "providerId": prov_id}
        )
        return sources_data.get("sources") or []
