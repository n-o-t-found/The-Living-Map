from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
                                Image, PageBreak, KeepTogether, ListFlowable, ListItem, HRFlowable, CondPageBreak)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FD = '/usr/share/fonts/truetype/dejavu/'
pdfmetrics.registerFont(TTFont('DV', FD + 'DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DV-B', FD + 'DejaVuSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('DV-I', FD + 'DejaVuSans-Oblique.ttf'))
pdfmetrics.registerFont(TTFont('DV-BI', FD + 'DejaVuSans-BoldOblique.ttf'))
pdfmetrics.registerFont(TTFont('DVM', FD + 'DejaVuSansMono.ttf'))
pdfmetrics.registerFontFamily('DV', normal='DV', bold='DV-B', italic='DV-I', boldItalic='DV-BI')

NAVY, TEAL, LIGHT, GRID = colors.HexColor('#1f3a5f'), colors.HexColor('#1f6f8b'), colors.HexColor('#eef3f8'), colors.HexColor('#b8c4d0')
W = A4[0] - 3.4 * cm

st = {
 'body': ParagraphStyle('body', fontName='DV', fontSize=8.6, leading=12, spaceAfter=4),
 'small': ParagraphStyle('small', fontName='DV', fontSize=7.6, leading=10.4),
 'cell': ParagraphStyle('cell', fontName='DV', fontSize=7.4, leading=9.8),
 'cellb': ParagraphStyle('cellb', fontName='DV-B', fontSize=7.4, leading=9.8, textColor=colors.white),
 'h1': ParagraphStyle('h1', fontName='DV-B', fontSize=13.5, leading=17, textColor=NAVY, spaceBefore=10, spaceAfter=5, keepWithNext=1),
 'h2': ParagraphStyle('h2', fontName='DV-B', fontSize=10, leading=13, textColor=TEAL, spaceBefore=7, spaceAfter=3, keepWithNext=1),
 'title': ParagraphStyle('title', fontName='DV-B', fontSize=21, leading=26, textColor=NAVY, spaceAfter=4),
 'sub': ParagraphStyle('sub', fontName='DV', fontSize=10, leading=14, textColor=colors.HexColor('#444444'), spaceAfter=2),
 'cap': ParagraphStyle('cap', fontName='DV-I', fontSize=7.4, leading=10, textColor=colors.HexColor('#444444'), spaceAfter=6),
 'code': ParagraphStyle('code', fontName='DVM', fontSize=7, leading=9.2, backColor=colors.HexColor('#f4f4f4'),
                        borderPadding=4, spaceAfter=6, spaceBefore=2),
 'box': ParagraphStyle('box', fontName='DV', fontSize=8.4, leading=11.8),
}

TAGS = {'CONFIRMED': '#1b7f3b', 'PROPOSED': '#1f4e79', 'ASSUMPTION': '#b45f06', 'OPEN': '#b00020', 'TESTED': '#1b7f3b',
        'UNTESTED': '#b00020', 'DESIGN ONLY': '#555555', 'NOT IMPLEMENTED': '#555555', 'DRAFT': '#b45f06', 'INTERPRETATION': '#6a3d9a',
        'IMPLEMENTED IN SIM': '#1b7f3b', 'OPEN DESIGN ISSUE': '#b00020', 'KNOWN BUG': '#b00020', 'NOT STARTED': '#b00020', 'PARTIAL': '#b45f06', 'DONE': '#1b7f3b'}
def T(k): return f'<font color="{TAGS[k]}"><b>[{k}]</b></font>'
def P(t, s='body'): return Paragraph(t, st[s])
def H1(t):
    hr = HRFlowable(width='100%', thickness=1.2, color=NAVY, spaceAfter=4)
    hr.keepWithNext = 1
    return [CondPageBreak(4 * cm), Paragraph(t, st['h1']), hr]
def H2(t): return Paragraph(t, st['h2'])
def bl(items, s='body', indent=11):
    return ListFlowable([ListItem(Paragraph(i, st[s]), leftIndent=indent, bulletColor=NAVY) for i in items],
                        bulletType='bullet', start='•', leftIndent=indent, bulletFontSize=8)
def tbl(rows, widths, header=True, zebra=True):
    data = []
    for ri, r in enumerate(rows):
        data.append([Paragraph(str(c), st['cellb'] if (header and ri == 0) else st['cell']) for c in r])
    t = Table(data, colWidths=[w * W for w in widths], repeatRows=1 if header else 0)
    sty = [('VALIGN', (0, 0), (-1, -1), 'TOP'), ('GRID', (0, 0), (-1, -1), 0.4, GRID),
           ('LEFTPADDING', (0, 0), (-1, -1), 4), ('RIGHTPADDING', (0, 0), (-1, -1), 4),
           ('TOPPADDING', (0, 0), (-1, -1), 2.5), ('BOTTOMPADDING', (0, 0), (-1, -1), 3)]
    if header: sty.append(('BACKGROUND', (0, 0), (-1, 0), NAVY))
    if zebra:
        for i in range(1, len(rows)):
            if i % 2 == 0: sty.append(('BACKGROUND', (0, i), (-1, i), LIGHT))
    t.setStyle(TableStyle(sty))
    return t
def box(paras, bg='#eef6ee', border='#1b7f3b'):
    t = Table([[paras]], colWidths=[W])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(bg)), ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(border)),
                           ('LEFTPADDING', (0, 0), (-1, -1), 8), ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                           ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6)]))
    return t
