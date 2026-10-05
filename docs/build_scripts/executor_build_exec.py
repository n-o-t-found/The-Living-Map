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
    c.drawString(1.7 * cm, 1.1 * cm, 'The Living Map — The Executor Robot  |  Design brief, 04/10/2026')
    c.drawRightString(A4[0] - 1.7 * cm, 1.1 * cm, f'Page {d.page}')
    c.setStrokeColor(GRID); c.line(1.7 * cm, 1.45 * cm, A4[0] - 1.7 * cm, 1.45 * cm)
    c.restoreState()

doc = BaseDocTemplate('/home/claude/execpdf/The_Living_Map_Executor_Robot.pdf', pagesize=A4,
                      leftMargin=1.7 * cm, rightMargin=1.7 * cm, topMargin=1.5 * cm, bottomMargin=1.9 * cm,
                      title='The Living Map — The Executor Robot', author='Project co-pilot (AI) for the TSYP14 team')
doc.addPageTemplates([PageTemplate(id='p', frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='f')], onPage=footer)])


S = []
S += [Spacer(1, 4), P('The Executor Robot', 'title'),
      P('The Living Map · TSYP14 Technical Challenge · Design brief and specification', 'sub'),
      P('Written on <b>04/10/2026</b> · Official Phase 1 submission deadline: <b>05/10/2026</b> · Companion to the “Phase 1 Project Status &amp; Technical Handover” and the “Outside Network Area” brief', 'sub'), Spacer(1, 6)]
S.append(box([P('<b>Who this is for</b>', 'box'), bl([
    'The person who owns the Executor robot in the team (the AI assumed one of four roles: Writer, Beacon, Outside Network, <b>Executor</b>) — and any new AI agent helping them.',
    'It explains what the Executor must do, what the organizers require, what has been designed so far, and what is still open.',
    '<b>Nothing for the Executor exists yet: no code, no simulation, no hardware chosen.</b> The only related code is the Writer simulation, which produces the beacons the Executor will read.',
    'Labels: ' + T('CONFIRMED') + ' official document or user · ' + T('PROPOSED') + ' suggested by the AI, not approved · ' + T('ASSUMPTION') + ' invented to make the design work · ' + T('OPEN') + ' no decision yet · ' + T('DESIGN ONLY') + ' not implemented · ' + T('INTERPRETATION') + ' the AI’s reading of the documents.'], 'box')], bg='#eef3f8', border='#1f3a5f'))

# ------------------------------------------------------------------ 1
S += H1('1. What the Executor is')
S.append(P('The Executor is the <b>second robot</b>. It enters the dangerous space <b>after</b> the Writer, with a mission, and finishes the job <b>without starting from zero</b>, because the Writer’s knowledge was left behind in beacons. The Writer is “first inside, alone”; the Executor “enters with a mission” (slide 3). ' + T('CONFIRMED')))
S.append(H2('1.1 What the official documents require'))
S.append(tbl([
    ['Requirement (source)', 'Meaning'],
    ['<b>Receives a mission</b>: extinguish · extract · seal · retrieve, tied to the chosen scenario (slide 3)', 'The mission must make sense for the environment you picked.'],
    ['<b>Enters informed</b>: no blind search; it already knows what to reach and what to avoid (slide 3)', 'It must carry knowledge in with it — this is the briefing.'],
    ['<b>Navigates by beacons</b>: “the beacons are the map”, it listens and follows, no GPS needed (slide 3)', 'Its navigation must really depend on the beacons the Writer left.'],
    ['<b>Trusts by age</b>: fresh beacons guide it; stale ones it verifies with its own sensors (slide 3; examples on slide 2)', 'It must judge each beacon by its age and cross-check with its own sensors.'],
    ['Use <b>at least 2 physical robots</b>, Writer and Executor (slide 6)', 'The Executor must be a real robot in the final prototype.'],
    ['Briefed <b>before entry</b>. Slide 3 says “briefed by the command post”; slide 5 gives the BRIEF role to the Outside Network Area; the rule says no direct robot↔command-post link', T('INTERPRETATION') + ' The command post decides the mission; the Outside Network Area prepares and delivers the briefing.'],
    ['Technical focus: <i>mission briefing · beacon-guided navigation · mission execution</i> (cahier des charges p.2)', 'These are the three things to show.'],
    ['Goal: “build an Executor Robot that receives a mission and navigates using inherited beacon information” (p.1)', 'The word “inherited” is the core idea.'],
], [0.50, 0.50]))
S.append(H2('1.2 Points at stake'))
S.append(P('Phase 1: <b>Executor robot: 5</b>, plus shared items it contributes to — technical solution diagrams 5, simulation demo 8, failure cases 3, implementation plan 3. Final phase: it is one of the two robots in the <b>physical prototype (15 points)</b>. <b>Gap to be aware of:</b> the current simulation covers only the Writer. A demo that never shows the Executor reading beacons would not show the chain the challenge is about.'))

