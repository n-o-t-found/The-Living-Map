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
    c.drawString(1.7 * cm, 1.1 * cm, 'The Living Map — Phase 1 Project Status & Technical Handover  |  Checkpoint 03/10/2026')
    c.drawRightString(A4[0] - 1.7 * cm, 1.1 * cm, f'Page {d.page}')
    c.setStrokeColor(GRID); c.line(1.7 * cm, 1.45 * cm, A4[0] - 1.7 * cm, 1.45 * cm)
    c.restoreState()

doc = BaseDocTemplate('/home/claude/handover/The_Living_Map_Phase1_Status_and_Handover.pdf', pagesize=A4,
                      leftMargin=1.7 * cm, rightMargin=1.7 * cm, topMargin=1.5 * cm, bottomMargin=1.9 * cm,
                      title='The Living Map — Phase 1 Project Status & Technical Handover', author='Project co-pilot (AI) for the TSYP14 team')
doc.addPageTemplates([PageTemplate(id='p', frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='f')], onPage=footer)])
S = []

# ===================================================================== COVER BLOCK
S += [Spacer(1, 4), P('The Living Map — Phase 1 Project Status &amp; Technical Handover', 'title'),
      P('TSYP14 Technical Challenge · IEEE RAS × IEEE AESS, Tunisia Section Chapters', 'sub'),
      P('Checkpoint written on <b>03/10/2026</b> · Official Phase 1 submission deadline: <b>05/10/2026</b>', 'sub'), Spacer(1, 6)]
S.append(tbl([
    ['Purpose', 'Let a new reader (the user) and a new AI agent understand the whole project at once, without losing the work already done.'],
    ['Primary sources', 'The two official documents (cahier des charges, 3 pages; presentation, 8 slides) and the work done so far with the AI co-pilot. Nothing in this document comes from outside these sources, except hardware facts that were looked up on the web and are marked as such.'],
    ['Project owner / role', 'The user is new to the project and is building the <b>Writer</b> subsystem. The split of the team into four roles (Writer, Beacon, Outside Network, Executor) was proposed by the AI; the names of the other three teammates are not known to the AI.'],
    ['Companion file', '<b>writer_sim_snapshot_2026-10-03.zip</b> — the Python simulation code exactly as it is today (work in progress, with known bugs, see section 6).'],
], [0.2, 0.8], header=False))
S.append(Spacer(1, 6))
S.append(box([P('<b>The project in 8 lines</b>', 'box'), bl([
    'The challenge asks for a <b>two-robot system</b> (Writer + Executor) and an <b>Outside Network Area</b> that together give an unmapped, GPS-denied space a memory, stored in radio beacons.',
    'The challenge is understood and a concept is designed (section 3). The Writer hardware has been chosen by the user (section 4).',
    'A <b>Python simulation of the Writer</b> exists (section 5). It works in many normal runs but is <b>not yet reliable</b>: some runs skip a room, show a wrong “stuck” event, or wander too long (section 6).',
    'Only the Writer is simulated. <b>Beacon radio, Outside Network, frame translation, Executor and the command-post live map are designed only, not implemented.</b>',
    'No physical hardware has been tested. Nothing is physically validated.',
    'The failure scenarios exist as command-line options in the code but <b>have never been run</b> (section 9).',
    'Interfaces with the teammates (beacon format, log format, direction meaning) are <b>drafts, not agreed</b> (sections 7 and 8).',
    'Nothing is packaged for submission yet: no GitHub repository, no report, no final diagrams, no clean demo output (sections 10–12).'], 'box')]))
S.append(Spacer(1, 6))
S.append(P('<b>Labels used everywhere in this document</b>'))
S.append(tbl([
    [T('CONFIRMED'), 'Written in the official documents, or stated explicitly by the user.'],
    [T('PROPOSED'), 'Suggested by the AI during the project. The user has not explicitly approved it.'],
    [T('ASSUMPTION'), 'A value or fact chosen to make the design or the simulation work. Must be validated (many only on real hardware).'],
    [T('OPEN'), 'No decision yet.'],
    [T('IMPLEMENTED IN SIM') + ' / ' + T('DESIGN ONLY'), 'Exists as code in the simulation / exists only as an idea or text.'],
    [T('TESTED') + ' / ' + T('UNTESTED'), 'The code path has / has not actually been run and observed.'],
    [T('INTERPRETATION'), 'The AI’s reading of the official documents (not written there).'],
], [0.26, 0.74], header=False))

# ===================================================================== 1 CHALLENGE
S += H1('1. Challenge overview')
S.append(H2('1.1 Name and organizers'))
S.append(P('<b>“The Living Map: Spatial Memory for Emergency Robots”</b> — TSYP14 Technical Challenge, organized by <b>IEEE RAS</b> (Robotics &amp; Automation Society) and <b>IEEE AESS</b> (Aerospace and Electronic Systems Society), Tunisia Section Chapters. ' + T('CONFIRMED')))
S.append(H2('1.2 The problem, in simple words'))
S.append(P('In disasters (collapsed buildings, mines, fires, contaminated zones) robots may have to work where <b>there is no GPS and no communication network</b>. They must explore, sense dangers, find victims, and report back despite poor connectivity. The key weakness stated by the organizers: <b>when a robot fails, leaves, or loses power, everything it learned can disappear with it.</b> The challenge wants a system that can <b>Sense → Communicate → Preserve critical information → Enable mission continuity.</b>'))
S.append(H2('1.3 The “Living Map” idea'))
S.append(P('A first robot enters an unmapped space alone and <b>leaves its knowledge behind in small radio beacons</b>. A second robot, entering later, <b>reads those beacons and continues the mission without starting from zero</b>. The space itself carries the memory — it does not depend on the first robot surviving. (The official scope text says this in other words.) ' + T('CONFIRMED')))
S.append(H2('1.4 What must be built'))
S.append(tbl([
    ['Part', 'Role (according to the official documents)'],
    ['<b>Writer robot</b>', 'Enters the GPS-denied space first, alone, with no map and no operator. Explores autonomously, senses events (at least 2 types, e.g. hazard, victim, hole, gas, junction, exit), decides in real time which findings are worth recording, deposits a beacon where each event is, then returns to the entrance.'],
    ['<b>Beacons</b>', 'Tiny ground transmitters that just broadcast a compact message saying <i>what</i> was found, <i>where to go</i> and <i>when</i> it was written. Messages must age (see below).'],
    ['<b>Outside Network Area</b>', 'The bridge between inside and outside. Inside: no GPS, no network. Outside: GPS, satellite time and communication exist. Defined by four roles (teams design the inside of it): <b>RECEIVE</b> what the Writer produced; <b>TRANSLATE</b> the robot’s private coordinates into real-world GPS; <b>CARRY</b> the information to a distant command post (wireless or satellite); <b>BRIEF</b> the Executor before it enters.'],
    ['<b>Executor robot</b>', 'Enters later with a mission (extinguish, extract, seal or retrieve — tied to the chosen scenario). Briefed before entry, so no blind search. Navigates using the beacons as its map, no GPS. “Trusts by age”: fresh beacons guide it, stale ones it verifies with its own sensors.'],
    ['<b>Command post</b>', 'Distant location that receives the information and displays a <b>live map</b>.'],
], [0.2, 0.8]))
S.append(Spacer(1, 4))
S.append(P('<b>Beacon aging (from the slides):</b> the same beacon is read differently as time passes. Slide examples: <i>fresh (2 min)</i> “trust as measured”; <i>aging (15 min)</i> “verify before crossing”; <i>stale (40 min)</i> “rely on your own senses”; <i>suspect (contradicted)</i> “live sensor disagrees: flag it, discard”. A beacon message has six items: identifier, WHAT, WHERE (direction to take from here), distance (metres to next beacon / target), WHEN (timestamp, which makes it age), version (lets a later agent overwrite it). ' + T('CONFIRMED')))
S.append(H2('1.5 The required communication chain'))
S.append(P('<b>Writer explores → events detected &amp; beacons deposited → Outside Network receives &amp; translates data → wireless / satellite communication → command post → Executor receives mission → Executor enters &amp; navigates using beacons.</b>'))
S.append(H2('1.6 Mandatory rules for every team'))
S.append(bl(['Complete registration before the deadline; choose <b>one</b> environment: Urban Search &amp; Rescue, Fire / Hazardous Building, Mines / Tunnels, or Nuclear / Contaminated Zone.',
             'Detect <b>at least 2 event types</b>; use <b>at least 2 physical robots</b> (Writer and Executor).',
             'Implement a <b>functional Outside Network Area</b>; <b>all</b> inside↔outside communication passes through it.',
             '<b>No direct link</b> between the robots and the command post.',
             'Prepare and demonstrate <b>failure cases</b> (slide 6).']))

