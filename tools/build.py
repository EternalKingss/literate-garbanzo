#!/usr/bin/env python3
"""Builds every page of the Lords Mobile Wonder Guide from the data in this file.

Edit the data (COMPS, BATTLES, FORMATIONS ...) and run:  python3 tools/build.py
The HTML files in the repo root are generated - edit here, not there.
"""
import html
import json
import os
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RALLY = 4_313_000  # full rally cap seen in today's reports

PAGES = [
    ("index.html", "Scout reader"),
    ("CompGears.html", "Comps"),
    ("formations.html", "Formations"),
    ("advanced.html", "Wonder rules"),
    ("battle-reports.html", "Battle log"),
    ("heroes.html", "Heroes & familiars"),
]

E = html.escape


def img(path):
    return quote(path)


# ---------------------------------------------------------------- comp codes
def code(digits, size=""):
    """digits: ('6','5','9') or ('14','3','3'). Renders each digit in its troop colour."""
    i, r, c = digits
    cls = f"code {size}".strip()
    return (f'<span class="{cls}" aria-label="{i}-{r}-{c} comp">'
            f'<span class="i">{i}</span><span class="r">{r}</span><span class="c">{c}</span></span>')


def ratio(i, r, c, thin=False):
    t = " thin" if thin else ""
    tot = (i + r + c) or 1
    lab = f"Infantry {i/tot:.0%}, ranged {r/tot:.0%}, cavalry {c/tot:.0%}"
    return (f'<div class="ratio{t}" role="img" aria-label="{lab}" style="--i:{i};--r:{r};--c:{c}">'
            f'<span class="i"></span><span class="r"></span><span class="c"></span></div>')


def m(n):
    """1_234_567 -> 1.23M, 40_000 -> 40K"""
    if n is None:
        return "—"
    if n >= 1_000_000:
        return f"{n/1e6:.2f}M"
    return f"{round(n/1000):,}K"


def src(kind, text):
    return f'<span class="src {kind}">{E(text)}</span>'


SRC_SHEET = src("", "sheet")
SRC_SITE = src("", "old site")
SRC_GAME = src("game", "game files")
SRC_OPEN = src("open", "untested")


def logref(*ids):
    return " ".join(src("log", f"log {i}") for i in ids)


# ---------------------------------------------------------------- page shell
def shell(fname, title, desc, body, scripts=False):
    nav = "".join(
        f'<a href="{f}"{" aria-current=\"page\"" if f == fname else ""}>{E(t)}</a>' for f, t in PAGES
    )
    js = '<script src="assets/site.js" defer></script>' if scripts else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)} · Lords Mobile Wonder Guide</title>
