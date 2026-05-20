"""CLI entry (`python -m indexer` from `apps/indexer`)."""

from __future__ import annotations

import asyncio
import logging
import sys
from datetime import datetime, timezone

import httpx

from indexer.metrics import incr
from indexer.robots_helper import respectful_delay
from indexer.vertex_push import build_document, publish_batch

LOGGER = logging.getLogger("quickpickr.indexer")


async def crawl_and_push(
    retailer: str,
    tier: str,
    zone_id: str,
    *,
    dry_run: bool,
    branch_parent: str,
) -> None:
    from indexer.adapters import ADAPTERS

    adapter = ADAPTERS[retailer]
    rl = adapter.rate_limit_policy()
    urls = adapter.discover_urls(zone_id=zone_id, tier=tier)

    LOGGER.info("%s URLs discovered tier=%s count=%d zone=%s", retailer, tier, len(urls), (zone_id or "")[:12])

    docs: list = []
    async with httpx.AsyncClient(
        headers={"User-Agent": "QuickPickrIndexerBot/1.0 (+mailto:support@example.com)"},
        follow_redirects=True,
        timeout=httpx.Timeout(12.0, connect=4.0),
    ) as client:
        for url in urls:
            await asyncio.sleep(await respectful_delay(url, rl["min_interval_seconds"]))
            try:
                r = await client.get(url)
                r.raise_for_status()
                parsed = adapter.parse_document(r.text, absolute_url=str(r.url))
                if not parsed.get("productUrl"):
                    parsed["productUrl"] = url
                crawled = datetime.now(timezone.utc).isoformat()
                fields = dict(
                    retailer=retailer,
                    zoneId=zone_id,
                    skuId=str(parsed.get("skuId") or parsed.get("title") or url)[:240],
                    title=parsed.get("title"),
                    packSize=parsed.get("packSize"),
                    priceInr=parsed.get("priceInr"),
                    imageUrl=parsed.get("imageUrl"),
                    productUrl=parsed["productUrl"],
                    crawledAt=crawled,
                    freshnessTier=tier,
                )
                docs.append(build_document(fields))
            except Exception:  # noqa: BLE001
                incr(f"parse_failure.retailer.{retailer}")
                LOGGER.exception("parse_failure url=%s", url[:120])

        if docs and not dry_run:
            incr(f"indexed_docs.tier.{tier}", len(docs))
            await asyncio.to_thread(publish_batch, branch_parent, docs)
        elif dry_run and docs:
            LOGGER.info("[dry-run] would import %d docs for %s", len(docs), retailer)


def sync_main(argv: list[str] | None = None) -> int:
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    p = argparse.ArgumentParser(description="QuickPickr ingestion job")
    p.add_argument("--retailer", required=True, choices=["blinkit", "zepto", "bigbasket", "instamart"])
    p.add_argument("--tier", required=True, choices=["hot", "warm", "long_tail"])
    p.add_argument("--zone-id", dest="zone_id", default="IND-zone-default")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args(argv)

    from pathlib import Path

    from dotenv import load_dotenv

    repo_root = Path(__file__).resolve().parents[2]
    load_dotenv(repo_root / ".env")

    branch = __import__("os").environ.get("VERTEX_DATA_STORE_BRANCH", "").strip()
    if not branch and not args.dry_run:
        LOGGER.error("Set VERTEX_DATA_STORE_BRANCH (imports disabled without it)")
        return 2

    asyncio.run(crawl_and_push(args.retailer, args.tier, args.zone_id, dry_run=args.dry_run, branch_parent=branch))
    LOGGER.info("indexer_finished retailer=%s tier=%s dry_run=%s", args.retailer, args.tier, args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(sync_main(sys.argv[1:]))
