from __future__ import annotations

from dataclasses import dataclass, field
from textwrap import dedent
from typing import Callable, Dict, List, Tuple


LOW_LUCIDITY_THRESHOLD = 2
COURAGE_FOR_AGENCY = 6
HIDDEN_OMEN_THRESHOLD = 5


@dataclass
class GameState:
    courage: int = 3
    lucidity: int = 4
    reason: int = 4
    sent_evidence: bool = False
    outside_contact: bool = False
    low_lucidity_streak: int = 0
    chapter: int = 0
    final_choice: str | None = None
    omen_marks: int = 0
    notes: List[str] = field(default_factory=list)
    omens: List[str] = field(default_factory=list)

    def apply(self, courage: int = 0, lucidity: int = 0, reason: int = 0, note: str | None = None) -> None:
        self.courage = max(0, min(self.courage + courage, 8))
        self.lucidity = max(0, min(self.lucidity + lucidity, 8))
        self.reason = max(0, min(self.reason + reason, 8))
        if note:
            self.notes.append(note)

    def mark_omen(self, text: str) -> None:
        self.omen_marks += 1
        self.omens.append(text)

    def register_checkpoint(self) -> None:
        if self.lucidity <= LOW_LUCIDITY_THRESHOLD:
            self.low_lucidity_streak += 1
            self.mark_omen("A scene ended with the mind dim and still walking.")
        else:
            self.low_lucidity_streak = 0


@dataclass
class CommandResult:
    status: str
    text: str


@dataclass
class Interaction:
    text: str
    effect: Callable[[GameState], None] | None = None
    tag: str | None = None
    once: bool = True
    repeat_text: str | None = None


@dataclass
class Scene:
    title: str
    prose: str
    think: str
    hint: str
    interactions: Dict[Tuple[str, str], Interaction]
    required_tags: set[str]
    continue_text: str
    blocked_text: str
    seen_tags: set[str] = field(default_factory=set)
    used_keys: set[Tuple[str, str]] = field(default_factory=set)


INTRO = dedent(
    """
    SISYPHUS v1.3
    State Police Archive / Case 14-77-WREN

    Booting memory...
    Booting weather...
    Booting the old harm...

    There is no save file for a hometown.
    """
).strip()


HELP_TEXT = dedent(
    """
    Commands:
    LOOK <THING>     inspect rooms, objects, gestures
    ASK <PERSON>     press a witness or memory
    READ <THING>     examine a notebook, file, memo, or note
    CALL <PERSON>    reach outside the room when possible
    DRINK <THING>    accept local anesthesia
    HOLD <THING>     keep paper, truth, or nerve in your own hands
    THINK            hear the internal voices
    STATUS           inspect COURAGE / LUCIDITY / REASON
    CONTINUE         leave the current subscene once enough has been faced
    HELP             show this screen
    QUIT             leave the game
    """
).strip()


ENDING_TEXT: Dict[str, str] = {
    "A": dedent(
        """
        The arrest happens in daylight because institutions prefer their violence visible enough to photograph. Gabriel
        does not resist. Evelyn spits once onto the courthouse steps, missing your shoes by less than an inch. Chief
        Bell keeps his hat on. Captain Rourke arrives in a dark coat and calls your work "messy but salvageable," which
        is as close to praise as men like him come.

        Gabriel tries, once, to tell them about your father. About the porch. About Lena Vale. About the night your
        mind split itself like wet wood. He sounds tired, furious, unwell. The county has been waiting years for a
        reason not to believe a Mercer man. It accepts the gift at once.

        The official story enters the archive cleanly. Dispossessed brother kills modernization patriarch and family in
        retaliatory spree. State investigator overcomes local entanglement and secures arrest. The papers love the shape
        of it. The shape is all they were ever hungry for.

        Months later, in Philadelphia, Mara asks why you wake up standing in the kitchen with your hand on the drawer
        where the knives are kept. You tell her you don't know. This is not entirely a lie.
        """
    ).strip(),
    "B": dedent(
        """
        You burn the copies first because paper is easier to kill than memory. The originals take longer. Plastic
        sleeves curl. Ink browns. Names blacken and leave behind a sugar smell that has no business belonging to
        evidence. Gabriel watches from the yard with his hands in his pockets. Evelyn does not watch at all. She stands
        at the sink, washing a cup that has already been washed.

        No one speaks of absolution. That would be theatrical. What returns instead is routine, which is the crueler
        thing. Gabriel finds work hauling scrap and repairing engines for men too poor to buy new parts. Evelyn keeps
        the house exact. You drive back east, then back again, then away, then back, until travel itself becomes an
        argument you are no longer invested in winning.

        Life resumes in the way punishment often does: not dramatically, but repeatedly. Breakfast. Calls. Bills. Rain
        in the gutters. A knife drawn once to cut meat, once to open a parcel, once because a dream climbed out of
        sleep wearing your father's voice.

        You do not heal. Neither do they. You continue. The rock does not become lighter. You only become more practiced
        at putting your shoulder to it.
        """
    ).strip(),
    "C": dedent(
        """
        You understand with dreadful calm that the law was only ever a more decorative method of deciding who gets to
        survive the story. Gabriel sees it in your face a second before he moves. Evelyn sees it sooner and does not
        move at all.

        What happens next is brief, ugly, and almost silent. The body remembers efficient things the conscience never
        consented to learn. When it is over, the kitchen is transformed into a room you have known your whole life
        without admitting it: the family room, stripped to function.

        You clean because cleaning is what comes after. You stage because staging is what men call hope when they are no
        longer entitled to innocence. Chief Bell will suspect. Maybe Bell always suspects everything. The county will
        nod at whatever version best preserves its habits.

        In the years that follow, you become meticulous. Commended, even. Your reports are clear. Your arrests are
        proper. Your shoes remain polished. On certain winter mornings you wake before dawn and stand very still in the
        dark, listening for the buried to begin speaking. Some mornings they do. Then you go to work.
        """
    ).strip(),
    "HIDDEN": dedent(
        """
        The truth does not arrive like lightning. It seeps. A stain through plaster. A smell under a door. By the time
        it forms words, part of you has known for days.

        Chief Bell sets the file on the table and does not sit down.

        "You wanted it to be your brother because family is easier to narrate when the guilt lives one chair over," he
        says. "You wanted the town to be corrupt, your mother to be complicit, Gideon Wren to be a tyrant, Gabriel to be
        the avenger, and yourself to be the man who solved it. That's a beautiful machine. Shame it runs on lies."

        The details come back without asking permission: Gideon sneering at the badge, the children upstairs, Mrs. Wren
        saying something about men who mistake authority for worth, your own voice turning official because official was
        the only kind of power you trusted, your hand already moving before your thoughts had become language.

        You killed them because you were insulted, because you were angry, because your brother had suffered, because the
        town had made you into a vessel for every unspent grievance in its streets. No grand motive survives contact with
        the act. Only impulse in a uniform.
        """
    ).strip(),
}