# ------------------------------------------------------------------ 2
S += H1('2. What the Executor depends on')
S.append(tbl([
    ['Input / output', 'From / to', 'Content', 'Status'],
    ['<b>Briefing</b> (I5)', 'Outside Network Area → Executor, before entry', 'Mission, target, ordered beacon chain, known hazards, clock synchronisation, trust rules (sketch in the Outside Network brief, section 4.3)', T('PROPOSED') + ' ' + T('DESIGN ONLY')],
    ['<b>Beacon broadcasts</b> (I2)', 'Beacons → Executor, inside the building', 'id, type, dir_deg, dist_m, t, ver, and for junctions the 4-bit exits mask (handover PDF, section 8.1)', T('PROPOSED') + '; radio technology ' + T('OPEN')],
    ['<b>Own sensors</b>', 'On the robot', 'LiDAR, gyro and wheel odometry, a thermal sensor, a floor sensor — to move safely and to cross-check beacons', T('PROPOSED') + '; nothing chosen'],
    ['<b>Movement and mission action</b>', 'Executor → the world', 'Drives to the target and performs the mission (simulated in Phase 1)', T('PROPOSED')],
    ['Report back', 'Executor → anyone', 'The documents do <b>not</b> require the Executor to send anything out. A decision log (what it trusted, discarded, verified) is useful for judges.', T('PROPOSED') + ' optional'],
], [0.17, 0.25, 0.43, 0.15]))

# ------------------------------------------------------------------ 3
S += H1('3. Behaviour: how the Executor works')
S.append(img('/home/claude/execpdf/exec_states.png', 0.97))
S.append(P('Figure 1 — Proposed Executor state flow (' + 'design only' + '). The main path is BRIEFED → ENTER → LISTEN → TRUST-CHECK → FOLLOW → ACT → EXIT, with a loop back to LISTEN for each beacon of the chain.', 'cap'))
S.append(tbl([
    ['State', 'What happens ' + '(proposed)', 'Leaves when'],
    ['<b>BRIEFED</b>', 'Waits at the entrance. Receives the briefing and the clock synchronisation, checks the briefing is complete, acknowledges.', 'Briefing valid. If none arrives it does <b>not</b> enter.'],
    ['<b>ENTER</b>', 'Starts its private frame at the entrance: position (0, 0), heading = direction of entry, the same convention as the Writer. Calibrates the gyro while standing still, then drives in.', 'Through the door.'],
    ['<b>LISTEN</b>', 'Moves towards the next expected beacon while listening on the radio, avoiding obstacles and holes.', 'A beacon is heard; or nothing is heard for too long.'],
    ['<b>TRUST-CHECK</b>', 'For each beacon: computes its age (now − t), checks its version, compares it with its own sensor, and classes it fresh / aging / stale / suspect (section 4).', 'Decision made.'],
    ['<b>FOLLOW</b>', 'Drives the next leg of the chain (fresh: normal speed; aging: slow and verify; stale: own senses decide).', 'Next beacon reached, or target reached.'],
    ['<b>LOCAL SEARCH</b>', 'Chain broken or beacon missing: explores locally (e.g. wall following as the Writer does) to find a beacon.', 'Beacon found, or search limit reached.'],
    ['<b>ACT</b>', 'At the target, performs the mission action. In Phase 1 the action is simulated.', 'Action done or aborted.'],
    ['<b>EXIT</b>', 'Leaves by retracing its own path. Whether the Executor must come back out is not stated in the documents.', T('OPEN')],
    ['<b>SAFE_STOP</b>', 'Stops all motion on tip-over, e-stop or an unrecoverable fault.', 'Manual reset.'],
], [0.15, 0.62, 0.23]))