<meta name="description" content="{E(desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@700;800&family=Red+Hat+Text:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 30 30'%3E%3Crect width='30' height='30' fill='%231e2925'/%3E%3Crect x='4' y='6' width='6' height='18' fill='%2393a9c4'/%3E%3Crect x='12' y='6' width='6' height='18' fill='%235fbba9'/%3E%3Crect x='20' y='6' width='6' height='18' fill='%23e2a94b'/%3E%3C/svg%3E">
<link rel="stylesheet" href="assets/site.css">
{js}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="bar"><div class="bar-inner">
<a class="brand" href="index.html">Wonder<span>Guide</span></a>
<nav class="nav" aria-label="Pages">{nav}</nav>
</div></header>
<main id="main">
{body}
</main>
<footer><div class="inner">
<span>Lords Mobile Wonder Guide. Built from real Wonder battle reports and the game's own data files. Updated 19 Nov 2026.</span>
<span>Video guides: <a href="https://www.youtube.com/@crystalbriefs" rel="noopener">Crystal Briefs on YouTube</a></span>
</div></footer>
</body>
</html>
"""


def write(fname, content):
    with open(os.path.join(ROOT, fname), "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", fname, len(content))


# ================================================================ BATTLE LOG
# side = dict(who, comp, tr=(inf, rng, cav) or None, total, form)
# att_loss / def_loss in troops. us = 'att' | 'def' | None (whose side the guild was on)
def S(who, comp, tr, form, total=None, note=""):
    t = total if total is not None else (sum(tr) if tr else None)
    return dict(who=who, comp=comp, tr=tr, form=form, total=t, note=note)


BATTLES = [
    # ---- guild fights, 19 Nov
    dict(id=1, day="19 Nov", group="guild", place="Chaos Citadel",
         att=S("T69 rally", "758ish", (1_635_572, 1_091_983, 1_585_445), "Ranged Phalanx", note="sent as 668, landed 7.5-5-7.5"),
         dfn=S("Lucky Bo", "857", (1_590_006, 1_051_136, 1_532_746), "Ranged Phalanx"),
         al=1_330_057, dl=1_349_985, us="att", tags=["mirror"],
         lesson="Both ranged fronts died. Then cav vs cav: we had 50K more cav and won the trade by about 20K."),
    dict(id=2, day="19 Nov", group="guild", place="Chaos Citadel (we held it)",
         att=S("Lucky Bo rally", "758", (1_483_061, 1_131_286, 1_698_653), "Ranged Phalanx"),
         dfn=S("T69 garrison", "758", (1_471_803, 1_185_170, 1_620_002), "Cavalry Phalanx"),
         al=1_397_675, dl=1_422_670, us="def", tags=["cav-into-range"],
         lesson="We switched to Cav Phalanx off a half-filled scout. Final rally was cav-heaviest. Our cav front killed his ranged but lost 78% of itself."),
    dict(id=3, day="19 Nov", group="guild", place="Chaos Citadel",
         att=S("T69 rally", "758ish", (1_621_513, 1_089_173, 1_602_314), "Ranged Phalanx", note="sent as 668"),
         dfn=S("Lucky Bo", "659ish", (1_371_218, 1_035_967, 1_824_444), "Ranged Phalanx"),
         al=1_531_496, dl=1_324_830, us="att", tags=["mirror"],
         lesson="He had 220K more cav. After both ranged died his cav ran into our infantry. Our extra infantry was a liability, not an edge."),
    dict(id=4, day="19 Nov", group="guild", place="Relay Bunker 2",
         att=S("T69 rally", "668", None, "Ranged Phalanx", total=4_313_000, note="breakdown not captured"),
         dfn=S("Big No0b", "1262", (2_583_143, 1_301_999, 384_854), "Ranged Phalanx", note="from scout"),
         al=1_321_744, dl=1_848_614, us="att", tags=["mirror"],
         lesson="Even ranged, about 1.3M more cav on our side. Big win."),
    dict(id=5, day="19 Nov", group="guild", place="Relay Bunker 2 (we held it)",
         att=S("Big No0b rally", "8-11-1", (1_643_729, 2_230_250, 296_020), "Ranged Phalanx"),
         dfn=S("T69 garrison", "758", (1_520_909, 1_081_416, 1_710_673), "Ranged Phalanx"),
         al=2_212_251, dl=1_297_498, us="def", tags=["mirror"],
         lesson="He doubled our ranged and still lost 99% of it. Our 1.71M cav decided it."),
    dict(id=6, day="19 Nov", group="guild", place="Relay Bunker 2 (we held it)",
         att=S("Big No0b rally", "8-11-1", (1_497_518, 2_386_071, 386_411), "Ranged Phalanx"),
         dfn=S("T69 garrison", "758", (1_492_352, 1_166_192, 1_654_456), "Ranged Phalanx"),
         al=1_877_138, dl=1_650_155, us="def", tags=["mirror"],
         lesson="Same idea, more ranged. 560K of his ranged survived and kept shooting our cav, so the win shrank from 915K to 227K."),
    dict(id=7, day="19 Nov", group="guild", place="Wonder hit (stronger account)",
         att=S("T69 rally", "7-9-4", (1_488_913, 2_018_162, 805_925), "Ranged Phalanx"),
         dfn=S("Stronger account", "9-6-4", (1_927_436, 1_300_497, 908_638), "Ranged Phalanx"),
         al=1_759_280, dl=1_877_075, us="att", tags=["mirror"],
         lesson="100K less cav but 720K more ranged. Their ranged died first, ours kept firing. Won against a stronger account."),
    dict(id=8, day="19 Nov", group="guild", place="Wonder hit (stronger account)",
         att=S("T69 rally", "055", (40_000, 2_546_220, 1_726_780), "Infantry Wedge"),
         dfn=S("Stronger account", "7-8-4", (1_548_095, 1_758_867, 961_670), "unknown"),
         al=1_808_860, dl=1_819_800, us="att", tags=["055"],
         lesson="Same shape as log 14 and the same result: an even trade at about 1.76M enemy ranged."),
    dict(id=9, day="19 Nov", group="guild", place="Our wonder (055 garrison)",
         att=S("Stronger account", "875", (1_719_967, 1_536_653, 1_056_379), "unknown"),
         dfn=S("T69 garrison", "055", (50_000, 2_755_000, 1_508_000), "unknown"),
         al=1_765_491, dl=1_427_410, us="def", tags=["055"],
         lesson="A 055 sitting as garrison beat an 875. The ranged stack did the killing, the cav soaked."),
    dict(id=10, day="19 Nov", group="guild", place="Chaos Citadel (Mc Qai)",
         att=S("T69 rally (strongest lead)", "055", (50_000, 2_381_485, 1_870_862), "Infantry Wedge"),
         dfn=S("Mc Qai", "758", (1_546_798, 1_032_137, 1_731_677), "Ranged Phalanx"),
         al=1_297_407, dl=2_405_949, us="att", tags=["055"],
         lesson="The exact matchup that lost in logs 12 and 15, flipped by a much stronger 055 lead. Stats decide 055 into 758."),
    dict(id=11, day="19 Nov", group="guild", place="Our wonder (no infantry)",
         att=S("857 rally", "857", (1_671_903, 1_127_485, 1_513_111), "unknown"),
         dfn=S("T69 garrison", "0-9-8", (0, 1_995_651, 1_849_327), "unknown", note="only 3.85M, not full"),
         al=958_111, dl=2_421_957, us="def", tags=["garrison"],
         lesson="More cav and more ranged than him, still crushed. No infantry meant his infantry ate our ranged unopposed."),
    # ---- shared reports, top accounts
    dict(id=12, day="18 Nov", group="shared", place="Chaos Citadel",
         att=S("HeyChars", "055", (40_000, 2_388_294, 1_884_701), "Infantry Wedge"),
         dfn=S("Defender", "857", (1_632_872, 1_131_000, 1_508_000), "Ranged Phalanx"),
         al=1_401_599, dl=1_239_099, us=None, tags=["055"],
         lesson="055 lost 64% of its cav to the Range Phalanx front."),
    dict(id=13, day="18 Nov", group="shared", place="Chaos Citadel",
         att=S("HeyChars", "884", (1_696_501, 1_696_499, 919_996), "Ranged Phalanx"),
         dfn=S("Defender", "866ish", (1_575_625, 1_168_500, 1_363_250), "Ranged Phalanx"),
         al=1_632_281, dl=1_571_127, us=None, tags=["mirror"],
         lesson="Defender lost all its ranged first and still came out ahead: it had 440K more cav."),
    dict(id=14, day="16 Nov", group="shared", place="Relay Bunker 3",
         att=S("Shared account", "055", (50_007, 2_418_135, 1_969_858), "Infantry Wedge"),
         dfn=S("OmaiGon", "785", (1_443_362, 1_765_501, 984_131), "Ranged Phalanx"),
         al=1_555_160, dl=1_571_834, us=None, tags=["055"],
         lesson="055 into 1.77M ranged: even. The old 1.1M ranged limit is too strict."),
    dict(id=15, day="17 Nov", group="shared", place="Chaos Citadel",
         att=S("Wolf BaziL", "055", (40_000, 2_389_187, 1_883_813), "Infantry Wedge"),
         dfn=S("Defender", "758", (1_496_504, 1_178_886, 1_612_529), "Ranged Phalanx"),
         al=1_398_981, dl=1_200_003, us=None, tags=["055"],
         lesson="055 into a 758 Range Phalanx at even-ish stats: defender wins."),
    dict(id=16, day="18 Nov", group="shared", place="Relay Bunker 3",
         att=S("Liangzai A", "?", None, "Infantry Wedge", total=4_113_846),
         dfn=S("Defender", "?", None, "Ranged Phalanx", total=4_313_000),
         al=1_606_553, dl=1_356_763, us=None, tags=["055"],
         lesson="Breakdown not captured. Infantry Wedge into Range Phalanx, defender wins."),
    # ---- old site reports (dates unknown)
    dict(id=17, day="earlier", group="old", place="Old site report",
         att=S("Attacker", "857", (1_650_000, 1_150_000, 1_490_000), "Cavalry Phalanx", total=4_290_000),
         dfn=S("Defender", "758", (1_490_000, 1_100_000, 1_600_000), "Ranged Phalanx", total=4_110_000),
         al=1_310_000, dl=1_490_000, us=None, tags=["cav-into-range"],
         lesson="Cav Phalanx beat Range Phalanx. Attacker lost 1.2M cav, defender lost all ranged."),
    dict(id=18, day="earlier", group="old", place="Old site report",
         att=S("Attacker", "?", None, "Cavalry Phalanx", total=4_290_000),
         dfn=S("Defender", "?", None, "Infantry Phalanx", total=4_170_000),
         al=1_890_000, dl=1_420_000, us=None, tags=[],
         lesson="Goes against the triangle and there's no troop breakdown to explain it. Treat as unexplained."),
    dict(id=19, day="earlier", group="old", place="Old site report",
         att=S("Attacker", "?", None, "Ranged Phalanx", total=4_290_000),
         dfn=S("Defender", "?", None, "Infantry Wedge", total=4_230_000),
         al=1_560_000, dl=1_480_000, us=None, tags=[],
         lesson="Close. Infantry Wedge held slightly better."),
    dict(id=20, day="earlier", group="old", place="Old site report",
         att=S("Attacker", "?", None, "Cavalry Phalanx", total=4_290_000),
         dfn=S("Defender", "?", None, "Ranged Phalanx", total=3_900_000, note="not full"),
         al=1_530_000, dl=1_750_000, us=None, tags=["cav-into-range"],
         lesson="Cav Phalanx won again, but the defender was 400K short."),
]

# re-number in display order: guild first, then shared, then old
for n, b in enumerate(BATTLES, 1):
    b["id"] = n


def result(b):
    """Margin from the attacker's view: positive = attacker came out ahead."""
    margin = b["dl"] - b["al"]
    if abs(margin) < 30_000:
        word, cls = "Even", "even"
    elif margin > 0:
        word, cls = "Attacker", "win"
    else:
        word, cls = "Defender", "loss"
    return margin, word, cls


