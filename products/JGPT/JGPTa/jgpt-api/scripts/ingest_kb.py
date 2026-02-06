#!/usr/bin/env python3
from __future__ import annotations
import asyncio
from app.db.init_db import init_db
from app.util.ingest import ingest_kb

async def main():
    init_db()
    report = await ingest_kb()
    print(report)

if __name__ == "__main__":
    asyncio.run(main())