# ===================================================================== 2 PHASE 1
S += H1('2. Phase 1 requirements')
S.append(H2('2.1 Required deliverables (cahier des charges p.2 and slide 8)'))
S.append(tbl([
    ['#', 'Deliverable', 'Official detail', 'Points shown in the scoring'],
    ['1', 'GitHub Repository', '—', '4'],
    ['2', 'Simulation Demo', 'Format (video / live) not specified', '8'],
    ['3', 'Short Technical Report', '<b>maximum 6 pages</b>', '2'],
    ['4', 'Implementation Plan', '—', '3'],
    ['5', 'Failure Cases', '—', '3'],
    ['6', 'Technical Solution &amp; Architecture', 'Scored through “Technical solution diagrams” and the 7 technical areas below', '5 (diagrams) + 7 areas'],
], [0.05, 0.27, 0.46, 0.22]))
S.append(Spacer(1, 4))
S.append(P('<b>The solution must address 7 areas</b> (each worth 5 points in the scoring list): Writer robot autonomy · Event detection &amp; beacon deposition · Beacon message &amp; signal design · Frame translation · Outside network architecture · Executor robot · System architecture &amp; data flow. A further criterion, <b>Innovation, Originality &amp; Creativity</b>, is worth 5 points.'))
S.append(H2('2.2 Deadlines and logistics (cahier des charges p.3, quoted)'))
S.append(tbl([
    ['Challenge Infosession', '14/09/2026'],
    ['<b>Phase 1 Submission Deadline</b>', '<b>05/10/2026</b>  (the document gives no time of day)'],
    ['Final Submission Deadline', '01/12/2026'],
    ['Prizes', '2 winning teams: 1st place 100 USD + certificate; 2nd place 50 USD + certificate'],
    ['Contact', 'aess@ieee.tn or ras@ieee.tn (“for any inquiries or clarifications”)'],
    ['Links inside the PDF (<b>not yet opened</b>)', 'Page 2, “System Architecture Diagram” button → https://drive.google.com/file/d/1qZa4lAYTphZSt2vkvdlQwV6-f3tDO-ov/view?usp=sharing<br/>Page 3, “Submit your project…” text → a Google Forms link (probably the submission form; to be verified): https://docs.google.com/forms/d/e/1FAIpQLSdq93a-_h-U7WJBD-WEemnmmmm0XX1aCt-I64BGmpNK2EXqtA/viewform?usp=dialog'],
], [0.3, 0.7], header=False))
S.append(Spacer(1, 3))
S.append(P(T('OPEN') + ' <b>Check the deadline.</b> The user mentioned at the start that Phase 1 was “due today” (03/10/2026); the official document says 05/10/2026. Confirm the real date, time and submission method (the Google Forms link above is the likely route).'))
S.append(H2('2.3 Full scoring grid (as printed — note the inconsistency)'))
S.append(tbl([
    ['Block', 'Items and points (as printed)'],
    ['Initial Phase (heading says <b>45 pts</b>)', 'GitHub 4 · Simulation demo 8 · Short technical report 2 · Innovation, originality &amp; creativity 5 · Implementation plan 3 · Failure cases 3 = <b>25</b>'],
    ['Technical aspects of the solution', 'Writer autonomy 5 · Event detection &amp; beacon deposition 5 · Beacon message &amp; signal design 5 · Frame translation 5 · Outside network area 5 · Executor robot 5 · Technical solution diagrams 5 = <b>35</b>'],
    ['Final Phase (50 pts)', 'Pitching &amp; Q&amp;A 8 · Quality of proposed solutions 8 · Technologies used 5 · <b>Physical prototype 15</b> · Project architecture 5 · User manual 4 · GitHub repository 5'],
    ['Bonus (5 pts)', '≥ 2 IEEE AESS members in the team: 2 · ≥ 2 RAS members: 2 · ≥ 1 YP member with both RAS and AESS memberships: 1'],
    ['Pitch (final phase)', 'English, 5 min pitch + 2 min Q&amp;A. Finalists provide: pitching &amp; Q&amp;A, complete physical prototype, proposed solution, technologies used, project architecture, user manual, GitHub repository.'],
], [0.28, 0.72]))
S.append(P(T('OPEN') + ' <b>Scoring inconsistency:</b> the Initial Phase is labelled 45 points, but the items listed under it and under “Technical aspects” add up to 60 (25 + 35). The total of the whole grid is 100 only if the Initial Phase counts as 45. Ask the organizers; until then treat <b>every</b> listed item as important. Not specified anywhere: submission platform/format, which simulator to use, whether the demo is a video, the report layout.', 'small'))