def side_cell(s):
    tr = s["tr"]
    if tr:
        bar = ratio(*tr, thin=True)
        nums = f'<span class="t-inf">{m(tr[0])}</span> / <span class="t-rng">{m(tr[1])}</span> / <span class="t-cav">{m(tr[2])}</span>'
    else:
        bar = ""
        nums = f"{m(s['total'])} total, split not captured"
    note = f"<br><small>{E(s['note'])}</small>" if s["note"] else ""
    return (f"<strong>{E(s['who'])}</strong> <small>{E(s['comp'])}</small><br>"
            f"<small>{E(s['form'])}</small><br>{nums}{bar}{note}")


def battles_table(rows, compact=False):
    out = ['<div class="table-wrap"><table><thead><tr>'
           '<th>#</th><th>Attacker</th><th>Defender</th><th class="num">Losses (att / def)</th><th>Result</th>'
           + ("" if compact else "<th>What decided it</th>") + "</tr></thead><tbody>"]
    for b in rows:
        margin, word, cls = result(b)
        if b["us"]:
            ours = margin if b["us"] == "att" else -margin
            if abs(margin) < 30_000:
                verdict = f'<span class="verdict even">Even</span>'
            elif ours > 0:
                verdict = f'<span class="verdict win">We won</span>'
            else:
                verdict = f'<span class="verdict loss">We lost</span>'
        else:
            verdict = f'<span class="verdict {"even" if word=="Even" else ""}">{word}{" ahead" if word!="Even" else ""}</span>'
        out.append(
            f'<tr data-group="{b["group"]}" data-tags="{" ".join(b["tags"])}" id="log-{b["id"]}">'
            f'<td class="num">{b["id"]}<br><small>{E(b["day"])}</small></td>'
            f'<td>{side_cell(b["att"])}</td><td>{side_cell(b["dfn"])}</td>'
            f'<td class="num">{m(b["al"])} / {m(b["dl"])}<br><small>by {m(abs(margin))}</small></td>'
            f'<td>{verdict}<br><small>{E(b["place"])}</small></td>'
            + ("" if compact else f'<td>{E(b["lesson"])}</td>') + "</tr>")
    out.append("</tbody></table></div>")
    return "\n".join(out)


def bid(old_marker):
    return old_marker  # ids are assigned in order above


