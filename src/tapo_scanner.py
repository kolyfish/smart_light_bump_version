import asyncio
from plugp100.discovery.tapo_discovery import TapoDiscovery

async def scan_tapo_devices(timeout=3):
    """
    Scans for Tapo devices on the local network.
    Returns a list of dictionaries containing device info.
    """
    try:
        devices = await TapoDiscovery.scan(timeout=timeout)
        results = []
        for d in devices:
            # Note: d is a DiscoveredDevice object
            info = {
                "ip": d.ip,
                "mac": d.mac,
                "model": d.device_model,
                "type": d.device_type,
                # nickname/alias might not be available in broadcast response clearly, 
                # but we can try to infer or just show model/IP
            }
            results.append(info)
        return results
    except Exception as e:
        print(f"Scan failed: {e}")
        return []

def get_tapo_devices_sync(timeout=3):
    return asyncio.run(scan_tapo_devices(timeout))

if __name__ == "__main__":
    print("Scanning...")
    devs = get_tapo_devices_sync()
    print(f"Found {len(devs)} devices:")
    for d in devs:
        print(d)