def img(path, w=1.0):
    from PIL import Image as PI
    iw, ih = PI.open(path).size
    return Image(path, width=W * w, height=W * w * ih / iw)

def footer(c, d):
    c.saveState()
    c.setFont('DV', 7); c.setFillColor(colors.HexColor('#666666'))
    c.drawString(1.7 * cm, 1.1 * cm, 'The Living Map — The Outside Network Area  |  Design brief, 03/10/2026')
    c.drawRightString(A4[0] - 1.7 * cm, 1.1 * cm, f'Page {d.page}')
    c.setStrokeColor(GRID); c.line(1.7 * cm, 1.45 * cm, A4[0] - 1.7 * cm, 1.45 * cm)
    c.restoreState()

doc = BaseDocTemplate('/home/claude/netpdf/The_Living_Map_Outside_Network_Area.pdf', pagesize=A4,
                      leftMargin=1.7 * cm, rightMargin=1.7 * cm, topMargin=1.5 * cm, bottomMargin=1.9 * cm,
                      title='The Living Map — The Outside Network Area', author='Project co-pilot (AI) for the TSYP14 team')
doc.addPageTemplates([PageTemplate(id='p', frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='f')], onPage=footer)])

S = []
S += [Spacer(1, 4), P('The Outside Network Area', 'title'),
      P('The Living Map · TSYP14 Technical Challenge · Design brief and specification', 'sub'),
      P('Written on <b>03/10/2026</b> · Official Phase 1 submission deadline: <b>05/10/2026</b> · Companion to “Phase 1 Project Status &amp; Technical Handover”', 'sub'), Spacer(1, 6)]
S.append(box([P('<b>Who this is for</b>', 'box'), bl([
    'The person who owns the Outside Network Area in the team (the AI assumed one of four roles: Writer, Beacon, <b>Outside Network</b>, Executor) — and any new AI agent helping them.',
    'It explains what the area is, what the organizers require, what has been designed so far, and what is still open.',
    '<b>Nothing in the Outside Network Area exists in code yet.</b> The only related code is the Writer side of the simulation, which produces the log this area will receive.',
    'Labels: ' + T('CONFIRMED') + ' official document or user · ' + T('PROPOSED') + ' suggested by the AI, not approved · ' + T('ASSUMPTION') + ' invented to make the design work · ' + T('OPEN') + ' no decision yet · ' + T('DESIGN ONLY') + ' not implemented · ' + T('INTERPRETATION') + ' the AI’s reading of the documents.'], 'box')], bg='#eef3f8', border='#1f3a5f'))