# ================================================================ COMPS
# parts on a 20-part rally unless 'fixed' gives absolute troop numbers
COMPS = [
    dict(key="659", digits=("6", "5", "9"), parts=(6, 5, 9), name="659",
         sub="The cav-heaviest standard comp. Wins Range Phalanx mirrors against anything with less cav.",
         form=["<strong>Cav Phalanx</strong> against comps low on ranged " + SRC_SITE,
               "<strong>Range Phalanx</strong> against ranged-heavy comps such as 866 " + SRC_SITE,
               "Defending a 659 hit: sit Cav Phalanx, or Range Phalanx if they run Saberfang or heavy cav gear " + SRC_SHEET],
         beats=["Range Phalanx: 965, 866 " + SRC_SHEET,
                "Cav Phalanx: 947, 956, 857, 749 " + SRC_SHEET,
                "Inf Phalanx: 884, 974, but pull if their lead is stronger " + SRC_SHEET,
                "Any Range Phalanx sitter with clearly less cav than your 1.9M " + logref(3, 13)],
         loses=["992 and 055 " + SRC_SITE,
                "668 in Cav Phalanx " + SRC_SITE + " " + SRC_OPEN,
                "884: sources disagree, see Wonder rules " + src("open", "disputed")],
         heroes="Cavalry-focused heroes and familiars.", shots=[("659 comp.png", "659 heroes and familiars"), ("659 gear.png", "659 gear"), ("659 option gear.png", "Alternative pieces")],
         gear="Gear: Cavalry ATK, Cavalry HP and Army stats. Cups can replace the Faith with the same jewels. Main hand: Champion Blade, Skullcrusher or Champion Edge. Off hand: Champion Light, Dragon Fist, Book of the Dead or Mitts."),
    dict(key="569", digits=("5", "6", "9"), parts=(5, 6, 9), name="569",
         sub="659 cav with more ranged and less infantry. The comp to bring when a Range Phalanx sitter has a lot of cav.",
         form=["<strong>Range Phalanx</strong> into a Range Phalanx sitter " + SRC_OPEN,
               "<strong>Cav Phalanx</strong> if their ranged was just wiped and not refilled " + SRC_OPEN],
         beats=["On paper, any 857 or 758 Range Phalanx sitter: you bring more cav and more ranged, which is the mirror check " + logref(1, 3, 5, 7)],
         loses=["Untested in our logs. Low infantry (about 1.08M) means a garrison built like this is a target for infantry-heavy rallies " + logref(11)],
         heroes="Same as 659, with 2 ranged heroes for Range Phalanx.", shots=[],
         gear="Same gear as 659."),
    dict(key="668", digits=("6", "6", "8"), parts=(6, 6, 8), name="668",
         sub="Balanced attack comp. Range Phalanx by default, with a planned switch against cav-heavy targets.",
         form=["<strong>Range Phalanx</strong> by default " + SRC_SITE + " " + SRC_SHEET,
               "<strong>Cav Phalanx</strong> against 659, 569 and 758 " + SRC_SITE + " " + SRC_OPEN + ". Careful: our only Cav Phalanx defence today lost narrowly when the rally came in Range Phalanx " + logref(2)],
         beats=["Range Phalanx: 884, 965, 776 " + SRC_SITE + " " + SRC_SHEET,
                "Range Phalanx: 857 " + SRC_SITE + " or 875 " + SRC_SHEET + " " + src("open", "disputed"),
                "1262-style infantry piles with low cav: won by 527K " + logref(4)],
         loses=["Range Phalanx: 659, 569, 758 " + SRC_SITE + " " + SRC_SHEET,
                "668 mirror: whoever has more cav " + SRC_SHEET],
         heroes="2 infantry, 2 ranged, 1 cavalry.", shots=[("668 comp.png", "668 heroes and lead march: 208K T5 + 167K T4 infantry"), ("659 gear.png", "Same gear as 659")],
         gear="Same gear as 659. Talents: Infantry 3, Ranged 3 and Cavalry 3 maxed, Army HP 1 and 2 maxed, Infantry 2 maxed, the rest into Ranged 2.",
         warn="Fillers keep turning this into a 758. Logs 1 and 3 landed at about 7.5-5-7.5. Check the rally screen reads about 30% / 30% / 40% before you launch."),
    dict(key="866", digits=("8", "6", "6"), parts=(8, 6, 6), name="866",
         sub="Infantry-heavy Range Phalanx comp for targets with low cav.",
         form=["<strong>Range Phalanx</strong> only, with the lead sending a full infantry march " + SRC_SITE + " " + SRC_SHEET],
         beats=["974, 884, 712 " + SRC_SITE + " " + SRC_SHEET, "992 " + SRC_SITE, "965: sources disagree " + src("open", "disputed")],
         loses=["659, 569, 758, 857, 208, 055 " + SRC_SITE, "668 " + SRC_SHEET],
         heroes="Infantry-focused heroes. Use 2 ranged heroes for Range Phalanx (the old page said 1–2).", shots=[("866 comp.png", "866 heroes and lead march"), ("866 gear.png", "866 gear"), ("866 option gear.png", "Alternative pieces")],
         gear="Gear: Infantry ATK and HP with some Ranged ATK."),
    dict(key="055", digits=("0", "5", "5"), fixed=(45_000, 2_400_000, 1_870_000), name="055",
         sub="Almost no infantry, a ranged stack and a cav stack. The cav soaks damage, the ranged does the killing.",
         form=["<strong>Infantry Wedge</strong> when attacking " + SRC_SITE + " " + logref(8, 10, 12, 14, 15),
               "Works as a garrison too: it beat an 875 " + logref(9)],
         beats=["When you're the stronger lead: 857, 758, 947, 659, 866, 668, 956, 848 " + SRC_SHEET + " " + logref(10),
                "At equal stats: 659 (harder), 749, 857, 956, 848, 947 " + SRC_SHEET,
                "875 hitting your 055 garrison " + logref(9)],
         loses=["758 or 857 in Range Phalanx when you're not stronger " + logref(12, 15),
                "Targets with about 1.76M ranged and under 1M cav: expect an even trade, not a win " + logref(8, 14)],
         heroes="Ranged and cavalry heroes, at most one infantry hero.", shots=[("055 comp.png", "055 heroes; lead sends the only infantry"), ("055 gear.png", "055 gear"), ("055 option gear.png", "Alternative pieces")],
         gear="Gear: Ranged and Cavalry stats equally.",
         warn="Only the lead sends infantry: 40–50K. Top accounts used 40K and 50K in every logged 055. Nobody else sends infantry.",
         counts_note="Typical landed split from the logs; ranged runs slightly above cav."),
    dict(key="208", digits=("2", "0", "8"), fixed=(1_029_200, 120_000, 3_163_800), name="208",
         sub="Cav strike with a controlled infantry buffer. Only for targets low on ranged.",
         form=["<strong>Range Wedge</strong>, carpeted fast " + SRC_SITE + " " + SRC_SHEET,
               "Experts only: show Ranged Phalanx uncarpeted to bait an experienced lead into Range Wedge. If they answer with Cav Phalanx you get wrecked " + SRC_SITE],
         beats=["965, 866, 956, 947, 857, 875, 767 " + SRC_SHEET,
                "Targets under 1.1M ranged in Infantry or Range Phalanx " + SRC_SITE],
         loses=["Anything over 1.1M ranged: switch to a 307 (more infantry, ranged stays 120K) " + SRC_SHEET,
                "Cav-heavy comps in Cav Phalanx when you've added infantry " + SRC_SITE],
         heroes="Use Gryphon if you don't have Jade Wyrm " + SRC_SHEET + ".", shots=[("208 comp.jpg", "208 heroes; lead sends 120K ranged + T5 infantry"), ("208 gear.png", "208 gear"), ("208  Champ gear.jpg", "Champion gear"), ("208 option gear.png", "Alternative pieces")],
         gear="The lead sends exactly 120K ranged and fills with T5 infantry. Everyone else sends cav. Never add ranged, only infantry.",
         counts_note="Lead sends the 120K ranged. Infantry is the only number you adjust."),
    dict(key="1433", digits=("14", "3", "3"), parts=(14, 3, 3), name="1433",
         sub="Infantry wall for targets with under 1M cav, such as 442-type comps.",
         form=["<strong>Infantry Phalanx</strong> " + SRC_SITE],
         beats=["Anything with under 1M cav, regardless of gear " + SRC_SITE,
                "442 and 974 " + SRC_SITE + "; 992 by the same logic " + SRC_OPEN],
         loses=["Anything with over 1M cav " + SRC_SITE,
                "As a garrison it's a target: a cav-heavy rally eats it. Don't sit in it"],
         heroes="4–5 infantry heroes. At most one ranged hero.", shots=[("1433 comp.png", "Check this screenshot: it shows the lead sending 0 infantry, which doesn't fit a 1433"), ("1433 gear.png", "1433 gear")],
         gear="Gear: Infantry ATK, Infantry HP and Army ATK. No carpet needed if the counts are right."),
    dict(key="992", digits=("9", "9", "2"), parts=(9, 9, 2), name="992 (enemy profile)",
         sub="What you'll see on Emperor and Baron wonders. Built to beat 424-type comps in Range Phalanx, almost always carpeted.",
         form=["They sit <strong>Range Phalanx</strong> " + SRC_SITE],
         beats=["Answer with a 1433 in Infantry Phalanx: infantry beats their ranged front and they have almost no cav to punish it " + SRC_SITE + " " + SRC_OPEN,
                "Or an 866 in Range Phalanx " + SRC_SITE],
         loses=["Don't send a 659 " + SRC_SITE,
                "Don't send a 055 or 208: their ranged is far above both limits",
                "The old site says 668 in Cav Phalanx; our Cav-into-Range results are mixed " + logref(2, 17, 20)],
         heroes="They usually run 1 infantry, 2 ranged, 2 cavalry heroes with Jade Wyrm, Blackwing and Queen Bee " + SRC_SITE + ".", shots=[], gear=""),
]