# ===================================================================== 3 SOLUTION
S += H1('3. Our proposed solution')
S.append(P('Everything in this section is ' + T('PROPOSED') + ' unless marked otherwise. The AI compared three solution levels (S1 simple “breadcrumb”, S2 “aging memory map”, S3 “mesh memory” with beacon-to-beacon relay and extra radio) and <b>recommended designing at S2 level while keeping the Phase 1 simulation as simple as S1</b>. The user then proceeded on that basis without a formal vote.'))
S.append(tbl([
    ['Item', 'Current concept', 'Status'],
    ['Environment', '<b>Fire / Hazardous Building</b>. Reason: its events map to cheap sensors (heat, missing floor, geometry) and the Executor mission “extinguish” can be demonstrated safely with proxies. Alternative discussed: Urban Search &amp; Rescue.', T('PROPOSED') + ' — not formally confirmed'],
    ['Writer robot', 'Wheeled robot, Arduino UNO Q + RPLIDAR; explores by right-hand wall following; detects hazard (heat), junction and hole; drops beacons by servo; returns to the entrance; uploads a log (section 4).', 'Hardware ' + T('CONFIRMED') + ' by user; logic ' + T('IMPLEMENTED IN SIM')],
    ['Beacons', 'Small RF broadcasters left on the floor, each carrying a compact message (what / direction / distance / time / version). The Writer writes the message by radio at drop time into a blank beacon with a unique ID (“D3”).', T('PROPOSED') + ' · ' + T('OPEN') + ' (D3)'],
    ['Outside Network Area', 'Raspberry Pi gateway with GPS near the entrance + a server/MQTT + a web live map at the command post. Satellite link <i>simulated</i> in Phase 1. Roles: Receive, Translate, Carry, Brief; store-and-forward queue if the link drops.', T('PROPOSED') + ' ' + T('DESIGN ONLY')],
    ['Executor robot', 'State flow BRIEFED → ENTER → LISTEN → TRUST-CHECK → FOLLOW → ACT → EXIT. Trust rule by beacon age: fresh = follow; aging = slow down and verify; stale = use own sensors; contradicted = flag and discard. Missing beacon: fall back to last heading/distance, then local search. Demo mission: “reach the hotspot and extinguish” (simulated action).', T('PROPOSED') + ' ' + T('DESIGN ONLY')],
], [0.17, 0.60, 0.23]))
S.append(Spacer(1, 4))
S.append(H2('3.1 How information survives if the Writer cannot continue'))
S.append(P('Knowledge is stored <b>twice</b>. (1) <b>In the beacons</b>, which stay on the ground with their messages even if the Writer dies. (2) <b>In the Writer’s log</b>, which reaches the Outside Network only if the Writer comes back to the entrance. If the Writer is lost, the beacons remain as the only record; the Outside Network then knows nothing from the log, and the Executor can still read the beacons it meets. The simulation has an option to kill the Writer at a chosen time to show exactly this (' + T('UNTESTED') + ').'))
S.append(H2('3.2 How the Executor uses inherited information'))
S.append(P('Before entry, the Outside Network briefs the Executor (mission, ordered beacon chain, clock synchronisation, trust rules — ' + T('PROPOSED') + '). Inside, the Executor listens to beacons, judges each one by its age and by its own sensors, and follows the chain to the target. It enters through the same entrance, so it can share the Writer’s <b>private frame</b> (origin = entrance, +x = direction of entry). How the Executor keeps its heading consistent is ' + T('OPEN') + '.'))
S.append(H2('3.3 System architecture'))
S.append(img('/home/claude/handover/fig/architecture.png', 0.97))
S.append(P('Figure 1 — Draft system architecture. Green = exists in the Python simulation; grey = designed only. Interfaces: I1 Writer→Beacon (message to write + drop); I2 Beacon→Executor (RF broadcast); I3 Writer→Outside Network (log, when the Writer returns); I4 Outside Network→Command post (GPS-referenced data for the live map); I5 Outside Network→Executor (briefing). All five are ' + T('PROPOSED') + ', none is agreed with the teammates.', 'cap'))
S.append(H2('3.4 Frame translation (private coordinates → GPS)'))
S.append(P(T('PROPOSED') + ' ' + T('DESIGN ONLY') + ' The Writer works in a <b>private frame</b>: origin at the entrance, x axis = direction of entry, y = left. The Outside Network has a GPS fix of the entrance and needs the building’s orientation (e.g. a compass heading taken outside — how to get it is not decided). It rotates each (x, y) by that heading to get East/North metres (E, N), then <font name="DVM">lat = lat0 + N / 111 320</font> and <font name="DVM">lon = lon0 + E / (111 320 · cos lat0)</font>. Error budget: dead-reckoning drift grows with distance, so far beacons have less certain GPS positions, while beacon-to-beacon guidance stays accurate locally. ' + T('ASSUMPTION') + ' Writer and Executor clocks are synchronised to GPS time before entry (needed for beacon timestamps and aging).'))

# ===================================================================== 4 WRITER
S += H1('4. Writer subsystem')
S.append(H2('4.1 Hardware'))
S.append(tbl([
    ['Component', 'Role in the Writer', 'Status'],
    ['<b>Arduino “Q”</b> (understood as <b>Arduino UNO Q</b>)', 'Main computer. Per Arduino documentation (web search, not verified on hardware): a Linux processor (Qualcomm QRB2210) <i>and</i> a real-time STM32U585 microcontroller on one board, linked by an RPC library called “Bridge”; 7–24 V DC input; USB peripherals need a powered USB-C dongle; processor I/O is 1.8 V. Proposed split: Linux side = “brain” (LiDAR, localization correction, exploration, event decisions, beacon policy, log, upload); microcontroller side = “reflexes” (motor PWM, encoders, IMU, servo, e-stop, watchdog).', 'Board: ' + T('CONFIRMED') + ' by user (exact model ' + T('ASSUMPTION') + '); split: ' + T('PROPOSED')],
    ['<b>RPLIDAR</b>', 'Navigation: obstacle distance, wall following, junction detection, heading correction. Model not given by the user (A1-class assumed). Its USB adapter probably also needs the powered USB-C hub — <b>test first</b>.', T('CONFIRMED') + ' (model ' + T('ASSUMPTION') + ')'],
    ['<b>Modulino Movement</b>', 'Per documentation: LSM6DSOX 6-axis IMU (3-axis gyroscope + 3-axis accelerometer, <i>no compass</i>). Use: heading from integrating the gyro (with bias calibration at start), tip-over detection, jolt hint. Raw sensor: the software integrates the gyro itself. Do <b>not</b> use the accelerometer for distance.', T('CONFIRMED') + ' (user has it)'],
    ['<b>Modulino Distance</b>', 'Per documentation: VL53L4CD time-of-flight sensor, 0–1200 mm, 3.3 V, Qwiic/I2C. Proposed role: <b>floor-facing hole detector</b> (gives the HOLE event). Alternatives: drop confirmation, or close-range front safety. One sensor = one role.', 'Owned: ' + T('CONFIRMED') + '; role: ' + T('PROPOSED') + ' ' + T('OPEN')],
    ['<b>Servo + beacon magazine</b>', 'Drops one beacon at a time. Concept: tube/stack magazine with a servo gate, plus an IR break-beam under the chute to confirm that a beacon fell. Servo model unknown; magazine not designed.', 'Servo: ' + T('CONFIRMED') + '; mechanism: ' + T('PROPOSED')],
    ['Not yet chosen (unknown whether owned)', 'Drive base (two driven wheels + caster suggested; 4-wheel skid steer gives poor odometry), wheel encoders, motor driver, a thermal sensor for the heat hazard (MLX90640 or AMG8833 suggested; the Modulino Thermo only measures air temperature and is not suitable), beacon write radio, battery + separate 5 V rail for servo/LiDAR, e-stop button.', T('PROPOSED') + ' ' + T('OPEN')],
    ['Simulated in code', 'LiDAR (120 rays, 360°), thermal sensor (hottest temperature + bearing), floor sensor (mm), encoders + gyro (dead reckoning with noise and bias), battery level, tilt (always 0 in the sim).', T('IMPLEMENTED IN SIM')],
], [0.19, 0.58, 0.23]))
S.append(H2('4.2 Responsibilities'))
S.append(bl(['Explore a GPS-denied, unmapped space alone and autonomously.', 'Know its own position well enough (dead reckoning + wall-based heading correction).',
             'Detect events, decide which are worth a beacon, and drop beacons within a limited stock.', 'Record everything in a log, return to the entrance, and upload the log to the Outside Network.',
             'Survive faults safely (stuck, drop failure, low battery, tip-over).']))
S.append(H2('4.3 Autonomous exploration and navigation strategy ' + T('IMPLEMENTED IN SIM')))
S.append(bl(['<b>Right-hand wall following</b> with LiDAR: keep ~0.40 m from the right wall; turn left in place if blocked ahead (<0.5 m) or if the floor is missing; curve right when the right wall disappears (opening). The controller uses the lateral error plus the wall angle (from a line fit of right-side LiDAR points, used only if the fit is good) and slows down in turns.',
             '<b>Localization:</b> dead reckoning (encoders for distance, gyro for heading, gyro bias calibrated during 3 s standing still) plus a <b>heading correction from walls</b>: when a straight wall is seen, the heading is nudged towards the nearest multiple of 90°. ' + T('ASSUMPTION') + ' This assumes walls are parallel to the x/y axes (see section 6).',
             '<b>Breadcrumb trail with loop erasure:</b> positions are stored every 0.25 m; if the robot returns to an earlier place, the loop in between is deleted, so the trail is always the shortest known way back (dead ends leave no trace).',
             'The right-hand rule covers the whole building only if the building has no islands/loops (the simulated building is tree-like) ' + T('ASSUMPTION') + '.']))