# ------------------------------------------------------------------ 1
S += H1('1. What the Outside Network Area is')
S.append(P('Inside the disaster zone there is <b>no GPS and no network</b>. Outside it, <b>GPS, satellite time and communication are available</b>. The Outside Network Area is the <b>bridge that connects the two worlds</b>. The organizers say that teams design its interior and that it is <b>defined by its roles, not by its parts</b> (slide 5). ' + T('CONFIRMED')))
S.append(H2('1.1 What the official documents require'))
S.append(tbl([
    ['Requirement (source)', 'Meaning'],
    ['Implement a <b>functional</b> Outside Network Area (instructions, slide 6)', 'It must really work in the demo. ' + T('INTERPRETATION') + ' A simulated satellite link is probably acceptable in Phase 1, but the area itself must run.'],
    ['Route <b>all</b> inside↔outside communication through it', 'The Writer, the Executor and the command post never talk to each other directly.'],
    ['<b>No direct link</b> between the robots and the command post', 'Even for convenience or debugging, do not connect a robot straight to the command post.'],
    ['Four roles: <b>RECEIVE · TRANSLATE · CARRY · BRIEF</b> (slide 5)', 'See section 2.'],
    ['Technical focus: command-post connection · satellite / wireless communication · data reception and forwarding (cahier des charges p.2)', 'The link to the command post can be wireless or satellite.'],
    ['Frame translation: private robot coordinates → real-world GPS coordinates', 'See section 5.'],
    ['Display a <b>live map</b> at the command post (goal list, p.1)', 'See the open question on “live” in section 9.'],
], [0.45, 0.55]))
S.append(H2('1.2 Where it sits in the official chain'))
S.append(P('Writer explores → events detected &amp; beacons deposited → <b>Outside Network receives &amp; translates data → wireless / satellite communication → command post</b> → Executor receives mission → Executor enters &amp; navigates using beacons.'))
S.append(H2('1.3 Points at stake in Phase 1'))
S.append(P('<b>Outside network area: 5</b> · <b>Frame translation: 5</b> · Technical solution diagrams: 5 (shared) · Failure cases: 3 (shared) · Implementation plan: 3 (shared). The Phase 1 deliverables also include the simulation demo (8 points), which should show this area working. The Final Phase adds a physical prototype (15 points).'))

# ------------------------------------------------------------------ 2
S += H1('2. The four roles in detail')
S.append(img('/home/claude/netpdf/net_internal.png', 0.97))
S.append(P('Figure 1 — Internal structure of the area (' + 'proposed' + '). The Writer side already exists in the simulation; everything else is a design.', 'cap'))
S.append(tbl([
    ['Role', 'Input', 'What it does (proposed)', 'Output'],
    ['<b>1 RECEIVE</b>', 'The Writer’s log (I3), sent when the Writer is back at the entrance', 'Accepts the upload; checks that required fields are present and the data is complete (a checksum is suggested); stores the raw log; ignores a duplicate of a log already received (same start time). If the Writer never returns, reports “no log”.', 'A validated log, in the Writer’s private frame'],
    ['<b>2 TRANSLATE</b>', 'Validated log + GPS fix of the entrance + building bearing', 'Converts every beacon, event and path point from the private frame to latitude/longitude (section 5). Attaches an uncertainty estimate that grows with distance.', 'GPS-referenced events, beacons and path'],
    ['<b>3 CARRY</b>', 'GPS-referenced data', 'Sends it to the command post over the chosen link. If the link is down, keeps it in a store-and-forward queue and resends later.', 'Data (I4) that feeds the live map'],
    ['<b>4 BRIEF</b>', 'The mission chosen at the command post + the translated data', 'Builds the Executor’s briefing: mission, ordered beacon chain from the entrance to the target, known hazards, clock synchronisation, trust rules. Delivers it to the Executor <b>before</b> it enters.', 'Briefing (I5)'],
], [0.13, 0.22, 0.45, 0.20]))