def comp_counts(cmp):
    if "fixed" in cmp:
        i, r, c = cmp["fixed"]
        return (f'<div class="counts" data-fixed>'
                f'<div><small class="t-inf">Infantry</small><b>{m(i)}</b></div>'
                f'<div><small class="t-rng">Ranged</small><b>{m(r)}</b></div>'
                f'<div><small class="t-cav">Cavalry</small><b>{m(c)}</b></div></div>'
                + (f'<p class="muted">{E(cmp.get("counts_note",""))}</p>' if cmp.get("counts_note") else ""))
    i, r, c = cmp["parts"]
    cells = []
    for lab, cls, p in (("Infantry", "t-inf", i), ("Ranged", "t-rng", r), ("Cavalry", "t-cav", c)):
        cells.append(f'<div><small class="{cls}">{lab}, {p} parts</small><b data-parts="{p}">{m(round(RALLY*p/20))}</b></div>')
    return f'<div class="counts">{"".join(cells)}</div>'


def comp_block(cmp):
    tr = cmp.get("fixed") or cmp["parts"]
    li = lambda xs: "<ul>" + "".join(f"<li>{x}</li>" for x in xs) + "</ul>"
    shots = ""
    if cmp["shots"]:
        shots = '<div class="shots">' + "".join(
            f'<figure><img src="{img(p)}" alt="{E(cap)}" loading="lazy"><figcaption>{E(cap)}</figcaption></figure>'
            for p, cap in cmp["shots"]) + "</div>"
    warn = f'<div class="note warn"><p>{cmp["warn"]}</p></div>' if cmp.get("warn") else ""
    gear = f"<p>{cmp['gear']}</p>" if cmp.get("gear") else ""
    return f"""<section class="comp" id="c{cmp['key']}">
<div class="comp-head"><h2>{code(cmp['digits'], 'mid')}<span class="sr">{E(cmp['name'])}</span></h2>{('<p class="tag">' + E(cmp['name'].split('(')[1].rstrip(')')) + '</p>') if '(' in cmp['name'] else ''}<p>{E(cmp['sub'])}</p>{ratio(*tr)}</div>
{comp_counts(cmp)}
{warn}
<div class="cols">
<div><h4>Formation</h4>{li(cmp['form'])}</div>
<div><h4 class="win">Beats</h4>{li(cmp['beats'])}</div>
<div><h4 class="loss">Loses to</h4>{li(cmp['loses'])}</div>
</div>
<p><strong>Heroes:</strong> {cmp['heroes']}</p>
{gear}
{shots}
</section>"""


def page_comps():
    toc = "".join(f'<li><a href="#c{c["key"]}">{E(c["key"])}</a></li>' for c in COMPS)
    body = f"""<div class="page-head">
<h1>Comps</h1>
<p class="lede">Troop counts are worked out from the comp's parts for your rally size. Beats and loses lists show where each claim comes from: your sheet, the old site, the battle log or the game files.</p>
</div>
<div class="rally-size">
<label for="rally">Rally size</label>
<input id="rally" type="text" inputmode="numeric" value="4,313,000" style="max-width:12rem" aria-describedby="rally-help">
<small id="rally-help">One part = rally ÷ 20. 055 and 208 use fixed lead numbers.</small>
</div>
<ul class="legend"><li class="li">Infantry</li><li class="lr">Ranged</li><li class="lc">Cavalry</li></ul>
<ul class="section-nav" aria-label="Comps on this page">{toc}</ul>
{''.join(comp_block(c) for c in COMPS)}
"""
    return shell("CompGears.html", "Comps", "Wonder rally comps for Lords Mobile with troop counts, formations and real results.", body, scripts=True)


# ================================================================ FORMATIONS
with open(os.path.join(ROOT, "tools", "formations.json")) as f:
    FORMS = json.load(f)

FORM_TEXT = {
    "Infantry Phalanx": "4 infantry squads in one wide front line. Cav sits on the outer flanks behind them, ranged at the back.",
    "Ranged Phalanx": "4 ranged squads in front. Infantry on the flanks just behind, cav at the back.",
    "Cavalry Phalanx": "4 cav squads in front. Ranged on the flanks behind, infantry at the back.",
    "Infantry Wedge": "Infantry stacked 2-deep in the centre, so narrower than Inf Phalanx. Ranged on the flanks, cav at the back.",
    "Ranged Wedge": "Ranged stacked 2-deep in the centre. Cav on the wide flanks, infantry at the back.",
    "Cavalry Wedge": "Cav stacked 2-deep in the centre. Infantry on the wide flanks, ranged at the back.",
}
COL = {"inf": "#93a9c4", "rng": "#5fbba9", "cav": "#e2a94b", "siege": "#6f7a74"}


def form_svg(name, squads):
    # field depth x: 0 (rear) .. 3100 (front); width y: 600..2800
    W, H = 340, 230
    sx = lambda x: 20 + x / 3200 * (W - 60)
    sy = lambda y: 15 + (y - 500) / 2500 * (H - 30)
    parts = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{E(name)} squad layout">',
             f'<line x1="{W-22}" y1="10" x2="{W-22}" y2="{H-10}" stroke="#3a4a43" stroke-dasharray="4 4"/>',
             f'<text x="{W-16}" y="{H/2}" fill="#a3afa6" font-size="11" transform="rotate(90 {W-16} {H/2})" text-anchor="middle">enemy side</text>']
    for s in squads:
        x, y = sx(s["x"]), sy(s["y"])
        parts.append(f'<rect x="{x-11:.1f}" y="{y-15:.1f}" width="22" height="30" rx="2" fill="{COL[s["t"]]}"/>')
    parts.append("</svg>")
    return "".join(parts)


