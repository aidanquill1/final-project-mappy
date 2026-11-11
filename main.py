"""MAPPY: a flag quiz website built with Drafter."""
import random
from dataclasses import dataclass

from drafter import *

try:
    from bakery import assert_equal
except ImportError:  # unit tests are optional at runtime
    assert_equal = None

# ---------------------------------------------------------------- constants
# To use the downloaded Hugging Face dataset instead of flagcdn, put the
# images in a "flags" folder named by lowercase code (fr.png) and change this.
FLAG_URL = "https://flagcdn.com/w320/{code}.png"
REGION_KEYS = {
    "africa": "Africa",
    "asia": "Asia",
    "europe": "Europe",
    "north_america": "North America",
    "south_america": "South America",
    "oceania": "Oceania",
}
GREEN = "#2e9e4f"
RED = "#d64545"
BORDER = "3px solid black"
PAGE_COLOR = "#EAE7E2"
# Expand icon (64x64 PNG) embedded as base64 so it works once deployed.
EXPAND_ICON = (
    "url(data:image/png;base64,"
    "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAIAAAAlC+aJAAAETUlEQVR42u1ay26rMBDFxnmpVSs5sEkiFmGXn+nHtP2Ldtnk"
    "B5JIJFLDV3WDhInUFkiCfRej68slQAhwH0SZRdXWeOYcjx8zYyMhhNJkwUrD5UrgSqCikJy2gusbIVTafHUTmQQ45xgX8k/x"
    "L/+ECZQzBvv9/uvrK4e9EOLm5qbVapX2QHUTJIuubdvPz8/b7VYIkUoSIYQQur+/f3l5eXh4OMsPdZoQvwvnnHMeBMFwOCyI"
    "Zjgc+r4PHUUBgS993y9uYjQaBUGQagKn8vZ93/d9jDHGGP2UGpdyEW0ggOH7+9v3/dReJKs/xphzjtCvRUIIGQwGn5+f4EdQ"
    "d3d39/r62u12i08hhBDnvNvtvr29PT09bbdbuR1xzm9vbz8+Pg6HQ3yOwDhmrpKEf4UQnuf1+32JEvi0Wq3pdBqGoeM4jDHP"
    "81zXDcNQVJAwDF3X9TyPMeY4ThiG0+m03W5LxPCz3+97nifhxaUQAUVRQCMhxLKshKIoisqhj3cEhZZlEUJgvGojILcwqXQ+"
    "n8PgFV+4+Qsa3Difz6W3wWKr1apKQFEUwzBmsxmgV1UVtC8WCyHEbrcTlQWULJdLGCNVVYHDbDYzDAMwVCJAKQXnSgM1coDu"
    "i8UioRwmKqW0BgKapjmOAy6GsamLQxZ6mKKO42iaVg8BxhgsuOVyWReHVPQIIVAYRRFjrBIB2VnXdcYYrFowWZ1D1tiDKjDE"
    "GNN1XQ7ieQQYY5RSOAX7/b7rutC03++r+yF/7Pf7PWBwXVfTNMBAKYVBLEQgEQsNBoN4qAMcSvvheM9JoI8HS4PBQIZbWbGQ"
    "knW+2LZtmqZpmpvNJnHolOYgxz7eMYE+jmGz2ZimOR6PjzHkEZASBEEQBKlNJTikopdd4ugTsUYWhhMEJN2sSCHO4fiMSwDK"
    "J5yF/iSGEx44GSnkczgcDvAZ/FJk5pTAoFQMBFI5IITW6zVAB/Tr9boE+iJSlcDx5IZgeDQayb3L9/3RaCSbJPpaQqkaCCS2"
    "dpkEJgjIphrR10ZATgbLshKbb3xDNE0TorTqM0cKqrE6DVnlbrdTFKXdbida5f9L15HOrguVkCiKVFU9LkXJP+UH19roH/DA"
    "P5lCtSk6HA4Y49VqNZlMJpOJbdtAiXOuKIpt2/D/1WqFMY5XTarKdRtt+EH2X4cSzQ7mLiGc/h8SmhwMJ1LKzWYzHo+Lp5RF"
    "lua5KeX7+zuklLZtF00pj5P6xP3FP0nqcy44LrGscgmFrUsoLV5Ocbfx5fVmX3A0/orpEi75mnrNCjtA/HqZEGIYBqVU0zRN"
    "03Rd13XdNM2ccz5/7KHWAnpAJ6XUMAxCSOJOv9IFx8mnBpC7pGrPmvdCiPy3EomnBjknMU5NMnu9Xq/XS6zR/EdLZxUHTn6c"
    "WOWAJ7UXSX3I0Ol0ptPp4+NjwbcwFd9KFDHR6XRSTTT+wVMmgUt4ctaIR38110av70avBK4E/rb8AICgZxNnc8NFAAAAAElF"
    "TkSuQmCC"
    ")"
)
COUNT_CHOICES = [("call", "All", 0), ("c100", "100", 100),
                 ("c50", "50", 50), ("c10", "10", 10)]