# ------------------------------------------------------------------ 3
S += H1('3. How it works in time (proposed sequence)')
S.append(tbl([
    ['Step', 'What happens', 'Who / note'],
    ['0 · Before entry', 'The gateway takes a GPS fix of the entrance and GPS time, records the building bearing, and sets the Writer’s clock.', 'Clock sync is an ' + T('ASSUMPTION') + ' (needed for beacon timestamps and aging).'],
    ['1 · Writer inside', 'The Writer explores alone. <b>No contact</b> with the outside — no network exists.', 'Official condition.'],
    ['2 · Writer returns', 'At the entrance the Writer uploads its log (I3). In the simulation the upload only succeeds within 1.5 m of the entrance, up to 3 tries.', 'RECEIVE. The 1.5 m is a simulation ' + T('ASSUMPTION') + '.'],
    ['3 · Translate', 'The log is converted to GPS coordinates.', 'TRANSLATE.'],
    ['4 · Carry', 'The data is sent to the command post; the live map updates.', 'CARRY. The map therefore updates when the log arrives, not while the Writer is exploring.'],
    ['5 · Mission', 'The command post chooses the mission (extinguish, extract, seal or retrieve).', 'Who chooses — a human operator or a rule — is ' + T('OPEN') + '.'],
    ['6 · Brief', 'The briefing (I5) is prepared and delivered to the Executor; its clock is set.', 'BRIEF. How it is delivered (Wi-Fi at the entrance, cable…) is ' + T('OPEN') + '.'],
    ['7 · Executor inside', 'The Executor enters and navigates by the beacons. Again no contact with the outside.', 'Executor teammate.'],
], [0.17, 0.53, 0.30]))

# ------------------------------------------------------------------ 4
S += H1('4. Interfaces')
S.append(H2('4.1 Input: the Writer’s log (I3) ' + T('DRAFT') + ' ' + T('IMPLEMENTED IN SIM') + ' (Writer side)'))
S.append(P('The Writer simulation already produces this JSON (structure shown, values are placeholders). All coordinates are in the Writer’s <b>private frame</b>: origin = entrance, x = direction of entry, y = left.'))
S.append(Paragraph('{ "robot":"writer", "frame":"private", "origin":"entrance", "start_time":&lt;epoch s&gt;, "end_time":&lt;epoch s&gt;,<br/>'
    '&nbsp; "status":"returned", "return_reason":"...",<br/>'
    '&nbsp; "path":[[x, y, heading_rad, t], ...],<br/>'
    '&nbsp; "beacons":[{"id","type","dir_deg","dist_m","t","ver",["exits"],"x","y","severity","score","confidence"}, ...],<br/>'
    '&nbsp; "decisions":[{"t","type","action","score","reason","x","y"}, ...],<br/>'
    '&nbsp; "stats":{"path_length_m","heading_corrections","drop_failures","stock_left","battery_end","stuck_events"} }', st['code']))
S.append(P('Beacon <font name="DVM">type</font> is HAZARD, JUNCTION, HOLE or WAYPOINT. <font name="DVM">dir_deg</font> is 0–359° in the private frame (0 = direction of entry, counter-clockwise). If the Writer is lost, <b>no log exists</b>. The log has not been agreed with the Outside Network owner, who may change the fields (' + T('OPEN') + ').', 'small'))
S.append(H2('4.2 Output to the command post (I4) ' + T('PROPOSED') + ' ' + T('DESIGN ONLY')))
S.append(Paragraph('{ "entrance":{"lat","lon","bearing_deg"}, "generated_at":&lt;epoch s&gt;, "writer_status":"returned | no_log",<br/>'
    '&nbsp; "events":[{"beacon_id","type","lat","lon","severity","t","uncertainty_m"}, ...],<br/>'
    '&nbsp; "path":[[lat, lon], ...], "warnings":["gps_missing", ...] }', st['code']))
S.append(H2('4.3 Output to the Executor (I5, the briefing) ' + T('PROPOSED') + ' ' + T('DESIGN ONLY')))
S.append(Paragraph('{ "mission":"EXTINGUISH | EXTRACT | SEAL | RETRIEVE", "target_beacon_id":&lt;id&gt;,<br/>'
    '&nbsp; "entrance_pose":{"heading_private_deg":0},<br/>'
    '&nbsp; "chain":[{"order","beacon_id","type","dir_to_next_deg","dist_to_next_m"}, ...],<br/>'
    '&nbsp; "hazards":[...], "clock_sync_epoch":&lt;s&gt;,<br/>'
    '&nbsp; "trust_rules":{fresh, aging, stale, suspect thresholds — values OPEN} }', st['code']))