def page_formations():
    cards = "".join(
        f'<div class="form" id="{n.split()[0].lower()}-{n.split()[1].lower()}"><h3>{E(n)}</h3>{form_svg(n, sq)}<p>{E(FORM_TEXT[n])}</p></div>'
        for n, sq in FORMS.items())
    body = f"""<div class="page-head">
<h1>Formations</h1>
<p class="lede">Where your squads actually stand, drawn from the game's own formation table. Every army fights as 16 squads: 4 infantry, 4 ranged, 4 cavalry and 4 siege.</p>
</div>
<ul class="legend"><li class="li">Infantry</li><li class="lr">Ranged</li><li class="lc">Cavalry</li><li style="--x:0"><span style="display:inline-block;width:.7em;height:.7em;background:#6f7a74;margin-right:.4em"></span>Siege</li></ul>
<div class="forms">{cards}</div>

<h2>The counter triangle</h2>
<p>The game's own skill names spell it out: <em>Infantry-Ranged Counter Boost</em>, <em>Ranged-Cavalry Counter Boost</em>, <em>Cavalry-Infantry Counter Boost</em>. {SRC_GAME}</p>
<div class="table-wrap"><table>
<thead><tr><th>Their front / biggest stack</th><th>Put in front</th><th>Phalanx to use</th></tr></thead>
<tbody>
<tr><td class="t-inf">Infantry</td><td class="t-cav">Cavalry</td><td>Cavalry Phalanx</td></tr>
<tr><td class="t-rng">Ranged</td><td class="t-inf">Infantry</td><td>Infantry Phalanx</td></tr>
<tr><td class="t-cav">Cavalry</td><td class="t-rng">Ranged</td><td>Ranged Phalanx</td></tr>
</tbody></table></div>
<p>There's no special Wonder mode. Wonder battles run on the same simulator as every other fight; Wonders only add stat bonuses for holding them and for titles. {SRC_GAME}</p>
<div class="note open"><p><strong>In Wonders the comp often matters more than the formation name.</strong> A 055 sits in "Infantry Wedge" with only 40–50K infantry, so its real front is ranged on the flanks with cav behind. Read the troop numbers, not the formation label.</p></div>

<h2>What the logs say about switching</h2>
<ul>
<li><strong>Cav Phalanx into a Range Phalanx</strong> costs most of your cav, but it isn't an automatic loss: it won twice in old reports and lost narrowly today. {logref(17, 20, 2)}</li>
<li><strong>Switch late.</strong> If they scout you sitting in Cav Phalanx, a smart lead comes in Range Phalanx.</li>
<li><strong>Only call off the final rally numbers.</strong> A scout of a half-filled rally got us the wrong call. {logref(2)}</li>
</ul>

<h2>Common mistakes</h2>
<ul>
<li>Running Cav Phalanx without enough infantry behind it, into an Infantry Phalanx.</li>
<li>Not switching after being scouted.</li>
<li>Reading the formation name instead of the troop numbers.</li>
<li>Only one ranged hero in Range Phalanx. This is a community rule we haven't tested: one ranged hero is said to push your middle ranged squad forward so it gets picked off. {SRC_OPEN}</li>
<li>Leaving formations unbound in your hotkeys. Range Wedge is the one people forget, and the 208 needs it.</li>
</ul>
"""
    return shell("formations.html", "Formations", "Real squad layouts for all six Lords Mobile formations and how they counter each other.", body)


# ================================================================ WONDER RULES
def mirror_rows():
    rows = []
    # (log id, our cav, their cav, our rng, their rng, margin for us)
    data = [(4, None, None, None, None, 527_000)]
    picks = [1, 3, 5, 6, 7, 13]
    for b in BATTLES:
        if b["id"] not in picks:
            continue
        a, d = b["att"]["tr"], b["dfn"]["tr"]
        margin, *_ = result(b)
        if b["us"] == "def":
            us, them, mm = d, a, -margin
        else:
            us, them, mm = a, d, margin
        rows.append((b["id"], us[2] - them[2], us[1] - them[1], mm, b["us"] is None))
    out = ['<div class="table-wrap"><table><thead><tr><th>Log</th><th class="num">Cav gap</th><th class="num">Ranged gap</th><th class="num">Result</th></tr></thead><tbody>']
    for i, cg, rg, mm, shared in rows:
        who = " (attacker's view)" if shared else ""
        res = f'<span class="{"win" if mm>0 else "loss"}">{"+" if mm>0 else "−"}{m(abs(mm))}</span>'
        out.append(f'<tr><td><a href="battle-reports.html#log-{i}">{i}</a>{who}</td>'
                   f'<td class="num t-cav">{"+" if cg>=0 else "−"}{m(abs(cg))}</td>'
                   f'<td class="num t-rng">{"+" if rg>=0 else "−"}{m(abs(rg))}</td><td class="num">{res}</td></tr>')
    out.append("</tbody></table></div>")
    return "".join(out)


def page_advanced():
    body = f"""<div class="page-head">
<h1>Wonder rules</h1>
<p class="lede">What 20 logged Wonder fights actually showed. Each rule links to the fights behind it. Where the old site and your sheet disagree and no fight has settled it, it's listed as open.</p>
</div>
<ul class="section-nav">
<li><a href="#mirror">Range Phalanx mirrors</a></li><li><a href="#garrison">Garrison minimums</a></li><li><a href="#c055">055</a></li>
<li><a href="#drift">Comp drift</a></li><li><a href="#stats">Stats</a></li><li><a href="#open">Open questions</a></li><li><a href="#community">Community theory</a></li>
</ul>

<h2 id="mirror">Range Phalanx mirrors: cav decides</h2>
<p>When both sides sit Range Phalanx, both ranged fronts die first. What's left is cav against whatever the other side has behind. In the logs, the side with more cav won every time unless the other side brought a much bigger ranged stack.</p>
<div class="note proven"><p><strong>Rule of thumb:</strong> work out your cav gap and your ranged gap against them. Cav counts about twice as much as ranged. If cav gap + half the ranged gap is negative, don't hit. This weighting is a rough fit to the six fights below, not a formula from the game.</p></div>
{mirror_rows()}
<ul>
<li>Extra <strong>infantry</strong> doesn't help a mirror. In log 3 we had 250K more infantry and lost, because their cav ate it.</li>
<li>A big <strong>ranged</strong> surplus shrinks the margin: in log 6 about 560K of their ranged survived and kept shooting our cav. {logref(5, 6)}</li>
<li>After every mirror your ranged is gone. Refill it before the next hit lands.</li>
</ul>

<h2 id="garrison">Garrison minimums</h2>
<div class="note warn"><p><strong>Never sit with no infantry.</strong> In log 11 we had more cav and more ranged than the attacker and lost by 1.46M, because his infantry hit our ranged with nothing in the way. {logref(11)}</p></div>
<div class="table-wrap"><table><thead><tr><th>Troop</th><th class="num">Hold at least</th><th>Why</th></tr></thead><tbody>
<tr><td class="t-inf">Infantry</td><td class="num">1.4M</td><td>Shields your ranged from infantry rallies.</td></tr>
<tr><td class="t-rng">Ranged</td><td class="num">1.1M</td><td>Your front in Range Phalanx. Without it, any cav-heavy rally or 055 walks in.</td></tr>
<tr><td class="t-cav">Cavalry</td><td class="num">1.6M (1.75M+ better)</td><td>Wins the mirrors. Each mirror chips 200–400K off it.</td></tr>
<tr><td>Total</td><td class="num">Full cap</td><td>Log 11 was 460K short.</td></tr>
</tbody></table></div>
<p>A 1433 is an attack comp. Don't sit in it: a cav-heavy rally eats it.</p>

<h2 id="c055">The 055, in numbers</h2>
<ul>
<li><strong>Infantry:</strong> the lead sends 40–50K and nobody else sends any. Every logged 055 used 40K or 50K.</li>
<li><strong>Ranged limit:</strong> the old "avoid over 1.1M ranged" is too strict. Into about 1.76M ranged with under 1M cav it traded even twice. {logref(8, 14)}</li>
<li><strong>Into 758/857 Range Phalanx:</strong> stats decide. Not stronger: defender wins {logref(12, 15)}. Clearly stronger: won by 1.1M {logref(10)}.</li>
<li><strong>As a garrison:</strong> beat an 875 from a stronger account. {logref(9)}</li>
<li>The old "2 infantry heroes" rule contradicted itself (one page said it helps you, another said avoid). Dropped until someone tests it.</li>
</ul>

<h2 id="drift">Comp drift and bad calls</h2>
<ul>
<li><strong>Fillers drift toward infantry.</strong> Rallies sent as 668 landed as 7.5-5-7.5 twice. Check the rally screen percentages before you launch. {logref(1, 3)}</li>
<li><strong>Call off final numbers only.</strong> Scouting a rally that's still filling gave the wrong formation. {logref(2)}</li>
<li><strong>Pull when outmatched.</strong> If the target has more cav than you in a mirror, skip it or let another rally soften it first.</li>
</ul>

<h2 id="stats">Stats</h2>
<p>Most of today's fights were between accounts with similar gear, so formation and comp decided them. A clearly stronger lead flips close matchups: the same 055-into-758 matchup lost twice and then won by 1.1M with the strongest lead. {logref(10, 12, 15)}</p>

<h2 id="open">Open questions</h2>
<p>Your sheet and the old site disagree on these, and no logged fight settles them yet. Screenshot the full report next time you see one.</p>
<div class="table-wrap"><table><thead><tr><th>Question</th><th>Sheet says</th><th>Old site says</th></tr></thead><tbody>
<tr><td>866 vs 965</td><td>866 loses</td><td>866 wins</td></tr>
<tr><td>668 in Range Phalanx beats</td><td>875</td><td>857</td></tr>
<tr><td>659 vs 884</td><td>659 in Inf Phalanx wins (pull if their lead is stronger)</td><td>Never send a 659 at an 884</td></tr>
<tr><td>Ranged heroes for 866</td><td>—</td><td>1–2, while the same site says Range Phalanx needs exactly 2</td></tr>
<tr><td>668 Cav Phalanx vs 659/569/758</td><td>Only lists the Range Phalanx losses</td><td>Cav Phalanx wins</td></tr>
</tbody></table></div>

<h2 id="community">Community theory we haven't tested</h2>
<p>These come from the old site. They might be right. None of today's reports confirm or rule them out.</p>
<ul>
<li><strong>Two ranged heroes in Range Phalanx.</strong> With one, your middle ranged squad sits forward and gets picked off; with zero or three it's said to be worse.</li>
<li><strong>Hero reach.</strong> A hero's tactical skill reaches slightly further than a plain squad attack, so squads with heroes hold back a step.</li>
<li><strong>442 vs 424 Range Phalanx.</strong> If the 424's ranged dies before half the 442's ranged, the 442 wins; if the 424's ranged is tanky, the 424 wins by a lot. 974, 992, 794 and 983 are 442 variants built around this.</li>
<li><strong>Attack vs HP.</strong> HP cuts your losses, attack raises kills. More attack can sometimes make a matchup worse, because it changes when familiars fire.</li>
</ul>
"""
    return shell("advanced.html", "Wonder rules", "Rules for Lords Mobile Wonder battles, backed by logged battle reports.", body)


