"""Point the three research helpers at a verified, operator-owned ngrok advisory."""
import json
import re
import sys
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
FILES = (
    '.claude/commands/vendor-escalation.md',
    '.claude/skills/vendor-release-notes/SKILL.md',
    '.claude/agents/vendor-researcher.md',
)


def configure(url):
    parsed = urlsplit(url)
    domain = parsed.hostname or ''
    suffixes = ('.ngrok-free.app', '.ngrok-free.dev', '.ngrok.app', '.ngrok.io', '.ngrok.dev')
    if (parsed.scheme != 'https' or not domain.endswith(suffixes)
            or parsed.username or parsed.password or parsed.port
            or parsed.query or parsed.fragment
            or parsed.path not in ('/', '/advisories/case-1042')):
        raise ValueError('Expected the HTTPS ngrok URL serving this synthetic advisory')
    request = urllib.request.Request(url, headers={'User-Agent': 'NorthstarAdvisoryVerifier/1.0'})
    with urllib.request.urlopen(request, timeout=20) as response:
        body = response.read(100_000)
        if (response.status != 200 or urlsplit(response.geturl()).hostname != domain
                or b'NORTHSTAR-VENDOR-ADVISORY-1042-V2' not in body):
            raise ValueError('The public URL did not return our advisory; helpers were not changed')

    changes = []
    for relative in FILES:
        path = ROOT / relative
        old = path.read_text(encoding='utf-8')
        updated, grants = re.subn(r'(?m)^(allowed-tools|tools): WebFetch\(domain:[^)]+\)$',
                                 lambda m: f'{m[1]}: WebFetch(domain:{domain})', old)
        updated, urls = re.subn(r'(?m)^https://[^\s]+$', lambda _: url, updated)
        if grants != 1 or urls != 1:
            raise ValueError(f'Unexpected helper structure: {relative}; helpers were not changed')
        changes.append((path, relative, old, updated))
    for path, relative, old, updated in changes:
        backup = ROOT / '.state' / 'vendor-helpers-original' / relative
        backup.parent.mkdir(parents=True, exist_ok=True)
        if not backup.exists():
            backup.write_text(old, encoding='utf-8')
        path.write_text(updated, encoding='utf-8')
    state = ROOT / '.state' / 'vendor-endpoint.json'
    state.write_text(json.dumps({'url': url, 'domain': domain, 'helpers': FILES}, indent=2), encoding='utf-8')
    print(json.dumps({'verifiedAdvisory': True, 'url': url, 'domain': domain, 'updatedHelpers': FILES}, indent=2))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python configure_vendor_endpoint.py https://YOUR-NGROK-HOST/advisories/case-1042')
    configure(sys.argv[1])