S.append(box([P(T('OPEN DESIGN ISSUE') + ' <b>Who builds the beacon chain?</b> When the Writer drops a beacon, it does not know where the <i>next</i> beacon will be. So each beacon holds information about its own event, and the true beacon-to-beacon directions and distances only become known from the complete log. The Outside Network (BRIEF) can compute the ordered chain from the log and give it to the Executor in the briefing. This is how the current design works, but it needs to be agreed with the Beacon and Executor teammates (see the handover PDF, section 8.2).', 'box')], bg='#fdecea', border='#b00020'))

# ------------------------------------------------------------------ 5
S += H1('5. Frame translation: private coordinates → GPS')
S.append(H2('5.1 The idea ' + T('PROPOSED') + ' ' + T('DESIGN ONLY')))
S.append(P('The Writer has no GPS, so it measures everything in its own frame. The gateway knows (a) the <b>GPS position of the entrance</b> (lat₀, lon₀) and (b) the <b>compass bearing b of the +x direction</b>, measured clockwise from north. For a point (x, y) in the private frame:'))
S.append(Paragraph('East&nbsp; = x·sin(b) − y·cos(b)<br/>North = x·cos(b) + y·sin(b)<br/>lat = lat₀ + North / 111 320<br/>lon = lon₀ + East / (111 320 · cos lat₀)', st['code']))
S.append(P('111 320 is roughly the number of metres in one degree of latitude. This flat-earth approximation is adequate over tens of metres. ' + T('ASSUMPTION') + ' The formulas are proposed, not yet coded or checked against a real GPS.', 'small'))
S.append(H2('5.2 Worked example (illustrative numbers only)'))
S.append(P('Made-up entrance at lat₀ = 36.8000°, lon₀ = 10.1800°; entry bearing b = 60°:'))
S.append(tbl([
    ['Beacon (private frame)', 'East / North from the entrance', 'Result (lat, lon)'],
    ['(1.0 m, 0.0 m)', '0.87 m / 0.50 m', '36.800004, 10.180010'],
    ['HAZARD at (8.0 m, 2.0 m)', '5.93 m / 5.73 m', '36.800051, 10.180067'],
    ['HOLE at (14.0 m, −3.0 m)', '13.62 m / 4.40 m', '36.800040, 10.180153'],
], [0.34, 0.33, 0.33]))
S.append(H2('5.3 Where the building bearing could come from ' + T('OPEN')))
S.append(tbl([
    ['Option', 'Idea', 'Trade-off'],
    ['A. Compass reading', 'Read a magnetometer outside, aligned with the entry direction', 'Cheap; distorted by metal and electronics — keep it away from the robot.'],
    ['B. Two GPS points', 'Take GPS fixes at the entrance and a second point along the entry line', 'No compass; accuracy limited by the GPS error over a short baseline.'],
    ['C. Map / satellite image', 'The operator reads the bearing from a map', 'Simple and robust for a demo; manual step.'],
    ['D. Stakes on the ground', 'Mark the entry direction physically and measure it', 'Very controlled; useful for the demo arena.'],
], [0.22, 0.43, 0.35]))
S.append(H2('5.4 Error budget — to state honestly in the report'))
S.append(bl(['A bearing error of 3° moves a point 10 m away about <b>0.5 m sideways</b> (10 m × sin 3°). The error grows with distance.',
             'The Writer’s dead-reckoning drift also grows with distance, so far beacons have less certain GPS positions. In the simulation the final position error was 0.02–0.08 m, but those use <b>simulated</b> sensors and prove nothing about real hardware.',
             'Consumer GPS is typically accurate to several metres (check the datasheet of the chosen module). For the command-post map this may dominate; for the Executor, local beacon-to-beacon guidance stays accurate, so translation matters most for the map and for reporting hazard positions.',
             'Recommended in the report: show the uncertainty on the map and say which parts are measured and which are assumed.']))