def determine_ending(state: GameState) -> str:
    if state.sent_evidence and state.outside_contact:
        return "A"
    if (state.low_lucidity_streak >= 3 and state.omen_marks >= 4) or (
        state.low_lucidity_streak >= 2 and state.omen_marks >= HIDDEN_OMEN_THRESHOLD
    ):
        return "HIDDEN"
    if state.lucidity <= 1 or state.reason <= 1:
        return "C"
    if state.final_choice == "TURN":
        return "A"
    if state.final_choice == "KILL":
        return "C"
    if state.final_choice == "BURN":
        return "B"
    if state.courage >= COURAGE_FOR_AGENCY:
        return "B"
    return "C"


def parse_command(raw: str) -> tuple[str, str]:
    parts = raw.strip().upper().split()
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


def _soften_repeat(text: str) -> str:
    return dedent(text).strip()


def _interaction(
    text: str,
    *,
    effect: Callable[[GameState], None] | None = None,
    tag: str | None = None,
    once: bool = True,
    repeat_text: str | None = None,
) -> Interaction:
    return Interaction(
        text=dedent(text).strip(),
        effect=effect,
        tag=tag,
        once=once,
        repeat_text=_soften_repeat(repeat_text or text),
    )


def _chain(*effects: Callable[[GameState], None]) -> Callable[[GameState], None]:
    def _runner(state: GameState) -> None:
        for effect in effects:
            effect(state)

    return _runner


def _send_evidence(state: GameState) -> None:
    state.sent_evidence = True
    state.apply(courage=1, lucidity=1, note="You sent the evidence package upriver.")


def _hold_evidence(state: GameState) -> None:
    state.apply(courage=1, reason=-1, note="You kept the evidence inside the county line.")


def _outside_call(state: GameState) -> None:
    state.outside_contact = True
    state.apply(reason=1, lucidity=-1, note="You let an outside voice touch the case.")


def _drink_whiskey(state: GameState) -> None:
    state.apply(lucidity=-1, reason=-1, note="You accepted whiskey as a local theology.")
    if state.lucidity <= 2:
        state.mark_omen("Whiskey lowered the room until the badge looked familiar for the wrong reason.")


def _notebook_effect(state: GameState) -> None:
    state.apply(reason=1, courage=1, note="You read the children's notebook instead of protecting yourself from it.")
    if state.lucidity <= 3:
        state.mark_omen("The policeman in the child's drawing stood with your posture.")


def _hospital_effect(state: GameState) -> None:
    state.apply(courage=2, lucidity=1, note="You read the hospital file in full.")
    if state.omen_marks >= 1:
        state.mark_omen("The file recognized you before you recognized yourself.")


def _porch_effect(state: GameState) -> None:
    state.apply(courage=1, note="You let the porch remain a map instead of a metaphor.")
    if state.lucidity <= 3:
        state.mark_omen("The porch felt less like a memory than a floor plan waiting for your name.")


def _bell_photo_effect(state: GameState) -> None:
    state.apply(courage=1, reason=1, note="You opened Bell's off-book envelope and saw the county posing beside its wound.")
    if state.lucidity <= 3:
        state.mark_omen("The line of laid-off men blurred until one of them wore your face.")


def _photo_effect(state: GameState) -> None:
    state.apply(courage=1, note="You read the family photograph as evidence rather than nostalgia.")
    if state.lucidity <= 3:
        state.mark_omen("In the old family photo you kept recognizing an officer nobody had hired yet.")


def _broken_memory_effect(state: GameState) -> None:
    state.apply(courage=1, lucidity=-1, reason=-1, note="Memory stopped narrating and started staging.")
    state.mark_omen("The missing sequence returned as police procedure with your hands already inside it.")


def build_think_text(scene: Scene, state: GameState) -> str:
    lines = [scene.think.strip()]
    if state.lucidity <= 2:
        lines.append("GLASS: The badge in the child's drawing has your posture when nobody is looking.")
        lines.append("MUD: Don't organize this. Let it stay swamp instead of fact.")
        lines.append("GLASS: Swamp is where evidence goes to die.")
        lines.append("MUD: Evidence is where sleep goes to die.")
    if state.low_lucidity_streak >= 1:
        lines.append("RUST: Low light makes old tools volunteer for work.")
        lines.append("GLASS: Stop calling violence a tool. That's how you forgive yourself.")
        lines.append("RUST: No. That's how you admit the county built you from scrap.")
    if state.omen_marks >= 2:
        lines.append("CHOIR: Porch. Badge. Insult. Children upstairs. The same room keeps rebuilding itself.")
        lines.append("MUD: Don't listen to them. They're making a story out of symptoms.")
        lines.append("CHOIR: Symptoms are how the truth survives when the narrative collapses.")
    if state.omen_marks >= 4:
        last_omen = state.omens[-1] if state.omens else "Something in you has started writing ahead of the facts."
        lines.append(f"CHOIR: {last_omen}")
        lines.append("GLASS: You're not the center of the case.")
        lines.append("RUST: You're the product. That's worse.")
    return "\n".join(lines)