# ================================================================ BATTLE LOG PAGE
def page_battles():
    body = f"""<div class="page-head">
<h1>Battle log</h1>
<p class="lede">Every Wonder fight with numbers we could read. "Losses" are wounded on each side; Wonder fights have no deaths. A fight within 30K either way is called even.</p>
</div>
<div class="filters" role="group" aria-label="Show fights">
<button type="button" data-filter="all" aria-pressed="true">All 20</button>
<button type="button" data-filter="guild" aria-pressed="false">Our guild, 19 Nov</button>
<button type="button" data-filter="shared" aria-pressed="false">Top accounts, 16–18 Nov</button>
<button type="button" data-filter="old" aria-pressed="false">Old site reports</button>
<button type="button" data-filter="mirror" aria-pressed="false">Range Phalanx mirrors</button>
<button type="button" data-filter="055" aria-pressed="false">055 fights</button>
</div>
<ul class="legend"><li class="li">Infantry</li><li class="lr">Ranged</li><li class="lc">Cavalry</li></ul>
{battles_table(BATTLES)}
<p class="muted">The old site's write-ups of logs 17–20 blamed hero setups and familiars without evidence. Those explanations are gone; the numbers are kept.</p>
"""
    return shell("battle-reports.html", "Battle log", "Logged Lords Mobile Wonder battle reports with troop splits and what decided each fight.", body, scripts=True)


# ================================================================ HEROES
FAMS = [
    ("Jade Wyrm", "5", "Cuts damage enemies deal by 9%", "4% of your troops fallen", "Any comp"),
    ("Blackwing", "5", "600% of your initial ranged ATK to one of the largest enemy squads", "4%", "Ranged front"),
    ("Gargantua", "5", "600% of your initial cav ATK to one of the largest enemy squads", "4%", "Cav comps"),
    ("Bon Appeti", "5", "600% of your initial infantry ATK to one of the largest enemy squads", "4%", "Infantry comps"),
    ("Queen Bee", "5", "150% of ranged ATK every few seconds, up to 5 times", "8%", "Range Phalanx"),
    ("Frostwing", "5", "150% of cav ATK every few seconds, up to 5 times", "8%", "Cav fronts"),
    ("Huey Hops", "5", "150% of infantry ATK every few seconds, up to 5 times", "8%", "Infantry damage"),
    ("Hell Drider", "4", "Petrifies one of the largest enemy squads for 11 seconds", "7%", "Any comp"),
    ("Mega Maggot", "4", "Stuns all enemy heroes for 5 seconds", "15%", "—"),
    ("Saberfang", "4", "Shield saves 7% of your cav from a killing blow", "12% of your cav fallen", "Cav that has to soak"),
    ("Snow Beast", "4", "Shield saves 7% of your ranged from a killing blow", "12% of your ranged fallen", "Range Phalanx"),
    ("Hoarder", "4", "Shield saves 7% of your infantry from a killing blow", "12% of your infantry fallen", "Infantry fronts"),
]


