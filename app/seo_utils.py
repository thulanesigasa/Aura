"""SEO utilities for the Aura platform.

Generates dynamic sitemap.xml and provides JSON-LD helpers.
"""

from datetime import datetime
from flask import url_for


def generate_sitemap_xml(shops, base_url="https://aura.co.za"):
    """Build a sitemap.xml string from a list of shop dicts.

    Each shop dict must have a 'slug' key.
    """
    urls = [
        {
            "loc": f"{base_url}/",
            "lastmod": datetime.utcnow().strftime("%Y-%m-%d"),
            "changefreq": "daily",
            "priority": "1.0",
        }
    ]

    for shop in shops:
        urls.append(
            {
                "loc": f"{base_url}/shop/{shop['slug']}",
                "lastmod": datetime.utcnow().strftime("%Y-%m-%d"),
                "changefreq": "weekly",
                "priority": "0.8",
            }
        )

    xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_parts.append(
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    )
    for u in urls:
        xml_parts.append("  <url>")
        xml_parts.append(f"    <loc>{u['loc']}</loc>")
        xml_parts.append(f"    <lastmod>{u['lastmod']}</lastmod>")
        xml_parts.append(f"    <changefreq>{u['changefreq']}</changefreq>")
        xml_parts.append(f"    <priority>{u['priority']}</priority>")
        xml_parts.append("  </url>")
    xml_parts.append("</urlset>")
    return "\n".join(xml_parts)


def build_local_business_jsonld(shop, base_url="https://aura.co.za"):
    """Return a JSON-LD dict for a LocalBusiness schema."""
    return {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": shop.get("name", ""),
        "description": shop.get("description", ""),
        "url": f"{base_url}/shop/{shop.get('slug', '')}",
        "telephone": shop.get("phone", ""),
        "address": {
            "@type": "PostalAddress",
            "streetAddress": shop.get("address", ""),
            "addressLocality": shop.get("city", ""),
            "addressRegion": shop.get("province", ""),
            "postalCode": shop.get("postal_code", ""),
            "addressCountry": "ZA",
        },
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": shop.get("latitude", 0),
            "longitude": shop.get("longitude", 0),
        },
        "openingHours": shop.get("opening_hours", ""),
        "image": shop.get("image_url", ""),
    }