S.append(H2('4.4 State machine ' + T('IMPLEMENTED IN SIM')))
S.append(img('/home/claude/handover/fig/state_machine.png', 0.92))
S.append(P('Figure 2 — Writer state machine as coded in writer.py. EXPLORE does the wall following, event detection and beacon decision. RETURN is used for early returns; when the right-hand tour ends back at the start, the robot goes directly to UPLOAD.', 'cap'))
S.append(H2('4.5 Event detection ' + T('IMPLEMENTED IN SIM') + ' · event set ' + T('PROPOSED')))
S.append(P('The challenge needs <b>at least 2 event types</b>; the current design has three, all listed as valid examples in slide 1 (hazard, hole, junction). The event set has not been formally confirmed by the user.'))
S.append(tbl([
    ['Event', 'How it is detected', 'Notes'],
    ['<b>HAZARD</b> (heat)', 'Thermal reading ≥ 45 °C. The Writer follows the reading up to its peak and emits <b>one</b> event. Severity = (peak − 45) / (85 − 45), clipped to 0..1. Range to the source is estimated from the peak with an assumed linear model (approximate).', 'Needs a real thermal sensor (not yet chosen). Demo with a safe heat source such as a heat pad — never real fire.'],
    ['<b>JUNCTION</b>', 'From the LiDAR: at least 3 of 4 directions (front, left, right, back) are “open” for 2 consecutive scans. Open = free range &gt; 1.5 m (right side: &gt; 1.0 m, the same test the wall follower uses). Records a 4-bit <i>exits</i> mask.', 'Needs no extra hardware. In an early run a junction fired at a corridor-to-room doorway (the merge radius was widened afterwards; <b>not re-checked</b>). False junctions inside rooms have not been examined.'],
    ['<b>HOLE</b> (missing floor)', 'The down-facing distance sensor, 0.30 m ahead, reads &gt; 150 mm instead of ~60 mm. The robot stops and turns away (it never drives into it).', 'Uses the Modulino Distance in the proposed role. A hole that spans the corridor acts as a blocked path.'],
], [0.17, 0.52, 0.31]))
S.append(H2('4.6 Beacon decision policy ' + T('IMPLEMENTED IN SIM') + ' ' + T('ASSUMPTION')))
S.append(P('Each candidate event gets a <b>score</b>; it is dropped only if the score is above a <b>threshold that rises as the magazine empties</b>, so the last beacons are kept for the most important events.'))
S.append(bl(['Score: HAZARD = 0.6 + 0.4 × severity · HOLE = 0.9 · JUNCTION = 0.5 · WAYPOINT (relay beacon when the gap to the last beacon exceeds the radio spacing) = 0.3, rising up to 0.7 as the gap doubles.',
             'Threshold = 0.2 + 0.7 × (1 − stock / capacity). With capacity 8: 0.29 with 7 left, 0.55 with 4 left, 0.81 with 1 left.',
             'No new beacon of the same type within a “novelty radius” of an existing one (HAZARD 2.0 m, HOLE 1.5 m, JUNCTION 2.0 m, WAYPOINT 2.0 m); no beacon within 0.6 m of any other (events merge).',
             'Every decision (drop / skip / fail) is logged with its reason, so the behaviour can be explained in the report. Trade-off visible here: when stock is low, chain continuity (relay beacons) can lose against event priority.']))
S.append(H2('4.7 Beacon deposition ' + T('IMPLEMENTED IN SIM') + ' (mechanism ' + T('DESIGN ONLY') + ')'))
S.append(P('On an accepted event the robot stops and builds the message (id, type, dir_deg, dist_m, t, ver [, exits]). The HAL call <font name="DVM">drop_beacon(message)</font> stands for: write the message into the beacon by radio → servo releases it → break-beam confirms the fall. The robot waits 1 s; if the drop failed it retries once; if it fails again it logs “fail” and the beacon stays in the magazine. In the simulation the beacon lands at the robot’s true position. No radio propagation is modelled.'))
S.append(H2('4.8 Logging, return to the entrance, upload ' + T('IMPLEMENTED IN SIM')))
S.append(bl(['<b>Log:</b> path (x, y, heading, time every 0.5 s), beacons, all decisions with reasons, statistics (path length, heading corrections, drop failures, stock left, battery, stuck events).',
             '<b>Return triggers:</b> magazine empty · battery ≤ 30 % · time limit 900 s · stuck twice · “exploration complete” (back near the start after having gone &gt; 3 m away).',
             '<b>Return behaviour:</b> follow the loop-erased breadcrumb trail backwards (pure pursuit to a point ≥ 0.6 m ahead) with a front-obstacle and no-floor safety.',
             '<b>Upload:</b> the log is generated and sent through the HAL; in the sim it only succeeds if the robot is within 1.5 m of the entrance; up to 3 tries, otherwise the status is “upload_failed” and the log stays on board.']))
S.append(H2('4.9 Confirmed versus assumed (Writer)'))
S.append(tbl([
    ['Confirmed (official documents / user)', 'Assumed or proposed (to validate)'],
    ['Challenge rules and the Writer’s role · user will use UNO Q (“Q”), RPLIDAR, servo dropper · user owns Modulino Movement and Modulino Distance',
     'Exact board model and LiDAR model · environment · event set · Modulino Distance as hole detector · thermal sensor choice · beacon write method · drive base, encoders, motors, power · all numbers in section 6.3 · wall-based heading correction · tree-like building · Brain/Reflex software split on the UNO Q'],
], [0.4, 0.6]))

# ===================================================================== 5 SIMULATION
S += H1('5. Current simulation')
S.append(P('A Python simulation of the Writer only. The Writer’s decision code talks to the world <b>only through a Hardware Abstraction Layer (HAL)</b>, so the same logic could later run on the real robot by writing a “real” HAL. ' + T('IMPLEMENTED IN SIM')))
S.append(tbl([
    ['File', 'Role'],
    ['<font name="DVM">hal.py</font>', 'The contract: abstract class <i>WriterHAL</i> with the functions the Writer may use — time (now, step), drive(v, w), get_pose, correct_heading, measured_speed, calibrate_imu, tilt_deg, battery, scan (LiDAR), read_thermal, floor_distance_mm, drop_beacon, upload_log. Documents the conventions (private frame, angles, units) and which UNO Q side would serve each call in Phase 2.'],
    ['<font name="DVM">sim_world.py</font>', '<i>World</i>: a 14 m × 8 m tree-like building on a 0.25 m grid — main corridor (1 m wide), four branches A–D, three rooms R1–R3, two heat sources, one collapsed-floor hole, optional low debris (invisible to the LiDAR). <i>SimHAL</i>: the simulated robot and sensors with imperfections (gyro bias 0.3°/s, encoder scale error 1.5 %, LiDAR noise, wheel slip); the Writer sees only its own <i>estimated</i> pose, never the true one.'],
    ['<font name="DVM">writer.py</font>', 'The Writer’s brain: <i>WriterConfig</i> (all tunable numbers), <i>State</i> (the state machine), <i>Writer</i> (wall following, heading correction, breadcrumb trail, event detection, beacon policy, drop sequence, return, upload, log export).'],
    ['<font name="DVM">run_demo.py</font>', 'Command-line runner. Options: <font name="DVM">--seed --stock --drop-fail-prob --battery-drain --kill-at --debris --out --gif</font>. Prints a result summary and decisions, writes <i>writer_log.json</i> (if uploaded), <i>beacons_on_ground.json</i> and a PNG (and optionally a GIF).'],
    ['<font name="DVM">viz.py</font>', 'Plots: map, true path, the Writer’s own estimate, beacons by type; optional animated GIF. (The PNG output was produced in earlier runs; the GIF function has <b>never been run</b>.)'],
    ['<font name="DVM">test_robust.py</font>', 'Helper created during debugging: runs many seeds and prints a one-line verdict each. Its “clean run” criterion is lenient (it does not check coverage of the building).'],
], [0.2, 0.8]))
S.append(Spacer(1, 3))
S.append(P('<b>Run:</b> <font name="DVM">python run_demo.py --out out</font> (Python 3 with numpy, matplotlib and Pillow; versions were not recorded). The folders <font name="DVM">out_default</font>, <font name="DVM">out_s3</font>, <font name="DVM">out_s10</font> in the working directory are <b>stale intermediate outputs and must not be used as results</b>; they are not in the snapshot.'))
S.append(H2('5.1 What the simulation currently demonstrates (in normal runs)'))
S.append(bl(['The Writer explores the simulated building autonomously, using only noisy LiDAR, thermal, floor, encoder and gyro data.',
             'It detects HAZARD, JUNCTION and HOLE events, scores them, and decides whether to deposit a beacon according to the policy.',
             'It simulates beacon deposition (beacons are placed on the ground with their messages) and records every decision with a reason.',
             'It generates a log (I3 draft), returns to the entrance, and exports/uploads the log.',
             'Typical normal run in the best seeds: about 57 m of path, about 250 s of simulated time, 5 beacons (2 HAZARD, about 2 JUNCTION, 1 HOLE). Earlier runs showed an end-of-run position error of 0.02–0.08 m between the true and estimated position.']))
