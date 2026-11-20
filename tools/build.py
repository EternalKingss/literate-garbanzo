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
    ("mechanics.html", "How fights work"),
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


def cb(vid, label="Crystal Briefs"):
    """Source tag linking to a Crystal Briefs video."""
    return f'<a class="src cb" href="https://www.youtube.com/watch?v={vid}" rel="noopener">{E(label)}</a>'


CB = dict(squads1="baXOyJ5J1yg", squads2="KDgKvfhta8g", heroes="6qXQtCi50VQ", basics="L0lk8kXS4jU",
          m424="DdEZd-BA4eE", m442="4Qn40m1g1vI", v442="E5ByrFJdlDc", rh="eiIlrkQI5dE", c055="7laMlO9ImEI",
          f055="70gKYpF4i3o", c208="9QsWC_LePco", c992="Icx51Z6L2Jc", hd="UYJfqiKXq6c", hdc="VLg3enn8ZgM",
          jade="jALYNGy6Yeo", atkhp="G84m4gLVpcY", s424="6LahRcocTl8", s442="iNBCSdD-eOU", cw="LS48XirT2sc",
          c244="vJ6XTlx8vPI", da1="sRUuHCz_xww", da2="-V_0ZFyUa5Y", morale="6MBD_WPPSFA", hero5="y5o_pyVrBHA",
          research="vkIguIWmVys")


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
         dfn=S("T69 garrison", "857", (1_632_872, 1_131_000, 1_508_000), "Ranged Phalanx"),
         al=1_401_599, dl=1_239_099, us="def", tags=["055"],
         lesson="055 lost 64% of its cav to the Range Phalanx front."),
    dict(id=13, day="18 Nov", group="shared", place="Chaos Citadel",
         att=S("HeyChars", "884", (1_696_501, 1_696_499, 919_996), "Ranged Phalanx"),
         dfn=S("T69 garrison", "866ish", (1_575_625, 1_168_500, 1_363_250), "Ranged Phalanx"),
         al=1_632_281, dl=1_571_127, us="def", tags=["mirror"],
         lesson="Defender lost all its ranged first and still came out ahead: it had 440K more cav."),
    dict(id=14, day="16 Nov", group="shared", place="Relay Bunker 3",
         att=S("T69 rally", "055", (50_007, 2_418_135, 1_969_858), "Infantry Wedge"),
         dfn=S("OmaiGon", "785", (1_443_362, 1_765_501, 984_131), "Ranged Phalanx"),
         al=1_555_160, dl=1_571_834, us="att", tags=["055"],
         lesson="055 into 1.77M ranged: even. The old 1.1M ranged limit is too strict."),
    dict(id=15, day="17 Nov", group="shared", place="Chaos Citadel",
         att=S("Wolf BaziL", "055", (40_000, 2_389_187, 1_883_813), "Infantry Wedge"),
         dfn=S("T69 garrison", "758", (1_496_504, 1_178_886, 1_612_529), "Ranged Phalanx"),
         al=1_398_981, dl=1_200_003, us="def", tags=["055"],
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
    # ---- our fights, 19 Nov evening batch (formations read from who took the losses)
    dict(id=21, day="19 Nov", group="guild", place="Our fight",
         att=S("T69 rally", "5-5-10", (1_114_450, 1_132_900, 2_065_650), "Ranged Phalanx?"),
         dfn=S("Opponent", "857", (1_653_631, 940_723, 1_519_316), "Ranged Phalanx?"),
         al=1_381_557, dl=1_154_382, us="att", tags=["mirror"],
         lesson="Both ranged fronts died. Attacker had 546K more cav and more ranged and still lost by 228K. The cav check called this wrong."),
    dict(id=22, day="19 Nov", group="guild", place="Our fight",
         att=S("Opponent", "857", (1_692_699, 1_181_299, 1_544_999), "Ranged Phalanx?"),
         dfn=S("T69 garrison", "857", (1_656_000, 1_132_000, 1_506_000), "Ranged Phalanx?"),
         al=1_470_617, dl=1_387_836, us="def", tags=["mirror"],
         lesson="True mirror, under 50K apart on every troop type. Defender ahead by 83K: at even counts, stats decide."),
    dict(id=23, day="19 Nov", group="guild", place="Our fight",
         att=S("Opponent", "758", (1_461_748, 1_131_100, 1_696_149), "Ranged Phalanx?"),
         dfn=S("T69 garrison", "758", (1_642_200, 1_143_800, 1_507_999), "Cavalry Phalanx (from losses)"),
         al=1_498_328, dl=1_432_089, us="def", tags=["cav-into-range"],
         lesson="Defender's ranged took zero losses and its cav took 1.23M, so it sat cav in front. Killed 1.06M of the rally's ranged and held by 66K with less cav."),
    dict(id=24, day="19 Nov", group="guild", place="Our fight",
         att=S("Opponent", "866", (1_704_036, 1_319_409, 1_289_554), "Ranged Phalanx?"),
         dfn=S("T69 garrison", "946", (1_998_195, 967_428, 1_347_368), "Ranged Phalanx?"),
         al=1_914_068, dl=1_355_103, us="def", tags=["mirror"],
         lesson="Defender had 350K less ranged and 300K more infantry. Both ranged died, then the rally's infantry got eaten (595K lost). Defender ahead by 559K."),
    dict(id=25, day="19 Nov", group="guild", place="Our fight",
         att=S("T69 rally", "5-10-4", (1_167_000, 2_203_000, 943_000), "Ranged Phalanx (from losses)"),
         dfn=S("Opponent", "6-5-9", (1_288_001, 1_131_501, 2_073_682), "Cavalry Phalanx (from losses)"),
         al=1_756_276, dl=1_854_071, us="att", tags=["cav-into-range"],
         lesson="2.2M ranged into a Cav Phalanx. Defender's ranged and infantry barely touched, its cav lost 1.69M. Attacker ahead by 98K."),
    dict(id=26, day="19 Nov", group="guild", place="Our fight (second hit)",
         att=S("T69 rally", "5-10-4", (1_119_400, 2_250_600, 943_000), "Ranged Phalanx (from losses)"),
         dfn=S("Opponent", "6-5-9", (1_288_000, 1_131_500, 2_073_593), "Cavalry Phalanx (from losses)"),
         al=1_758_136, dl=1_863_637, us="att", tags=["cav-into-range"],
         lesson="Same hit again, same result: attacker ahead by 106K. Cav in front loses to a 2M+ ranged stack."),
    dict(id=27, day="19 Nov", group="guild", place="Our fight",
         att=S("T69 rally", "866", (1_597_065, 1_330_965, 1_237_920), "Ranged Phalanx?"),
         dfn=S("Opponent", "776", (1_537_453, 1_498_434, 1_181_285), "Ranged Phalanx?"),
         al=1_595_890, dl=1_766_712, us="att", tags=["mirror"],
         lesson="Both ranged died. Attacker had 168K less ranged and about 57K more cav and infantry. Attacker ahead by 171K."),
    dict(id=28, day="19 Nov", group="guild", place="Our fight",
         att=S("T69 rally", "1055", (2_072_796, 1_138_295, 1_101_909), "Ranged Phalanx?"),
         dfn=S("Opponent", "866", (1_587_336, 1_277_403, 1_172_528), "Ranged Phalanx?"),
         al=1_417_565, dl=1_753_274, us="att", tags=["mirror"],
         lesson="Infantry-heavy rally with less cav and less ranged won by 335K. Its 485K extra infantry chewed through their ranged, then their infantry (397K lost)."),
    dict(id=29, day="19 Nov", group="guild", place="Our fight",
         att=S("T69 rally", "055", (50_000, 2_738_810, 1_502_190), "Infantry Wedge"),
         dfn=S("Opponent", "749", (1_534_193, 925_951, 1_852_333), "Infantry Phalanx (from losses)"),
         al=1_569_065, dl=1_391_511, us="att", tags=["055"],
         lesson="First 055 into an Infantry Phalanx. Defender's ranged untouched, infantry lost 1.14M, cav only 13%. The 055 lost 88% of its cav. Defender ahead by 178K."),
    dict(id=30, day="19 Nov", group="guild", place="Our fight",
         att=S("T69 rally", "6-1-13", (1_253_442, 213_998, 2_845_560), "unknown"),
         dfn=S("Opponent", "4-2-13", (942_795, 463_173, 2_841_752), "unknown"),
         al=1_478_635, dl=1_292_965, us="att", tags=[],
         lesson="Cav against cav, about 2.84M each. Not a standard Wonder comp. Defender ahead by 186K."),
    dict(id=31, day="19 Nov", group="guild", place="Our fight",
         att=S("Opponent", "794", (1_527_843, 1_847_913, 937_244), "Ranged Phalanx?"),
         dfn=S("T69 garrison", "848", (1_688_460, 940_237, 1_684_303), "Ranged Phalanx?"),
         al=1_521_562, dl=1_780_971, us="def", tags=["mirror"],
         lesson="Ranged-heavy rally with 747K LESS cav won by 259K. Its ranged outlived the defender's (38% survived), the same shape as log 7."),
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
         sub="The cav-heaviest standard comp: a cav-heavy 424.",
         form=["<strong>Cav Phalanx</strong> against comps low on ranged " + SRC_SITE,
               "<strong>Range Phalanx</strong> against ranged-heavy comps such as 866 " + SRC_SITE,
               "Defending a 659 hit: sit Cav Phalanx, or Range Phalanx if they run Saberfang or heavy cav gear " + SRC_SHEET],
         beats=["Range Phalanx: 965, 866 " + SRC_SHEET,
                "Cav Phalanx: 947, 956, 857, 749 " + SRC_SHEET,
                "Range Phalanx mirrors where it had far more cav " + logref(3, 13) + ", but cav alone doesn't decide mirrors " + logref(21)],
         loses=["992 and 055 " + SRC_SITE,
                "668 in Cav Phalanx " + SRC_SITE + " " + SRC_OPEN,
                "884 and 974: a 442 is a natural counter to a 659 " + cb(CB["atkhp"]) + " " + SRC_SITE],
         heroes="Cavalry-focused heroes and familiars.", shots=[("659 comp.png", "659 heroes and familiars"), ("659 gear.png", "659 gear"), ("659 option gear.png", "Alternative pieces")],
         gear="Gear: Cavalry ATK, Cavalry HP and Army stats. Cups can replace the Faith with the same jewels. Main hand: Champion Blade, Skullcrusher or Champion Edge. Off hand: Champion Light, Dragon Fist, Book of the Dead or Mitts."),
    dict(key="569", digits=("5", "6", "9"), parts=(5, 6, 9), name="569",
         sub="659 cav with more ranged and less infantry.",
         form=["<strong>Range Phalanx</strong> into a Range Phalanx sitter " + SRC_OPEN,
               "<strong>Cav Phalanx</strong> if their ranged was just wiped and not refilled " + SRC_OPEN],
         beats=["Untested. More cav and ranged than an 857 or 758 doesn't settle a mirror on its own " + logref(21)],
         loses=["Untested in our logs. Low infantry (about 1.08M) means a garrison built like this is a target for infantry-heavy rallies " + logref(11)],
         heroes="Same as 659, with 2 ranged heroes for Range Phalanx.", shots=[],
         gear="Same gear as 659."),
    dict(key="668", digits=("6", "6", "8"), parts=(6, 6, 8), name="668",
         sub="Balanced attack comp. Range Phalanx by default, with a planned switch against cav-heavy targets.",
         form=["<strong>Range Phalanx</strong> by default " + SRC_SITE + " " + SRC_SHEET,
               "<strong>Cav Phalanx</strong> against 659, 569 and 758 " + SRC_SITE + " " + SRC_OPEN + ". Careful: our only Cav Phalanx defence today lost narrowly when the rally came in Range Phalanx " + logref(2)],
         beats=["Range Phalanx: 965, 776 " + SRC_SITE + " " + SRC_SHEET + "",
                "857 in Range Phalanx: a toss-up. To hit an 857, a 442 (884, 794) is the better send " + cb(CB["v442"]),
                "1262-style infantry piles with low cav: won by 527K " + logref(4)],
         loses=["Range Phalanx: 659, 569, 758 " + SRC_SITE + " " + SRC_SHEET,
                "884, 794 and 875 in Range Phalanx: the 442 win. Against them use Cav Phalanx with a stat edge, or an infantry-heavy comp " + logref(31) + " " + cb(CB["v442"]),
                "442 types sitting Ranged Phalanx: their ranged outlives yours " + logref(31) + " " + cb(CB["m442"])],
         heroes="1 infantry, 2 ranged, 2 cavalry. The sheet's 2-2-1 is what a 055 or 208 feeds on " + cb(CB["s424"]) + ".", shots=[("668 comp.png", "668 lead march: 208K T5 + 167K T4 infantry. The heroes shown are the sheet's 2-2-1; swap one infantry hero for a cav hero"), ("659 gear.png", "Same gear as 659")],
         gear="Same gear as 659. Talents: Infantry 3, Ranged 3 and Cavalry 3 maxed, Army HP 1 and 2 maxed, Infantry 2 maxed, the rest into Ranged 2.",
         warn="Fillers keep turning this into a 758. Logs 1 and 3 landed at about 7.5-5-7.5. Check the rally screen reads about 30% / 30% / 40% before you launch."),
    dict(key="866", digits=("8", "6", "6"), parts=(8, 6, 6), name="866",
         sub="Infantry-heavy Range Phalanx comp for targets with low cav.",
         form=["<strong>Range Phalanx</strong> only, with the lead sending a full infantry march " + SRC_SITE + " " + SRC_SHEET],
         beats=["974, 884, 712 " + SRC_SITE + " " + SRC_SHEET, "992 " + SRC_SITE, "965 " + SRC_SITE],
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
         heroes="4 ranged + 1 cav hero, no infantry hero. Familiars: ranged pact-5s, Cav Shield, cav stacker.", shots=[("055 comp.png", "055 heroes; lead sends the only infantry"), ("055 gear.png", "055 gear"), ("055 option gear.png", "Alternative pieces")],
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
         heroes="4 cav heroes + 1 army hero. Familiars: 2 cav pact-5, cav stacker, Cav Shield, then Jade Wyrm or Gryphon " + SRC_SHEET + " " + cb(CB["c208"]) + ".", shots=[("208 comp.jpg", "208 heroes; lead sends 120K ranged + T5 infantry"), ("208 gear.png", "208 gear"), ("208  Champ gear.jpg", "Champion gear"), ("208 option gear.png", "Alternative pieces")],
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
<tr><td class="t-inf">Infantry pile, under 1M cav</td><td class="t-cav">Cavalry</td><td>Cavalry Phalanx</td></tr>
<tr><td class="t-inf">Infantry, in a mixed comp</td><td class="t-rng">Ranged</td><td>Ranged Phalanx {cb(CB["basics"])}</td></tr>
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
<li>Only one ranged hero in Range Phalanx. Your middle ranged squad ends up out of line and gets bypassed or picked off; three is just as bad. Use exactly two. {cb(CB["rh"])}</li>
<li>Leaving formations unbound in your hotkeys. Range Wedge is the one people forget, and the 208 needs it.</li>
</ul>
"""
    return shell("formations.html", "Formations", "Real squad layouts for all six Lords Mobile formations and how they counter each other.", body)


# ================================================================ WONDER RULES (rulebook)
def _parts(t):
    T = sum(t)
    return [x / T * 20 for x in t]


def mirror_model(a, d):
    """Working mirror rule. Returns ('ATT'|'DEF'|'EVEN', reason)."""
    pa, pd = _parts(a), _parts(d)
    heavy = lambda p: p[1] >= 7.5
    if heavy(pa) and pa[2] < 3:
        return "DEF", "attacker is ranged-heavy with no cav guard"
    if heavy(pd) and pd[2] < 3:
        return "ATT", "defender is ranged-heavy with no cav guard"
    if heavy(pa) and not heavy(pd):
        lead = a[1] - d[1]
        return ("ATT" if lead >= 700_000 else "DEF"), f"442 attacker, ranged lead {m(lead)}"
    if heavy(pd) and not heavy(pa):
        lead = d[1] - a[1]
        return ("DEF" if lead >= 700_000 else "ATT"), f"442 defender, ranged lead {m(lead)}"
    gap = a[0] - d[0]
    return ("ATT" if gap > 0 else "DEF"), f"424 mirror, infantry gap {'+' if gap >= 0 else '−'}{m(abs(gap))}"


def mirror_model_rows():
    out = ['<div class="table-wrap"><table><thead><tr><th>Log</th><th>Fight</th><th>Rule says</th>'
           '<th class="num">Result</th><th></th></tr></thead><tbody>']
    hits = n = 0
    for b in BATTLES:
        if "mirror" not in b["tags"] or not b["att"]["tr"] or not b["dfn"]["tr"]:
            continue
        a, d = b["att"]["tr"], b["dfn"]["tr"]
        pred, why = mirror_model(a, d)
        margin, *_ = result(b)
        act = "ATT" if margin > 0 else "DEF"
        ok = pred == act
        hits += ok; n += 1
        out.append(f'<tr><td><a href="battle-reports.html#log-{b["id"]}">{b["id"]}</a></td>'
                   f'<td>{E(b["att"]["comp"])} into {E(b["dfn"]["comp"])}</td>'
                   f'<td>{"Attacker" if pred == "ATT" else "Defender"}: {E(why)}</td>'
                   f'<td class="num">{"Attacker" if act == "ATT" else "Defender"} by {m(abs(margin))}</td>'
                   f'<td><span class="status {"ok" if ok else "bad"}">{"✓" if ok else "✗"}</span></td></tr>')
    out.append("</tbody></table></div>")
    return "".join(out), hits, n


def grade(g):
    label = {"proven": "Proven", "strong": "Strong", "working": "Working", "theory": "Theory"}[g]
    return f'<span class="grade {g}">{label}</span>'


def rule(gid, g, title, call, why, evidence):
    return (f'<article class="rule-card" id="{gid}"><header>{grade(g)}<h3>{title}</h3></header>'
            f'<p class="call">{call}</p><p><strong>Why:</strong> {why}</p><p class="ev">{evidence}</p></article>')


def page_advanced():
    mrows, mhits, mn = mirror_model_rows()
    V = CB
    body = f"""<div class="page-head">
<h1>Wonder rules</h1>
<p class="lede">Every rule here says what to do, why it works, and how sure we are. Built from all {len(BATTLES)} logged fights and Crystal Briefs' tests. When they disagree, tests and logs beat the old site, which beats the sheet.</p>
</div>
<ul class="section-nav">
<li><a href="#idea">The core idea</a></li><li><a href="#defend">Holding</a></li><li><a href="#mirror">Mirrors</a></li>
<li><a href="#c055">055</a></li><li><a href="#c208">208</a></li><li><a href="#garrison">Garrison</a></li><li><a href="#boost">What to boost</a></li><li><a href="#drift">Habits</a></li>
</ul>
<div class="grades"><p>{grade("proven")} our logs and his tests agree. {grade("strong")} 3+ of our fights, all the same way. {grade("working")} fits our fights but was fitted to them: the next fights test it. {grade("theory")} his tests only, not in our logs yet.</p></div>

<h2 id="idea">The core idea</h2>
<p>Every Wonder fight has two phases. <strong>Phase 1, the front trade:</strong> the fronts meet and each side's troops hit the troop they counter. Whatever is still standing goes into <strong>phase 2</strong>, where the targeting sends each side's back line onto whatever the other side has left. {cb(V["squads2"])} {cb(V["basics"])}</p>
<p>You win by doing two things: <strong>win the front trade, and still have a guard for phase 2.</strong> Every comp is a different way of doing that:</p>
<ul>
<li><strong>442s</strong> win phase 1 with sheer ranged, and their cav guards their infantry in phase 2.</li>
<li><strong>055s</strong> skip the front trade: they break through at the edges and hit your cav directly.</li>
<li><strong>208s</strong> send a little infantry to win the trade against your ranged while their cav runs straight for phase 2.</li>
<li><strong>A garrison with no infantry</strong> can't fight phase 1 at all.</li>
</ul>
<p>Every rule below is one of these.</p>

<h2 id="defend">Holding: what to sit in</h2>
{rule("d055", "proven", "Against a 055: Ranged or Infantry Phalanx. Never Ranged Wedge.",
  "Sit Ranged Phalanx with only 1 infantry hero, or Infantry Phalanx.",
  "A 055 wins by breaking your ranged front at the edges and walking its ranged onto your cav. In Infantry Phalanx your front is infantry, the one troop its ranged can't beat, so it never gets through. In Ranged Phalanx it needs your 2 infantry heroes to reach both cav squads; with 1, it reaches one. Ranged Wedge hands it the edges.",
  f"Held in Ranged Phalanx {logref(12, 15, 16)} and Infantry Phalanx {logref(29)}; in log 29 your cav lost only 13%. {cb(V['f055'])} {cb(V['da2'])}")}
{rule("dcav", "strong", "Cav in front only against a small ranged stack.",
  "Cav Phalanx holds against about 1.1M ranged. Against 2M+ ranged, don't.",
  "Their ranged gets about three full volleys into your cav before your infantry reaches it. Each volley scales with how much ranged they have, so a 2M stack shreds the cav in phase 1.",
  f"Won or even at about 1.1M {logref(2, 17, 20, 23)}; lost at 2.2M twice {logref(25, 26)}. {cb(V['basics'])}")}
{rule("d442", "theory", "Against a ranged-heavy 442: Infantry Phalanx.",
  "Sit Infantry Phalanx.",
  "Infantry is the counter to ranged, so you win phase 1, and a 442 only has about 4 parts of cav to punish your infantry front. A cav front would face their 2M ranged (see above).",
  f"{cb(V['basics'])} {cb(V['v442'])}")}
{rule("d208", "theory", "Against a 208: Ranged Wedge.",
  "Sit Ranged Wedge, with a Cav Shield familiar if you have it.",
  "A 208 needs its cav to reach your infantry. In Ranged Wedge your cav stands in front of your infantry and blocks it, and two of its infantry squads end up stacked on one of your ranged squads, so its front trade slows down.",
  f"{SRC_SHEET} {cb(V['f055'])} {cb(V['c208'])}")}
{rule("dmix", "theory", "Against a mixed rally with infantry biggest: Ranged Phalanx.",
  "Ranged Phalanx. Cav in front only against an infantry pile with under 1M cav.",
  "With a cav front, their ranged and cav back line wear your cav down through phase 1. In Ranged Phalanx your cav sits behind and hits their infantry at full strength in phase 2.",
  f"{cb(V['basics'])}")}

<h2 id="mirror">Ranged Phalanx mirrors</h2>
{rule("mguard", "proven", "A ranged-heavy comp needs its cav guard.",
  "Keep at least 3 of 20 parts in cav (about 650K). Never send an 8-11-1.",
  "A 442 wins the ranged trade, then the other side's infantry and cav go looking for targets. Its cav is what stands in the way. Without it, they run straight into its infantry.",
  f"8-11-1 lost twice into a 758 {logref(5, 6)}; a 1262 with 385K cav lost by 527K {logref(4)}. {cb(V['c992'])}")}
{rule("m442", "working", "A 442 needs a big ranged lead.",
  "A ranged-heavy rally wins when it brings about 700K more ranged than the target. Under that, the target wins.",
  "The 442 win only happens if their ranged is dead before half of yours is. That takes a big ranged surplus plus enough infantry; a small surplus just turns it into a slugging match the 424 wins.",
  f"Won with +717K and +907K {logref(7, 31)}; lost with +527K {logref(13)}. {cb(V['m442'])}")}
{rule("m424", "working", "424 against 424: more infantry wins.",
  "When neither side is ranged-heavy, the side with more infantry usually wins. Within about 100K, it's stats and heroes.",
  "With the ranged fronts gone, infantry is the troop that soaks the other side's back line and keeps killing. Exception so far: a 222K cav edge beat a 250K infantry edge in log 3.",
  f"Fits logs 1, 21, 24, 27 and 28; misses log 3, and log 22 was a 36K coin flip. Crystal Briefs adds that in a true even mirror, whoever's ranged dies first can flip it. {cb(V['m424'])}")}
<p><strong>The working rule called {mhits} of {mn} logged mirrors.</strong> The old "more cav wins" called 6. It was fitted to these same fights, so the real test is the next ones. Every mirror you screenshot gets checked here automatically.</p>
{mrows}

<h2 id="c055">The 055</h2>
{rule("e055", "proven", "Infantry buffer: 50–60K, T4 or better. Not 40K.",
  "Only the lead sends infantry: 50–60K at T4 or above. Nobody else sends any.",
  "The buffer is a timer. At the start every enemy squad aims at the closest 055 squads, which is the infantry at the tip. It stays locked on until that squad dies. The buffer has to soak their opening, including their infantry heroes' big skill hits, and die at the right moment so their squads retarget where the 055 wants. Die too early and the 055 never reaches their cav. Last too long and it never does either: in his test, 100K left their cav completely untouched. How long it lasts depends on how hard their ranged hits, and today's top accounts hit far harder than his 2022 tests. That's why our 40K 055s failed and 50K got through.",
  f"40K into Ranged Phalanx lost twice and barely touched their cav (0 and 11%) {logref(12, 15)}. 50K won by 1.1M {logref(10)} and traded even into 1.77M ranged, reaching 35% of their cav {logref(14)}. {cb(V['f055'])} {cb(V['c055'])}")}
{rule("t055", "proven", "Who to hit with a 055.",
  "A 424 sitting Ranged Phalanx with 2 infantry heroes. Not an Infantry Phalanx sitter.",
  "Its ranged has to break their ranged front to reach the cav. Against an infantry front it's fighting its counter, so it never gets through. If you know they sit Infantry Phalanx, Crystal Briefs sends the 055 in Ranged Phalanx instead.",
  f"Into Infantry Phalanx it lost by 178K and reached 13% of their cav {logref(29)}. {cb(V['f055'])}")}
{rule("b055", "theory", "How to build it.",
  "Infantry Wedge. Heroes: 4 ranged, 1 cav, no infantry hero. Familiars: ranged pact-5s, Cav Shield, cav stacker. Gear: ranged attack and cav HP first. Did it work? About half their cav dead means yes.",
  "Ranged heroes speed up breaking their front. Your cav ends up as the front line in Infantry Wedge, so it needs HP and the shield. An infantry hero breaks the targeting the buffer sets up.",
  f"{cb(V['c055'])}")}

<h2 id="c208">The 208</h2>
{rule("e208", "theory", "Who to hit with a 208, and how.",
  "Hit infantry-heavy 424s (947, 1046 type) sitting Ranged Phalanx with about 1.1M ranged or less. Send it in Ranged Wedge.",
  "Each of its infantry squads takes one of their ranged squads, which is its counter, while the two front cav squads go past the ranged to reach their infantry. Its infantry must survive the whole fight; any damage on the 208's infantry in the report means it failed. Thick ranged means the infantry can't finish in time. Ranged Wedge on their side blocks the cav, and a 442's ranged is too much.",
  f"{cb(V['c208'])} {SRC_SHEET}")}

<h2 id="garrison">Garrison</h2>
{rule("g0inf", "strong", "Never hold with no infantry.",
  "Hold 1.4M+ infantry, 1.1M+ ranged, 1.6M+ cav, at full cap.",
  "Infantry is your only answer to their ranged. With none, their ranged survives the front trade untouched and shoots your cav for the whole fight, while their infantry eats your ranged. Ranged is your front in Ranged Phalanx. Cav is your phase-2 guard.",
  f"More cav and ranged than the attacker, no infantry, lost by 1.46M {logref(11)}.")}
{rule("gstat", "proven", "A big stat or T5 gap beats the right formation.",
  "Don't take or send a hit into a much stronger lead and expect the counter to save you.",
  "Each squad's strength is stats × tier × count. A big enough gap wins the front trade no matter how it's set up.",
  f"The same 055-into-758 matchup lost twice and then won by 1.1M with the strongest lead {logref(10, 12, 15)}. {cb(V['da2'])}")}
{rule("gheroes", "theory", "Heroes set where your squads stand.",
  "Exactly 2 ranged heroes whenever you sit Ranged Phalanx. 1-2-2 on a 424.",
  "A squad with a hero stands one step back, which changes who reaches whom. With 1 or 3 ranged heroes your middle ranged squads end up out of line.",
  f"{cb(V['rh'])} {cb(V['s424'])}")}

<h2 id="boost">What to boost</h2>
<p>Gear, jewels and talents should feed the part of the fight your comp has to win. Find the troop that has to survive or has to kill, and boost that stat. {cb(V["atkhp"])} {cb(V["research"])}</p>
<div class="table-wrap"><table class="stack"><thead><tr><th>Comp</th><th>Boost first</th><th>Why</th></tr></thead><tbody>
<tr><td>442: 884, 794, 875</td><td><span class="t-rng">Ranged HP</span>, then <span class="t-inf">Infantry ATK</span>, then <span class="t-cav">Cav HP</span></td><td>The 442 win needs your ranged alive after theirs is dead. Infantry attack kills their ranged sooner. Cav HP keeps the guard standing. Log 13 lost with a 527K ranged lead, short of the line.</td></tr>
<tr><td>424 in Ranged Phalanx: 857, 758, 668</td><td><span class="t-inf">Infantry HP</span> and <span class="t-cav">Cav HP</span>; don't stack <span class="t-rng">Ranged ATK</span></td><td>Infantry soaks phase 2, which is why more infantry wins these mirrors. In his test, raising attack made this mirror worse while HP helped. Keep cav stats within about 100 of ranged.</td></tr>
<tr><td>Any comp sitting Cav Phalanx</td><td><span class="t-cav">Cav HP</span> + Cav Shield</td><td>Your cav eats about three full ranged volleys before your infantry arrives.</td></tr>
<tr><td>055</td><td><span class="t-rng">Ranged ATK</span> and <span class="t-cav">Cav HP</span>; skip ranged HP</td><td>Ranged attack breaks their front faster. Your cav is the real front line in Infantry Wedge. Your ranged should never take hits except from familiars.</td></tr>
<tr><td>208</td><td><span class="t-cav">Cav ATK and HP</span> equally; <span class="t-inf">Infantry ATK</span> against thick ranged</td><td>Cav does the killing and has to survive the walk in. Infantry attack only matters when their ranged is thick enough to slow your infantry.</td></tr>
<tr><td>1433 / Infantry Phalanx</td><td><span class="t-inf">Infantry HP and ATK</span></td><td>Infantry is both the front and the damage.</td></tr>
<tr><td>Holding a wonder in Ranged Phalanx</td><td><span class="t-rng">Ranged HP</span>, <span class="t-inf">Infantry HP</span>, <span class="t-cav">Cav ATK</span></td><td>Ranged is your front. Infantry is your answer to their ranged. Cav kills their infantry in phase 2.</td></tr>
</tbody></table></div>
<p><strong>Before any of that:</strong> counter stats, the enemy-debuff research and T5 multiply everything. Flat stats only add. {cb(V["research"])}</p>
<p class="muted">Reading a loss: if your front died before theirs, that troop needed HP. If theirs lived too long, your counter troop needed attack.</p>

<h2 id="drift">Habits</h2>
{rule("hfinal", "strong", "Call off final numbers only.",
  "Switch formation after the last scout, not while the rally is filling.",
  "The comp you're countering changes until it lands.",
  f"Switched off a half-filled scout and lost {logref(2)}.")}
{rule("hdrift", "strong", "Check the rally screen before launch.",
  "Your 668 should read about 30 / 30 / 40.",
  "Fillers drift toward infantry, and a 668 that lands as a 758 is a different comp.",
  f"Landed at about 7.5-5-7.5 twice {logref(1, 3)}.")}
{rule("hrefill", "strong", "Refill ranged after every mirror.",
  "Top your ranged back up before the next hit lands.",
  "Both ranged fronts die in every mirror.",
  f"{logref(1, 3, 5, 6, 22, 27, 28)}")}
"""
    return shell("advanced.html", "Wonder rules", "Lords Mobile Wonder rules with the reason behind each one and how strong the evidence is.", body)


# ================================================================ HOW FIGHTS WORK
def mirror_check_rows():
    """Every logged Range Phalanx mirror with a troop breakdown, and whether the old cav rule called it."""
    out = ['<div class="table-wrap"><table><thead><tr><th>Log</th><th>Shape</th><th class="num">Cav gap</th>'
           '<th class="num">Ranged gap</th><th class="num">Attacker</th><th>Cav rule</th></tr></thead><tbody>']
    hits = n = 0
    for b in BATTLES:
        if "mirror" not in b["tags"] or not b["att"]["tr"] or not b["dfn"]["tr"]:
            continue
        a, d = b["att"]["tr"], b["dfn"]["tr"]
        margin, *_ = result(b)
        score = (a[2] - d[2]) + 0.5 * (a[1] - d[1])
        ok = (score > 0) == (margin > 0)
        hits += ok; n += 1
        cg, rg = a[2] - d[2], a[1] - d[1]
        out.append(
            f'<tr><td><a href="battle-reports.html#log-{b["id"]}">{b["id"]}</a></td>'
            f'<td>{E(b["att"]["comp"])} into {E(b["dfn"]["comp"])}</td>'
            f'<td class="num t-cav">{"+" if cg >= 0 else "−"}{m(abs(cg))}</td>'
            f'<td class="num t-rng">{"+" if rg >= 0 else "−"}{m(abs(rg))}</td>'
            f'<td class="num"><span class="{"win" if margin > 0 else "loss"}">{"won" if margin > 0 else "lost"} by {m(abs(margin))}</span></td>'
            f'<td><span class="status {"ok" if ok else "bad"}">{"called it" if ok else "wrong"}</span></td></tr>')
    out.append("</tbody></table></div>")
    return "".join(out), hits, n


def page_mechanics():
    rows, hits, n = mirror_check_rows()
    V = CB
    body = f"""<div class="page-head">
<h1>How fights work</h1>
<p class="lede">Everything Crystal Briefs found in his Wonder tests, checked against our {len(BATTLES)} logged fights. He tests with both accounts' stats matched, so his results show the mechanics with gear taken out. They're from 2022–23 and one pair of testers; read the numbers as directions, not exact values.</p>
</div>
<ul class="section-nav">
<li><a href="#engine">The engine</a></li><li><a href="#formations">Formations</a></li><li><a href="#mirrors">Range Phalanx mirrors</a></li>
<li><a href="#heroes">Heroes</a></li><li><a href="#familiars">Familiars</a></li><li><a href="#stats">Stats &amp; research</a></li>
<li><a href="#playbooks">Comp playbooks</a></li><li><a href="#why">Why each comp wins</a></li><li><a href="#disagree">Where sources disagree</a></li>
</ul>
<p class="muted">Tags: {src("cb", "Crystal Briefs")} links to the video. {src("log", "log N")} is one of our fights. {SRC_SHEET} is your spreadsheet.</p>

<h2 id="engine">The engine</h2>
<p>A fight is a 40-second simulation between squads, not between single troops. Once you know the squad rules, odd reports start making sense. {cb(V["squads1"])} {cb(V["squads2"])}</p>
<ul>
<li><strong>Every troop type makes exactly 4 squads</strong>, each a quarter of that type. Each tier is split evenly across the 4. Inside a squad the lowest tier dies first.</li>
<li><strong>A squad attacks one enemy squad at a time</strong>, starting with the closest. It only switches target when that squad is completely dead. Who switches onto whom (retargeting) decides most Wonder fights.</li>
<li><strong>Cav moves fastest, ranged slowest.</strong> Tier doesn't change battle speed.</li>
<li><strong>T5 is about 1.33× T4.</strong> A big T5 gap beats a correct formation; in his Dragon Arena reviews the side with far more T5 kept winning "countered" fights. {cb(V["da2"])}</li>
<li><strong>Morale decides nothing.</strong> The bar in the movie is drawn backwards from the final losses. {cb(V["morale"])}</li>
<li><strong>The battle movie is accurate.</strong> Watch it to see which squad hit which. That's how you tell why a fight went wrong.</li>
</ul>

<h2 id="formations">Formations in mixed fights</h2>
<p>A formation only sets where your squads start, so it decides who takes damage first. It doesn't buff anything. {cb(V["basics"])}</p>
<ul>
<li><strong>Putting your counter troop in front is the weak way to counter.</strong> With mixed comps, Ranged Phalanx beats Infantry Phalanx, Infantry Phalanx beats Cav Phalanx, and Cav Phalanx beats Ranged Phalanx. The winner is the side whose back line keeps hitting at full strength.</li>
<li><strong>Cav Phalanx into Ranged Phalanx is the weakest of the three.</strong> Ranged gets about three full volleys into the cav before the infantry arrives. Our logs agree. A cav front held or broke even against about 1.1M ranged {logref(2, 17, 20, 23)}. It lost twice to a 2.2M ranged stack {logref(25, 26)}.</li>
<li><strong>Don't trust the drill on the formation page.</strong> It changes the troop split when you change formation, so it can't compare formations. {cb(V["basics"])}</li>
<li><strong>Cav Wedge is never the best pick for a 424</strong>, except maybe against Infantry Phalanx. It loses to Ranged Phalanx because its infantry can only reach the two outer ranged squads. {cb(V["cw"])}</li>
<li><strong>Ranged Wedge:</strong> never take a 055 in it. It's the formation that blunts a 208. Against a cav blast already sitting Ranged Phalanx, stay in Ranged Phalanx: Ranged Wedge lets the cav reach your infantry. {cb(V["f055"])} {cb(V["c208"])} {cb(V["da1"])}</li>
</ul>

<h2 id="mirrors">Range Phalanx mirrors</h2>
<p>Both sides sit Ranged Phalanx. The two outer ranged squads on each side die first, then the middle ones. What happens after that decides the fight.</p>
<ul>
<li><strong>424 vs 424:</strong> the side whose ranged dies <em>first</em> usually wins. Once both fronts are gone, the targeting sends the other side's back line onto the winner's cav, and onto the loser's infantry. This is how weaker accounts beat stronger ones, and why more attack can lose you a mirror. The fix for the stronger side is a 1-2-2 hero lineup or sitting Cav Phalanx instead. {cb(V["m424"])} {cb(V["atkhp"])}</li>
<li><strong>442 vs 424:</strong> results swing to big wins or big losses, rarely close. The 442 wins big if the 424's ranged is dead before half the 442's ranged is. You can spot it in the report: about half the 442's ranged survives. {cb(V["m442"])} {cb(V["v442"])} Logs 7 and 31 look exactly like this: a ranged-heavy rally won both, once with 747K less cav. {logref(7, 31)}</li>
<li><strong>A 442 still needs its cav.</strong> After it wins the ranged trade, its cav is what keeps the enemy off its infantry. {cb(V["c992"])} Our 8-11-1 rallies, with under 400K cav, lost twice into a 758. {logref(5, 6)}</li>
</ul>
<div class="note warn"><p><strong>The old cav rule is retired.</strong> "More cav wins a mirror" was fitted to our first 6 mirrors. Across all {n} mirrors with numbers it called {hits}. "More infantry wins" called 5. "Whoever's ranged dies first" called 7. Troop counts alone don't decide mirrors; heroes, familiars and stats do. The working rule that replaced it (cav guard, ranged lead, then infantry) is on <a href="advanced.html#mirror">Wonder rules</a>.</p></div>
{rows}

<h2 id="heroes">Heroes</h2>
<p>A hero's stats matter less than its tactical skill. The skill hits for double a normal squad attack about four times a fight, and it scales with the squad's size. In his test a hero with no useful stats added about 20% damage, while 20 army attack from another hero added about 1.5%. The hero's troop type has to match the squad or the skill never fires. {cb(V["heroes"])}</p>
<p>A squad with a hero stands one step further back, because the skill reaches further than a normal attack. That shifts who reaches whom, so the number of heroes of each type changes how a fight plays out. {cb(V["squads2"])} {cb(V["rh"])}</p>
<div class="table-wrap"><table class="stack"><thead><tr><th>You're running</th><th>Heroes (infantry-ranged-cav)</th><th>Why</th></tr></thead><tbody>
<tr><td>Any comp sitting Ranged Phalanx</td><td><strong>Exactly 2 ranged</strong></td><td>With 1 or 3, your middle ranged squads stand out of line and the targeting turns on you. With 0, don't sit Ranged Phalanx at all. {cb(V["rh"])}</td></tr>
<tr><td>424 types: 857, 758, 947, 749, 659</td><td><strong>1-2-2</strong></td><td>The safest lineup. 2-2-1 is easy prey for a 055 or a 208; it only helps against 442s. 2-1-2 only if you never sit Ranged Phalanx. {cb(V["s424"])}</td></tr>
<tr><td>442 types: 884, 974, 875, 992, 794</td><td><strong>2-2-1</strong></td><td>Fine as standard. 1-2-2 gives more cav damage if they sit Infantry Phalanx. Never 3 ranged. {cb(V["s442"])} {cb(V["da1"])}</td></tr>
<tr><td>055 (attacking)</td><td><strong>0-4-1</strong></td><td>4 ranged heroes speed up breaking their ranged front. Any infantry hero breaks the 055's targeting. {cb(V["c055"])}</td></tr>
<tr><td>Holding against a 055</td><td><strong>Only 1 infantry hero</strong></td><td>With 2 infantry heroes a 055 reaches both your cav squads; with 1 it reaches one. {cb(V["f055"])} {cb(V["da2"])}</td></tr>
<tr><td>208</td><td><strong>4 cav + 1 army hero</strong></td><td>Your cav-blast heroes. An infantry army hero is ideal but makes little difference. {cb(V["c208"])}</td></tr>
<tr><td>Cav Phalanx</td><td>Use Rose Knight over Storm Fox</td><td>Storm Fox, or only 1 cav hero, can send their ranged further into your cav in Cav Phalanx mirrors. {cb(V["cw"])}</td></tr>
</tbody></table></div>
<p><strong>Worth owning for Wonders:</strong> Chronicler (passive counter stat, just for owning it), the three Wonder heroes (+600K Wonder army size), Watcher (army attack and HP, free), and the army heroes Strong Stress of the Sea, Lore Weaver, Berserker and Dream Witch. Ethereal Guide for 055. {cb(V["hero5"])}</p>

<h2 id="familiars">Familiars</h2>
<p>No familiar is best everywhere. Pick them for what you expect to face. {cb(V["hd"])} {cb(V["jade"])} {cb(V["hdc"])}</p>
<div class="table-wrap"><table class="stack"><thead><tr><th>Familiar</th><th>Great when</th><th>Wasted when</th></tr></thead><tbody>
<tr><td><strong>Pact-5 damage</strong> (Blackwing, Gargantua, Bon Appeti…)</td><td>You can't predict the fight: always decent, never the best in his tests. Run the troop types you have most of.</td><td>Ranged ones on a 424. When swapping one out, drop the 600% one of your smallest troop type first.</td></tr>
<tr><td><strong>Jade Wyrm</strong></td><td>Top 5 in every Wonder test. Also cuts the pact-5 damage you take. Best with a shield familiar.</td><td>Can backfire in a 424 Ranged Phalanx mirror, where you want your ranged to die first.</td></tr>
<tr><td><strong>Hell Drider</strong></td><td>Freezes their biggest squad for 11 s once you've lost 7%. Huge when that squad is the type that counters your front, e.g. you sit Ranged Phalanx and it freezes their infantry (about a 175K swing). Best when attacking a fort you've scouted.</td><td>When it freezes anything else. A 794 or 785 dodges it, because their biggest squad is ranged. Don't pair it with Tempestite: both freeze the same squad.</td></tr>
<tr><td><strong>Shield familiars</strong></td><td>Ranged Shield if you mostly sit Ranged Phalanx, and on any 442. Cav Shield for Cav Phalanx and on a 208. Infantry Shield also soaks pact-5 hits when your infantry takes them.</td><td>When that troop type isn't the one getting hit.</td></tr>
<tr><td><strong>Griffin</strong></td><td>Best in Infantry Phalanx vs Cav Phalanx. Helps a 424 in Cav Phalanx beat 442s.</td><td>Less useful the higher your stats already are.</td></tr>
<tr><td><strong>Stackers</strong> (Goblin etc.)</td><td>Best in Cav Phalanx vs Cav Phalanx. Cav stacker is a must on a 055.</td><td>On a front that's being countered.</td></tr>
</tbody></table></div>
<p><strong>Hell Drider by comp:</strong> 442 types ★★★★★, cav-heavy 424 ★★★★, infantry-heavy 424 ★★★, 208 ★★, 055 ★. {cb(V["hdc"])}</p>

<h2 id="stats">Stats &amp; research</h2>
<ul>
<li><strong>Attack and HP: raise both.</strong> They work together. More attack can lose a 424 Ranged Phalanx mirror, because you kill their ranged first. Stat changes also move when familiars fire. {cb(V["atkhp"])}</li>
<li><strong>Multiplying stats beat adding stats.</strong> In order: counter stats (research, Chronicler, Jade Wyrm), then the enemy-debuff research (it hits all their stats), then T5. For Wonders, the coalition army-size research adds 1M to your rally. {cb(V["research"])}</li>
<li><strong>Talents:</strong> max army attack and HP, then spread the rest evenly across the individual attacks. A 208 maxes infantry and cav attack. {cb(V["s424"])} {cb(V["c208"])}</li>
<li><strong>Comp before stat spread.</strong> On a 424, keep your cav stat within about 100 of your ranged. {cb(V["s424"])}</li>
</ul>

<h2 id="playbooks">Comp playbooks</h2>
<h3>424 types (857, 758, 947, 749, 659, 848)</h3>
<p>Beat most comps at your level and every formation works except Cav Wedge. If you don't know what's coming, Ranged Phalanx. Heroes 1-2-2; infantry and cav pact-5 familiars; Cav Shield if you'll sit Cav Phalanx. Weak spots: 442s in Ranged Phalanx, and 055s or 208s when you run 2 infantry heroes. {cb(V["s424"])}</p>
<h3>442 types (884, 974, 875, 992, 794, 785)</h3>
<p>Sit Ranged Phalanx about 90% of the time; switch to Ranged Wedge if a strong 208 is coming. Ranged Shield always. Infantry-heavy comps are their natural counter. {cb(V["s442"])}</p>
<ul>
<li>Against 424s in Ranged Phalanx: plain 884 is the best trigger for the 442 win. 974 is close, 875 lost narrowly. {cb(V["v442"])}</li>
<li>Against Infantry Phalanx: 875 (more cav) is best. Against Cav Phalanx: 884, and 884 in Infantry Phalanx crushes it. {cb(V["v442"])}</li>
<li>974 beats 992 and plain 884. {cb(V["v442"])} The cav in a 992 shields its infantry after the win. {cb(V["c992"])}</li>
</ul>
<h3>055</h3>
<ul>
<li><strong>Target:</strong> any 424 with 2 infantry heroes. Cav-heavy 424s are ideal. {cb(V["c055"])}</li>
<li><strong>Infantry buffer:</strong> 40–60K T4 or better. About 20K or about 100K fails. Use less against a weaker ranged front. Our logs used 40–50K. {cb(V["f055"])}</li>
<li><strong>Formation:</strong> Infantry Wedge only. Heroes 0-4-1. Familiars: ranged pact-5s, Cav Shield, cav stacker. Gear: ranged attack and cav HP first.</li>
<li><strong>Did it work?</strong> About half their cav dead means yes. In our logs 12 and 15 the defender's cav was barely touched, so those 055s never got through. {logref(12, 15)}</li>
<li><strong>Against Hell Drider</strong> a cav-heavy 055 such as 0-9-11 still wins. {cb(V["f055"])}</li>
</ul>
<h3>208</h3>
<p>Target: infantry-heavy 424s (947, 1046) in Ranged Phalanx. The 208 attacks in Ranged Wedge. Its two front cav squads must survive; if the report shows damage on the 208's infantry, it failed. Riskier against thick ranged. A 307 beats 442s more easily but is weaker against Ranged Wedge. Familiars: 2 cav pact-5, cav stacker, Cav Shield, plus Jade Wyrm or Griffin. {cb(V["c208"])}</p>
<h3>Ranged-cav comps (4-8-8, 4-10-6, our 5-10-4)</h3>
<p>Weak against infantry-heavy 424s, fine against cav-heavy ones. 4-10-6 is the most stable against Ranged Phalanx, but Ranged Wedge kills it. {cb(V["c244"])} Our 5-10-4 beat a Cav Phalanx twice. {logref(25, 26)}</p>

<h2 id="why">Why each comp wins</h2>
<p>To call a matchup nobody has logged, check how each comp wins and whether the other comp can stop that from happening. Five mechanics cover almost everything:</p>
<ol>
<li><strong>The ranged trade.</strong> In Ranged Phalanx the two ranged fronts kill each other first. Your infantry kills their ranged; their infantry kills yours. More infantry means their ranged dies faster; more ranged means yours lasts longer. {cb(V["m442"])} {cb(V["m424"])}</li>
<li><strong>The 442 win.</strong> A ranged-heavy comp wins big if the other side's ranged is dead before half of its own is. Its surviving ranged then shoots their cav, and their cav is stuck fighting the troop that counters it. Needs lots of ranged <em>and</em> enough infantry. {cb(V["m442"])} {logref(7, 31)}</li>
<li><strong>The cav guard.</strong> After a 442 wins the ranged trade, its cav is what keeps their infantry and cav off its own infantry. Under about 2 parts of cav, that guard breaks. {cb(V["c992"])} {logref(5, 6)}</li>
<li><strong>Back-line formations.</strong> Ranged Phalanx beats Infantry Phalanx, Infantry Phalanx beats Cav Phalanx, Cav Phalanx beats Ranged Phalanx. The winner's back line hits at full strength while it eats the other side's front. Cav into ranged is the weakest of the three. {cb(V["basics"])}</li>
<li><strong>Breaking through.</strong> 055 and 208 get past a ranged front to the infantry and cav behind it. A 055 needs a defender with 2 infantry heroes; a 208 needs thin ranged and an infantry-heavy target. {cb(V["c055"])} {cb(V["c208"])}</li>
</ol>

<div class="table-wrap"><table class="stack"><thead><tr><th>Family</th><th>How it wins</th><th>How it loses</th></tr></thead><tbody>
<tr><td>Cav-heavy 424<br><small>659, 569, 749</small></td><td>Ranged trade, then its big cav runs through their infantry. Cav Phalanx against comps with little ranged.</td><td>A 442 wins the ranged trade and shoots its cav (it only has 5–6 infantry to stop that). A 055's favourite target.</td></tr>
<tr><td>Balanced 424<br><small>668, 758, 857, 848</small></td><td>Flexible: every formation works but Cav Wedge. Wins mirrors on stats, heroes and familiars.</td><td>A well-built 442 in Ranged Phalanx. 055 and 208 when it runs 2 infantry heroes.</td></tr>
<tr><td>Infantry-heavy<br><small>947, 956, 965, 866, 1046</small></td><td>Its infantry wins the ranged trade fast. The natural counter to 442s, and solid in Infantry Phalanx.</td><td>208 in Ranged Wedge, and cav-heavy comps once its thin cav is gone.</td></tr>
<tr><td>442 family<br><small>884, 875, 794, 785, 974</small></td><td>The 442 win against 424s in Ranged Phalanx. 794 and 785 also dodge Hell Drider.</td><td>Infantry-heavy comps in Infantry Phalanx; Cav Phalanx with a stat edge. Without its cav guard (8-11-1, 992) it falls apart.</td></tr>
</tbody></table></div>

<h3>Matchups worked out this way</h3>
<div class="table-wrap"><table class="stack"><thead><tr><th>Matchup</th><th>Working</th><th>Call</th></tr></thead><tbody>
<tr><td>668 into 875 (Ranged Phalanx)</td><td>875 is a 442. Its 8 infantry kills the 668's 6 ranged fast; the 668's 6 infantry is slow on the 875's 7 ranged. That's the 442 win. Even an 857, with 8 infantry, only just beat an 875 in his test.</td><td><span class="status bad">875 wins. Sheet overruled</span></td></tr>
<tr><td>668 into 884 or 794</td><td>Same as above but worse: more of their ranged to chew through. Log 31 is this shape and the 424 lost.</td><td><span class="status bad">668 loses</span></td></tr>
<tr><td>Answering an 884 or 875 with a 668</td><td>Don't trade ranged with it. Cav Phalanx with Cav Shield or Griffin is the 424's best formation against a 442; an 857 in Cav Phalanx nearly held an 884 at equal stats. Better: an infantry-heavy comp in Infantry Phalanx.</td><td><span class="status open">Cav Phalanx, needs a stat edge</span></td></tr>
<tr><td>668 into 857 (Ranged Phalanx)</td><td>A true 424 mirror. 857's extra infantry kills your ranged faster, but it has fewer ranged so its own front dies sooner too: the two cancel out. Heroes and stats decide. To hit an 857, send an 884 or 794 instead: that's the 442 win.</td><td><span class="status open">Toss-up. Send a 442 instead</span></td></tr>
<tr><td>659 into 884</td><td>659 has 6 infantry against 8 ranged and 5 ranged against 8 infantry: the 442 win in its clearest form. His test: an 884 beat a 659 even when the 659 sat Infantry Phalanx.</td><td><span class="status bad">Don't send it</span></td></tr>
<tr><td>866 into 965</td><td>Both infantry-heavy with 6 ranged. The 965's extra infantry kills the 866's ranged first, which in a 424-style mirror helps the 866. After the trade, the 866's 6 cav beats the 965's 5 on their infantry.</td><td><span class="status ok">Edge 866, agrees with old site</span></td></tr>
<tr><td>668 Cav Phalanx into 659, 569, 758</td><td>Cav into ranged is the weakest counter, but these sit about 1.1M ranged. Cav fronts held or broke even there and only lost against a 2.2M ranged stack.</td><td><span class="status ok">Works if their ranged is about 1.1M {logref(17, 20, 23, 25)}</span></td></tr>
</tbody></table></div>
<p class="muted">These calls come from mechanics, not logged fights. Each one is a guess with a reason; screenshot the report when you see one and it goes in the log.</p>

<h2 id="disagree">Where sources disagree</h2>
<p><strong>Order of trust:</strong> Crystal Briefs' tests and our logs first, then the old site, then the sheet. Every conflict below is settled that way, and the rest of the site follows it.</p>
<div class="table-wrap"><table class="stack"><thead><tr><th>Question</th><th>What each source says</th><th>Followed</th></tr></thead><tbody>
<tr><td>Who wins a Range Phalanx mirror</td><td>Old rule: more cav. All {n} mirrors: cav called {hits}. Crystal Briefs: timing of the ranged dying, heroes, familiars.</td><td><span class="status ok">Tests + logs: <a href="advanced.html#mirror">working rule</a></span></td></tr>
<tr><td>668 in Ranged Phalanx vs 884</td><td>Sheet: 668 wins. Crystal Briefs: 442s beat 424-types in Ranged Phalanx. Log 31: a 794 beat our 848.</td><td><span class="status ok">Tests + logs: 668 loses</span></td></tr>
<tr><td>659 vs 884</td><td>Sheet: 659 in Infantry Phalanx wins. Old site: never send it. Crystal Briefs: a 442 counters a 659.</td><td><span class="status ok">Tests + site: don't send it</span></td></tr>
<tr><td>Their infantry is biggest: sit what?</td><td>Old rule: cav in front. Crystal Briefs: against mixed infantry-front rallies, Ranged Phalanx holds best.</td><td><span class="status ok">Tests: Ranged Phalanx (cav front only vs an infantry pile with under 1M cav)</span></td></tr>
<tr><td>Hero lineup for 424-types (668, 758, 857)</td><td>Sheet: 2-2-1. Crystal Briefs: 1-2-2; 2-2-1 is what 055s and 208s feed on.</td><td><span class="status ok">Tests: 1-2-2</span></td></tr>
<tr><td>Infantry heroes and the 055</td><td>Old site contradicted itself. Crystal Briefs: attacker runs none; defender holds with 1.</td><td><span class="status ok">Tests</span></td></tr>
<tr><td>Ranged heroes in Ranged Phalanx</td><td>Old site: 1–2 for an 866. Crystal Briefs: exactly 2.</td><td><span class="status ok">Tests: 2</span></td></tr>
<tr><td>Taking a 055 in Infantry Phalanx</td><td>Crystal Briefs: works, but loses to a well-built 055. Log 29: held by 178K.</td><td><span class="status ok">Both work</span></td></tr>
<tr><td>668 in Ranged Phalanx vs 857 or 875</td><td>Old site: beats 857. Sheet: beats 875. Worked out <a href="#why">above</a>: vs 857 a toss-up, vs 875 a loss.</td><td><span class="status ok">Mechanics: 857 toss-up, 875 loses</span></td></tr>
<tr><td>866 vs 965</td><td>Old site: 866 wins. Sheet: 866 loses. Worked out <a href="#why">above</a>: edge 866.</td><td><span class="status ok">Mechanics + site: 866</span></td></tr>
</tbody></table></div>
<p class="muted">Videos used: {len(V)} narrated Crystal Briefs videos. His war-action videos are music only, so they're not included.</p>
"""
    return shell("mechanics.html", "How fights work", "How Lords Mobile Wonder fights resolve: squads, targeting, heroes, familiars and stats, checked against real battle reports.", body)


# ================================================================ BATTLE LOG PAGE
def page_battles():
    body = f"""<div class="page-head">
<h1>Battle log</h1>
<p class="lede">Every Wonder fight with numbers we could read. "Losses" are wounded on each side; Wonder fights have no deaths. A fight within 30K either way is called even.</p>
</div>
<div class="filters" role="group" aria-label="Show fights">
<button type="button" data-filter="all" aria-pressed="true">All {len(BATTLES)}</button>
<button type="button" data-filter="guild" aria-pressed="false">Our fights, 19 Nov</button>
<button type="button" data-filter="shared" aria-pressed="false">16–18 Nov</button>
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
<p>When each familiar pays off is on <a href="mechanics.html#familiars">How fights work</a>. In short: Jade Wyrm is always top 5, shields go on the troop type that takes the hits, and Hell Drider only helps when it freezes the type that counters your front. {cb(CB["jade"])} {cb(CB["hdc"])}</p>
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
<h3>Hero setups</h3>
<p>Heroes change where squads stand, not just stats. Full reasoning on <a href="mechanics.html#heroes">How fights work</a>.</p>
<ul>
<li><strong>Sitting Range Phalanx:</strong> exactly 2 ranged heroes, never 1 or 3. {cb(CB["rh"])}</li>
<li><strong>424 types:</strong> 1 infantry, 2 ranged, 2 cavalry. 2-2-1 is prey for 055 and 208. {cb(CB["s424"])}</li>
<li><strong>442 types:</strong> 2 infantry, 2 ranged, 1 cavalry. {cb(CB["s442"])}</li>
<li><strong>055:</strong> 4 ranged, 1 cavalry, no infantry hero. Holding against one: only 1 infantry hero. {cb(CB["c055"])}</li>
<li><strong>208:</strong> 4 cavalry heroes and 1 army hero. {cb(CB["c208"])}</li>
<li><strong>1433 / Infantry Phalanx:</strong> 4–5 infantry heroes, at most 1 ranged. {SRC_SITE}</li>
<li><strong>Cav Phalanx:</strong> prefer Rose Knight to Storm Fox. {cb(CB["cw"])}</li>
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
        ("Counter their biggest stack", "Their cav: ranged in front. Their ranged: infantry in front. Their infantry: Ranged Phalanx, or cav in front if they have under 1M cav."),
        ("Mirrors: guard, lead, infantry", "Ranged-heavy needs 3+ parts cav and about 700K more ranged. Otherwise more infantry wins. Called 10 of 12 logged mirrors."),
        ("055: 50–60K infantry, not 40K", "Both 40K 055s failed against today's ranged. Hold against one in Ranged or Infantry Phalanx, never Ranged Wedge."),
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

<h2>Six rules from {len(BATTLES)} logged fights</h2>
<ul class="rules">{rl}</ul>
<p>The evidence for each rule is on <a href="advanced.html">Wonder rules</a>, and every fight is in the <a href="battle-reports.html">battle log</a>. Troop counts for each comp are on <a href="CompGears.html">Comps</a>.</p>
"""
    return shell("index.html", "Scout reader", "Lords Mobile Wonder guide: read a scout and pick a formation, backed by real battle reports.", body, scripts=True)


if __name__ == "__main__":
    write("index.html", page_home())
    write("CompGears.html", page_comps())
    write("formations.html", page_formations())
    write("advanced.html", page_advanced())
    write("mechanics.html", page_mechanics())
    write("battle-reports.html", page_battles())
    write("heroes.html", page_heroes())