# ------------------------------------------------------------------ 6
S += H1('6. Design options')
S.append(tbl([
    ['Level', 'Idea', 'Advantages', 'Limits'],
    ['<b>Simple</b>', 'A laptop runs a Python program (receive, translate, queue, brief). GPS from a USB/phone GPS or fixed test coordinates. The “satellite” link is a Wi-Fi or local-network simulation. Map shown in a browser.', 'Fast; enough for the Phase 1 simulation; easy to test failure cases.', 'Weak as a physical prototype.'],
    ['<b>Intermediate</b>', 'Raspberry Pi gateway with a GPS module at the entrance, a message broker (MQTT) and a web map at the command post; a long-range radio or a cellular link between gateway and command post.', 'Realistic; a strong story for the judges; close to the final prototype.', 'More hardware to build and debug.'],
    ['<b>Ambitious</b>', 'A real satellite modem or long-range link with full store-and-forward.', 'Most impressive.', 'Costly and risky; not needed for Phase 1.'],
], [0.15, 0.42, 0.24, 0.19]))
S.append(Spacer(1, 3))
S.append(P(T('PROPOSED') + ' <b>Recommendation:</b> simulate the <b>simple</b> level for Phase 1, and <b>describe the intermediate level</b> as the hardware plan for the final phase. This is a suggestion; the owner of this area decides. Hardware candidates for the final phase (none chosen): a small computer as gateway, a GPS module, a local link to receive the Writer’s log at the entrance (the UNO Q is believed to have Wi-Fi — ' + T('ASSUMPTION') + ', to verify), a long-range link to the command post, a PC with a browser map, and power for the gateway outdoors.'))

# ------------------------------------------------------------------ 7
S += H1('7. Phase 1 simulation plan')
S.append(P('Goal: a small program that behaves like the area, takes the Writer’s log as input, and shows each role working. Everything below is ' + T('NOT STARTED') + '.'))
S.append(bl(['<b>Four functions</b>, one per role: <font name="DVM">receive(log)</font>, <font name="DVM">translate(log, gps0, bearing)</font>, <font name="DVM">carry(data, link)</font> with a queue, <font name="DVM">brief(data, mission)</font>.',
             '<b>Inputs:</b> the Writer simulation’s <font name="DVM">writer_log.json</font>. The Writer simulation is not fully reliable yet, so a hand-made log in the same format is a good starting point.',
             '<b>Outputs:</b> a GPS-referenced data file (I4), a briefing file (I5), and a simple map picture or web page showing events and path.',
             '<b>Link:</b> a software object that can be switched up and down, to demonstrate store-and-forward.']))
S.append(tbl([
    ['Test', 'Input', 'Expected result', 'Status'],
    ['T1 Normal', 'Valid log', 'GPS file, map and briefing are produced', T('NOT STARTED')],
    ['T2 Link down', 'Valid log; link off, then on', 'Data queued, then delivered when the link returns', T('NOT STARTED')],
    ['T3 No log', 'Writer lost, nothing received', 'Status “no_log”; briefing marked “no inherited data”; the Executor must rely on beacons only', T('NOT STARTED')],
    ['T4 Bad log', 'Truncated or corrupted file', 'Rejected with a clear message; re-upload requested', T('NOT STARTED')],
    ['T5 No GPS fix', 'Valid log; no GPS position', 'Map in the private frame with a visible warning', T('NOT STARTED')],
    ['T6 Duplicate', 'Same log uploaded twice', 'Processed once', T('NOT STARTED')],
], [0.15, 0.25, 0.45, 0.15]))

