# -*- coding: utf-8 -*-
"""Canonical BKS collection plan for Shopify.

This module keeps collection rules, copy, SEO and template assignments in one
place so the dashboard and command-line scripts do not drift apart.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


Rule = dict[str, str]


@dataclass(frozen=True)
class CollectionSpec:
    group: str
    title: str
    handle: str
    body_html: str
    rules: tuple[Rule, ...]
    seo_title: str
    seo_description: str
    template: str = "collection"
    template_scope: str = "bks-managed"
    disjunctive: bool = False
    sort_order: str = "manual"
    published: bool = True

    @property
    def effective_template(self) -> str:
        if self.template == "collection" and self.template_scope != "default-excluded-system":
            return f"collection.{self.handle}"
        return self.template

    @property
    def template_suffix(self) -> str | None:
        template = self.effective_template
        if self.template == "collection":
            if template == "collection":
                return None
        if template == "collection":
            return None
        if template.startswith("collection."):
            return template.removeprefix("collection.")
        return template

    @property
    def rule_label(self) -> str:
        joiner = " OR " if self.disjunctive else " AND "
        return joiner.join(
            f"{rule['column']} {rule['relation']} {rule['condition']}"
            for rule in self.rules
        )

    @property
    def seo_description_chars(self) -> int:
        return len(self.seo_description)

    def to_row(self) -> dict[str, Any]:
        row = asdict(self)
        row["base_template"] = self.template
        row["template"] = self.effective_template
        row["rule"] = self.rule_label
        row["template_suffix"] = self.template_suffix or ""
        row["template_scope"] = self.template_scope
        row["seo_description_chars"] = self.seo_description_chars
        row["missing_batch_16"] = self.handle in MISSING_COLLECTION_HANDLES
        return row


def tag_rule(tag: str) -> Rule:
    return {"column": "tag", "relation": "equals", "condition": tag}


EDITORIAL_COLLECTIONS: tuple[CollectionSpec, ...] = (
    CollectionSpec(
        "Editoriali",
        "BKS Hours",
        "bks-hours",
        "<p>Urban contemplation, painterly register, hyperrealist surface. BKS Hours is the signature collection — city light, interior silence, daily life rendered in an AI-generated visual language drawn from the hyperrealist tradition. Every piece in Hours carries the mark of stillness.</p>",
        (tag_rule("collection:hours"),),
        "BKS Hours Collection — AI-Art Wearables",
        "BKS Hours: urban contemplation, hyperrealist AI-art prints on sneakers, outerwear, bags and swimwear. Made to order at bakabo.club.",
        "collection.bks-hours",
        "bks-editorial-template",
    ),
    CollectionSpec(
        "Editoriali",
        "BKS Glyph",
        "bks-glyph",
        "<p>Symbol, code, sign. BKS Glyph is the brand's graphic DNA — a proprietary visual alphabet built from abstract marks, hand-drawn fragments, and invented hieroglyphs. Each piece in Glyph carries a coded field: not decoration, but a system.</p>",
        (tag_rule("collection:glyph"),),
        "BKS Glyph Collection — Coded AI-Art Prints",
        "BKS Glyph: symbolic, coded AI-art prints on all-over garments and accessories. Hand-drawn register, abstract marks. Made to order at bakabo.club.",
        "collection.bks-glyph",
        "bks-editorial-template",
    ),
    CollectionSpec(
        "Editoriali",
        "BKS Marker",
        "bks-marker",
        "<p>The brush, the wall, the mark left behind. BKS Marker is the urban graphic collection — gestural, painted, decisive. AI-generated prints built on the energy of street drawing: drip, stroke, color block, hand-applied sign.</p>",
        (tag_rule("collection:marker"),),
        "BKS Marker Collection — Urban AI-Art Prints",
        "BKS Marker: gestural, urban AI-art prints on garments and accessories. Brush, stroke, drip — graphic energy made wearable. Made to order at bakabo.club.",
        "collection.bks-marker",
        "bks-editorial-template",
    ),
    CollectionSpec(
        "Editoriali",
        "BKS Riviera",
        "bks-riviera",
        "<p>Salt, sun, terracotta, deep blue. BKS Riviera is the resort permanent — Mediterranean coastal energy translated into AI-generated pattern. Swim trunks, shirts, and accessories for life at the water's edge.</p>",
        (tag_rule("collection:riviera"),),
        "BKS Riviera Collection — Mediterranean AI-Art",
        "BKS Riviera: Mediterranean resort collection. AI-art prints on swimwear and accessories — salt, sun, coastal pattern. Made to order at bakabo.club.",
        "collection.bks-riviera",
        "bks-editorial-template",
    ),
    CollectionSpec(
        "Editoriali",
        "BKS Pulse",
        "bks-pulse",
        "<p>Rhythm, vibration, visual motion. BKS Pulse is the optical collection — AI-generated patterns built from geometric repetition, kinetic fields, and modular grids that move as you wear them.</p>",
        (tag_rule("collection:pulse"),),
        "BKS Pulse Collection — Optical AI-Art Prints",
        "BKS Pulse: kinetic, optical AI-art prints on all-over garments and accessories. Geometric repetition, visual vibration. Made to order at bakabo.club.",
        "collection.bks-pulse",
        "bks-editorial-template",
    ),
    CollectionSpec(
        "Editoriali",
        "BKS Token",
        "bks-token",
        "<p>Pixel, game, digital field. BKS Token is the arcade collection — AI-generated patterns drawn from the low-bit visual language of electronic games and kaleidoscopic digital color. Each piece is a collectible object.</p>",
        (tag_rule("collection:token"),),
        "BKS Token Collection — Arcade AI-Art Prints",
        "BKS Token: arcade AI-art prints on all-over garments. Pixel, low-bit color fields and collectible wearable objects. Made to order at bakabo.club.",
        "collection.bks-token",
        "bks-editorial-template",
    ),
    CollectionSpec(
        "Editoriali",
        "BKS Flag",
        "bks-flag",
        "<p>Abstract fields, coded color, graphic blocks. BKS Flag is the pop-collage collection — AI-generated compositions built from color planes, stenciled surfaces, and invented banners. Dada energy, contemporary register.</p>",
        (tag_rule("collection:flag"),),
        "BKS Flag Collection — Pop Collage AI-Art",
        "BKS Flag: abstract color fields and graphic blocks. AI-art pop-collage prints on all-over garments and accessories. Made to order at bakabo.club.",
        "collection.bks-flag",
        "bks-editorial-template",
    ),
    CollectionSpec(
        "Editoriali",
        "BKS Folklore",
        "bks-folklore",
        "<p>Imaginary worlds, drawn stories, invented memory. BKS Folklore is the figurative collection — AI-generated narrative prints built from private mythology, fable animals, garden archetypes, and flat-drawn illustration. Wholly invented, never borrowed.</p>",
        (tag_rule("collection:folklore"),),
        "BKS Folklore Collection — Figurative AI-Art",
        "BKS Folklore: figurative AI-art prints on all-over garments. Invented narrative, fable animals, flat-drawn illustration. Made to order at bakabo.club.",
        "collection.bks-folklore",
        "bks-editorial-template",
    ),
)


NAV_COLLECTIONS: tuple[CollectionSpec, ...] = (
    CollectionSpec(
        "Navigazione",
        "New Arrivals",
        "new-arrivals",
        "<p>The full BKS Studio catalog — AI-generated all-over print garments and accessories, made to order. Sneakers, outerwear, swimwear, bags, and more across the eight permanent collections.</p>",
        (tag_rule("drop:catalog-reset-2026"),),
        "New Arrivals — BKS Studio AI-Art",
        "New arrivals from BKS Studio: AI-generated all-over print wearables across eight collections. Made to order at bakabo.club.",
        template_scope="default-excluded-system",
        sort_order="created-desc",
    ),
    CollectionSpec(
        "Navigazione",
        "Swimwear",
        "swimwear",
        "<p>Swim trunks and one-piece swimsuits from all eight BKS collections. AI-generated all-over prints, quick-dry fabric. Made to order.</p>",
        (tag_rule("type:swim-trunks"), tag_rule("type:one-piece-swimsuit")),
        "BKS Swimwear — AI-Art All-Over Print",
        "BKS Studio swimwear: AI-art all-over print swim trunks and one-piece swimsuits from eight collections. Made to order at bakabo.club.",
        disjunctive=True,
    ),
    CollectionSpec(
        "Navigazione",
        "Outerwear",
        "outerwear",
        "<p>Puffer jackets and windbreakers from all eight BKS collections. AI-generated all-over prints on technical outerwear silhouettes. Made to order.</p>",
        (tag_rule("type:puffer-jacket"), tag_rule("type:windbreaker")),
        "BKS Outerwear — AI-Art Puffers & Windbreakers",
        "BKS Studio outerwear: AI-art all-over print puffer jackets and windbreakers from eight collections. Made to order at bakabo.club.",
        disjunctive=True,
    ),
)


PRODUCT_TYPE_COLLECTIONS: tuple[CollectionSpec, ...] = (
    CollectionSpec(
        "Tipo prodotto",
        "Sneakers",
        "sneakers",
        "<p>All-over print sneakers from all eight BKS collections. AI-generated graphic low-tops, made to order.</p>",
        (tag_rule("type:sneakers"),),
        "BKS Sneakers — AI-Art All-Over Print",
        "BKS Studio all-over print sneakers from eight collections. AI-generated graphic low-tops in multiple colorways. Made to order at bakabo.club.",
    ),
    CollectionSpec(
        "Tipo prodotto",
        "Swim Trunks",
        "swim-trunks",
        "<p>All-over print swim trunks from all eight BKS collections. AI-generated patterns on quick-dry fabric, made to order.</p>",
        (tag_rule("type:swim-trunks"),),
        "BKS Swim Trunks — AI-Art All-Over Print",
        "BKS Studio all-over print swim trunks from eight collections. AI-generated patterns on quick-dry fabric. Made to order at bakabo.club.",
    ),
    CollectionSpec(
        "Tipo prodotto",
        "One-Piece Swimsuit",
        "one-piece-swimsuit",
        "<p>All-over print one-piece swimsuits from all eight BKS collections. AI-generated graphic fields on form-fitting swimwear, made to order.</p>",
        (tag_rule("type:one-piece-swimsuit"),),
        "BKS One-Piece Swimsuit — AI-Art Print",
        "BKS Studio all-over print one-piece swimsuits from eight collections. AI-generated graphic fields on form-fitting swimwear. Made to order.",
    ),
    CollectionSpec(
        "Tipo prodotto",
        "Puffer Jacket",
        "puffer-jacket",
        "<p>All-over print puffer jackets from all eight BKS collections. AI-generated graphic fields on quilted outerwear silhouettes, made to order.</p>",
        (tag_rule("type:puffer-jacket"),),
        "BKS Puffer Jackets — AI-Art All-Over Print",
        "BKS Studio all-over print puffer jackets from eight collections. AI-generated patterns on quilted outerwear. Made to order at bakabo.club.",
    ),
    CollectionSpec(
        "Tipo prodotto",
        "Windbreaker",
        "windbreaker",
        "<p>All-over print windbreaker jackets from all eight BKS collections. AI-generated graphic fields on technical shell silhouettes, made to order.</p>",
        (tag_rule("type:windbreaker"),),
        "BKS Windbreakers — AI-Art All-Over Print",
        "BKS Studio all-over print windbreakers from eight collections. AI-generated patterns on technical shell outerwear. Made to order at bakabo.club.",
    ),
    CollectionSpec(
        "Tipo prodotto",
        "Athletic Shorts",
        "athletic-shorts",
        "<p>All-over print athletic long shorts from all eight BKS collections. AI-generated graphic fields, made to order.</p>",
        (tag_rule("type:athletic-shorts"),),
        "BKS Athletic Shorts — AI-Art All-Over Print",
        "BKS Studio all-over print athletic long shorts from eight collections. AI-generated graphic fields on technical fabric. Made to order at bakabo.club.",
    ),
    CollectionSpec(
        "Tipo prodotto",
        "Lounge Pants",
        "lounge-pants",
        "<p>All-over print lounge pants from all eight BKS collections. AI-generated graphic fields on relaxed-fit fabric, made to order.</p>",
        (tag_rule("type:lounge-pants"),),
        "BKS Lounge Pants — AI-Art All-Over Print",
        "BKS Studio all-over print lounge pants from eight collections. AI-generated patterns on relaxed-fit fabric. Made to order at bakabo.club.",
    ),
    CollectionSpec(
        "Tipo prodotto",
        "Pullover Hoodie",
        "pullover-hoodie",
        "<p>All-over print pullover hoodies from all eight BKS collections. AI-generated graphic fields on fleece-lined silhouettes, made to order.</p>",
        (tag_rule("type:pullover-hoodie"),),
        "BKS Pullover Hoodies — AI-Art All-Over Print",
        "BKS Studio all-over print pullover hoodies from eight collections. AI-generated patterns on fleece-lined silhouettes. Made to order at bakabo.club.",
    ),
    CollectionSpec(
        "Tipo prodotto",
        "Racerback Dress",
        "racerback-dress",
        "<p>All-over print racerback dresses from all eight BKS collections. AI-generated graphic fields on a fitted athletic silhouette, made to order.</p>",
        (tag_rule("type:racerback-dress"),),
        "BKS Racerback Dresses — AI-Art All-Over Print",
        "BKS Studio all-over print racerback dresses from eight collections. AI-generated fields on fitted athletic silhouette. Made to order at bakabo.club.",
    ),
    CollectionSpec(
        "Tipo prodotto",
        "Travel Bag",
        "travel-bag",
        "<p>All-over print travel bags from all eight BKS collections. AI-generated graphic fields on waterproof-coated duffels, made to order.</p>",
        (tag_rule("type:travel-bag"),),
        "BKS Travel Bags — AI-Art All-Over Print",
        "BKS Studio all-over print travel bags from eight collections. AI-generated patterns on waterproof-coated duffel silhouette. Made to order at bakabo.club.",
    ),
    CollectionSpec(
        "Tipo prodotto",
        "Backpack",
        "backpack",
        "<p>All-over print backpacks from all eight BKS collections. AI-generated graphic fields on 13L multi-compartment silhouettes, made to order.</p>",
        (tag_rule("type:backpack"),),
        "BKS Backpacks — AI-Art All-Over Print",
        "BKS Studio all-over print backpacks from eight collections. AI-generated patterns on 13L multi-compartment silhouettes. Made to order at bakabo.club.",
    ),
    CollectionSpec(
        "Tipo prodotto",
        "Flip Flop",
        "flip-flop",
        "<p>All-over print flip flops from all eight BKS collections. AI-generated graphic fields on the strap and footbed, made to order.</p>",
        (tag_rule("type:flip-flop"),),
        "BKS Flip Flops — AI-Art All-Over Print",
        "BKS Studio all-over print flip flops from eight collections. AI-generated patterns on strap and footbed. Made to order at bakabo.club.",
    ),
    CollectionSpec(
        "Tipo prodotto",
        "Cozy Slipper",
        "cozy-slipper",
        "<p>All-over print cozy slippers from all eight BKS collections. AI-generated graphic fields on an indoor slip-on silhouette, made to order.</p>",
        (tag_rule("type:cozy-slipper"),),
        "BKS Cozy Slippers — AI-Art All-Over Print",
        "BKS Studio all-over print cozy slippers from eight collections. AI-generated patterns on indoor slip-on silhouette. Made to order at bakabo.club.",
    ),
    CollectionSpec(
        "Tipo prodotto",
        "Women's Tee",
        "womens-tee",
        "<p>All-over print women's cut-and-sew tees from all eight BKS collections. AI-generated graphic fields on a fitted silhouette, made to order.</p>",
        (tag_rule("type:womens-tee"),),
        "BKS Women's Tee — AI-Art All-Over Print",
        "BKS Studio all-over print women's cut-and-sew tees from eight collections. AI-generated patterns on fitted silhouette. Made to order at bakabo.club.",
    ),
)


ALL_COLLECTIONS: tuple[CollectionSpec, ...] = EDITORIAL_COLLECTIONS + NAV_COLLECTIONS + PRODUCT_TYPE_COLLECTIONS

MISSING_COLLECTION_HANDLES: frozenset[str] = frozenset(
    {
        "sneakers",
        "swim-trunks",
        "one-piece-swimsuit",
        "racerback-dress",
        "pullover-hoodie",
        "puffer-jacket",
        "windbreaker",
        "athletic-shorts",
        "lounge-pants",
        "travel-bag",
        "backpack",
        "flip-flop",
        "cozy-slipper",
        "womens-tee",
        "swimwear",
        "outerwear",
    }
)

MANAGED_HANDLES: frozenset[str] = frozenset(spec.handle for spec in ALL_COLLECTIONS)

TEMPLATE_EXCLUDED_HANDLES: frozenset[str] = frozenset(
    {
        "new-arrivals",
        "avada-best-sellers",
        "digital-goods-vat-tax",
    }
)

LEGACY_COLLECTION_METAFIELDS: tuple[dict[str, str], ...] = (
    {"label": "BKS 🏄 Pullover Hoodie", "problem": "Emoji + legacy label format", "action": "Eliminare definizione"},
    {"label": "BKS 👟 Line 1 Sneakers", "problem": 'Emoji + "Line 1" naming legacy', "action": "Eliminare definizione"},
    {"label": "BKS 🎒 Backpack", "problem": "Emoji in metafield label", "action": "Eliminare definizione"},
    {"label": "BKS 🎯 Flip Flops", "problem": 'Emoji + mismatch con handle "flip-flop"', "action": "Eliminare definizione"},
    {"label": "BKS 💼 Duffel Bag", "problem": "Tipo non attivo nel catalogo BKS 2026", "action": "Eliminare definizione"},
    {"label": "BKS 🧥 Windbreaker Jackets", "problem": 'Emoji + plurale non standard "Jackets"', "action": "Eliminare definizione"},
    {"label": "BKS Line 2 👟 Sneakers", "problem": 'Naming legacy "Line 2"', "action": "Eliminare definizione"},
    {"label": "BKS 🏖️ Beach towels", "problem": "Categoria non attiva nel catalogo 2026", "action": "Eliminare definizione"},
    {"label": "BKS 🏝️ Island Sneakers", "problem": "Legacy nome linea", "action": "Eliminare definizione"},
    {"label": "BKS 👑 Tiaras & Stamps...", "problem": "Legacy prodotto dismesso", "action": "Eliminare definizione"},
    {"label": "BKS 🇯🇵 Japan Sneakers", "problem": "Bandiera nazione + legacy", "action": "Eliminare definizione"},
    {"label": "BKS 🍊 Mondello Sneakers", "problem": "Legacy nome luogo", "action": "Eliminare definizione"},
    {"label": "BKS 🧥 Puffer Jacket", "problem": "Emoji su tipo prodotto attivo", "action": "Eliminare definizione"},
    {"label": "BKS 🥿 Indoor Slippers", "problem": 'Emoji + mismatch con "cozy-slipper"', "action": "Eliminare definizione"},
    {"label": "BKS 🕹️ Arcade Sneakers", "problem": "Emoji + legacy naming", "action": "Eliminare definizione"},
    {"label": "BKS 🐟 Fish Citizens...", "problem": "Legacy nome prodotto", "action": "Eliminare definizione"},
    {"label": "BKS 🏊 Swim Trunks", "problem": "Emoji", "action": "Eliminare definizione"},
    {"label": "BKS 💃 Chic One-Piece...", "problem": 'Emoji + voce legacy "Chic"', "action": "Eliminare definizione"},
)


def collection_to_payload(spec: CollectionSpec) -> dict[str, Any]:
    """Return a Shopify REST smart_collection payload."""
    return {
        "smart_collection": {
            "title": spec.title,
            "handle": spec.handle,
            "body_html": spec.body_html,
            "rules": list(spec.rules),
            "disjunctive": spec.disjunctive,
            "sort_order": spec.sort_order,
            "published": spec.published,
            "template_suffix": spec.template_suffix,
            "metafields_global_title_tag": spec.seo_title,
            "metafields_global_description_tag": spec.seo_description,
        }
    }


def specs_for_missing_batch() -> tuple[CollectionSpec, ...]:
    return tuple(spec for spec in ALL_COLLECTIONS if spec.handle in MISSING_COLLECTION_HANDLES)