@dataclass
class Country:
    """A country with its region and two-letter flag code."""
    name: str
    region: str
    code: str


@dataclass
class Question:
    """One quiz question: the correct flag code and four answer choices.
    Only the short code is stored to keep the saved state small."""
    code: str
    choices: list[str]


@dataclass
class Missed:
    """A wrongly answered question (flag code) and what was picked."""
    code: str
    said: str


COUNTRIES: list[Country] = [
    Country("Egypt", "Africa", "eg"), Country("Nigeria", "Africa", "ng"),
    Country("Kenya", "Africa", "ke"), Country("South Africa", "Africa", "za"),
    Country("Morocco", "Africa", "ma"), Country("Ethiopia", "Africa", "et"),
    Country("Ghana", "Africa", "gh"), Country("Algeria", "Africa", "dz"),
    Country("Tanzania", "Africa", "tz"), Country("Senegal", "Africa", "sn"),
    Country("Uganda", "Africa", "ug"), Country("Tunisia", "Africa", "tn"),
    Country("Japan", "Asia", "jp"), Country("China", "Asia", "cn"),
    Country("India", "Asia", "in"), Country("South Korea", "Asia", "kr"),
    Country("Thailand", "Asia", "th"), Country("Vietnam", "Asia", "vn"),
    Country("Indonesia", "Asia", "id"), Country("Philippines", "Asia", "ph"),
    Country("Pakistan", "Asia", "pk"), Country("Saudi Arabia", "Asia", "sa"),
    Country("Turkey", "Asia", "tr"), Country("Nepal", "Asia", "np"),
    Country("France", "Europe", "fr"), Country("Germany", "Europe", "de"),
    Country("Italy", "Europe", "it"), Country("Spain", "Europe", "es"),
    Country("Portugal", "Europe", "pt"), Country("Ireland", "Europe", "ie"),
    Country("Poland", "Europe", "pl"), Country("Sweden", "Europe", "se"),
    Country("Norway", "Europe", "no"), Country("Greece", "Europe", "gr"),
    Country("Netherlands", "Europe", "nl"),
    Country("Switzerland", "Europe", "ch"),
    Country("United States", "North America", "us"),
    Country("Canada", "North America", "ca"),
    Country("Mexico", "North America", "mx"),
    Country("Cuba", "North America", "cu"),
    Country("Jamaica", "North America", "jm"),
    Country("Costa Rica", "North America", "cr"),
    Country("Panama", "North America", "pa"),
    Country("Guatemala", "North America", "gt"),
    Country("Haiti", "North America", "ht"),
    Country("Honduras", "North America", "hn"),
    Country("Bahamas", "North America", "bs"),
    Country("Dominican Republic", "North America", "do"),
    Country("Brazil", "South America", "br"),
    Country("Argentina", "South America", "ar"),
    Country("Chile", "South America", "cl"),
    Country("Peru", "South America", "pe"),
    Country("Colombia", "South America", "co"),
    Country("Venezuela", "South America", "ve"),
    Country("Ecuador", "South America", "ec"),
    Country("Bolivia", "South America", "bo"),
    Country("Uruguay", "South America", "uy"),
    Country("Paraguay", "South America", "py"),
    Country("Guyana", "South America", "gy"),
    Country("Suriname", "South America", "sr"),
    Country("Australia", "Oceania", "au"),
    Country("New Zealand", "Oceania", "nz"),
    Country("Fiji", "Oceania", "fj"),
    Country("Papua New Guinea", "Oceania", "pg"),
    Country("Samoa", "Oceania", "ws"), Country("Tonga", "Oceania", "to"),
    Country("Vanuatu", "Oceania", "vu"),
    Country("Solomon Islands", "Oceania", "sb"),
    Country("Palau", "Oceania", "pw"), Country("Kiribati", "Oceania", "ki"),
    Country("Tuvalu", "Oceania", "tv"), Country("Nauru", "Oceania", "nr"),
]