# ------------------------------------------------------------------ 4
S += H1('4. Trust by age')
S.append(P('The slides stress this behaviour strongly (' + T('INTERPRETATION') + ' it is probably what the organizers most want to see in the Executor). The slides show the <i>same beacon</i> at different ages: <b>fresh (2 min)</b> “trust as measured”; <b>aging (15 min)</b> “possible hazard — verify before crossing”; <b>stale (40 min)</b> “old warning — rely on your own senses”; <b>suspect (contradicted)</b> “live sensor disagrees — flag it, discard”. ' + T('CONFIRMED')))
S.append(img('/home/claude/execpdf/trust_timeline.png', 0.97))
S.append(P('Figure 2 — Trust states over time. The 2 / 15 / 40 min markers are the slide’s examples, not official thresholds. The band boundaries (5 and 30 min) are an AI assumption.', 'cap'))
S.append(H2('4.1 Rules ' + T('PROPOSED')))
S.append(tbl([
    ['State', 'How it is decided', 'Executor behaviour'],
    ['<b>Fresh</b>', 'Age below the fresh limit; no contradiction', 'Follow the beacon as measured, at normal speed.'],
    ['<b>Aging</b>', 'Age between the fresh and stale limits', 'Slow down; verify with its own sensor <i>before crossing</i> the area the beacon describes.'],
    ['<b>Stale</b>', 'Age above the stale limit', 'Treat the beacon as a hint only; its own sensors decide what to do.'],
    ['<b>Suspect</b>', 'Its own live sensor contradicts the beacon, at <b>any</b> age', 'Flag it, discard it, record the reason.'],
], [0.14, 0.38, 0.48]))
S.append(H2('4.2 What “contradicted” means for each event type ' + T('PROPOSED')))
S.append(tbl([
    ['Beacon type', 'Own sensor used', 'Contradiction example'],
    ['HAZARD (heat)', 'Thermal sensor', 'The beacon says a heat source is ahead, but the Executor, near that spot, reads only ambient temperature. The source may have gone out, or the position may be wrong. The reverse (heat where no beacon warned) is a <b>new</b> hazard to log.'],
    ['HOLE (missing floor)', 'Floor-facing distance sensor', 'The beacon says no floor ahead, but the floor is there (or the reverse). <b>Keep the floor sensor on at all times</b>, even for trusted beacons: it is a safety sensor.'],
    ['JUNCTION', 'LiDAR', 'The beacon’s exits mask lists open directions that the LiDAR does not see.'],
    ['WAYPOINT', '—', 'No event to contradict; only age and position matter.'],
], [0.17, 0.20, 0.63]))
S.append(H2('4.3 Points still open about aging'))
S.append(bl(['<b>Thresholds</b> ' + T('OPEN') + ': the slides give examples at 2 / 15 / 40 min; the AI suggested 5 and 30 min. Nothing is coded. The AI’s reasoning: they should depend on how fast the scenario changes (a fire changes faster than a mine).',
             '<b>Who ages the message?</b> ' + T('OPEN') + ' The cahier des charges lists a “message aging mechanism” under <i>Beacon Design</i>, which can mean the beacon itself degrades its message over time. The current proposal is the opposite: the Executor computes the age from the timestamp. This needs agreement with the Beacon teammate.',
             '<b>Version and overwriting.</b> The slide says the version “lets a later agent overwrite” the beacon. ' + T('INTERPRETATION') + ' This could mean the Executor should be able to <i>re-write</i> beacons with updated information (for example “hazard extinguished”). That would require a radio transmitter on the Executor. ' + T('OPEN') + ' — it is not required by the rules, but it would be a strong demonstration of the idea.',
             '<b>Clocks.</b> Age only works if the Writer’s and Executor’s clocks agree. ' + T('ASSUMPTION') + ' Both are synchronised to GPS time before entry (see the Outside Network brief).']))