def make_scenes() -> List[Scene]:
    return [
        Scene(
            title="Chapter 1.1: The police station lobby",
            prose=dedent(
                """
                The station has the tired cleanliness of a place that gave up on dignity and settled for bleach. A fake
                ficus droops in the corner like a punished man. Carla Wynn sits behind the desk and says your name like
                she is checking whether an old debt has matured. Outside, dawn has not committed itself. Inside, the
                county has already begun treating your return as an administrative weather event.
                """
            ).strip(),
            think="RUST: Towns like this don't die. They cool.\nGLASS: Begin with the fresh dead.\nMUD: Keep driving.\nCHOIR: Home again, little witness.",
            hint="Available leads: LOOK LOBBY, LOOK DESK, ASK CARLA, READ DISPATCH, CONTINUE.",
            interactions={
                ("LOOK", "LOBBY"): _interaction(
                    """
                    The lobby smells of bleach, paperwork, wet wool, burnt coffee, and the stale patience of people
                    waiting for the state to remember them in the correct order. Somebody has painted the walls a
                    cheerful municipal cream that only makes the fluorescent lights look more judgmental.
                    """
                ),
                ("LOOK", "DESK"): _interaction(
                    """
                    Carla's desk is a geography of low-grade emergency: paper cups furred brown at the rim, a county
                    calendar featuring waterfalls nobody in Saint Barrow has the money or temperament to visit, a
                    telephone that rings with the moist indignation of the recently abandoned.
                    """
                ),
                ("ASK", "CARLA"): _interaction(
                    """
                    "Town spends twenty years trying to get rid of its sons," Carla says. "One bad week and suddenly it
                    wants one back."

                    "I didn't know it wanted me."

                    "It doesn't. It wants paperwork with a familiar face attached. That's not the same thing."

                    When you ask about Gabriel, she studies your coat, your badge, the city sewn into your posture. "The
                    county says his name the way church women say appetite. Quietly, but with real interest."
                    """,
                    effect=lambda state: state.apply(courage=1, note="You pressed Carla about Gabriel."),
                    tag="CARLA",
                ),
                ("READ", "DISPATCH"): _interaction(
                    """
                    WREN FAMILY HOMICIDE.
                    LOCAL REQUESTING STATE SUPPORT.
                    RETURNING OFFICER: MERCER, JONAH.

                    Returning, you think. As if there had been another verb available.
                    """
                ),
            },
            required_tags={"CARLA"},
            blocked_text="You are not done with the lobby yet. The county is still introducing itself through Carla.",
            continue_text="You leave the desk and head toward Bell's office with the old town already climbing your back.",
        ),
        Scene(
            title="Chapter 1.2: Chief Bell's office",
            prose=dedent(
                """
                Chief Amos Bell has turned age into a style of hospitality. His office smells of cedar polish, old
                coffee, and the long defeat of public service. He rises smiling with most of his face and almost none of
                his eyes. Behind him, file cabinets stand like blunt gray priests.
                """
            ).strip(),
            think="GLASS: He knows something adjacent to the truth.\nRUST: Men like Bell never mine. They buy what falls out of workers.\nMUD: Drink the coffee.\nCHOIR: Ask him who dug.",
            hint="Available leads: LOOK OFFICE, ASK BELL, READ CASEBOARD, CONTINUE.",
            interactions={
                ("LOOK", "OFFICE"): _interaction(
                    """
                    The office has the civic warmth of a room paid for by taxes and bad faith in equal measure. A county
                    map hangs on the wall with old pushpins still marking flood zones, overdose clusters, and one school
                    closure from a decade ago. The pins remain because local government mistakes retention for care.
                    """
                ),
                ("ASK", "BELL"): _interaction(
                    """
                    "Memory is the problem with towns like this," Bell says. "Big cities can sin and keep moving. Towns
                    sin in place. That's why everybody here looks so tired. They keep sleeping in the same courtroom."

                    "You asked for state support."

                    "I asked for help. State sent biography."
                    """,
                    effect=lambda state: state.apply(reason=1, note="You took Bell's measure in daylight."),
                    tag="BELL",
                ),
                ("READ", "CASEBOARD"): _interaction(
                    """
                    Bell's board holds the present case in dry fragments: no forced entry, Gideon Wren mutilated beyond
                    necessity, Mrs. Wren in the pantry, children upstairs, partial boot impression near the service
                    porch, papers missing from the study. Even pinned to cork, class murder tries to look like weather.
                    """
                ),
            },
            required_tags={"BELL"},
            blocked_text="Bell has not yet finished turning tragedy into county language.",
            continue_text="You leave Bell's office with coffee smell in your clothes and the Wren address in your jaw.",
        ),
        Scene(
            title="Chapter 2.1: The Wren house exterior",
            prose=dedent(
                """
                The Wren house stands above town on Orchard Rise, where the old owners built homes designed to look
                permanent. Wide porch. Stone lions. Dead hydrangeas. Money translated into architecture by people who
                expected weather to respect invoices. Police tape moves in the wind with the weak ceremony of institutional grief.
                """
            ).strip(),
            think="GLASS: Start with the house pretending not to know what happened inside it.\nRUST: Money rots slower, not cleaner.\nMUD: Stay outside.\nCHOIR: The porch again.",
            hint="Available leads: LOOK PORCH, LOOK DRIVE, ASK PATROLMAN, CONTINUE.",
            interactions={
                ("LOOK", "PORCH"): _interaction(
                    """
                    The porch runs wide across the front of the house like a declaration of social confidence. Yet the
                    boards by the service side hold a different language: mud smears, a partial print, the kind of mark
                    that says a body once believed exit was still possible.
                    """,
                    effect=_porch_effect,
                    tag="PORCH",
                ),
                ("LOOK", "DRIVE"): _interaction(
                    """
                    Gravel, tire marks, winter grass, tape, one dropped latex glove now collecting cold water in its
                    fingers. Crime scenes always look accidental once enough people have photographed them.
                    """
                ),
                ("ASK", "PATROLMAN"): _interaction(
                    """
                    The patrolman recognizes you and pretends not to. "Nothing new outside," he says. "House is worse
                    than it looks. Which is saying something."
                    """,
                    tag="PATROLMAN",
                ),
            },
            required_tags={"PORCH"},
            blocked_text="The house has barely introduced itself.",
            continue_text="You step inside with the service porch still moving at the edge of your mind.",
        ),
        Scene(
            title="Chapter 2.2: Foyer and study",
            prose=dedent(
                """
                Inside, the foyer still believes in respectability. The study still believes in ownership. Coats are
                gone, bodies are gone, but arrangement remains. In wealthy houses the furniture continues asserting moral
                authority long after the blood has begun disagreeing. Wealth does not prevent violence. It only delays
                the moment when violence is allowed to look ordinary.
                """
            ).strip(),
            think=(
                "GLASS: The room has already testified.\n"
                "RUST: Progress always leaves receipts.\n"
                "MUD: Do not touch the desk. Touching makes it intimate.\n"
                "GLASS: Intimacy is not evidence.\n"
                "RUST: In a town like this, intimacy is how evidence reproduces.\n"
                "CHOIR: Read what rich men call transition and then act surprised when it births revenge."
            ),
            hint="Available leads: LOOK FOYER, LOOK DESK, READ CALENDAR, READ DRAWER, CONTINUE.",
            interactions={
                ("LOOK", "FOYER"): _interaction(
                    """
                    Umbrella stand, mirror, runner rug, silver bowl for keys. The ordinary paraphernalia of people who
                    expected tomorrow to arrive on time. Domestic order is often just confidence with polishing cloths.
                    """
                ),
                ("LOOK", "DESK"): _interaction(
                    """
                    Gideon Wren's desk smells like old paper and the sweet medicinal rot of expensive cigars. The folders
                    are color-coded. That small fact contains an entire philosophy: the world is manageable; pain can be
                    categorized; loss is a metric; a town can be converted into a line item called transition.

                    The bloodstain has already browned into topography. Violence did not merely interrupt the room. It
                    revised the room into plain English.

                    GLASS: You're drifting.
                    RUST: No. You're pretending homicide is separate from what made the county hungry.
                    MUD: Stop talking. The room is still warm where the lie used to sit.
                    """,
                    effect=lambda state: state.apply(courage=1, note="You stayed in Gideon Wren's study long enough to hate its furniture."),
                    tag="DESK",
                ),
                ("READ", "CALENDAR"): _interaction(
                    """
                    One entry has been circled twice:

                    DINNER - BELL / MERCER CLAIMS / TRANSITION PACKAGE.

                    Mercy has terrible penmanship when translated through management.
                    """
                ),
                ("READ", "DRAWER"): _interaction(
                    """
                    Old correspondence. Layoff claims. Compensation disputes. Union pressure. One letter refers to a
                    meeting with Bell and "the state boy who came home polished." The phrase lands wrong and keeps
                    landing.
                    """
                ),
            },
            required_tags={"DESK"},
            blocked_text="The study is still pretending to be cleaner than its vocabulary.",
            continue_text="You move deeper into the house, from ownership into domestic aftermath.",
        ),
        Scene(
            title="Chapter 2.3: Pantry and children's rooms",
            prose=dedent(
                """
                The pantry and the upstairs rooms belong to the part of the house that expected repetition: preserved
                fruit, schoolwork, beds half made, tomorrow's small tasks. Which is to say they are the rooms least built
                for massacre and therefore the ones that indict it most completely.
                """
            ).strip(),
            think="MUD: Go outside.\nGLASS: Stay.\nRUST: Children inherit weather before forecast.\nCHOIR: The drawing. The hat. The badge.",
            hint="Available leads: LOOK PANTRY, LOOK ROOM, READ NOTEBOOK, CONTINUE.",
            interactions={
                ("LOOK", "PANTRY"): _interaction(
                    """
                    Shelves of preserves. Flour in labeled bins. Vinegar. Salt. Christmas tins waiting for a holiday that
                    now belongs to evidence tags. The pantry is the cruelest room in the house because it was built to
                    outlast winter, not history.
                    """
                ),
                ("LOOK", "ROOM"): _interaction(
                    """
                    A blanket half folded. A plastic horse under the dresser. Stickers on the mirror applied with the
                    furious imprecision of a child who assumed correction would always be available tomorrow.
                    """
                ),
                ("READ", "NOTEBOOK"): _interaction(
                    """
                    Dad says people here hate him because they want the world to stay broken in a familiar way.

                    On the next page a child has drawn factory stacks, a church steeple, a police car, and a little man
                    in a hat too large for his body. Adults dismiss this sort of drawing as childish until the day it
                    starts looking like testimony.
                    """,
                    effect=_notebook_effect,
                    tag="NOTEBOOK",
                ),
            },
            required_tags={"NOTEBOOK"},
            blocked_text="You have not yet let the children revise your theory of the house.",
            continue_text="You leave the Wren place with paper dust on your fingers and innocence lodged like glass in your throat.",
        ),
        Scene(
            title="Chapter 3.1: The mother house exterior and kitchen",
            prose=dedent(
                """
                Your mother's house has not changed because change requires either hope or money. The porch sags in the
                exact places it used to. The screen door still snaps shut like an old insult. Inside, the kitchen smells
                of coffee, bleach, onions, and radiator heat, which is to say it smells like every season you survived here.
                """
            ).strip(),
            think="RUST: She kept the house alive with triage.\nGLASS: Do not confuse procedure with love.\nMUD: Eat and say nothing.\nCHOIR: The sink remembers more than you do.",
            hint="Available leads: LOOK KITCHEN, LOOK SINK, LOOK PORCH, CONTINUE.",
            interactions={
                ("LOOK", "KITCHEN"): _interaction(
                    """
                    A pot simmers without urgency. A dish towel lies folded on the table. A Bible sits under a gas bill.
                    A cigarette burn from twenty years ago still interrupts the varnish with more honesty than most men
                    ever brought to the room.
                    """,
                    tag="KITCHEN",
                ),
                ("LOOK", "SINK"): _interaction(
                    """
                    The enamel sink is chipped near the drain. You remember blood in it once, though memory refuses to
                    say whose. Kitchens are where this family processed both hunger and aftermath.
                    """
                ),
                ("LOOK", "PORCH"): _interaction(
                    """
                    Under the porch, darkness gathers in a shape no grown man should still fear and no child should ever
                    have learned to map.
                    """,
                    effect=_porch_effect,
                ),
            },
            required_tags={"KITCHEN"},
            blocked_text="The house has only just let you in.",
            continue_text="Your mother sets stew on the table the way officials set terms.",
        ),
        Scene(
            title="Chapter 3.2: The meal that is not a meal",
            prose=dedent(
                """
                Evelyn puts food between you and the weather because that is the oldest arrangement this family ever
                managed to honor. The chair complains beneath you in the same pitch it used to make when your father
                dropped into it after third shift. Your body remembers before your mind catches up.
                """
            ).strip(),
            think=(
                "GLASS: She is telling the truth in the shape she can bear.\n"
                "RUST: Poor men call weather what rich men authored.\n"
                "MUD: Let the stew do the talking.\n"
                "GLASS: Stew is not testimony.\n"
                "RUST: In this house, stew is how women keep testimony alive.\n"
                "CHOIR: Ask like a son. Ask like a cop. Fail both ways, then pretend the failure was professionalism."
            ),
            hint="Available leads: ASK EVELYN, READ BIBLE, CONTINUE.",
            interactions={
                ("ASK", "EVELYN"): _interaction(
                    """
                    "You want facts," Evelyn says. "Fine. Your father broke a plate over my shoulder on Christmas Eve and
                    everybody called it a hard season. Gabriel worked twelve years at the foundry and when the line shut
                    down they gave him a pamphlet and a coffee mug and called it restructuring. You disappeared for half
                    your life and when you came back in a state car they called it service. Facts are what men name
                    things after they've already decided not to care."

                    She looks at you like she is deciding whether your badge counts as an apology or an insult.

                    "Men love confession because it lets them feel noble while making another woman clean up the
                    consequence," she says. "Cleanup is where people live. Confession lasts a minute. Cleanup lasts
                    decades. You want a case with a beginning and an end because your institution sells closure in
                    packets. This house never had closure. It had heat bills."

                    She keeps talking the way a woman talks when she has been interrupted for forty years and finally
                    decides to stop cooperating.

                    "You want to know why I don't cry?" she asks. "Because crying is expensive. It takes time. It takes
                    privacy. It takes the belief that somebody will hold the room steady while you fall apart. I never
                    had that. I had dishes. I had the electric bill. I had you boys growing like weeds in a yard full of
                    broken glass. I had Harrow coming home with his hands smelling like the plant and his mouth smelling
                    like the bar and his conscience smelling like nothing at all."

                    GLASS: This is testimony. Hold onto it.
                    MUD: This is fire. Get away from it.
                    RUST: This is the county's unpaid labor speaking.
                    CHOIR: This is what the town survives on: women turning emergencies into routine.

                    "Men like your father didn't think of themselves as violent," Evelyn says, voice steady. "They
                    thought of themselves as entitled to release. And women like me learn the worst arithmetic: how to
                    subtract damage without ever reaching zero."

                    She glances at the sink as if it is an old judge.

                    "Cleanup isn't just mopping. Cleanup is hiding bruises under sleeves so the school doesn't ask
                    questions it can't afford. Cleanup is making jokes so the neighbors can keep their comfort. Cleanup
                    is teaching a boy to flinch quietly. Cleanup is sending one son out into the world with a badge
                    because at least a badge is a story people respect. Cleanup is staying behind with the other son and
                    making sure his anger doesn't burn the house down. And sometimes," she says, almost gently, "cleanup
                    is failing anyway and still getting up at six to make coffee."

                    GLASS: She's building a motive.
                    MUD: She's building a prison.
                    RUST: Motive and prison are the same blueprint here.
                    CHOIR: You came back looking for a killer. She is describing a sentence.
                    """,
                    effect=lambda state: state.apply(courage=1, reason=1, note="You forced Evelyn into the old vocabulary of layoffs and blame."),
                    tag="EVELYN",
                ),
                ("READ", "BIBLE"): _interaction(
                    """
                    The Bible is full of recipe cards, funeral leaflets, appointment reminders, and one electric bill
                    folded so often it has become almost devotional. Your mother's religion has never been purely
                    theological. It is part scripture, part triage, part unpaid clerical labor.
                    """
                ),
            },
            required_tags={"EVELYN"},
            blocked_text="The meal is still hiding behind procedure.",
            continue_text="The bowls cool. The old room refuses absolution. You drift toward Gabriel's empty room.",
        ),
        Scene(
            title="Chapter 3.3: Gabriel's empty room",
            prose=dedent(
                """
                Gabriel's room waits the way damaged men wait: neatly, without optimism, every object making only the
                claim it can survive. Repair manuals, a radio chassis, sorted screws, work boots under the bed, a
                calendar from the last full year of the plant still hanging because replacing it would imply sequence.
                """
            ).strip(),
            think="RUST: Broken machines confess in diagrams.\nGLASS: Men like Gabriel prefer parts to testimony.\nMUD: Leave the room untouched.\nCHOIR: He stayed. You polished.",
            hint="Available leads: LOOK ROOM, LOOK RADIO, CONTINUE.",
            interactions={
                ("LOOK", "ROOM"): _interaction(
                    """
                    Nothing here is decorative. Everything is provisional, repairable, or waiting to fail in a known way.
                    In wounded houses that can pass for peace.
                    """,
                    effect=lambda state: state.apply(courage=1, note="You entered Gabriel's room as a brother before acting like an officer."),
                    tag="ROOM",
                ),
                ("LOOK", "RADIO"): _interaction(
                    """
                    The radio chassis lies open beneath his tools. Gabriel trusts broken machines because they confess
                    their damage in diagrams. Human beings take years to admit even the obvious fracture and generally
                    insist on calling it complexity when cornered.
                    """
                ),
            },
            required_tags={"ROOM"},
            blocked_text="The room still expects at least one honest look.",
            continue_text="You leave with dust on your cuffs and the feeling that repair can become a religion if disappointment stays long enough.",
        ),
        Scene(
            title="Chapter 4.1: Hospital records office",
            prose=dedent(
                """
                Saint Barrow Memorial has been renovated in the shallow way failing hospitals are renovated: new signage,
                old despair. The clerk, Norma Leith, remembers you not as a detective but as a boy covered in blood and
                trying to keep his hands from existing.
                """
            ).strip(),
            think="GLASS: Ask what the file already knows.\nRUST: Hospitals archive pain in polite fonts.\nMUD: Leave before language hardens.\nCHOIR: The woman in the kitchen.",
            hint="Available leads: ASK NORMA, READ FILE, CONTINUE.",
            interactions={
                ("ASK", "NORMA"): _interaction(
                    """
                    "You were a quiet one," Norma says. "Quiet scared me more than screaming did."

                    "What was I treated for?"

                    "Trauma. Dissociative episodes. Gaps in autobiographical recall. A county-sized quantity of
                    possibility. Your town used to run on possibles. Saved everybody the trouble of certainty."
                    """
                ),
                ("READ", "FILE"): _interaction(
                    """
                    ADMISSION NOTES:
                    Patient arrived accompanied by mother and older male sibling. Shirt saturated with blood. Repeatedly
                    asks whether "he is still under the porch."

                    NURSING OBSERVATION:
                    Requests permission to wash hands repeatedly though hands appear already cleaned. States "It won't
                    stop being in the lines."

                    PSYCHIATRIC CONSULT:
                    Mentions father. Mentions "the woman in the kitchen" and later denies ever saying this.
                    """,
                    effect=_hospital_effect,
                    tag="FILE",
                ),
            },
            required_tags={"FILE"},
            blocked_text="The file is still waiting to be read in the only tone it respects.",
            continue_text="The hospital returns your name to you in an older font and you carry it down to the county archive.",
        ),
        Scene(
            title="Chapter 4.2: County archive basement",
            prose=dedent(
                """
                The county archive basement is colder than the weather outside because buildings that store denied facts
                eventually generate their own climate. Steel shelves, damp boxes, rust smell, white light. Paper is what
                a town uses when it wants to admit a thing happened without agreeing to remember it.
                """
            ).strip(),
            think="RUST: Informally. Stabilization. Community.\nGLASS: Bureaucracy teaches violence to conjugate politely.\nMUD: Mistake atmosphere for evidence if you want to go mad efficiently.\nCHOIR: Every file box is a coffin for a fact somebody outlived.",
            hint="Available leads: READ MEMO, READ REPORTS, CONTINUE.",
            interactions={
                ("READ", "MEMO"): _interaction(
                    """
                    SUBJECT: COMMUNITY STABILIZATION FOLLOWING PHASE-OUT

                    Recommendations:
                    - increased patrol presence near foundry district taverns
                    - discourage organized demonstrations likely to trigger press attention
                    - facilitate private discussions between management and "aggrieved heads of household"

                    Aggrieved heads of household. The phrase smells like whiskey, aftershave, and fear of elections.
                    """,
                    effect=lambda state: state.apply(reason=1, note="You read the archive memo and found Bell inside the weather."),
                    tag="MEMO",
                ),
                ("READ", "REPORTS"): _interaction(
                    """
                    Domestic disturbance reports involving Harrow Mercer. None resulted in charges. One complaint is
                    filed by Evelyn, then crossed out and rewritten as anonymous. Another ends with "parties counseled
                    informally." Such a beautiful word for abandonment.
                    """
                    ,
                    tag="REPORTS",
                ),
            },
            required_tags={"MEMO"},
            blocked_text="The basement has not yet handed you the county's preferred euphemisms.",
            continue_text="You take the copied pages upstairs where the city begins calling through your phone.",
        ),
        Scene(
            title="Chapter 4.3: The superior call",
            prose=dedent(
                """
                Rourke calls while you are holding copied reports under your arm. His name on the screen feels like a
                city interrupting a confession. Between the fluorescent light and the damp paper, the choice looks more
                moral than it is.
                """
            ).strip(),
            think="GLASS: Chain of custody exists because men lie.\nRUST: Outsiders call it objectivity when they don't have to bury consequences.\nMUD: Close the laptop.\nCHOIR: Hold the paper. Hold the blood.",
            hint="Available leads: CALL ROURKE, HOLD FILES, CONTINUE.",
            interactions={
                ("CALL", "ROURKE"): _interaction(
                    """
                    "What have you got?" Rourke asks.

                    "Fragments."

                    "Then stop admiring them and package them. Local chief sent a strange preliminary. Smells like family
                    contamination."

                    You hate the phrase enough to send the packet just to stop hearing it.
                    """,
                    effect=_send_evidence,
                    tag="ROURKE",
                ),
                ("HOLD", "FILES"): _interaction(
                    """
                    You close the laptop without transmitting anything. Pride disguises itself as stewardship so
                    elegantly you almost salute it.
                    """,
                    effect=_hold_evidence,
                    tag="HELD",
                ),
            },
            required_tags=set(),
            blocked_text="The city is still asking what kind of son you plan to be with evidence in your hands.",
            continue_text="By evening the county has had time to sour and Bell has had time to choose a bar.",
        ),
        Scene(
            title="Chapter 5.1: The bar",
            prose=dedent(
                """
                The Lantern has not changed decor since the Carter administration and has not changed ethics since Cain.
                Neon beer signs hum against knotty pine walls. The air is salted with fryer grease, bleach, stale hops,
                and the wet-wool smell of men who have spent the day inside jackets older than ambition.
                """
            ).strip(),
            think=(
                "RUST: Older cops confuse corruption with regional flavor.\n"
                "GLASS: He wants you softened.\n"
                "MUD: Another drink and everything becomes atmosphere.\n"
                "GLASS: Atmosphere is how men avoid authorship.\n"
                "RUST: Atmosphere is how counties govern.\n"
                "CHOIR: Father, chief, brother, self. Different hats on one weather system."
            ),
            hint="Available leads: LOOK BAR, ASK BELL, DRINK WHISKEY, CONTINUE.",
            interactions={
                ("LOOK", "BAR"): _interaction(
                    """
                    The booths are split and patched. Somebody carved GO HOME into the table long enough ago for the
                    edges to have softened. Two men at the bar recognize you and immediately become interested in their
                    bottles. That, more than any insult, tells you you've returned home.
                    """
                ),
                ("ASK", "BELL"): _interaction(
                    """
                    "Every small town has two justice systems," Bell says. "The one in the statute book and the one in
                    the diner. Most folks only ever meet the second one."

                    "And you work both?"

                    "I work weather," Bell says. "Statutes are for court. Weather is for keeping the county from chewing
                    through its own leash."

                    "That's a pretty name for corruption."

                    "Corruption is what outsiders call local memory when it won't sit still for handcuffs," he says.
                    Then, quieter: "You know what I hate about state boys? Not the badge. The tone. You all come in
                    talking like the world is a spreadsheet that simply needs better sorting."

                    His eyes linger on your mouth a fraction longer than the conversation requires.
                    When you wet your lip without thinking, he notices that too and does not grant either of you the
                    courtesy of looking away.

                    He takes a slow sip as if tasting the county itself.

                    "You know what modernization did?" he asks. "It taught half this county to speak the language of
                    resentment in complete sentences. Before that, most men only knew how to drink it. Then Wren and his
                    breed came through with charts, consultants, transition packages, all that laminated optimism. They
                    didn't just take wages. They professionalized humiliation. That's harder to forgive."

                    GLASS: He's romanticizing the county's rage. Beware.
                    RUST: No. He's confessing what the county prays to in private.
                    MUD: He's selling you a story because stories are cheaper than accountability.
                    CHOIR: He's selling you the county's excuse because excuses are its only export now.

                    "Before Wren, a man could lose his job and still pretend it was personal," Bell continues. "He could
                    point to a foreman, a fight, a bad week. It stayed human-sized. Then modernization arrives with its
                    binder full of inevitability: market forces, global competition, efficiency. You hear those words
                    enough and you start believing humiliation is physics, not authorship. That's when resentment becomes
                    religious."

                    He taps the side of his glass with one finger. A small, tidy sound. A municipal metronome.

                    "You know what a seminar is in a dying town?" he says. "It's a funeral where nobody says the name of
                    the dead. They tell you to adapt. They tell you to re-skill. They tell you to network. It's the same
                    sermon every time: become someone else. The cruel part is they say it like self-improvement instead
                    of eviction."

                    You realize he has been talking not to persuade you but to position you. To name the anger so it
                    won't name him. To put a collar on the county's teeth and claim he's doing public safety.

                    "And you," Bell adds, smiling, "you came back wearing the state's grammar. You know what that does to
                    a place like this? It turns everybody's misery into a file. It turns every insult into motive. The
                    county loves that. The county wants to feel structured while it rots."

                    When he reaches across the table, it is only to brush an invisible fleck from your sleeve. He lets
                    his knuckles drag just enough to make the gesture quit pretending to be accidental.

                    GLASS: He's baiting you into defensiveness.
                    RUST: He's right and he's weaponizing it.
                    MUD: Let him. Arguing will just make you louder.
                    CHOIR: Loud men are easier to blame. Quiet men are easier to use.
                    """,
                    effect=lambda state: state.apply(reason=1, note="You let Bell preach his civic corruption at full volume."),
                    tag="BELLBAR",
                ),
                ("DRINK", "WHISKEY"): _interaction(
                    """
                    The whiskey tastes of oak, sugar, and municipal despair. Around here, drinking is often mistaken for
                    honesty because both eventually lower the lights. You can feel your mind trying to translate the
                    county into something manageable: a case file, a motive, a list of names. Whiskey teaches a different
                    grammar. It makes everything sound inevitable. Bell watches you swallow with the patience of a man
                    waiting to see whether desire and opportunity will decide to use the same door.
                    """,
                    effect=_drink_whiskey,
                    once=False,
                    repeat_text="Another swallow. The room softens and grows more persuasive in all the wrong directions.",
                ),
            },
            required_tags={"BELLBAR"},
            blocked_text="Bell is still setting the moral weather for the night.",
            continue_text="Bell pays and says there is something else you should see off the books.",
        ),
        Scene(
            title="Chapter 5.2: The off-book files",
            prose=dedent(
                """
                The annex room the county calls storage is really conscience overflow. A desk, a light with a bad buzz,
                metal cabinets, a lock turned with too much care. For a minute the brown envelope stays untouched while
                Bell stands close enough for the whole exchange to become deniable. His fingers find your hand first,
                not to shake it, only to turn it over as if there were something written in the palm worth reading.
                Later he smooths a hand once through your hair with the absentminded care of a man pretending this is
                tenderness and not leverage. You let none of it stop because the envelope remains unopened on purpose.
                By the time he finally leaves the packet in the center of the desk and you have finished putting your
                clothes back into county order, the county's oldest bargain has already been conducted in private.
                """
            ).strip(),
            think="GLASS: Open it.\nRUST: County power keeps backups for guilt the way churches keep basements.\nMUD: Leave it sealed.\nCHOIR: He wants you implicated because implicated men are predictable.",
            hint="Available leads: READ ENVELOPE, ASK BELL, CONTINUE.",
            interactions={
                ("READ", "ENVELOPE"): _interaction(
                    """
                    Inside are duplicated witness statements, a severance petition, and one photograph of Gideon Wren
                    shaking hands outside the plant while a line of laid-off men stand behind the frame looking like
                    unpaid scenery to history.
                    """,
                    effect=_bell_photo_effect,
                    tag="ENVELOPE",
                ),
                ("ASK", "BELL"): _interaction(
                    """
                    "A badge doesn't make a man moral," Bell says. "It just gives him a filing cabinet for his appetite."
                    """,
                    tag="BELLANNEX",
                ),
            },
            required_tags={"ENVELOPE"},
            blocked_text="The envelope is still closed and Bell knows it.",
            continue_text="The annex smell follows you outside where the cold has the decency to be honest.",
        ),
        Scene(
            title="Chapter 5.3: After midnight choice",
            prose=dedent(
                """
                Outside the annex, night has become a material rather than an absence. Your car smells of paper, whiskey,
                and cologne. One cuff sits wrong where you fixed it too quickly and your hair refuses the shape you gave
                it back. The phone in your pocket feels like an accusation with reception.
                """
            ).strip(),
            think="GLASS: Call someone from away.\nRUST: Distance is not innocence. It is shipping.\nMUD: Stay in the parking lot until language blurs.\nCHOIR: The town always re-enters the line.",
            hint="Available leads: CALL MARA, DRINK WHISKEY, CONTINUE.",
            interactions={
                ("CALL", "MARA"): _interaction(
                    """
                    "Tell me something true," Mara says.

                    "This town still smells the same."

                    "That's not truth. That's weather."

                    "Bell has files he shouldn't. My brother is standing at the far end of every theory like a patient
                    man with his hands in his pockets."

                    She is quiet for a beat. "There is a kind of loyalty that is just fear with family photographs around it."
                    """,
                    effect=_outside_call,
                    tag="MARA",
                ),
                ("DRINK", "WHISKEY"): _interaction(
                    """
                    You drink alone in the parking lot like a man trying to make solitude look procedural.
                    """,
                    effect=_drink_whiskey,
                    once=False,
                    repeat_text="Another swallow. The dark starts arranging itself around whatever version of you it prefers.",
                ),
            },
            required_tags=set(),
            blocked_text="The night still expects you to let one outside voice cross the county line.",
            continue_text="You drive toward the hollow where your brother keeps stripped machines and unrepaired years.",
        ),
        Scene(
            title="Chapter 6.1: The approach",
            prose=dedent(
                """
                The hollow beyond the old service road is where Saint Barrow sends machines after it can no longer
                imagine them as useful. Rusted appliances and stripped car doors have weathered into local geology.
                Gabriel waits beneath a lean-to roof repairing a radio, which somehow makes the meeting crueler.
                """
            ).strip(),
            think="GLASS: He expected you.\nRUST: Brotherly love in damaged houses resembles shared labor on a grave.\nMUD: Stay in the truck.\nCHOIR: Witness or officer. Pick one and fail the other.",
            hint="Available leads: LOOK HOLLOW, LOOK RADIO, CONTINUE.",
            interactions={
                ("LOOK", "HOLLOW"): _interaction(
                    """
                    Broken washers, doors, bent fan housings, old mufflers. The place looks less like a dump than a
                    museum of interrupted usefulness.
                    """
                ),
                ("LOOK", "RADIO"): _interaction(
                    """
                    The radio chassis lies open beneath Gabriel's hands, obedient in a way memory never is. He trusts
                    broken machines because they confess their damage in diagrams.
                    """,
                    tag="RADIO",
                ),
            },
            required_tags={"RADIO"},
            blocked_text="The hollow expects at least one silent look before the talking starts.",
            continue_text="Gabriel sets down the screwdriver. The confession begins by pretending to be conversation.",
        ),
        Scene(
            title="Chapter 6.2: The first confession",
            prose=dedent(
                """
                Gabriel does not look surprised to see you. That hurts more than a threat would. His voice has the
                patience of a man who spent years swallowing things too large to digest and now regrets having such a
                strong throat.
                """
            ).strip(),
            think=(
                "GLASS: Push him past motive.\n"
                "RUST: Hate is never a straight road.\n"
                "MUD: Leave the badge in the truck.\n"
                "GLASS: The badge is the only language you have left.\n"
                "RUST: The badge is a coat you wear over the same old house.\n"
                "CHOIR: Ask him who dug. Ask him who washed. Ask him who remembered for you."
            ),
            hint="Available leads: ASK GABRIEL, CONTINUE.",
            interactions={
                ("ASK", "GABRIEL"): _interaction(
                    """
                    "People think rage is loud," Gabriel says. "Most of mine happened while fixing carburetors."

                    "Did you kill Gideon Wren?"

                    "Not the way you mean."

                    "Then explain it the way you mean."

                    Gabriel rubs his thumb along the rim of a screw tin. "That's the trouble with cops. You all think
                    sequence is truth. In a real family it's usually blood first, then motive invented afterward so
                    everybody can sleep."

                    He keeps his eyes on the radio for a moment longer than necessary. "The plant didn't close all at
                    once," he adds. "It closed in pieces. A shift lost here. A friend moved away there. One machine quiet
                    for a week, then forever. By the time the gates looked dead, half the men were already ghosts with
                    lunch pails. Gideon Wren didn't just shut a place. He taught us what it felt like to become
                    historical while still needing groceries."

                    He wipes his hands on a rag that used to be a T-shirt. The cloth is so worn it feels less like
                    fabric than like a memory trying to keep its shape.

                    "You know what I told myself every time I wanted to hurt someone?" he says. "I told myself wanting
                    isn't doing. I told myself the difference made me decent. That as long as the murder stayed in my
                    head, I was still good."

                    He laughs once, bitter and embarrassed, as if the thought has finally become childish enough to be
                    humiliating.

                    "But the head is a room too," he says. "And rooms rot if you keep dead things in them."

                    GLASS: He's confessing without admitting guilt.
                    RUST: He's confessing the county's moral technique: fantasize, then call it restraint.
                    MUD: Let him have the illusion. It's all he's got.
                    CHOIR: Illusion is what kept him alive. Illusion is what killed the Wrens.

                    "So I fixed radios," he continues. "I fixed engines. I fixed whatever small thing would take my
                    hands and keep them busy. Because idle hands don't just get into trouble. Idle hands remember. Idle
                    hands start counting humiliations, and counting turns into arithmetic, and arithmetic turns into a
                    plan."

                    "And did it work?"

                    He finally meets your eyes. "It worked until it didn't," he says. "That's what coping is. It's a
                    patch job on a machine you can't replace."

                    GLASS: Ask him about Gideon.
                    MUD: Don't. You'll make him real.
                    RUST: Gideon was already real. That's the point.
                    CHOIR: The point is the shape of a man who learned to survive by repairing everything except himself.
                    """,
                    effect=lambda state: state.apply(courage=1, reason=1, note="You stayed long enough for Gabriel to shift from anger into memory."),
                    tag="GABRIEL",
                ),
            },
            required_tags={"GABRIEL"},
            blocked_text="Gabriel has not yet been made to choose between resentment and memory.",
            continue_text="He asks to see the copied hospital note. You hand it over because there is no dignified way not to.",
        ),
        Scene(
            title="Chapter 6.3: The broken memory",
            prose=dedent(
                """
                The hospital photocopy trembles in Gabriel's hand only once. Then he steadies it with the concentration
                mechanics reserve for stripped bolts and priests reserve for the already lost.
                """
            ).strip(),
            think="GLASS: Listen to the sentence before you defend yourself from it.\nRUST: Self-defense and family cleanup often share a shovel.\nMUD: Deny the porch.\nCHOIR: The missing sequence is coming back dressed as procedure.",
            hint="Available leads: READ COPY, THINK, CONTINUE.",
            interactions={
                ("READ", "COPY"): _interaction(
                    """
                    "You killed him," Gabriel says finally. "Self-defense first. Panic second. Then Lena in the kitchen
                    because terror makes a lousy judge and a fast one. I buried them. Ma saw us come back. That's the
                    cleanest version available and it still isn't clean."
                    """,
                    effect=_chain(lambda state: state.apply(courage=2, lucidity=-1, note="Gabriel gave the first direct confession of the old night."), _broken_memory_effect),
                    tag="COPY",
                ),
            },
            required_tags={"COPY"},
            blocked_text="The old night is still deciding whether to return as fact or hallucination.",
            continue_text="You leave the hollow carrying your brother's version of the night back toward the house that produced it.",
        ),
        Scene(
            title="Chapter 7.1: Evelyn at the table",
            prose=dedent(
                """
                Evelyn is waiting at the table as if she has known the minute of your return since the day you first
                learned to lie. There is a cup in front of her clean enough to be ceremonial. Gabriel arrives not long
                after. Families like this communicate through gravity more than speech.
                """
            ).strip(),
            think=(
                "RUST: The rock is real. So are your hands.\n"
                "GLASS: Choose the form of your guilt.\n"
                "MUD: Sit down forever.\n"
                "GLASS: Sitting down is a choice.\n"
                "MUD: So is surviving.\n"
                "CHOIR: Mother. Brother. Badge. Blood. Every oath in the room is trying to kill the others."
            ),
            hint="Available leads: LOOK TABLE, ASK EVELYN, CONTINUE.",
            interactions={
                ("LOOK", "TABLE"): _interaction(
                    """
                    Cheap bread, overdue notices, cooling stew, bruised fruit at Christmas, your father's fists, your
                    mother's triage. The table has held all of it. Tonight it holds a cup and the possibility that truth
                    may simply be whatever leaves the fewest people alive to contradict it.
                    """
                ),
                ("ASK", "EVELYN"): _interaction(
                    """
                    "If you tell them," Evelyn says, "we tell them about your father. About Lena. About what came home in
                    your clothes that night."

                    "That's a threat."

                    "No," she says. "That's inventory."

                    Gabriel keeps looking at the table. That, more than the words, makes the room unbearable. In decent
                    families silence protects love. In damaged ones it serves as corroboration.

                    "You think the law will sort motives into neat bins?" he says without looking up. "It won't. It'll
                    take the ugliest version of all of us and staple it to the county."

                    "You want me to bury it," you say.

                    Evelyn's mouth twitches, almost a smile, then decides not to waste the energy. "No," she says. "I
                    want you to admit burial is the only skill this place ever taught any of us properly."
                    """,
                    effect=lambda state: state.apply(courage=1, reason=1, note="You let Evelyn speak the family threat without interruption."),
                    tag="EVELYNFINAL",
                ),
            },
            required_tags={"EVELYNFINAL"},
            blocked_text="The threat has not yet been allowed into official language.",
            continue_text="Evelyn slides an old family photograph across the table like an exhibit entered too late to help anyone.",
        ),
        Scene(
            title="Chapter 7.2: Hidden evidence in the house",
            prose=dedent(
                """
                The photograph is older than your badge and newer than your innocence. Snow starts outside with the
                hesitation of something deciding whether the county deserves another covering.
                """
            ).strip(),
            think="GLASS: Read the photo like evidence.\nRUST: Childhood is a deposition adults don't sign.\nMUD: Fold it shut.\nCHOIR: Someone in the frame is already rehearsing a uniform.",
            hint="Available leads: READ PHOTO, LOOK PORCH, CONTINUE.",
            interactions={
                ("READ", "PHOTO"): _interaction(
                    """
                    Harrow Mercer stands in front of the porch with a beer in one hand and an ownership expression in the
                    rest of his body. Your mother is off to the side, already beginning the long labor of enduring him.
                    You and Gabriel are boys in the frame, both looking past the camera as if childhood had already
                    taught you the person taking the picture was not necessarily the danger worth tracking.
                    """,
                    effect=_photo_effect,
                    tag="PHOTO",
                ),
                ("LOOK", "PORCH"): _interaction(
                    """
                    The porch boards hold their own dark geometry over the yard. Some memories survive not as events but
                    as architecture. The body forgets in narrative and remembers in floorplans.
                    """,
                    effect=_porch_effect,
                ),
            },
            required_tags={"PHOTO"},
            blocked_text="The old photograph is still trying to tell you what kind of boy stood inside the future badge.",
            continue_text="You stand. No one moves to stop you. That is its own verdict.",
        ),
    ]


