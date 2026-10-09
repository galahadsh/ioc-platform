import argparse
import ipaddress
import os

import geoip2.database
import geoip2.errors
import psycopg2


GEOIP_DB = "/app/geoip/GeoLite2-City.mmdb"


def connect_db():
    return psycopg2.connect(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ.get("POSTGRES_PORT", "5432"),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    if not 1 <= args.limit <= 1000:
        parser.error("--limit debe estar entre 1 y 1000")

    if not os.path.isfile(GEOIP_DB):
        raise SystemExit(f"No existe la base GeoIP: {GEOIP_DB}")

    conn = connect_db()

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, valor
                FROM iocs
                WHERE LOWER(TRIM(tipo)) = 'ip'
                  AND NULLIF(TRIM(country), '') IS NULL
                ORDER BY id
            """)
            rows = cursor.fetchall()

        analyzed = 0
        matched = 0
        skipped = 0
        updated = 0

        with geoip2.database.Reader(GEOIP_DB) as reader:
            for ioc_id, raw_ip in rows:
                if analyzed >= args.limit:
                    break

                try:
                    ip = ipaddress.ip_address(str(raw_ip).strip())
                except ValueError:
                    skipped += 1
                    continue

                if not ip.is_global:
                    skipped += 1
                    continue

                analyzed += 1

                try:
                    result = reader.city(str(ip))
                except geoip2.errors.AddressNotFoundError:
                    skipped += 1
                    continue

                country = result.country.iso_code
                region = result.subdivisions.most_specific.name
                city = result.city.name

                if not country:
                    skipped += 1
                    continue

                matched += 1

                print(
                    f"IOC {ioc_id} | {ip} | "
                    f"País: {country} | "
                    f"Región: {region or '-'} | "
                    f"Ciudad: {city or '-'}"
                )

                if args.apply:
                    with conn.cursor() as cursor:
                        cursor.execute("""
                            UPDATE iocs
                            SET country = %s,
                                region = %s,
                                city = %s
                            WHERE id = %s
                              AND NULLIF(TRIM(country), '') IS NULL
                        """, (country, region, city, ioc_id))
                        updated += cursor.rowcount

        if args.apply:
            conn.commit()
        else:
            conn.rollback()

        print("\n=== RESULTADO GEOIP ===")
        print(f"IP públicas consultadas: {analyzed}")
        print(f"IP geolocalizadas: {matched}")
        print(f"IP omitidas: {skipped}")
        print(f"Registros actualizados: {updated}")
        print(f"Modo: {'APLICACIÓN' if args.apply else 'SIMULACIÓN'}")

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
