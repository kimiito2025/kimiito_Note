from collections import Counter
from ipaddress import ip_address
from scapy.all import PcapNgReader, IP, IPv6, DNS, DNSQR, TCP, Raw

PCAP_PATH = r"10_working/10_MoD/03_webex/webexcc.pcapng"
OUT_EVENTS = r"10_working/10_MoD/03_webex/webexcc_signin_events.txt"
OUT_SUMMARY = r"10_working/10_MoD/03_webex/webexcc_top_domains.txt"

INTEREST_KEYS = [
    "webex",
    "wxcc",
    "cisco",
    "wbx2",
    "ciscospark",
    "engage",
    "ciscoccservice",
    "microsoft",
    "login",
    "split",
]


def is_private_ip(ip: str) -> bool:
    try:
        return ip_address(ip).is_private
    except Exception:
        return False


def extract_sni_from_client_hello(payload: bytes) -> str | None:
    if len(payload) < 5:
        return None

    content_type = payload[0]
    if content_type != 0x16:
        return None

    record_len = int.from_bytes(payload[3:5], "big")
    if len(payload) < 5 + record_len:
        return None

    rec = payload[5 : 5 + record_len]
    if len(rec) < 4 or rec[0] != 0x01:
        return None

    hs_len = int.from_bytes(rec[1:4], "big")
    if len(rec) < 4 + hs_len:
        return None

    body = rec[4 : 4 + hs_len]
    pos = 0

    if len(body) < 34:
        return None

    pos += 2  # client version
    pos += 32  # random

    if pos >= len(body):
        return None
    session_id_len = body[pos]
    pos += 1 + session_id_len

    if pos + 2 > len(body):
        return None
    cipher_len = int.from_bytes(body[pos : pos + 2], "big")
    pos += 2 + cipher_len

    if pos >= len(body):
        return None
    comp_len = body[pos]
    pos += 1 + comp_len

    if pos + 2 > len(body):
        return None
    ext_len = int.from_bytes(body[pos : pos + 2], "big")
    pos += 2
    end_ext = min(len(body), pos + ext_len)

    while pos + 4 <= end_ext:
        ext_type = int.from_bytes(body[pos : pos + 2], "big")
        ext_size = int.from_bytes(body[pos + 2 : pos + 4], "big")
        pos += 4
        if pos + ext_size > end_ext:
            break

        ext_data = body[pos : pos + ext_size]
        pos += ext_size

        if ext_type != 0x0000:
            continue

        if len(ext_data) < 5:
            continue

        list_len = int.from_bytes(ext_data[0:2], "big")
        p = 2
        list_end = min(len(ext_data), 2 + list_len)

        while p + 3 <= list_end:
            name_type = ext_data[p]
            name_len = int.from_bytes(ext_data[p + 1 : p + 3], "big")
            p += 3
            if p + name_len > list_end:
                break
            if name_type == 0:
                server_name = ext_data[p : p + name_len].decode("ascii", errors="ignore").strip().lower()
                return server_name or None
            p += name_len

    return None


def main() -> None:
    packets = []
    ip_counter = Counter()
    first_ts = None

    with PcapNgReader(PCAP_PATH) as pcap:
        for pkt in pcap:
            ts = float(pkt.time)
            if first_ts is None:
                first_ts = ts

            src = dst = None
            if IP in pkt:
                src, dst = pkt[IP].src, pkt[IP].dst
            elif IPv6 in pkt:
                src, dst = pkt[IPv6].src, pkt[IPv6].dst

            if src:
                ip_counter[src] += 1
            if dst:
                ip_counter[dst] += 1

            packets.append((ts, pkt, src, dst))

    local_candidates = [ip for ip in ip_counter if is_private_ip(ip)]
    local_ip = sorted(local_candidates, key=lambda x: ip_counter[x], reverse=True)[0]

    dns_counter = Counter()
    sni_counter = Counter()
    events = []

    for ts, pkt, src, dst in packets:
        if src != local_ip:
            continue
        rel = ts - first_ts

        if DNS in pkt and pkt[DNS].qr == 0 and DNSQR in pkt:
            qname = pkt[DNSQR].qname.decode(errors="ignore").rstrip(".").lower()
            dns_counter[qname] += 1
            if any(k in qname for k in INTEREST_KEYS):
                events.append((rel, "DNS Query", qname, f"{src} -> {dst}"))

        if TCP in pkt and Raw in pkt and int(pkt[TCP].dport) == 443:
            sni = extract_sni_from_client_hello(bytes(pkt[Raw].load))
            if sni:
                sni_counter[sni] += 1
                if any(k in sni for k in INTEREST_KEYS):
                    events.append((rel, "TLS ClientHello", sni, f"{src} -> {dst}:443"))

    seen = set()
    collapsed = []
    for item in sorted(events, key=lambda x: x[0]):
        key = (item[1], item[2])
        if key in seen:
            continue
        seen.add(key)
        collapsed.append(item)

    with open(OUT_EVENTS, "w", encoding="utf-8") as f:
        f.write(f"LOCAL_IP: {local_ip}\n")
        f.write(f"FIRST_TS: {first_ts}\n\n")
        for rel, etype, target, path in collapsed:
            f.write(f"{rel:8.3f}s | {etype:15s} | {target:60s} | {path}\n")

    with open(OUT_SUMMARY, "w", encoding="utf-8") as f:
        f.write(f"LOCAL_IP: {local_ip}\n")
        f.write("\n[Top DNS Queries]\n")
        for name, count in dns_counter.most_common(120):
            if any(k in name for k in INTEREST_KEYS):
                f.write(f"{count:4d} {name}\n")
        f.write("\n[Top TLS SNI]\n")
        for name, count in sni_counter.most_common(200):
            if any(k in name for k in INTEREST_KEYS):
                f.write(f"{count:4d} {name}\n")

    print(f"Wrote: {OUT_EVENTS}")
    print(f"Wrote: {OUT_SUMMARY}")
    print(f"Events: {len(collapsed)}")


if __name__ == "__main__":
    main()