@dataclass
class State:
    """All data the website remembers between pages."""
    quiz: list[Question]
    position: int
    score: int
    streak: int
    answered: bool
    picked: str
    missed: list[Missed]
    regions: list[str]
    flag_count: int  # 0 means "all flags"


# ------------------------------------------------------------ helper logic
def collect_regions(africa: bool, asia: bool, europe: bool,
                    north_america: bool, south_america: bool,
                    oceania: bool) -> list[str]:
    """Return the region names whose checkboxes are ticked."""
    ticked = {"africa": africa, "asia": asia, "europe": europe,
              "north_america": north_america,
              "south_america": south_america, "oceania": oceania}
    chosen = []
    for key, is_ticked in ticked.items():
        if is_ticked:
            chosen.append(REGION_KEYS[key])
    return chosen


def pick_count(c10: bool, c50: bool, c100: bool, call: bool) -> int:
    """Return the largest ticked flag count (0 = all, default 10)."""
    if call:
        return 0
    if c100:
        return 100
    if c50:
        return 50
    return 10


def build_pool(regions: list[str]) -> list[Country]:
    """Return all countries in the given regions (all if too few)."""
    pool = [country for country in COUNTRIES if country.region in regions]
    if len(pool) < 4:
        return list(COUNTRIES)
    return pool


def find_country(code: str) -> Country:
    """Return the country with the given flag code."""
    for country in COUNTRIES:
        if country.code == code:
            return country
    return COUNTRIES[0]


def make_question(country: Country, pool: list[Country]) -> Question:
    """Build a question with the answer plus 3 random wrong choices.
    Not unit tested because of randomization."""
    others = [other.name for other in pool if other.name != country.name]
    choices = random.sample(others, 3) + [country.name]
    random.shuffle(choices)
    return Question(country.code, choices)


def make_quiz(pool: list[Country], flag_count: int) -> list[Question]:
    """Build a shuffled quiz of flag_count questions (0 = whole pool)."""
    total = len(pool) if flag_count == 0 else min(flag_count, len(pool))
    chosen = random.sample(pool, total)
    return [make_question(country, pool) for country in chosen]


def reset_game(state: State, quiz: list[Question]) -> None:
    """Start a fresh run of the given quiz."""
    state.quiz = quiz
    state.position = 0
    state.score = 0
    state.streak = 0
    state.answered = False
    state.picked = ""
    state.missed = []


def is_last_question(state: State) -> bool:
    """Return True if the current question is the final one."""
    return state.position >= len(state.quiz) - 1


def colored(text: str, color: str) -> str:
    """Return text in the given font color."""
    return change_color(text, color)


# ------------------------------------------------------- styled components
def flag_image(code: str, height: int) -> Image:
    """Return the flag image at a fixed height, so the page never jumps
    around while images load (bordered through the site CSS)."""
    return Image(FLAG_URL.format(code=code), height=height)


def expand_button() -> Button:
    """Return the expand-icon button that opens the full screen options."""
    return Button(" ", open_options, style_background_image=EXPAND_ICON,
                  style_background_size="contain",
                  style_background_repeat="no-repeat",
                  style_background_position="center",
                  style_background_color="white", style_border=BORDER,
                  style_border_radius="10px", style_width="50px",
                  style_height="50px")


def styled_button(text: str, route_fn, color: str = "white") -> Button:
    """Return a bordered, rounded button with the given background."""
    return Button(text, route_fn, style_border=BORDER,
                  style_border_radius="20px", style_background_color=color,
                  style_color="black", style_padding="10px 30px",
                  style_font_size="20px")


def panel(*content, **style) -> Div:
    """Return a bordered box around the content."""
    return Div(*content, style_border=BORDER, style_padding="20px",
               style_border_radius="10px", **style)


def checkbox_row(name: str, label: str, ticked: bool) -> Div:
    """Return a checkbox with its label on the same line."""
    return Div(CheckBox(name, ticked), Span(" " + label))