# ------------------------------------------------------------------ 5
S += H1('5. Navigating by beacons — the hard part')
S.append(H2('5.1 What a beacon actually tells the Executor'))
S.append(P('The current beacon message (handover PDF, section 8) carries <font name="DVM">dir_deg</font> and <font name="DVM">dist_m</font>, but their meaning depends on the type: for HAZARD, the bearing and a <i>rough</i> range to the heat source; for HOLE, the direction of the missing floor and 0.3 m; for JUNCTION and WAYPOINT, the Writer’s heading at the drop and a <b>placeholder</b> distance (3.5 m) that is <b>not</b> the real distance to the next beacon. The reason: when the Writer drops a beacon, it does not yet know where the next one will be.'))
S.append(box([P(T('OPEN DESIGN ISSUE') + ' <b>Beacons only, or beacons plus briefing?</b> Because of the point above, the true geometry between beacons (where the next beacon is, from this one) can only be computed from the Writer’s complete log, by the Outside Network, and delivered in the briefing. So in the current design the Executor depends on <b>both</b> the briefing (geometry) and the beacons (confirmation, age, trust). A judge may ask: “is the memory really in the space?” The team must decide whether this is acceptable, or whether the beacons should carry more (for example the direction and distance <i>back</i> to the previous beacon, which the Writer does know at drop time).', 'box')], bg='#fdecea', border='#b00020'))
S.append(H2('5.2 Proposed approach ' + T('PROPOSED') + ' ' + T('DESIGN ONLY')))
S.append(bl(['The briefing gives the ordered chain, with each beacon’s position in the shared private frame and the expected direction and distance to the next one.',
             'The Executor drives towards the next expected beacon using dead reckoning (wheels and gyro) with obstacle avoidance, and starts listening.',
             'When a beacon is heard it is judged (section 4). A trusted beacon can also <b>correct the robot’s drift</b>: its position is known from the briefing, so the Executor can reset its estimated position when it is at the beacon.',
             'The same heading correction as the Writer (using straight walls) can be reused. It has the same weakness: it assumes the walls run along the x and y axes.']))
S.append(H2('5.3 How does it know it is at a beacon? ' + T('OPEN')))
S.append(tbl([
    ['Option', 'Idea', 'Trade-off'],
    ['A. “Heard” = in range', 'A beacon is “reached” when it is heard at all', 'Simplest; the precision equals the radio range, which is probably several metres.'],
    ['B. Signal strength', 'Use how strong the signal is: stronger means closer; follow the increase', 'Cheap, but indoor signal strength is noisy; must be measured on hardware.'],
    ['C. A ranging radio (e.g. ultra-wideband)', 'Measures distance directly', 'Most precise; more and costlier hardware on both beacons and robot.'],
], [0.24, 0.40, 0.36]))
S.append(P('None of these has been tested. How radio behaves inside a building is unknown and <b>must be measured</b> before the design is trusted. The choice depends on the radio technology the Beacon teammate selects.', 'small'))
S.append(H2('5.4 If there is no briefing chain (fallback)'))
S.append(P('If the Writer is lost, no log exists and the briefing contains only the mission. The Executor could still follow each heard beacon’s direction, and use the junction exits mask to choose branches. This works only in simple layouts: at a junction the direction stored in the beacon is the way the Writer happened to continue, which may not lead to the target. ' + T('ASSUMPTION') + ' This is a weak mode and should be shown as such.'))

# ------------------------------------------------------------------ 6
S += H1('6. Hardware (everything proposed, nothing chosen)')
S.append(tbl([
    ['Function', 'Need', 'Note'],
    ['Drive base and odometry', 'Two driven wheels with encoders and an IMU for heading', 'Could copy the Writer’s design so that code can be shared.'],
    ['Main computer', 'Runs the trust logic, the chain follower and the sensors', 'The UNO Q (as on the Writer) would allow reuse of the same software structure. ' + T('OPEN')],
    ['Obstacle and junction sensing', 'LiDAR', 'Same role as on the Writer; also used to check the junction exits.'],
    ['Heat verification', 'Thermal sensor', 'Needed to contradict or confirm a HAZARD beacon. Not chosen.'],
    ['Floor verification and safety', 'Floor-facing distance sensor', 'Needed to confirm a HOLE beacon and to avoid falling.'],
    ['Beacon receiver', 'A radio that matches the beacons', 'Depends on the Beacon teammate’s choice. ' + T('OPEN')],
    ['Beacon transmitter (optional)', 'To re-write beacons (version overwrite)', 'Only if the team decides the Executor updates beacons.'],
    ['Link for the briefing', 'To receive the briefing at the entrance', 'Depends on the Outside Network design. ' + T('OPEN')],
    ['Mission tool', 'The device that “extinguishes”, “seals”, “extracts” or “retrieves”', 'Not chosen. For a demo, a safe stand-in is advised (an indicator light, a servo arm or a flag). Real fire or water near the electronics is not recommended.'],
    ['Power and safety', 'Battery, a separate rail for actuators, an emergency stop', 'As for the Writer.'],
], [0.22, 0.34, 0.44]))
S.append(H2('6.1 What can be reused from the Writer code'))
S.append(tbl([
    ['Reusable', 'New for the Executor'],
    ['The hardware-abstraction structure · wall following and obstacle avoidance · gyro calibration and the wall-based heading correction · stuck detection · tip-over and battery safety · logging of decisions · retracing its own path',
     'A way to listen to beacons (the Writer’s interface has no “listen” function; one would have to be added) · the trust module · the chain follower · the briefing reader · the mission action · optional beacon re-writing'],
], [0.5, 0.5]))
S.append(P('This is a suggestion; the code has not been adapted. ' + T('PROPOSED'), 'small'))

