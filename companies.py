"""Candidate company universe for UK-remote SDR hunting.
Sectors chosen from Si's brief: fintech first, then cloud infra, cybersecurity,
B2B SaaS, data, and energy/commercial finance. No HR tech, no prop tech.
"""

CANDIDATES = {
"fintech": """Monzo, Starling Bank, Revolut, Wise, Checkout.com, GoCardless, Modulr, Thought Machine,
10x Banking, ClearBank, Zopa, Marshmallow, Zilch, Curve, Freetrade, Plum, Moneybox, Tide, Pleo,
Payhawk, Soldo, Ebury, Airwallex, Rapyd, PPRO, Paddle, Primer, TrueLayer, Yapily, Tink, Codat,
Griffin, Lendable, Funding Circle, iwoca, Capital on Tap, YouLend, Kriya, Trade Ledger, Taulia,
Modern Treasury, Unit, Column, Moov, Stripe, Adyen, Mollie, SumUp, Dojo, Teya, Nuvei, Marqeta,
Highnote, Lithic, Thredd, Enfuce, Weavr, Solaris, Swan, Toqio, Vodeno, Featurespace,
ComplyAdvantage, Onfido, Sumsub, Veriff, Persona, Alloy, Sardine, Fingerprint, Quantexa, Ripjar,
Napier, Feedzai, Chainalysis, Elliptic, TRM Labs, Fireblocks, Copper, Kraken, Coinbase, Bitpanda,
Nium, Currencycloud, Banked, Volt, Vyne, Token.io, Sequence, Fintary, Atlar, Numeral, Cledara,
Juni, Vertice, Duna, Kani, Lightyear, Wealthify, Nutmeg, PensionBee, Smart Pension, Cushon""",

"cloudinfra": """Grafana Labs, HashiCorp, Docker, CircleCI, Harness, JFrog, Sonar, Snyk, Sysdig, Datadog,
Dynatrace, Elastic, Chronosphere, Honeycomb, Cribl, Confluent, Redpanda, Databricks, Snowflake,
ClickHouse, Timescale, Cockroach Labs, Neon, PlanetScale, SingleStore, Yugabyte, Redis, MongoDB,
Couchbase, Aiven, DigitalOcean, Scaleway, Civo, Render, Vercel, Netlify, Cloudflare, Fastly,
Nutanix, SUSE, Canonical, Mirantis, Spectro Cloud, Northflank, Qovery, Coder, Gitpod, GitLab,
JetBrains, Sourcegraph, LaunchDarkly, Statsig, Temporal, Camunda, Tray.io, Workato, Boomi,
Celigo, Prismatic, Merge, Nango, Pulumi, Spacelift, env0, Firefly, CloudZero, Vantage, Finout,
Zesty, Cast AI, Ably, Pusher, Twilio, Vonage, MessageBird, Sinch, Nylas, Postman, Kong, Tyk,
Solo.io, Ambassador Labs, Buoyant, Isovalent, Netdata, Better Stack, Incident.io, FireHydrant,
Rootly, PagerDuty, Grafana, InfluxData, QuestDB, StarTree, Imply, Materialize, Estuary, Airbyte,
Fivetran, dbt Labs, Hightouch, Census, Rudderstack, Snowplow, Monte Carlo, Soda, Sifflet, Metaplane""",

"cybersecurity": """CrowdStrike, SentinelOne, Zscaler, Netskope, Cato Networks, Wiz, Orca Security,
Aqua Security, Checkmarx, Veracode, Semgrep, Socket, Chainguard, Tailscale, Teleport, StrongDM,
1Password, Bitwarden, Keeper Security, CyberArk, BeyondTrust, Delinea, Okta, JumpCloud, Silverfort,
Push Security, Material Security, Abnormal Security, Egress, Mimecast, Proofpoint, Darktrace,
Vectra AI, ExtraHop, Corelight, Arctic Wolf, Huntress, Red Canary, Expel, Panther, Hunters,
Recorded Future, Flashpoint, Censys, runZero, Bitsight, SecurityScorecard, UpGuard, Vanta, Drata,
Secureframe, Sprinto, Scrut, Hyperproof, LogicGate, Immersive Labs, Hack The Box, Pentera,
Cymulate, SafeBreach, AttackIQ, NetSPI, Bugcrowd, HackerOne, Intigriti, YesWeHack, Snyk, Jit,
Cycode, Legit Security, Endor Labs, Ox Security, Apiiro, Backslash, Astrix, Oasis Security,
Entro, Clutch Security, Descope, Stytch, WorkOS, Frontegg, Cerbos, Oso, Permit.io, Opal""",

"salestech_b2b": """Cognism, Lusha, Apollo.io, Outreach, Salesloft, Gong, Clari, Highspot, Seismic,
Showpad, Mindtickle, Nooks, Regie.ai, Amplemarket, Clay, Common Room, Warmly, Unify, 6sense,
Demandbase, ZoomInfo, Bombora, G2, Attio, HubSpot, Pipedrive, Close, Copper CRM, Freshworks,
Intercom, Zendesk, Front, Dixa, Ada, Forethought, Sierra, Decagon, Parloa, PolyAI, Cresta,
Observe.AI, Invoca, Aircall, Dialpad, RingCentral, Zoom, Miro, Notion, Airtable, Asana, Monday.com,
Linear, Productboard, Pendo, Amplitude, Mixpanel, Heap, FullStory, Contentsquare, Hotjar, Dovetail,
Typeform, Qualtrics, SurveyMonkey, Sprig, Maze, UserTesting, Docebo, 360Learning, Kahoot""",

"energy_finance": """Octopus Energy, Kraken Technologies, Kaluza, Axle Energy, Field Energy, Zenobe,
Modo Energy, Enode, Tibber, ev.energy, Wallbox, Aira, Sunsave, Arcadia, Uplight, Origami Energy,
Habitat Energy, Flexitricity, Piclo, Elexon, Montel, Amperon, Enode, Gridcog, Watershed, Sweep,
Plan A, Persefoni, Normative, Greenly, Sylvera, BeZero, Patch, Supercritical, Altruistiq,
Cur8, Isometric, ClimateView, Cervest, Jupiter Intelligence, Kettle, Descartes Underwriting,
FloodFlash, Concirrus, Cytora, hyperexponential, Send Technology, Artificial Labs, Eigen
Technologies, Zego, Superscript, Stubben Edge, Tractable, Shift Technology, Sprout.ai, Instanda""",
}


def company_list():
    out = []
    for sector, blob in CANDIDATES.items():
        for name in blob.replace("\n", " ").split(","):
            name = name.strip()
            if name:
                out.append((name, sector))
    # de-duplicate on name, keeping first sector
    seen, uniq = set(), []
    for name, sector in out:
        k = name.lower()
        if k not in seen:
            seen.add(k)
            uniq.append((name, sector))
    return uniq


def slug_variants(name):
    import re
    base = name.lower().strip()
    base = base.replace("&", "and")
    alnum = re.sub(r"[^a-z0-9]+", "", base)
    hyphen = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    nosuffix = re.sub(r"[^a-z0-9]+", "", re.sub(r"\b(labs|inc|technologies|technology|security|energy|io|ai|com|uk|group|ltd|limited)\b", "", base))
    first = re.sub(r"[^a-z0-9]+", "", base.split()[0]) if base.split() else alnum
    variants = [alnum, hyphen, nosuffix, first]
    out, seen = [], set()
    for v in variants:
        if v and v not in seen and len(v) > 2:
            seen.add(v)
            out.append(v)
    return out


if __name__ == "__main__":
    cl = company_list()
    print(len(cl), "candidate companies")
