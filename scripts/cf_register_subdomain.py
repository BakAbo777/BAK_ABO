"""Register bakabo.workers.dev subdomain via Cloudflare API."""
import requests, urllib3
urllib3.disable_warnings()  # type: ignore

ACCOUNT_ID = "e796d289f744035eee2641e853d8a5af"
CF_TOKEN   = "cfoat_ttdWlIIC0R52Kg3klNqzmBpAGbQRm5oVItDO1yfGsCU.o045AJ39otUUuvu5_G5k31ao_oRDE77mTLus8k8KRAE"
SUBDOMAIN  = "bakabo"

HDR = {
    "Authorization": f"Bearer {CF_TOKEN}",
    "Content-Type": "application/json",
}

# Check current subdomain
r = requests.get(
    f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/workers/subdomain",
    headers=HDR, timeout=15, verify=False
)
print("Current:", r.status_code, r.text[:200])

# Register subdomain
r2 = requests.put(
    f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/workers/subdomain",
    headers=HDR,
    json={"subdomain": SUBDOMAIN},
    timeout=15, verify=False
)
print("Register:", r2.status_code, r2.text[:300])