def page_heroes():
    fam_rows = "".join(
        f"<tr><td><strong>{E(n)}</strong></td><td class='num'>{p}</td><td>{E(e)}</td><td>{E(t)}</td><td>{E(b)}</td></tr>"
        for n, p, e, t, b in FAMS)
    body = f"""<div class="page-head">
<h1>Heroes &amp; familiars</h1>
<p class="lede">Familiar battle effects are checked against the game's own text. The hero list is a community ranking and may be behind the current meta.</p>
</div>

<h2>Familiar battle talents</h2>
<p>These fire during the fight once enough of your troops have fallen. Effect wording and thresholds come from the game's strings and the Lords Mobile Pro rankings. {SRC_GAME}</p>
<div class="table-wrap"><table>
<thead><tr><th>Familiar</th><th class="num">Pact</th><th>Effect</th><th>Fires when</th><th>Best in</th></tr></thead>
<tbody>{fam_rows}</tbody></table></div>
<div class="note"><p><strong>Corrected from the old site:</strong> Hell Drider and Snow Beast are Pact 4, not Pact 3, and their battle effects are a petrify and a ranged shield, not gathering or Wonder DEF. Each shield familiar triggers on its own troop type falling, not on cavalry.</p></div>

<h3>Familiars by formation</h3>
<ul>
<li><strong>Range Phalanx:</strong> Snow Beast, Blackwing or Queen Bee, Jade Wyrm, Hell Drider</li>
<li><strong>Cav Phalanx:</strong> Gargantua, Frostwing, Saberfang, Jade Wyrm, Hell Drider</li>
<li><strong>Inf Phalanx:</strong> Bon Appeti, Huey Hops, Hoarder, Jade Wyrm, Hell Drider</li>
</ul>
<p>Watch enemy Jade Wyrms: in an even fight, a 9% damage cut can decide it. Run your own to cancel it.</p>

<h2>Heroes</h2>
<p>Community ranking from the old site. Use the hero type that matches the troops you want to protect: it changes how those squads stand.</p>
<div class="table-wrap"><table>
<thead><tr><th class="t-inf">Infantry</th><th class="t-rng">Ranged</th><th class="t-cav">Cavalry</th></tr></thead>
<tbody>
<tr><td>Twilight Priestess</td><td>Petite Devil</td><td>Barbarian</td></tr>
<tr><td>Grim Wolf</td><td>Grove Guardian</td><td>Storm Fox</td></tr>
<tr><td>The Big Guy</td><td>Snow Queen</td><td>Child of Light</td></tr>
<tr><td>Oath Keeper</td><td>Black Crow</td><td>Vengeful Centaur</td></tr>
<tr><td></td><td></td><td>Lore Weaver (strong army stats)</td></tr>
</tbody></table></div>
<p><strong>Free-to-play picks:</strong> Rose Knight (army ATK), Trickster (research), Prima Donna (healing), Demon Slayer (infantry in war), Tracker (single-hit damage).</p>
<h3>Hero setups by formation</h3>
<ul>
<li><strong>Range Phalanx:</strong> 2 ranged heroes. 1 infantry, 2 ranged, 2 cavalry is the old site's pick.</li>
<li><strong>Inf Phalanx:</strong> 2 infantry, 2 ranged, 1 cavalry; for a 1433, 4–5 infantry heroes.</li>
<li><strong>055:</strong> ranged and cavalry heroes, at most one infantry.</li>
</ul>

<h2>Utility familiars</h2>
<p class="muted">Listed by the old site; not checked against the game.</p>
<ul>
<li>Goblin (Pact 3): gold every 24 hours</li>
<li>Gemming Gremlin (Pact 3): gems every 2 days</li>
<li>Hoarder (Pact 4): random jewels every 3 days</li>
<li>Mecha Trojan (Pact 4): extra rally capacity</li>
<li>Grim Reaper (Pact 4): kills high-tier troops in an enemy's barracks</li>
<li>Aquiris (Pact 1): stamina every 12 hours</li>
<li>Territe (Pact 1): faster merging</li>
</ul>
"""
    return shell("heroes.html", "Heroes & familiars", "Lords Mobile familiar battle talents checked against game data, plus hero picks for Wonder war.", body)


# ================================================================ HOME
def page_home():
    rules = [
        ("Read numbers, not names", "A 055 sits in \"Infantry Wedge\" with 40K infantry. The biggest stack tells you what's really in front."),
        ("Counter their biggest stack", "Their infantry: your cav in front. Their ranged: your infantry in front. Their cav: your ranged in front."),
        ("Mirrors go to cav", "Range Phalanx vs Range Phalanx: more cav wins. Cav counts about twice as much as ranged."),
        ("Never sit with no infantry", "Hold 1.4M+ infantry, 1.1M+ ranged, 1.6M+ cav, full cap."),
        ("Call off final numbers", "Half-filled rallies change. Switch late, after the last scout."),
        ("Check the rally screen", "Fillers drift toward infantry. Your 668 is useless if it lands as a 758."),
    ]
    rl = "".join(f"<li><b>{E(a)}</b><p>{E(b)}</p></li>" for a, b in rules)
    body = f"""<section class="home-hero">
<h1>Read a scout, pick the formation.</h1>
<p class="lede">Type the troop totals from a scout or a rally screen. You get the comp, what to sit in if they hit you, and what to send if you hit them.</p>
</section>

<form class="scout" id="scout" autocomplete="off" onsubmit="return false">
<fieldset class="a-their">
<legend>Their troops</legend>
<div class="trio">
<div><label class="li" for="ti">Infantry</label><input id="ti" type="text" autocapitalize="off" spellcheck="false" placeholder="1.55m"></div>
<div><label class="lr" for="tr">Ranged</label><input id="tr" type="text" autocapitalize="off" spellcheck="false" placeholder="1.03m"></div>
<div><label class="lc" for="tc">Cavalry</label><input id="tc" type="text" autocapitalize="off" spellcheck="false" placeholder="1.73m"></div>
</div>
<p class="hint">Holder's march plus all allied troops. 50k, 1.3m and 1,300,000 all work. Fill two and the third is worked out from the rally cap.</p>
<div class="row go"><button type="button" id="go">Get the call</button><button type="button" id="clear" class="quiet">Clear</button>
<label for="cap" class="cap-l">Rally cap</label><input id="cap" type="text" value="4,313,000" autocapitalize="off" spellcheck="false"></div>
</fieldset>
<div class="readout a-read" id="readout" aria-live="polite" data-empty tabindex="-1">Enter at least two of their troop totals, then press Get the call.</div>
<fieldset class="a-yours">
<legend>Your troops (optional)</legend>
<div class="trio">
<div><label class="li" for="yi">Infantry</label><input id="yi" type="text" autocapitalize="off" spellcheck="false"></div>
<div><label class="lr" for="yr">Ranged</label><input id="yr" type="text" autocapitalize="off" spellcheck="false"></div>
<div><label class="lc" for="yc">Cavalry</label><input id="yc" type="text" autocapitalize="off" spellcheck="false"></div>
</div>
<p class="hint">Leave empty to get a comp to send. Fill them in to check a mirror and your holding minimums.</p>
</fieldset>
</form>

<h2>Six rules from 20 logged fights</h2>
<ul class="rules">{rl}</ul>
<p>The evidence for each rule is on <a href="advanced.html">Wonder rules</a>, and every fight is in the <a href="battle-reports.html">battle log</a>. Troop counts for each comp are on <a href="CompGears.html">Comps</a>.</p>
"""
    return shell("index.html", "Scout reader", "Lords Mobile Wonder guide: read a scout and pick a formation, backed by real battle reports.", body, scripts=True)


if __name__ == "__main__":
    write("index.html", page_home())
    write("CompGears.html", page_comps())
    write("formations.html", page_formations())
    write("advanced.html", page_advanced())
    write("battle-reports.html", page_battles())
    write("heroes.html", page_heroes())
