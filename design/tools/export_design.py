"""캔버스(.dc.html) 시안을 브라우저에서 바로 열리는 정적 HTML과 PNG로 내보낸다.

사용: python export_design.py <project 폴더> <출력 폴더>
"""

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

# (원본 아트보드, 출력 이름, 넘길 props, 화면 폭)
SCREENS = [
    ("Main", "_common-styleguide", {}, 1440),
    ("AdminHeader", "SCR-A-013-admin-header", {}, 1440),
    ("UserHeader", "SCR-U-004-user-header", {}, 1440),
    ("Login", "SCR-C-001-login", {}, 1440),
    ("Login", "SCR-C-001-login-user-app", {"app": "사용자 앱", "showError": False, "showSignupDone": True}, 1440),
    ("Password", "SCR-C-002-password-forced", {}, 1440),
    ("Dashboard", "SCR-C-003-dashboard", {}, 1440),
    ("DashboardExpanded", "SCR-C-003-dashboard-deck-expanded", {}, 1440),
    ("StatsPanel", "SCR-C-003-stats-panel-all", {}, 420),
    ("Graph", "SCR-C-004-graph", {}, 1440),
    ("ExcelModal", "SCR-C-006-excel", {}, 560),
    ("Users", "SCR-A-001-users", {}, 1440),
    ("UserDetail", "SCR-A-002-user-detail", {}, 600),
    ("Admins", "SCR-A-003-admins", {}, 1440),
    ("Zones", "SCR-A-004-zones", {}, 1440),
    ("ZoneNeighbors", "SCR-A-005-zone-neighbors", {}, 640),
    ("Cameras", "SCR-A-006-cameras", {}, 1440),
    ("CameraForm", "SCR-A-007-camera-form", {}, 600),
    ("LiveView", "SCR-A-008-live-view", {}, 1200),
    ("Playback", "SCR-A-009-playback", {}, 1440),
    ("Events", "SCR-A-010-events", {}, 1440),
    ("EventDetail", "SCR-A-011-event-detail", {}, 960),
    ("ActionModal", "SCR-A-011-action", {}, 560),
    ("History", "SCR-A-012-history", {}, 1440),
    ("Signup", "SCR-U-001-signup", {}, 1440),
    ("Pending", "SCR-U-002-pending", {}, 1440),
    ("Withdraw", "SCR-U-003-withdraw", {}, 560),
]

# 링크 대상: 원본 아트보드 → 첫 번째 출력 파일
LINKS = {}
for src, out, _, _ in SCREENS:
    LINKS.setdefault(src + ".dc.html", out + ".html")