# ------------------------------------------------------------------ 8
S += H1('8. Failure cases of this area ' + T('DESIGN ONLY'))
S.append(tbl([
    ['What fails', 'Consequence', 'Planned response'],
    ['Link to the command post goes down', 'The map is not updated', 'Store-and-forward queue; resend; show “last update” time'],
    ['The Writer is lost (no log)', 'The area has no data', 'Report “no log”; the Executor is briefed with the mission only and relies on beacons'],
    ['GPS fix missing or poor', 'Positions cannot be put on a real map', 'Show the private frame and a warning; show uncertainty when the fix is poor'],
    ['Log corrupted or incomplete', 'Wrong or missing beacons on the map', 'Validate fields and checksum; reject and ask for a re-upload'],
    ['Wrong building bearing', 'The whole map is rotated', 'Check against known landmarks; display the bearing used so it can be questioned'],
    ['Clock not synchronised', 'Beacon aging is wrong', 'Synchronise from GPS time before entry; log the sync time'],
    ['Briefing not delivered', 'Executor enters without its mission', 'Do not release the Executor until delivery is acknowledged'],
], [0.28, 0.27, 0.45]))

# ------------------------------------------------------------------ 9
S += H1('9. Open decisions')
S.append(P('“Responsible” assumes the four-role split; the real names are unknown. No decision below has been made.', 'small'))
S.append(tbl([
    ['Item', 'Current status', 'Decision needed', 'Responsible'],
    ['Building bearing source', 'Four options in 5.3', 'Choose one for the demo and the final prototype', 'Outside Network owner'],
    ['Who builds the beacon chain', 'Outside Network (BRIEF) in the current design', 'Agree with Beacon and Executor teammates', 'Beacon + Outside Network + Executor'],
    ['Log format (I3)', 'Draft produced by the Writer sim', 'Confirm or change the fields', 'Outside Network owner + Writer owner'],
    ['Briefing format (I5) and delivery method', 'Sketch in 4.3; delivery unknown', 'Fix fields; choose how the Executor receives it', 'Outside Network + Executor'],
    ['Trust / aging thresholds', 'Slide examples 2/15/40 min; AI proposal 5/30 min; not coded', 'Choose values and who applies them', 'Beacon + Executor'],
    ['Who chooses the mission', 'Unknown', 'Human operator at the command post, or an automatic rule', 'Whole team'],
    ['“Live” map', 'Updates only when the Writer’s log arrives', 'Is that acceptable as “live”? Ask the organizers if unsure', 'Whole team (aess@ieee.tn, ras@ieee.tn)'],
    ['Link technology', 'Wireless or satellite allowed; none chosen', 'Choose what is simulated now and what is built later', 'Outside Network owner'],
    ['Clock synchronisation', 'GPS time before entry (assumption)', 'Who sets the clocks and how', 'Outside Network owner'],
    ['What is real in the final prototype', 'Nothing physical yet', 'Decide the hardware list (section 6)', 'Outside Network owner'],
], [0.20, 0.28, 0.32, 0.20]))

# ------------------------------------------------------------------ 10
S += H1('10. What this area must deliver, and next steps')
S.append(tbl([
    ['', 'Task', 'Why'],
    ['☐', 'Confirm the log format (I3) with the Writer owner, and the briefing format (I5) with the Executor teammate', 'Everything else depends on the interfaces'],
    ['☐', 'Decide the building-bearing source and the simulated link', 'Needed for translation and the demo'],
    ['☐', 'Write the four functions and run tests T1–T6 on a sample log', 'Simulation demo (8) and Outside network area (5)'],
    ['☐', 'Write the frame-translation note with the worked example and the error budget', 'Frame translation (5)'],
    ['☐', 'Draw the final architecture and data-flow diagrams of the area', 'Technical solution diagrams (5)'],
    ['☐', 'Write the failure cases (section 8) and record T2–T6 results', 'Failure cases (3)'],
    ['☐', 'List the final-phase hardware, a timeline to 01/12/2026, and the risks', 'Implementation plan (3); physical prototype (15) later'],
    ['☐', 'Write the “Outside Network and Executor” part of the 6-page report (about 0.7 pages shared with the Executor)', 'Technical report (2)'],
], [0.04, 0.62, 0.34]))
S.append(Spacer(1, 4))
S.append(P('<b>Not yet done by anyone:</b> opening the two links inside the official cahier des charges — the “System Architecture Diagram” resource (a Google Drive file) and the submission form. The architecture diagram resource may show what the organizers expect for this area, so open it first. Links are listed in section 2.2 of the handover PDF.'))
doc.build(S)
print('built')