S.append(P(T('ASSUMPTION') + ' <b>No physical validation of any kind has been done.</b> All numbers come from a simulation with invented sensor models.'))
S.append(img('/home/claude/handover/fig/building.png', 0.78))
S.append(P('Figure 3 — Layout of the simulated building (static drawing, no run results). The robot starts at the entrance heading east.', 'cap'))

# ===================================================================== 6 LIMITS
S += H1('6. Simulation limitations and debugging status')
S.append(box([P('<b>Read this section carefully.</b> The simulation is <b>not yet fully reliable</b>. It works in many runs but is not consistent enough to be presented as a clean demo. The remaining problems have <b>not been diagnosed</b>.', 'box')], bg='#fdecea', border='#b00020'))
S.append(Spacer(1, 4))
S.append(H2('6.1 What the multi-seed tests found ' + T('KNOWN BUG')))
S.append(P('Normal scenario only (no failure options). A first check on seeds 0–11 found that all 12 runs ended “returned” with HAZARD, JUNCTION and HOLE beacons — but that check does not look at coverage. A second check on seeds 0–13 compared the true path to five zones (rooms R1, R2, R3, the hole corridor, the east end of the main corridor):'))
S.append(tbl([
    ['Observation', 'Seeds', 'Comment'],
    ['<b>A whole room was skipped</b>', 'seed 3 (room R1, only 1 hazard found); seed 10 (room R3)', 'Real problem; the right-hand tour did not cover the building.'],
    ['<b>Wrong “stuck” event</b> in a world <i>without</i> debris', 'seed 10 (1 stuck event)', 'Real problem; the robot was blocked by something the controller should have avoided (probably a wall collision).'],
    ['<b>Path much longer than normal</b>', 'seed 1: 110.0 m, 479 s · seed 9: 81.3 m, 349 s (normal ≈ 46–58 m, ≈ 210–250 s)', 'Probably re-circling or wandering; cause unknown.'],
    ['East end “missed”', 'seeds 0 and 7', 'Probably a test artefact (the test zone x ≥ 12.8 m is tighter than the robot’s stop distance before the wall). Not verified.'],
    ['Possible duplicate hazard beacon', 'seed 4 (3 HAZARD beacons for 2 heat sources)', 'Not examined; may be a split detection of one hot spot.'],
    ['Seeds without any flagged problem', '2, 4 (see above), 5, 6, 8, 11, 12, 13', 'Most runs are fine, but the system is chaotic: small noise changes can change the whole trajectory.'],
], [0.3, 0.33, 0.37]))
S.append(Spacer(1, 3))
S.append(P(T('KNOWN BUG') + ' <b>The right-hand exploration behaviour has a bug that is being investigated.</b> The plots for seeds 3 and 10 were generated but <b>not yet inspected</b>; that was the immediate next step when development was stopped. Next-agent tip: instrument the Writer from the inside (a logging hook in writer.py). Calling <font name="DVM">hal.scan()</font> from a debug script consumes the random-number stream and changes the trajectory (this misled one debugging session).'))
S.append(H2('6.2 Bugs already found and fixed in this session (effect not individually re-verified)'))
S.append(bl(['Junctions on the <b>right</b> side were missed because the robot turns into them before they are confirmed → junction test for the right side now uses the same threshold as the wall follower; confirmation shortened to 2 scans; junction merge radius widened to 2.0 m.',
             'The LiDAR line-fit was polluted near openings and made the robot steer early into branches → the fit is now used for control only if it is good (residual &lt; 0.05 m, length ≥ 0.7 m).',
             'The controller ignored wall angles above 45°, which caused a wrong left turn (and a U-turn back to the entrance) when leaving branch A → large angles are accepted (clipped), the robot slows in turns, gains retuned (kd 1.2, kphi 2.0).']))
S.append(H2('6.3 Simplifications and assumptions ' + T('ASSUMPTION')))
S.append(bl(['<b>Heading correction assumes walls are aligned with the x/y axes</b> (Manhattan-world). It stands in for real LiDAR scan matching and would be wrong in caves, mines with curved tunnels, or rotated buildings. The report must say so.',
             'The building is tree-like (no loops/islands) so the right-hand rule can cover it; a building with loops would break this.',
             'No radio model: beacon range, reception, interference and aging are <b>not simulated</b>. The beacon spacing is only a policy number.',
             'Not simulated at all: Outside Network, frame translation, Executor, command-post live map, trust-by-age behaviour. Beacon aging is not implemented in the Writer code (it belongs to the Beacon/Executor side).',
             'The sensors are simplistic (e.g. thermal field of view ±70° with linear falloff; floor sensor 60/240 mm). Tilt is always 0, so the tip-over safety can never trigger in the sim.']))
S.append(P('<b>Parameters that are NOT validated</b> (all ' + T('ASSUMPTION') + '; most can only be validated on real hardware):', 'body'))
S.append(tbl([
    ['Group', 'Parameter = value (as in the code)'],
    ['Motion', 'cruise speed 0.30 m/s · wall distance 0.40 m · front stop 0.50 m · “wall lost” threshold 1.0 m · gains kd 1.2, kphi 2.0 · turn rate 1.0 rad/s · gyro calibration 3 s'],
    ['Sensors / events', 'heat threshold 45 °C · severity reference 85 °C · assumed source temperature for range 80 °C · hole threshold 150 mm · floor look-ahead 0.30 m · “open direction” 1.5 m · junction confirmation 2 scans'],
    ['Beacon policy', 'magazine capacity 8 (the real number of beacons is unknown) · <b>radio spacing 3.5 m</b> (must be measured) · min gap 0.6 m · novelty radii 2.0/1.5/2.0/2.0 m · scores 0.6+0.4·sev / 0.9 / 0.5 / 0.3→0.7 · threshold 0.2+0.7·(1−stock/capacity) · drop wait 1 s · 2 attempts · confidence = max(0.2, 1 − path/200 m) (heuristic)'],
    ['Return / safety', 'battery reserve 30 % · time limit 900 s · loop-erase radius 0.32 m · stuck = speed &lt; 0.03 m/s for 2 s while commanded &gt; 0.1 m/s, 2 events → return · tilt limit 35°'],
    ['<b>Trust / aging thresholds</b>', 'Slide examples: 2 / 15 / 40 min. AI-proposed: fresh &lt; 5 min, aging 5–30 min, stale &gt; 30 min, suspect = contradicted. <b>Not implemented in code; ' + T('OPEN') + '</b> (Beacon + Executor teammates).'],
    ['Simulated physics', 'gyro bias 0.3°/s (0.03°/s left after calibration) · encoder scale error 1.5 % · LiDAR 120 rays, 6 m, noise 0.02 m · robot radius 0.14 m · thermal source 90 °C, linear falloff to 25 °C over 2.5 m, range 3 m · battery drain constant'],
], [0.17, 0.83]))