EXPAND_JS = r"""
(arg) => {
  const files = arg.files, links = arg.links;
  const heads = [];
  const lookup = (scope, path) => {
    path = path.trim();
    if (path === 'true') return true;
    if (path === 'false') return false;
    if (/^-?\d+(\.\d+)?$/.test(path)) return Number(path);
    return path.split('.').reduce((o, k) => (o == null ? undefined : o[k]), scope);
  };
  const interp = (str, scope) => {
    const whole = str.match(/^\s*\{\{([^}]+)\}\}\s*$/);
    if (whole) return { whole: true, val: lookup(scope, whole[1]) };
    return { whole: false, val: str.replace(/\{\{([^}]+)\}\}/g, (m, p) => {
      const v = lookup(scope, p); return v == null ? '' : String(v);
    }) };
  };
  const expand = (node, scope, parent) => {
    if (node.nodeType === 3) { parent.appendChild(document.createTextNode(interp(node.textContent, scope).val)); return; }
    if (node.nodeType !== 1) return;
    const tag = node.nodeName.toLowerCase();
    if (tag === 'sc-for') {
      const list = interp(node.getAttribute('list'), scope).val || [];
      const as = node.getAttribute('as');
      list.forEach((it, i) => {
        const s = Object.assign({}, scope, { [as]: it, $index: i });
        node.childNodes.forEach((c) => expand(c, s, parent));
      });
      return;
    }
    if (tag === 'sc-if') {
      if (interp(node.getAttribute('value'), scope).val) node.childNodes.forEach((c) => expand(c, scope, parent));
      return;
    }
    if (tag === 'dc-import') {
      const props = {};
      for (const a of node.attributes) {
        if (a.name === 'name' || a.name.startsWith('hint-')) continue;
        props[a.name.replace(/-([a-z])/g, (m, c) => c.toUpperCase())] = interp(a.value, scope).val;
      }
      const r = compile(node.getAttribute('name') + '.dc.html', props);
      const t = document.createElement('template');
      t.innerHTML = r.body;
      parent.appendChild(t.content);
      return;
    }
    const el = document.importNode(node, false);
    for (const a of [...el.attributes]) {
      if (!a.value.includes('{{')) continue;
      const r = interp(a.value, scope);
      if (r.whole && (r.val === false || r.val == null)) el.removeAttribute(a.name);
      else if (r.whole && r.val === true) el.setAttribute(a.name, '');
      else el.setAttribute(a.name, String(r.val));
    }
    if (el.hasAttribute('href') && links[el.getAttribute('href')]) el.setAttribute('href', links[el.getAttribute('href')]);
    node.childNodes.forEach((c) => expand(c, scope, el));
    parent.appendChild(el);
  };
  const compile = (name, props) => {
    const doc = new DOMParser().parseFromString(files[name], 'text/html');
    const script = doc.querySelector('script[data-dc-script]');
    const decl = JSON.parse(script.getAttribute('data-props') || '{}');
    const p = {};
    for (const k in decl) if (decl[k] && 'default' in decl[k]) p[k] = decl[k].default;
    Object.assign(p, props);
    class DCLogic { constructor(pr) { this.props = pr; this.state = {}; } setState() {} forceUpdate() {} }
    const Comp = new Function('DCLogic', script.textContent + '\nreturn Component;')(DCLogic);
    const vals = new Comp(p).renderVals();
    const xdc = doc.querySelector('x-dc');
    const helmet = xdc.querySelector('helmet');
    if (helmet && !heads.includes(helmet.innerHTML)) heads.push(helmet.innerHTML);
    const out = document.createElement('div');
    xdc.childNodes.forEach((c) => { if (c.nodeName !== 'HELMET') expand(c, vals, out); });
    return { body: out.innerHTML, title: doc.title };
  };
  const r = compile(arg.entry, arg.props);
  return { title: r.title, body: r.body, heads };
}
"""


def main() -> None:
    project, out = Path(sys.argv[1]), Path(sys.argv[2])
    (out / "screens").mkdir(parents=True, exist_ok=True)
    (out / "png").mkdir(parents=True, exist_ok=True)
    # 캔버스에서 받은 폴더면 we.css가 함께 있다. 저장소의 src/에는 없고 출력 폴더의 we.css를 그대로 쓴다
    if (project / "we.css").exists():
        (out / "we.css").write_text((project / "we.css").read_text(encoding="utf-8"), encoding="utf-8")
    files = {p.name: p.read_text(encoding="utf-8") for p in project.glob("*.dc.html")}
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        page.set_content("<!doctype html><html><body></body></html>")
        for src, name, props, width in SCREENS:
            r = page.evaluate(EXPAND_JS, {"files": files, "links": LINKS, "entry": src + ".dc.html", "props": props})
            html = (
                '<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
                f"<title>{r['title']}</title>\n"
                '<link rel="stylesheet" href="../we.css">\n'
                + "\n".join(h.strip() for h in r["heads"])
                + "\n</head>\n<body>\n"
                + r["body"].strip()
                + "\n</body>\n</html>\n"
            )
            path = out / "screens" / (name + ".html")
            path.write_text(html, encoding="utf-8")
            shot = browser.new_page(viewport={"width": width, "height": 600})
            shot.goto(path.resolve().as_uri(), wait_until="networkidle")
            shot.evaluate("document.fonts.ready")
            shot.screenshot(path=str(out / "png" / (name + ".png")), full_page=True)
            shot.close()
            print(name)
        browser.close()


if __name__ == "__main__":
    main()