def options_panel(state: State, show_expand: bool) -> Div:
    """Build the bordered options box with region and count checkboxes."""
    title = Header("Options", 3)
    if show_expand:
        title = Div(title, expand_button(), style_display="flex",
                    style_justify_content="space-between",
                    style_align_items="center")
    parts = [title, Text("Regions")]
    for key, region in REGION_KEYS.items():
        parts.append(checkbox_row(key, region, region in state.regions))
    parts.append(Text("Number of flags"))
    for name, label, amount in COUNT_CHOICES:
        parts.append(checkbox_row(name, label, state.flag_count == amount))
    return panel(*parts)


def save_choices(state: State, africa: bool, asia: bool, europe: bool,
                 north_america: bool, south_america: bool, oceania: bool,
                 c10: bool, c50: bool, c100: bool, call: bool) -> None:
    """Store the ticked options in the state."""
    state.regions = collect_regions(africa, asia, europe, north_america,
                                    south_america, oceania)
    state.flag_count = pick_count(c10, c50, c100, call)


# ------------------------------------------------------------------ routes
@route
def index(state: State) -> Page:
    """Home page with title, PLAY button, and options on the right."""
    left = Div(Header("MAPPY", 1), LineBreak(), LineBreak(),
               styled_button("PLAY", start_game), style_width="55%")
    right = Div(options_panel(state, True), style_width="40%")
    return Page(state, [panel(Div(left, right, style_display="flex",
                                  style_justify_content="space-between"))])


@route
def open_options(state: State, africa: bool, asia: bool, europe: bool,
                 north_america: bool, south_america: bool, oceania: bool,
                 c10: bool, c50: bool, c100: bool, call: bool) -> Page:
    """Full screen options page."""
    save_choices(state, africa, asia, europe, north_america, south_america,
                 oceania, c10, c50, c100, call)
    return Page(state, [panel(Header("MAPPY Options", 1),
                              options_panel(state, False),
                              styled_button("SAVE & BACK", index))])


@route
def start_game(state: State, africa: bool, asia: bool, europe: bool,
               north_america: bool, south_america: bool, oceania: bool,
               c10: bool, c50: bool, c100: bool, call: bool) -> Page:
    """Save options, build a quiz, and show the first question."""
    save_choices(state, africa, asia, europe, north_america, south_america,
                 oceania, c10, c50, c100, call)
    pool = build_pool(state.regions)
    reset_game(state, make_quiz(pool, state.flag_count))
    return question(state)


@route
def try_again(state: State) -> Page:
    """Rebuild a quiz with the same options."""
    pool = build_pool(state.regions)
    reset_game(state, make_quiz(pool, state.flag_count))
    return question(state)


@route
def study_missed(state: State) -> Page:
    """Quiz only on the flags that were missed."""
    if len(state.missed) == 0:
        return results(state)
    regions = [find_country(missed.code).region for missed in state.missed]
    pool = build_pool(regions)
    redo = [make_question(find_country(missed.code), pool) for missed in state.missed]
    reset_game(state, redo)
    return question(state)


def answer_button(state: State, text: str, route_fn) -> Button:
    """Make an answer button, green/red once the question is answered."""
    if not state.answered:
        return styled_button(text, route_fn)
    correct = find_country(state.quiz[state.position].code).name
    color = GREEN if text == correct else RED
    return styled_button(text, route_fn, color)


@route
def question(state: State) -> Page:
    """Show the current flag and its four answer choices."""
    if len(state.quiz) == 0:
        return index(state)
    current = state.quiz[state.position]
    total = len(state.quiz)
    top = Div(Text(f"Streak = {state.streak} 🔥"),
              Text(f"Question {state.position + 1} / {total}"),
              Text(f"Score {state.score}/{total}"),
              style_display="flex", style_justify_content="space-between")
    routes = [choose_0, choose_1, choose_2, choose_3]
    buttons = []
    for text, route_fn in zip(current.choices, routes):
        buttons.append(answer_button(state, text, route_fn))
    grid = Div(*buttons, style_display="grid",
               style_grid_template_columns="1fr 1fr", style_gap="20px",
               style_text_align="center")
    next_part = Span("")
    if state.answered:
        label = "RESULTS" if is_last_question(state) else "NEXT >>"
        next_part = styled_button(label, next_question)
    bottom = Div(styled_button("QUIT", quit_game), next_part,
                 style_display="flex", style_justify_content="space-between")
    flag = Div(flag_image(current.code, 200),
               style_text_align="center", style_padding="20px")
    return Page(state, [panel(top, flag, grid, LineBreak(), bottom)])