# ===================================================================== 7 OPEN DECISIONS
S += H1('7. Open design decisions')
S.append(P('“Responsible teammate” assumes the four-role split proposed by the AI (Writer = the user). Names and the actual allocation of the other three people are unknown. <b>No decision below has been made silently; all need a human decision.</b>'))
S.append(tbl([
    ['Item', 'Current status', 'Decision still needed', 'Responsible teammate'],
    ['Environment', 'Fire / Hazardous Building ' + T('PROPOSED') + ' (sim built for it)', 'Confirm, or switch to another of the four environments', 'Whole team (user decides)'],
    ['Event types', 'HAZARD, JUNCTION, HOLE coded. Earlier default discussed: hazard + junction', 'Confirm the set; every type must also be understood by the Executor and shown on the live map', 'Writer owner + Executor teammate'],
    ['Distance sensor role', 'Assumed floor-facing hole detector; the user never answered the question', 'Choose: hole detector, drop confirmation, or front safety', 'Writer owner (user)'],
    ['Beacon write method (“D3”)', 'Proposed: blank beacon with unique ID, message written by radio at drop time. Alternatives: wired contacts in the magazine; pre-programmed beacons', 'Pick one; it fixes interface I1 and the Writer’s radio hardware', 'Beacon teammate + Writer owner'],
    ['Beacon message format', 'Fields proposed (section 8); byte layout, encoding, CRC and RF technology (BLE / ESP-NOW / LoRa) not defined', 'Define bytes, RF technology, range test plan', 'Beacon teammate'],
    ['Beacon-to-beacon direction', ' ' + T('OPEN DESIGN ISSUE') + ' see section 8.2', 'Decide how the chain is represented and who builds it', 'Beacon + Outside Network + Executor'],
    ['Outside Network log format (I3)', 'Draft JSON produced by the sim (section 8.3)', 'Confirm fields, units, frame, status values', 'Outside Network teammate'],
    ['Outside Network design', 'Raspberry Pi + GPS + MQTT + web map; satellite link simulated ' + T('PROPOSED'), 'Confirm architecture and what is simulated in Phase 1', 'Outside Network teammate'],
    ['Frame translation inputs', 'Entrance GPS fix + building orientation ' + T('PROPOSED'), 'How to obtain the orientation; error model', 'Outside Network teammate'],
    ['Shared frame with the Executor', 'Same private frame idea; heading consistency not solved', 'How the Executor knows its heading inside', 'Executor + Outside Network'],
    ['Aging / trust thresholds', 'Slide examples vs AI proposal; not coded', 'Choose thresholds and who applies them (beacon message vs Executor)', 'Beacon + Executor teammates'],
    ['Radio range and spacing', '3.5 m ' + T('ASSUMPTION'), 'Measure on hardware; set spacing', 'Beacon + Writer'],
    ['Clock synchronisation', 'GPS time before entry ' + T('ASSUMPTION'), 'Who sets the clocks and how', 'Outside Network teammate'],
    ['Phase 1 submission details', 'Not in the documents; a Google Forms link exists in the PDF', 'Open the links; email aess@ieee.tn / ras@ieee.tn if unclear', 'User'],
    ['Deadline and scoring grid', 'Deadline 05/10/2026 vs “due today”; 45 vs 60 points', 'Verify with organizers', 'User'],
], [0.17, 0.33, 0.30, 0.20]))

# ===================================================================== 8 BEACON
S += H1('8. Beacon information')
S.append(H2('8.1 Current proposed beacon message ' + T('PROPOSED') + ' ' + T('IMPLEMENTED IN SIM')))
S.append(tbl([
    ['Field', 'Meaning (current design only)', 'Maps to slide item'],
    ['<font name="DVM">id</font>', 'Unique beacon number given by the Writer, 1, 2, 3 … (increases only after a successful drop).', 'identifier'],
    ['<font name="DVM">type</font>', 'What the beacon is about: HAZARD, JUNCTION, HOLE or WAYPOINT (a relay beacon dropped only to keep the chain unbroken). In the sim it is a text label; the Beacon teammate must encode it in a few bits.', 'WHAT'],
    ['<font name="DVM">dir_deg</font>', 'Direction 0–359° in the private frame (0 = direction of entry, counter-clockwise positive). Depends on type: HAZARD = bearing towards the hot spot; HOLE = the Writer’s heading when it stopped (towards the missing floor); JUNCTION and WAYPOINT = the Writer’s travel heading at the drop.', 'WHERE'],
    ['<font name="DVM">dist_m</font>', 'HAZARD = <i>rough</i> estimated range to the heat source (from the peak temperature with an assumed model); HOLE = 0.3 m (floor-sensor look-ahead); JUNCTION and WAYPOINT = the nominal radio spacing 3.5 m, <b>a placeholder, not a real distance to the next beacon</b>.', 'distance'],
    ['<font name="DVM">t</font>', 'Time the message was written (epoch seconds). Needs a GPS-synchronised clock ' + T('ASSUMPTION') + '. Used for aging by whoever reads the beacon.', 'WHEN'],
    ['<font name="DVM">ver</font>', 'Version, 1 at drop; a later agent can overwrite with a higher number. Not used anywhere in the code yet.', 'version'],
    ['<font name="DVM">exits</font> (junctions only)', '<b>4-bit mask</b> of open directions in the private frame, rounded to the nearest 90°: bit0 = East (0°), bit1 = North (90°), bit2 = West (180°), bit3 = South (270°). Example 0111 = open East, North and West. Computed from the Writer’s heading and the LiDAR.', '— (extra; not on the slide)'],
], [0.17, 0.62, 0.21]))
S.append(P('Byte layout, number of bits per field, CRC and the radio technology are <b>not defined</b>. (An earlier chat estimate of “about 11 bytes” was only a rough guess ' + T('ASSUMPTION') + '.) The log also stores per beacon, <i>not on the air</i>: position x, y in the private frame, severity, decision score, confidence.', 'small'))
S.append(H2('8.2 ' + T('OPEN DESIGN ISSUE') + ' — the next beacon is unknown at drop time'))
S.append(box([P('<b>The Writer does not know where the <i>next</i> beacon will be when it drops the current one.</b> The slides describe a beacon as holding “direction to take from here” and “metres to next beacon / target”, but at drop time that next beacon does not exist yet. Therefore, in the current concept each beacon stores information about the <b>detected event</b> (type, direction and rough distance to the event), and the placeholder distance for junction/relay beacons is only the nominal spacing. The <b>beacon-to-beacon chain</b> (which beacon follows which, with the true direction and distance between them) may have to be <b>constructed later by the Outside Network</b> from the Writer’s log and delivered in the Executor’s briefing.<br/><br/><b>This needs agreement with the Beacon and Outside Network teammates (and the Executor teammate).</b> Options for discussion — none is decided: (a) as now: event info on the beacon, chain built by the Outside Network; (b) the Writer re-writes the previous beacon after dropping the next one (hard mechanically); (c) each beacon stores the direction/distance <i>back</i> to the previous beacon, which is known at drop time; (d) a combination. Option (a) is what the code does today and it makes the Executor depend on its briefing rather than only on the beacons — a point judges may question.', 'box')], bg='#fdecea', border='#b00020'))
S.append(H2('8.3 Log sent to the Outside Network (interface I3, draft) ' + T('DRAFT') + ' ' + T('IMPLEMENTED IN SIM')))
S.append(P('JSON, all positions in the private frame (illustrative structure, not a result):'))
S.append(Paragraph('{ "robot":"writer", "frame":"private", "origin":"entrance", "axes":"x = direction of entry, y = left, angles CCW (degrees)",<br/>'
                   '&nbsp; "start_time":&lt;epoch s&gt;, "end_time":&lt;epoch s&gt;, "status":"returned", "return_reason":"...",<br/>'
                   '&nbsp; "path":[[x, y, heading_rad, t], ...],<br/>'
                   '&nbsp; "beacons":[{"id","type","dir_deg","dist_m","t","ver",["exits"],"x","y","severity","score","confidence"}, ...],<br/>'
                   '&nbsp; "decisions":[{"t","type","action":"drop|skip|fail","score","reason","x","y"}, ...],<br/>'
                   '&nbsp; "stats":{"path_length_m","heading_corrections","drop_failures","stock_left","battery_end","stuck_events"} }', st['code']))