def run_scene_command(scene: Scene, state: GameState, raw_command: str) -> CommandResult:
    verb, target = parse_command(raw_command)
    if not verb:
        return CommandResult("stay", "Type a command. The room will not do the work for you.")
    if verb == "HELP":
        return CommandResult("stay", HELP_TEXT)
    if verb == "STATUS":
        return CommandResult("stay", render_status(state))
    if verb == "THINK":
        return CommandResult("stay", build_think_text(scene, state))
    if verb == "QUIT":
        return CommandResult("quit", "You leave the case where you found it: still waiting.")
    if verb == "CONTINUE":
        if not scene.required_tags.issubset(scene.seen_tags):
            return CommandResult("stay", scene.blocked_text)
        if scene.title == "Chapter 4.3: The superior call" and not state.sent_evidence and "HELD" not in scene.seen_tags:
            _hold_evidence(state)
        state.chapter += 1
        state.register_checkpoint()
        return CommandResult("advance", scene.continue_text)

    interaction = scene.interactions.get((verb, target))
    if interaction is None:
        return CommandResult("stay", "The command lands, but the room does not answer in that direction.")

    key = (verb, target)
    first_use = key not in scene.used_keys
    if interaction.once and key in scene.used_keys:
        return CommandResult("stay", interaction.repeat_text or interaction.text)

    scene.used_keys.add(key)
    if interaction.tag:
        scene.seen_tags.add(interaction.tag)
    if interaction.effect:
        interaction.effect(state)
    if not interaction.once and not first_use:
        return CommandResult("stay", interaction.repeat_text or interaction.text)
    return CommandResult("stay", interaction.text)