# ------------------------------------------------------------------ 7
S += H1('7. Phase 1 simulation plan ' + T('NOT STARTED'))
S.append(bl(['Use the <b>same simulated building</b> and the beacons left by a Writer run.',
             'Reception model: a beacon is heard when the robot is within a chosen radius. ' + T('ASSUMPTION') + ' — no radio physics is simulated.',
             'The file <font name="DVM">beacons_on_ground.json</font> contains <font name="DVM">true_x</font> and <font name="DVM">true_y</font>, which exist only for plotting. <b>The Executor must not use them</b>: they are the simulation’s hidden ground truth. It should use only what would be on the air, plus the positions given in the briefing.',
             'Time can be shifted in the simulation to test aging.',
             'The Writer simulation is not fully reliable yet. Seeds without a flagged problem in the earlier tests were 2, 4, 5, 6, 8, 11, 12 and 13, or a hand-made beacon set can be used.',
             'Suggested success criterion: the Executor reaches within 0.5 m of the target and performs the action, never enters a hole, and logs every trust decision. ' + T('ASSUMPTION')]))
S.append(tbl([
    ['Test', 'Setup', 'Expected result', 'Status'],
    ['E1 Normal', 'Fresh beacons, valid briefing', 'Follows the chain, reaches the target, acts', T('NOT STARTED')],
    ['E2 Aging / stale', 'Clock moved forward so beacons become aging, then stale', 'Aging: slows and verifies. Stale: relies on its own sensors. Still reaches the target', T('NOT STARTED')],
    ['E3 Contradicted', 'The heat source is removed after the Writer’s run', 'Thermal reading is ambient: the HAZARD beacon is flagged suspect and discarded; the outcome is reported', T('NOT STARTED')],
    ['E4 Missing beacon', 'One beacon of the chain removed', 'Falls back to local search; continues or gives up cleanly', T('NOT STARTED')],
    ['E5 No log', 'Briefing contains the mission only', 'Weak beacon-only mode: reaches the target or stops safely with a clear status', T('NOT STARTED')],
    ['E6 Heading drift', 'Larger gyro bias', 'Heading correction and beacon position resets keep it on course; shows the limit', T('NOT STARTED')],
    ['E7 Version', 'Two versions of the same beacon', 'The higher version wins', T('NOT STARTED')],
], [0.15, 0.30, 0.40, 0.15]))

# ------------------------------------------------------------------ 8
S += H1('8. Failure cases ' + T('DESIGN ONLY'))
S.append(tbl([
    ['What fails', 'Consequence', 'Planned response'],
    ['A beacon is stale', 'Old information may be wrong', 'Use as a hint only; own sensors decide'],
    ['A beacon is contradicted by a sensor', 'Wrong guidance or a false alarm', 'Flag, discard, record; continue with the next beacon'],
    ['A beacon in the chain is missing or dead', 'The chain is broken', 'Fall back to the last direction and distance, then local search; give up after a limit'],
    ['No beacon can be received (radio failure)', 'The Executor is blind', 'Rely on dead reckoning and the briefing; stop safely if lost'],
    ['Heading drifts or is lost', 'The robot steers off course', 'Wall-based correction and beacon position resets; stop if the estimate is clearly wrong'],
    ['Stuck on an obstacle the LiDAR cannot see', 'No progress', 'Back up and turn; after repeated stalls, abort and exit'],
    ['The target is blocked (for example by a hole)', 'The mission cannot be completed', 'Report “target unreachable”; do not cross'],
    ['Briefing not delivered or corrupted', 'Entering without a plan', 'Do not enter until a valid briefing is acknowledged'],
    ['Clocks not synchronised', 'Ages are wrong, so trust is wrong', 'Synchronise from GPS time before entry; log the sync'],
    ['Low battery', 'Mission cannot finish', 'Abort and exit while energy remains'],
    ['Tip-over', 'Danger to the robot', 'SAFE_STOP'],
], [0.30, 0.25, 0.45]))