def record_answer(state: State, index_chosen: int) -> Page:
    """Grade the chosen answer and update score, streak, and misses."""
    current = state.quiz[state.position]
    if state.answered:
        return question(state)
    state.picked = current.choices[index_chosen]
    state.answered = True
    if state.picked == find_country(current.code).name:
        state.score += 1
        state.streak += 1
    else:
        state.streak = 0
        state.missed.append(Missed(current.code, state.picked))
    return question(state)


@route
def choose_0(state: State) -> Page:
    """Player picked the first choice."""
    return record_answer(state, 0)


@route
def choose_1(state: State) -> Page:
    """Player picked the second choice."""
    return record_answer(state, 1)


@route
def choose_2(state: State) -> Page:
    """Player picked the third choice."""
    return record_answer(state, 2)


@route
def choose_3(state: State) -> Page:
    """Player picked the fourth choice."""
    return record_answer(state, 3)


@route
def next_question(state: State) -> Page:
    """Go to the next question, or to the results after the last one."""
    if not state.answered:  # ignore stray or double clicks
        return question(state)
    if is_last_question(state):
        return results(state)
    state.position += 1
    state.answered = False
    state.picked = ""
    return question(state)


@route
def quit_game(state: State) -> Page:
    """Ask for confirmation so a stray click cannot end the quiz."""
    return Page(state, [panel(Header("Quit this quiz?", 2),
                              styled_button("YES, QUIT", go_home),
                              styled_button("KEEP PLAYING", question))])


@route
def go_home(state: State) -> Page:
    """Clear the quiz and go to the home page."""
    reset_game(state, [])
    return index(state)


def missed_row(missed: Missed) -> Div:
    """Return one wrong answer: bordered flag, what was said, answer."""
    words = Div(Div(Span("You said: "), Span(colored(missed.said, RED))),
                Div(Span("Answer: "),
                    Span(colored(find_country(missed.code).name, GREEN))))
    return Div(flag_image(missed.code, 80), words,
               style_display="flex", style_gap="30px",
               style_align_items="center", style_padding="10px")


@route
def results(state: State) -> Page:
    """Final score page with buttons and the list of missed flags."""
    buttons = [styled_button("HOME", go_home)]
    if len(state.missed) > 0:
        buttons.append(styled_button("STUDY MISSED", study_missed))
    buttons.append(styled_button("TRY AGAIN", try_again))
    body = [Div(Header("Final Score", 1),
                Header(f"{state.score}/{len(state.quiz)}", 2),
                style_text_align="center"),
            Div(*buttons, style_display="flex", style_gap="30px",
                style_justify_content="center"),
            Header("Wrong answers", 3)]
    for missed in state.missed:
        body.append(missed_row(missed))
    return Page(state, [panel(*body)])


# ------------------------------------------------------------- unit tests
if assert_equal is not None:
    _test = State([], 0, 2, 2, False, "", [], ["Asia"], 10)
    assert_equal(pick_count(False, False, False, False), 10)
    assert_equal(pick_count(True, True, False, False), 50)
    assert_equal(pick_count(False, False, True, False), 100)
    assert_equal(pick_count(False, False, False, True), 0)
    assert_equal(collect_regions(True, False, True, False, False, False),
                 ["Africa", "Europe"])
    assert_equal(len(build_pool(["Oceania"])), 12)
    assert_equal(len(build_pool([])), len(COUNTRIES))
    assert_equal(find_country("fr").name, "France")
    assert_equal(is_last_question(_test), True)
    assert_equal(next_question(_test).state.position, 0)
    assert_equal(quit_game(_test).state.score, 2)
    assert_equal(go_home(_test).state.score, 0)

add_website_css("body", f"background-color: {PAGE_COLOR};")
add_website_css("img", f"border: {BORDER};")
add_website_css("button, input[type=submit]",
                f"border: {BORDER}; border-radius: 20px; color: black;")
set_website_title("MAPPY")
set_site_information(
    author="YOUR NAME",
    description="MAPPY is a flag quiz that teaches the countries of the "
                "world by region.",
    sources=["https://huggingface.co/datasets/Aniket96/country-flags-dataset"],
    planning=["planning_document.pdf"],
    links=["https://github.com/YOUR-USERNAME/YOUR-REPO"],
)
# Debug info is left ON while testing so any error message is visible.
# Put hide_debug_information() back before you submit.
# hide_debug_information()
start_server(State([], 0, 0, 0, False, "", [], list(REGION_KEYS.values()), 0))