def render_status(state: GameState) -> str:
    return f"COURAGE={state.courage}  LUCIDITY={state.lucidity}  REASON={state.reason}"


def present_scene(scene: Scene, state: GameState) -> None:
    print()
    print(scene.title)
    print("-" * len(scene.title))
    print(scene.prose)
    print()
    print(scene.hint)
    while True:
        command = input("> ")
        result = run_scene_command(scene, state, command)
        print()
        print(result.text)
        if result.status == "quit":
            raise SystemExit(0)
        if result.status == "advance":
            break


def choose_final_path(state: GameState) -> None:
    forced = determine_ending(state)
    if forced in {"A", "C", "HIDDEN"} or state.courage < COURAGE_FOR_AGENCY:
        return

    print()
    print("Final choices: TURN / BURN / KILL")
    print("Type THINK if you want the voices one last time.")
    while True:
        command = input("> ").strip().upper()
        if command == "HELP":
            print(HELP_TEXT)
            continue
        if command == "THINK":
            print(
                "RUST: The rock is real. So are your hands.\n"
                "GLASS: Choose the form of your guilt.\n"
                "MUD: Lie down in it. Let the town decide.\n"
                "CHOIR: Family. Law. Blood. Choose which altar gets the knife."
            )
            continue
        if command in {"TURN", "BURN", "KILL"}:
            state.final_choice = command
            return
        print("Type TURN, BURN, or KILL.")


def play() -> None:
    state = GameState()
    print(INTRO)
    print()
    print("Type HELP for verbs. Type THINK when you want the other weather.")
    for scene in make_scenes():
        present_scene(scene, state)
    choose_final_path(state)
    ending = determine_ending(state)
    print()
    print(f"Ending {ending}")
    print("-" * (7 + len(ending)))
    print(ENDING_TEXT[ending])
    if state.notes:
        print()
        print("Case notes retained:")
        for note in state.notes[-8:]:
            print(f"- {note}")
    print()
    print("Some people imagine punishment as a door closing.")
    print("Here it is a road you already know by heart, driven again before dawn.")


if __name__ == "__main__":
    play()