# ------------------------------------------------------------------ 9
S += H1('9. Open decisions')
S.append(P('“Responsible” assumes the four-role split; real names are unknown. No decision below has been made.', 'small'))
S.append(tbl([
    ['Item', 'Current status', 'Decision needed', 'Responsible'],
    ['Event types the Executor must handle', 'HAZARD, JUNCTION, HOLE coded on the Writer', 'Confirm; each one needs a sensor on the Executor to cross-check it', 'Writer owner + Executor owner'],
    ['Aging thresholds', 'Slide examples 2 / 15 / 40 min; AI proposal 5 / 30 min', 'Choose values; depend on the scenario', 'Beacon + Executor owners'],
    ['Who ages the message', 'Reader-side in the current proposal; the cahier lists a “message aging mechanism” under Beacon Design', 'Decide: beacon degrades its message, or the Executor computes the age', 'Beacon + Executor owners'],
    ['Beacons only vs briefing-assisted', 'Briefing-assisted in the current design', 'Accept, or put more geometry on the beacons', 'Whole team'],
    ['Proximity method and receiver radio', 'Three options in 5.3; none tested', 'Choose after radio tests', 'Beacon + Executor owners'],
    ['Heading consistency', 'Shared private-frame convention; method not decided', 'Wall correction, beacon resets, or both', 'Executor + Outside Network owners'],
    ['Does the Executor re-write beacons', 'Not required; the slide’s word “overwrite” suggests it', 'Decide; needs a transmitter and a write protocol', 'Beacon + Executor owners'],
    ['Mission and physical stand-in', 'Demo mission “reach the hot spot and extinguish”, simulated', 'Confirm the mission and a safe tool', 'Whole team'],
    ['Must the Executor exit?', 'Not stated in the documents', 'Decide; matters for “extract” and “retrieve”', 'Whole team'],
    ['Briefing delivery', 'Not decided', 'Link and acknowledgement method', 'Outside Network + Executor owners'],
    ['Computer and hardware reuse', 'UNO Q suggested for reuse', 'Choose', 'Executor owner'],
], [0.20, 0.28, 0.32, 0.20]))

# ------------------------------------------------------------------ 10
S += H1('10. What the Executor must deliver, and next steps')
S.append(tbl([
    ['', 'Task', 'Why'],
    ['☐', 'Agree the briefing (I5) with the Outside Network owner, and the beacon message and aging rules with the Beacon owner', 'Everything else depends on these interfaces'],
    ['☐', 'Decide the aging thresholds, who computes the age, and beacons-only vs briefing-assisted', 'Core of “trust by age”'],
    ['☐', 'Write a simulated Executor (reception, trust module, chain follower, mission action) and run tests E1–E7', 'Executor robot (5) and the simulation demo (8)'],
    ['☐', 'Draw the Executor architecture and data-flow diagrams (state flow in Figure 1 is a draft)', 'Technical solution diagrams (5)'],
    ['☐', 'Write the Executor failure cases (section 8) and record the results of the tests', 'Failure cases (3)'],
    ['☐', 'List the final-phase hardware, a timeline to 01/12/2026, and the risks', 'Implementation plan (3); physical prototype (15) later'],
    ['☐', 'Write the “Outside Network and Executor” part of the 6-page report (about 0.7 pages shared with the Outside Network owner)', 'Technical report (2)'],
], [0.04, 0.62, 0.34]))
S.append(Spacer(1, 4))
S.append(P('<b>Not yet done by anyone:</b> opening the two links inside the official cahier des charges — the “System Architecture Diagram” resource (a Google Drive file) and the submission form. The architecture diagram may show what the organizers expect for the Executor. The links are listed in section 2.2 of the handover PDF.'))
doc.build(S)
print('built')