S.append(P('If the Writer is lost, no log exists; the sim then writes only <i>beacons_on_ground.json</i> (what an Executor could still read).', 'small'))

# ===================================================================== 9 FAILURE CASES
S += H1('9. Failure cases')
S.append(P('<b>Important:</b> only normal runs have been executed. <b>None of the failure scenarios below has been run.</b> The first five exist as code paths or command-line options; the others are design ideas only.'))
S.append(tbl([
    ['Scenario', 'What fails', 'What the simulation should demonstrate / expected response', 'Status'],
    ['<b>Writer dies</b> <font name="DVM">--kill-at T</font>', 'Power/crash at time T, or falling into the hole', 'No log is uploaded (status “lost”); beacons already dropped stay on the ground and are written to beacons_on_ground.json — the core “knowledge survives” story.', T('UNTESTED')],
    ['<b>Servo / drop failure</b> <font name="DVM">--drop-fail-prob p</font>', 'Servo jam or radio write fails; no break-beam confirmation', 'Retry once; if it fails again log “fail”, keep the beacon in the magazine, continue exploring.', T('UNTESTED')],
    ['<b>Low battery</b> <font name="DVM">--battery-drain x</font>', 'Battery reaches the 30 % reserve', 'Stop exploring, return by the breadcrumb trail, upload the log (reason “battery reserve reached”).', T('UNTESTED')],
    ['<b>Hidden debris / stuck</b> <font name="DVM">--debris</font>', 'Low obstacle the LiDAR cannot see blocks the wheels', 'Stall detected (commanded &gt; 0.1 m/s, measured &lt; 0.03 m/s for 2 s) → back up and turn; a second stall → return with reason “stuck”. (A stuck event also appeared <i>without</i> debris in seed 10 — a bug symptom, see 6.1.)', T('UNTESTED')],
    ['Magazine empty / time limit', 'No beacons left / mission too long', 'Return and upload (coded in the return triggers).', T('UNTESTED')],
    ['Upload failure', 'Robot not within range of the Outside Network', 'Up to 3 tries, then status “upload_failed”, log kept on board (coded).', T('UNTESTED')],
    ['Tip-over', 'Robot flips or tilts &gt; 35°', 'SAFE_STOP (coded) — cannot be triggered in the sim because tilt is always 0.', T('UNTESTED')],
    ['LiDAR dropout', 'No scans arrive', 'Stop, then use the breadcrumb return.', T('DESIGN ONLY')],
    ['“Brain” crash', 'Linux side stops sending commands', 'Microcontroller watchdog stops the motors (Phase 2 hardware idea).', T('DESIGN ONLY')],
    ['Localization drift', 'Gyro/encoder errors grow', 'Wall-based heading correction in the sim; confidence value on each beacon. No dedicated failure test.', 'Partly modelled; ' + T('UNTESTED') + ' as a scenario'],
    ['Stale or contradicted beacon; missing beacon; Outside link loss', 'Executor / Outside Network side', 'Trust-by-age rules; fallback to own sensors; store-and-forward queue.', T('DESIGN ONLY') + ' (other teammates; no code)'],
], [0.20, 0.20, 0.42, 0.18]))

# ===================================================================== 10 GITHUB
S += H1('10. GitHub repository plan')
S.append(P(T('PROPOSED') + ' No repository exists yet as far as this project record shows. Goal: a judge should understand the project in two minutes.'))
S.append(Paragraph('living-map/<br/>├── README.md<br/>├── requirements.txt<br/>├── simulation/<br/>├── docs/<br/>├── results/<br/>└── report/', st['code']))
S.append(tbl([
    ['Path', 'What goes in it'],
    ['<font name="DVM">README.md</font>', 'One-paragraph pitch · the challenge in 5 lines · architecture figure · how to run the demo (exact commands) · what is simulated and what is not · results figure · links to docs/ and report/ · team and roles · honest limitations.'],
    ['<font name="DVM">requirements.txt</font>', 'numpy, matplotlib, Pillow (the libraries used so far; add versions once known).'],
    ['<font name="DVM">simulation/</font>', 'hal.py, sim_world.py, writer.py, run_demo.py, viz.py, test_robust.py; later the Outside Network, frame translation and Executor modules written by the teammates; a short README of its own with the command-line options.'],
    ['<font name="DVM">docs/</font>', 'Architecture and data-flow diagrams · Writer state machine · beacon message format · interface specs I1–I5 · frame-translation note · an ASSUMPTIONS list (section 6.3) · this handover PDF · implementation plan.'],
    ['<font name="DVM">results/</font>', '<b>Only</b> outputs generated from the final code: normal-run PNG/GIF, sample writer_log.json and beacons_on_ground.json, and one output per failure scenario with a caption saying what it shows. No stale files.'],
    ['<font name="DVM">report/</font>', 'Final technical report PDF (max 6 pages) and its source.'],
], [0.22, 0.78]))

# ===================================================================== 11 REPORT
S += H1('11. Technical report plan (maximum 6 pages)')
S.append(P('The report itself is worth only 2 points, but it carries the explanation of the seven technical areas (35 points), the diagrams (5), the plan (3) and the failure cases (3). Page budgets are a ' + T('PROPOSED') + ' guide (total ≈ 5.8 pages).'))
S.append(tbl([
    ['#', 'Section', 'Pages', 'Available now?', 'Still missing'],
    ['1', 'Introduction and Challenge', '0.4', 'Material available (section 1 here)', 'Write it for the report'],
    ['2', 'Proposed Solution', '0.5', 'Material available (section 3)', 'Confirm environment/events; innovation paragraph'],
    ['3', 'System Architecture', '0.7', 'Draft diagram (Figure 1)', 'Final diagram + data-flow diagram; confirm interfaces with teammates'],
    ['4', 'Writer Robot', '0.7', 'Material available (section 4); state machine drawn', 'Write-up; hardware wiring sketch'],
    ['5', 'Event Detection and Beacon Deposition', '0.6', 'Material available (4.5–4.7)', 'Clean simulation results after the bug fix'],
    ['6', 'Beacon Message and Communication', '0.5', 'Partial (section 8)', '<b>OPEN</b>: byte layout, RF technology, chain issue, aging rules'],
    ['7', 'Outside Network and Executor', '0.7', 'Partial — concept only', 'Teammates’ designs; frame-translation example with numbers; Executor logic'],
    ['8', 'Simulation', '0.5', 'Partial (section 5)', 'Reliable run, figures, demo video'],
    ['9', 'Failure Cases', '0.4', 'Partial (section 9)', 'Run and record the scenarios'],
    ['10', 'Implementation Plan', '0.5', 'Partial (hardware list, Phase 2 items)', 'Timeline to 01/12/2026, budget, risks, owners'],
    ['11', 'Limitations and Future Work', '0.3', 'Material available (section 6, 12)', 'Write it for the report'],
], [0.04, 0.27, 0.07, 0.30, 0.32]))

