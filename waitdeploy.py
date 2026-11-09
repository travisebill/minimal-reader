import subprocess, time, json
def sh(c):
    return subprocess.run(c, shell=True, capture_output=True, text=True).stdout.strip()
print('=== wait deploy ===')
for i in range(30):
    out = sh('gh run list --repo travisebill/minimal-reader --limit 1 --json status,conclusion,headSha')
    try:
        d = json.loads(out)[0]
        line = d['status'] + ' ' + str(d.get('conclusion')) + ' ' + d.get('headSha','')[:7]
    except Exception:
        line = out[:40]
    print('  [' + str(i) + '] ' + line)
    if 'completed' in line:
        break
    time.sleep(8)
