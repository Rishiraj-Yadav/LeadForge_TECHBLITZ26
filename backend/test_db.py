"""Quick DB connection test."""
import ssl, asyncio, sys
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

async def test():
    import asyncpg
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    host = "aws-1-ap-southeast-2.pooler.supabase.com"
    print(f"Connecting to {host}:6543 ...", file=sys.stderr)
    try:
        conn = await asyncio.wait_for(
            asyncpg.connect(
                user="postgres.wdrtsmyzwzjrsmmllqnl",
                password="rishiraj@leadforge",
                host=host,
                port=6543,
                database="postgres",
                ssl=ctx,
                statement_cache_size=0,
            ),
            timeout=10
        )
        print("CONNECTED OK", file=sys.stderr)
        ver = await conn.fetchval("SELECT version()")
        print(f"PG: {ver[:80]}", file=sys.stderr)
        await conn.close()
    except asyncio.TimeoutError:
        print("TIMEOUT after 10s", file=sys.stderr)
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)

asyncio.run(test())
print("DONE", file=sys.stderr)