# ===================================================================== 12 REMAINING
S += H1('12. Work remaining')
S.append(H2('MUST DO FOR PHASE 1'))
S.append(tbl([
    ['', 'Task', 'Why / note'],
    ['☐', '<b>Verify the real deadline and submission route</b>: open the two links in the cahier des charges (architecture diagram, Google Form); email aess@ieee.tn / ras@ieee.tn if unclear.', 'Deadline is 05/10/2026 in the document.'],
    ['☐', '<b>Diagnose and fix the exploration bug</b> (skipped rooms, false “stuck”, wandering). Inspect the plots of seeds 3, 10, 1, 9 first; instrument from inside the Writer.', 'Then rerun a multi-seed test with a proper <b>coverage</b> criterion until results are consistent.'],
    ['☐', '<b>Run and record the failure scenarios</b> (writer dies, servo jam, low battery, debris, magazine empty, upload failure).', 'Needed for “Failure Cases” and part of the demo.'],
    ['☐', '<b>Generate clean simulation outputs</b> (PNG, GIF, logs) from the final code; delete stale outputs; test the GIF function once.', 'Needed for the demo and the report.'],
    ['☐', '<b>Minimal simulation of the rest of the chain</b>: Outside Network (receive, frame translation to GPS, forward, simple live map) and Executor following beacons in the same world.', 'Today only the Writer is simulated, but the 7 required areas include them. Assign owners; agree the interfaces first.'],
    ['☐', '<b>Agree interfaces with teammates</b>: beacon message/D3, log format I3, direction meaning (section 8.2), event set.', 'Section 7.'],
    ['☐', '<b>Diagrams</b>: final system architecture, data flow, Writer state machine (draft exists), beacon message layout, frame translation.', '5 points for diagrams.'],
    ['☐', '<b>Implementation plan</b>: hardware list, timeline to 01/12/2026, risks, who does what.', '3 points.'],
    ['☐', '<b>Technical report</b> (≤ 6 pages) following section 11.', '2 points + carries the rest.'],
    ['☐', '<b>README and GitHub repository</b> organised as in section 10.', '4 points.'],
    ['☐', '<b>Final check</b> against the six deliverables and the seven areas.', 'Last step before submitting.'],
], [0.04, 0.62, 0.34]))
S.append(H2('SHOULD DO IF TIME ALLOWS (realistic only)'))
S.append(bl(['Add a simple radio-range model to the simulation so the beacon spacing is justified, not just assumed.',
             'Implement beacon aging/trust in the simulated Executor (Beacon/Executor teammates).',
             'Add a second building layout containing a loop, to show honestly where the right-hand rule fails.',
             'Compare the wall-based heading correction against a simple scan-matching correction.',
             'An innovation paragraph for the report: score-based beacon rationing, aging and trust, the dual-processor split of the UNO Q.',
             'Pitch outline (the pitch is only in the final phase).']))
S.append(H2('FINAL PHASE / LATER (physical work — nothing here has been started)'))
S.append(bl(['RPLIDAR integration on the UNO Q (including the powered USB-C hub question) and real scan processing.',
             'Real beacon radio tests: technology choice, range inside a building, power use.', 'Physical beacon dispenser (servo gate, magazine, break-beam).',
             'Drive base, encoders, motor driver, power rails, e-stop; thermal sensor; Modulino Movement/Distance integration.',
             'Real robot navigation and tuning of every parameter in section 6.3; hardware validation of the Writer, beacons, Executor.',
             'Real Outside Network (GPS + link to a command post); complete physical prototype (15 points); user manual; pitch in English (5 min + 2 min Q&amp;A).']))

# ===================================================================== 13 NEXT AGENT
S.append(PageBreak())
S += H1('13. Instructions for the next AI agent')
S.append(box([bl([
    '<b>Read this PDF first</b>, completely, then <b>read the official cahier des charges</b> (The_Living_Map_Spatial_Memory_for_Emergency_Robots_1.pdf) and the presentation (presentation.pdf). They are the primary source of truth. Never invent requirements.',
    '<b>Do not restart the project from zero</b> and do not redesign decided parts without a reason. Decided: the challenge reading, the four-role split, the Writer hardware (UNO Q, RPLIDAR, Modulino Movement and Distance, servo), the HAL-based simulation, the beacon policy structure.',
    '<b>Continue from the current status</b> (section 14). Ask the user for the zip <font name="DVM">writer_sim_snapshot_2026-10-03.zip</font>; the working folder of the previous session may no longer exist.',
    '<b>First finish the missing Phase 1 deliverables</b>, in this order: verify the deadline and submission route → fix/stabilise the simulation → run the failure scenarios → clean results → diagrams → report → README/GitHub → final check (section 12).',
    '<b>Keep assumptions and untested items clearly labeled</b> with the labels of this document. Never claim physical validation. Never present an untested scenario as tested.',
    '<b>Priorities:</b> working simulation, report, diagrams, GitHub, failure cases and implementation plan — in that spirit, not new features.',
    '<b>Help the user step by step.</b> The user is new to the project. Use clear, direct language; explain technical words simply; do not dump large amounts of information; keep the pace fast because of the deadline.',
    '<b>Working agreement set by the user:</b> for each major decision give <i>Problem → Options → Trade-offs → Decision → Next action</i>; do <b>not</b> make the final choice silently; challenge assumptions; point out weak points and contradictions; distinguish what is technically possible now from what needs research; label assumptions; do not make unrealistic claims.',
    '<b>Known traps:</b> (1) the multi-seed “clean run” test is lenient — use coverage; (2) debugging scripts that call <font name="DVM">hal.scan()</font> change the random stream; (3) the folders out_default/out_s3/out_s10 are stale; (4) the heading correction only works for axis-aligned walls; (5) the scoring grid says 45 but sums to 60.'], 'box')], bg='#eef3f8', border='#1f3a5f'))

# ===================================================================== 14 SUMMARY
S += H1('14. Final summary table')
S.append(tbl([
    ['Area', 'Status', 'Priority'],
    ['Challenge understanding', 'Done', 'Low'],
    ['Writer concept', 'Done', 'Low'],
    ['Writer simulation', 'Mostly done / debugging (not reliable yet)', '<font color="#b00020"><b>HIGH</b></font>'],
    ['Event detection', 'Designed (implemented in sim)', '<font color="#b00020"><b>HIGH</b></font>'],
    ['Beacon logic', 'Designed (implemented in sim)', '<font color="#b00020"><b>HIGH</b></font>'],
    ['Beacon interface', 'Open', '<font color="#b00020"><b>HIGH</b></font>'],
    ['Outside Network interface', 'Draft', '<font color="#b00020"><b>HIGH</b></font>'],
    ['Failure cases', 'Designed, testing needed', '<font color="#b00020"><b>HIGH</b></font>'],
    ['GitHub', 'Not packaged yet', '<font color="#b00020"><b>HIGH</b></font>'],
    ['Diagrams', 'Not completed (two drafts in this PDF)', '<font color="#b00020"><b>HIGH</b></font>'],
    ['Report', 'Not completed', '<font color="#b00020"><b>HIGH</b></font>'],
    ['Implementation plan', 'Partial', '<font color="#b00020"><b>HIGH</b></font>'],
    ['Physical hardware validation', 'Not done', 'Later'],
    ['<i>Added by the AI for completeness:</i> Outside Network + Executor simulation', 'Not started', '<font color="#b00020"><b>HIGH</b></font>'],
    ['<i>Added:</i> Deadline / submission route / scoring clarification', 'Open (links not yet opened)', '<font color="#b00020"><b>HIGH</b></font>'],
], [0.46, 0.38, 0.16]))

S += H1('Appendix — How the project got here (short timeline)')
S.append(tbl([
    ['Step', 'What happened'],
    ['1', 'The two official documents were read; the challenge, Phase 1 deliverables, problems and three solution levels were analysed.'],
    ['2', 'The team split into four roles was proposed (Writer, Beacon, Outside Network, Executor) with a shared interface contract I1–I5.'],
    ['3', 'The user, owner of the Writer, chose UNO Q + RPLIDAR + servo; the AI filled the gaps (drive base, power, thermal sensor, beacon write method…). The IMU was explained; the user then said they own Modulino Movement and Modulino Distance.'],
    ['4', 'The AI built the Writer simulation (hal, sim_world, writer, run_demo, viz, test_robust). First runs worked; several bugs were found and fixed (section 6.2).'],
    ['5', 'Multi-seed testing exposed remaining problems (section 6.1). Development was <b>stopped on purpose</b> to write this handover.'],
], [0.07, 0.93]))

doc.build(S)
print('built')
