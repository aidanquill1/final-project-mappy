"""MAPPY: a flag quiz website built with Drafter."""
import base64
import random
from dataclasses import asdict, dataclass
from typing import Callable

from drafter import *

try:
    import os
except ImportError:  # some browser-based Python versions have no os module
    os = None
try:
    import json
    import tempfile
except ImportError:
    json = None
    tempfile = None
try:
    from bakery import assert_equal
except ImportError:  # unit tests are optional at runtime
    assert_equal = None

# ---------------------------------------------------------------- constants
# The flag images live in the MAPS folder next to MAPPY.py (Vietnam.png, ...).
MAPS_FOLDER = "."
REGION_NAMES = ["Africa", "Asia", "Europe", "North America", "South America",
                "Oceania"]
GREEN = "#2e9e4f"
RED = "#d64545"
GREY = "#cfcbc4"
BORDER = "3px solid black"
PAGE_COLOR = "#EAE7E2"
COUNT_CHOICES = [("All", 0), ("100", 100), ("50", 50), ("10", 10)]
CHOICE_COUNTS = ["4", "3", "2"]
SAVE_FILE = "mappy_save.json"
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

# Every country, grouped by region. Names must match the PNG file names
# in the MAPS folder exactly (run check_flags.py to find mismatches).
COUNTRY_REGIONS = {
    "Africa": [
        "Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi", "Cameroon",
        "Cape Verde", "Central African Republic", "Chad", "Comoros",
        "Democratic Republic of the Congo", "Republic of the Congo", "Djibouti", "Egypt",
        "Equatorial Guinea", "Eritrea", "Eswatini", "Ethiopia", "Gabon", "Gambia", "Ghana",
        "Guinea", "Guinea-Bissau", "Ivory Coast", "Kenya", "Lesotho", "Liberia", "Libya",
        "Madagascar", "Malawi", "Mali", "Mauritania", "Mauritius", "Morocco", "Mozambique",
        "Namibia", "Niger", "Nigeria", "Rwanda", "Sao Tome and Principe", "Senegal", "Seychelles",
        "Sierra Leone", "Somalia", "South Africa", "South Sudan", "Sudan", "Tanzania", "Togo",
        "Tunisia", "Uganda", "Zambia", "Zimbabwe",
    ],
    "Asia": [
        "Afghanistan", "Armenia", "Azerbaijan", "Bahrain", "Bangladesh", "Bhutan", "Brunei",
        "Cambodia", "China", "Georgia", "India", "Indonesia", "Iran", "Iraq", "Israel", "Japan",
        "Jordan", "Kazakhstan", "Kuwait", "Kyrgyzstan", "Laos", "Lebanon", "Malaysia", "Maldives",
        "Mongolia", "Myanmar", "Nepal", "North Korea", "Oman", "Pakistan", "Palestine",
        "Philippines", "Qatar", "Saudi Arabia", "Singapore", "South Korea", "Sri Lanka", "Syria",
        "Taiwan", "Tajikistan", "Thailand", "Timor-Leste", "Turkey", "Turkmenistan",
        "United Arab Emirates", "Uzbekistan", "Vietnam", "Yemen",
    ],
    "Europe": [
        "Albania", "Andorra", "Austria", "Belarus", "Belgium", "Bosnia and Herzegovina", "Bulgaria",
        "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia", "Finland", "France", "Germany",
        "Greece", "Hungary", "Iceland", "Ireland", "Italy", "Kosovo", "Latvia", "Liechtenstein",
        "Lithuania", "Luxembourg", "Malta", "Moldova", "Monaco", "Montenegro", "Netherlands",
        "North Macedonia", "Norway", "Poland", "Portugal", "Romania", "Russia", "San Marino",
        "Serbia", "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland", "Ukraine",
        "United Kingdom", "Vatican City",
    ],
    "North America": [
        "Antigua and Barbuda", "Bahamas", "Barbados", "Belize", "Canada", "Costa Rica", "Cuba",
        "Dominica", "Dominican Republic", "El Salvador", "Grenada", "Guatemala", "Haiti",
        "Honduras", "Jamaica", "Mexico", "Nicaragua", "Panama", "Saint Kitts and Nevis",
        "Saint Lucia", "Saint Vincent and the Grenadines", "Trinidad and Tobago", "United States",
    ],
    "South America": [
        "Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Ecuador", "Guyana", "Paraguay",
        "Peru", "Suriname", "Uruguay", "Venezuela",
    ],
    "Oceania": [
        "Australia", "Fiji", "Kiribati", "Marshall Islands", "Micronesia", "Nauru", "New Zealand",
        "Palau", "Papua New Guinea", "Samoa", "Solomon Islands", "Tonga", "Tuvalu", "Vanuatu",
    ],
}


@dataclass
class Country:
    """A country: its flag image file, its name, and its region."""
    image: str
    name: str
    region: str


@dataclass
class Question:
    """One quiz question: the correct country name and its choices.
    Only the name is stored to keep the saved state small."""
    name: str
    choices: list[str]


@dataclass
class Missed:
    """A wrongly answered question (country name) and what was picked."""
    name: str
    said: str


def load_countries() -> list[Country]:
    """Build a Country (image path, name, region) for every country."""
    countries = []
    for region, names in COUNTRY_REGIONS.items():
        for name in names:
            countries.append(Country(f"{MAPS_FOLDER}/{name}.png", name, region))
    return countries


COUNTRIES: list[Country] = load_countries()


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
    hard_mode: bool
    num_choices: int
    fullscreen: bool  # True while the full screen options page is open


def new_state() -> State:
    """Return the starting state of the website."""
    return State([], 0, 0, 0, False, "", [], list(REGION_NAMES), 0, False, 4,
                 False)


@dataclass
class TestState(State):
    """A State used only by the unit tests (it is never saved to disk)."""


# ---------------------------------------------------------- flag file checker
# Integrated from Check_flags.py. Run automatically when MAPPY starts.
def code_names() -> list[str]:
    """Return every country name listed in COUNTRY_REGIONS."""
    return [name for names in COUNTRY_REGIONS.values() for name in names]


def file_names() -> list[str]:
    """Return PNG filenames without extensions from the same folder as MAPPY.py."""
    if os is None:
        return []
    here = os.path.dirname(os.path.abspath(__file__))
    maps_folder = os.path.join(here, MAPS_FOLDER)
    try:
        return [name[:-4] for name in os.listdir(maps_folder)
                if name.lower().endswith(".png")]
    except OSError:
        print("Flag check: image folder is unavailable.")
        return []


def check_flags() -> None:
    """Check local PNG filenames without preventing the website from starting."""
    try:
        if os is None:
            print("Flag check skipped: filesystem access is unavailable.")
            return
        here = os.path.dirname(os.path.abspath(__file__))
        maps_folder = os.path.join(here, MAPS_FOLDER)
        if not os.path.isdir(maps_folder):
            print("Flag check skipped: image folder not found.")
            return
        in_code = set(code_names())
        on_disk = set(file_names())
        print("In the code but NO file:", sorted(in_code - on_disk))
        print("File exists but NOT in the code:", sorted(on_disk - in_code))
    except Exception as error:
        print("Flag check skipped:", error)


# ------------------------------------------------------- saving / restoring
# ADVANCED TECHNIQUE (not covered in class): after every page the progress is
# written to a small JSON file in the computer's temp folder. If the browser
# page ever refreshes and Drafter hands us a brand new state, the next route
# loads the saved progress back so the quiz and settings are not lost.
# If files are unavailable (e.g. after deploying) these functions do nothing.
def save_path() -> str:
    """Return where the progress file is kept."""
    return os.path.join(tempfile.gettempdir(), SAVE_FILE)


def save_progress(state: State) -> None:
    """Write the state to the progress file (ignored for unit tests)."""
    if type(state) is not State:
        return
    try:
        with open(save_path(), "w", encoding="utf-8") as file:
            json.dump(asdict(state), file)
    except (OSError, NameError, AttributeError, TypeError):
        pass


def fill_state(state: State, data: dict) -> None:
    """Copy saved data into the state."""
    state.quiz = [Question(q["name"], list(q["choices"]))
                  for q in data["quiz"]]
    state.missed = [Missed(m["name"], m["said"]) for m in data["missed"]]
    state.regions = list(data["regions"])
    state.position = data["position"]
    state.score = data["score"]
    state.streak = data["streak"]
    state.answered = data["answered"]
    state.picked = data["picked"]
    state.flag_count = data["flag_count"]
    state.hard_mode = data["hard_mode"]
    state.num_choices = data["num_choices"]
    state.fullscreen = data["fullscreen"]


def restore_progress(state: State) -> None:
    """If the state was reset to brand new, load the saved progress."""
    if state != new_state():
        return
    try:
        with open(save_path(), encoding="utf-8") as file:
            fill_state(state, json.load(file))
    except (OSError, ValueError, KeyError, TypeError, NameError,
            AttributeError):
        pass


# ------------------------------------------------------------ helper logic
def build_pool(regions: list[str]) -> list[Country]:
    """Return all countries in the given regions (all if none given)."""
    pool = [country for country in COUNTRIES if country.region in regions]
    if len(pool) < 4:
        return list(COUNTRIES)
    return pool


def count_available(regions: list[str], amount: int) -> bool:
    """Return True if the regions hold enough flags for this count."""
    return amount == 0 or amount <= len(build_pool(regions))


def fix_count(state: State) -> None:
    """Switch to 'All' if the chosen count no longer fits the regions."""
    if not count_available(state.regions, state.flag_count):
        state.flag_count = 0


def apply_extras(state: State, hard_mode: bool, num_choices: str) -> None:
    """Store the hard mode box and the choices drop-down."""
    state.hard_mode = hard_mode
    state.num_choices = int(num_choices) if num_choices in CHOICE_COUNTS else 4


def find_country(name: str) -> Country:
    """Return the Country with the given name."""
    for country in COUNTRIES:
        if country.name == name:
            return country
    return COUNTRIES[0]


def make_question(country: Country, pool: list[Country],
                  num_choices: int) -> Question:
    """Build a question with the answer plus random wrong choices.
    Not unit tested because of randomization."""
    others = [other.name for other in pool if other.name != country.name]
    choices = random.sample(others, min(num_choices - 1, len(others)))
    choices.append(country.name)
    random.shuffle(choices)
    return Question(country.name, choices)


def new_quiz(state: State) -> list[Question]:
    """Build a shuffled quiz from the chosen regions and flag count."""
    pool = build_pool(state.regions)
    wrong_pool = list(COUNTRIES) if state.hard_mode else pool
    total = len(pool) if state.flag_count == 0 else state.flag_count
    chosen = random.sample(pool, min(total, len(pool)))
    return [make_question(country, wrong_pool, state.num_choices)
            for country in chosen]


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
def flag_source(image: str) -> str:
    """Return the flag as an embedded data URI, found relative to this file.
    ADVANCED TECHNIQUE (not covered in class): the PNG is read and encoded
    with base64 so the browser gets the picture itself and does not depend
    on the folder Drafter happens to be running from. If the file cannot be
    read (e.g. after deploying), the plain relative path is used instead."""
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(here, image), "rb") as file:
            encoded = base64.b64encode(file.read()).decode("ascii")
        return "data:image/png;base64," + encoded
    except (OSError, NameError, AttributeError):
        return image


def flag_image(image: str, height: int) -> Image:
    """Return the flag image at a fixed height, so the page never jumps
    around while images load (bordered through the site CSS)."""
    return Image(flag_source(image), height=height)


def expand_button() -> Button:
    """Return the expand-icon button that opens the full screen options."""
    return Button(" ", open_options, style_background_image=EXPAND_ICON,
                  style_background_size="contain",
                  style_background_repeat="no-repeat",
                  style_background_position="center",
                  style_background_color="white", style_border=BORDER,
                  style_border_radius="10px", style_width="50px",
                  style_height="50px")


def styled_button(text: str, route_fn: Callable, color: str = "white") -> Button:
    """Return a bordered, rounded button with the given background."""
    return Button(text, route_fn, style_border=BORDER,
                  style_border_radius="20px", style_background_color=color,
                  style_color="black", style_padding="10px 30px",
                  style_font_size="20px")


def choice_button(text: str, route_fn: Callable, selected: bool,
                  available: bool) -> Button:
    """Return an option button: green when selected, and grey and crossed
    out with a 'Not Available' tooltip when it cannot be chosen."""
    style = {"style_border": BORDER, "style_border_radius": "15px",
             "style_padding": "6px 16px", "style_font_size": "16px",
             "style_background_color": "white", "style_color": "black"}
    if selected:
        style["style_background_color"] = GREEN
        style["style_color"] = "white"
    if not available:
        style["style_background_color"] = GREY
        style["style_color"] = "#8a8a8a"
        style["style_text_decoration"] = "line-through"
        style["style_cursor"] = "not-allowed"
        try:
            return Button(text, route_fn, title="Not Available", **style)
        except TypeError:  # this Drafter version has no tooltip support
            pass
    return Button(text, route_fn, **style)


def panel(*content: object, **style: object) -> Div:
    """Return a bordered box around the content."""
    return Div(*content, style_border=BORDER, style_padding="20px",
               style_border_radius="10px", **style)


def checkbox_row(name: str, label: str, ticked: bool) -> Div:
    """Return a checkbox with its label on the same line."""
    return Div(CheckBox(name, ticked), Span(" " + label))


def button_row(*buttons: Button) -> Div:
    """Lay buttons out side by side, wrapping onto new lines."""
    return Div(*buttons, style_display="flex", style_flex_wrap="wrap",
               style_gap="8px", style_padding="6px 0px")


def options_panel(state: State, show_expand: bool) -> Div:
    """Build the bordered options box."""
    title = Header("Options", 3)
    if show_expand:
        title = Div(title, expand_button(), style_display="flex",
                    style_justify_content="space-between",
                    style_align_items="center")
    region_routes = [toggle_africa, toggle_asia, toggle_europe,
                     toggle_north_america, toggle_south_america,
                     toggle_oceania]
    region_buttons = []
    for name, route_fn in zip(REGION_NAMES, region_routes):
        region_buttons.append(
            choice_button(name, route_fn, name in state.regions, True))
    count_routes = [set_count_all, set_count_100, set_count_50, set_count_10]
    count_buttons = []
    for (label, amount), route_fn in zip(COUNT_CHOICES, count_routes):
        count_buttons.append(choice_button(
            label, route_fn, state.flag_count == amount,
            count_available(state.regions, amount)))
    total = len(build_pool(state.regions))
    return panel(title, Text("Regions"), button_row(*region_buttons),
                 Text(f"Number of flags ({total} available)"),
                 button_row(*count_buttons),
                 checkbox_row("hard_mode",
                              "Hard mode: wrong answers from any region",
                              state.hard_mode),
                 Text("Answer choices"),
                 SelectBox("num_choices", CHOICE_COUNTS,
                           str(state.num_choices)))


# ------------------------------------------------------------------- pages
def home_page(state: State) -> Page:
    """Build the home page with PLAY and an optional RESUME button."""
    buttons = [styled_button("PLAY", start_game)]
    if len(state.quiz) > 0:
        buttons.append(styled_button("RESUME", resume_game))
    left = Div(Header("MAPPY", 1), LineBreak(), LineBreak(),
               button_row(*buttons), style_width="55%")
    right = Div(options_panel(state, True), style_width="40%")
    save_progress(state)
    return Page(state, [panel(Div(left, right, style_display="flex",
                                  style_justify_content="space-between"))])


def options_page(state: State) -> Page:
    """Build the full screen options page."""
    save_progress(state)
    return Page(state, [panel(Header("MAPPY Options", 1),
                              options_panel(state, False),
                              LineBreak(),
                              styled_button("SAVE & BACK", close_options))])


def options_view(state: State) -> Page:
    """Show whichever options screen is currently open."""
    if state.fullscreen:
        return options_page(state)
    return home_page(state)


# ------------------------------------------------------------ option routes
@route
def index(state: State) -> Page:
    """Restore an active quiz after a refresh, otherwise show home."""
    restore_progress(state)
    state.fullscreen = False
    if len(state.quiz) > 0:
        return question(state)
    return home_page(state)


@route
def resume_game(state: State) -> Page:
    """Continue an unfinished quiz without changing its progress."""
    restore_progress(state)
    if len(state.quiz) > 0:
        return question(state)
    return home_page(state)


@route
def open_options(state: State, hard_mode: bool,
                 num_choices: str) -> Page:
    """Open the full screen options page."""
    restore_progress(state)
    apply_extras(state, hard_mode, num_choices)
    state.fullscreen = True
    return options_page(state)


@route
def close_options(state: State, hard_mode: bool,
                  num_choices: str) -> Page:
    """Leave the full screen options page."""
    restore_progress(state)
    apply_extras(state, hard_mode, num_choices)
    state.fullscreen = False
    return home_page(state)


def toggle_region(state: State, region: str) -> Page:
    """Tick or untick a region (at least one stays ticked)."""
    chosen = list(state.regions)
    if region in chosen:
        if len(chosen) > 1:
            chosen.remove(region)
    else:
        chosen.append(region)
    state.regions = [name for name in REGION_NAMES if name in chosen]
    fix_count(state)
    return options_view(state)


@route
def toggle_africa(state: State, hard_mode: bool,
                  num_choices: str) -> Page:
    """Tick or untick Africa."""
    restore_progress(state)
    apply_extras(state, hard_mode, num_choices)
    return toggle_region(state, "Africa")


@route
def toggle_asia(state: State, hard_mode: bool,
                num_choices: str) -> Page:
    """Tick or untick Asia."""
    restore_progress(state)
    apply_extras(state, hard_mode, num_choices)
    return toggle_region(state, "Asia")


@route
def toggle_europe(state: State, hard_mode: bool,
                  num_choices: str) -> Page:
    """Tick or untick Europe."""
    restore_progress(state)
    apply_extras(state, hard_mode, num_choices)
    return toggle_region(state, "Europe")


@route
def toggle_north_america(state: State, hard_mode: bool,
                         num_choices: str) -> Page:
    """Tick or untick North America."""
    restore_progress(state)
    apply_extras(state, hard_mode, num_choices)
    return toggle_region(state, "North America")


@route
def toggle_south_america(state: State, hard_mode: bool,
                         num_choices: str) -> Page:
    """Tick or untick South America."""
    restore_progress(state)
    apply_extras(state, hard_mode, num_choices)
    return toggle_region(state, "South America")


@route
def toggle_oceania(state: State, hard_mode: bool,
                   num_choices: str) -> Page:
    """Tick or untick Oceania."""
    restore_progress(state)
    apply_extras(state, hard_mode, num_choices)
    return toggle_region(state, "Oceania")


def pick_count(state: State, amount: int) -> Page:
    """Choose how many flags (ignored if the regions hold too few)."""
    if count_available(state.regions, amount):
        state.flag_count = amount
    return options_view(state)


@route
def set_count_all(state: State, hard_mode: bool,
                  num_choices: str) -> Page:
    """Use every flag in the chosen regions."""
    restore_progress(state)
    apply_extras(state, hard_mode, num_choices)
    return pick_count(state, 0)


@route
def set_count_100(state: State, hard_mode: bool,
                  num_choices: str) -> Page:
    """Use 100 flags."""
    restore_progress(state)
    apply_extras(state, hard_mode, num_choices)
    return pick_count(state, 100)


@route
def set_count_50(state: State, hard_mode: bool,
                 num_choices: str) -> Page:
    """Use 50 flags."""
    restore_progress(state)
    apply_extras(state, hard_mode, num_choices)
    return pick_count(state, 50)


@route
def set_count_10(state: State, hard_mode: bool,
                 num_choices: str) -> Page:
    """Use 10 flags."""
    restore_progress(state)
    apply_extras(state, hard_mode, num_choices)
    return pick_count(state, 10)


# ------------------------------------------------------------- quiz routes
@route
def start_game(state: State, hard_mode: bool,
               num_choices: str) -> Page:
    """Build a quiz from the options and show the first question."""
    restore_progress(state)
    apply_extras(state, hard_mode, num_choices)
    state.fullscreen = False
    reset_game(state, new_quiz(state))
    return question(state)


@route
def try_again(state: State) -> Page:
    """Rebuild a quiz with the same options."""
    restore_progress(state)
    reset_game(state, new_quiz(state))
    return question(state)


@route
def study_missed(state: State) -> Page:
    """Quiz only on the flags that were missed."""
    restore_progress(state)
    if len(state.missed) == 0:
        return results(state)
    pool = build_pool(state.regions)
    wrong_pool = list(COUNTRIES) if state.hard_mode else pool
    redo = [make_question(find_country(missed.name), wrong_pool,
                          state.num_choices) for missed in state.missed]
    reset_game(state, redo)
    return question(state)


def answer_button(state: State, text: str, route_fn: Callable) -> Button:
    """Make an answer button, green/red once the question is answered."""
    if not state.answered:
        return styled_button(text, route_fn)
    color = GREEN if text == state.quiz[state.position].name else RED
    return styled_button(text, route_fn, color)


@route
def question(state: State) -> Page:
    """Show the current flag and its answer choices."""
    restore_progress(state)
    if len(state.quiz) == 0:
        return home_page(state)
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
    flag = Div(flag_image(find_country(current.name).image, 200),
               style_text_align="center", style_padding="20px")
    save_progress(state)
    return Page(state, [panel(top, flag, grid, LineBreak(), bottom)])


def record_answer(state: State, index_chosen: int) -> Page:
    """Grade the chosen answer and update score, streak, and misses."""
    restore_progress(state)
    if len(state.quiz) == 0 or state.answered:
        return question(state)
    current = state.quiz[state.position]
    state.picked = current.choices[index_chosen]
    state.answered = True
    if state.picked == current.name:
        state.score += 1
        state.streak += 1
    else:
        state.streak = 0
        state.missed.append(Missed(current.name, state.picked))
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
    restore_progress(state)
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
    restore_progress(state)
    return Page(state, [panel(Header("Quit this quiz?", 2),
                              styled_button("YES, QUIT", quit_to_home),
                              styled_button("KEEP PLAYING", question))])


@route
def quit_to_home(state: State) -> Page:
    """Return home while preserving the unfinished quiz for RESUME."""
    restore_progress(state)
    state.fullscreen = False
    return home_page(state)


@route
def go_home(state: State) -> Page:
    """Clear the quiz and go to the home page."""
    restore_progress(state)
    reset_game(state, [])
    state.fullscreen = False
    return home_page(state)


def missed_row(missed: Missed) -> Div:
    """Return one wrong answer: bordered flag, what was said, answer."""
    words = Div(Div(Span("You said: "), Span(colored(missed.said, RED))),
                Div(Span("Answer: "), Span(colored(missed.name, GREEN))))
    return Div(flag_image(find_country(missed.name).image, 80), words,
               style_display="flex", style_gap="30px",
               style_align_items="center", style_padding="10px")


@route
def results(state: State) -> Page:
    """Final score page with buttons and the list of missed flags."""
    restore_progress(state)
    if len(state.quiz) == 0:
        return home_page(state)
    buttons = [styled_button("HOME", go_home)]
    if len(state.missed) > 0:
        buttons.append(styled_button("STUDY MISSED", study_missed))
    buttons.append(styled_button("TRY AGAIN", try_again))
    heading = [Header("Final Score", 1),
               Header(f"{state.score}/{len(state.quiz)}", 2)]
    body = [Div(*heading, style_text_align="center"),
            Div(*buttons, style_display="flex", style_gap="30px",
                style_justify_content="center"),
            Header("Wrong answers", 3)]
    for missed in state.missed:
        body.append(missed_row(missed))
    save_progress(state)
    return Page(state, [panel(*body)])


# ------------------------------------------------------------- unit tests
# Each test uses TestState so save_progress does not overwrite player data.
# Randomized routes (start_game, try_again, study_missed) are not unit tested:
# their question order and distractor choices change on each run.
# Their deterministic supporting helpers are tested below.
if assert_equal is not None:
    def test_state() -> TestState:
        """Create an isolated state for one deterministic unit test."""
        return TestState(**asdict(new_state()))

    def test_quiz_state() -> TestState:
        """Create a state with a predictable question for route tests."""
        state = test_state()
        state.quiz = [Question("Zambia", ["Zambia", "Ghana",
                                           "Kenya", "Angola"]),
                      Question("Ghana", ["Ghana", "Zambia",
                                          "Kenya", "Angola"])]
        return state

    assert_equal(len(COUNTRIES), 197)
    assert_equal(len(load_countries()), len(COUNTRIES))
    assert_equal(count_available(["Oceania"], 100), False)
    assert_equal(count_available(["Oceania"], 10), True)
    assert_equal(count_available(["Oceania"], 0), True)
    assert_equal(len(build_pool(["Oceania"])),
                 len(COUNTRY_REGIONS["Oceania"]))
    assert_equal(len(build_pool([])), len(COUNTRIES))
    assert_equal(find_country("Zambia").image, "./Zambia.png")
    assert_equal(find_country("Vietnam").region, "Asia")
    assert_equal(flag_source("./missing.png"), "./missing.png")
    assert_equal(is_last_question(test_state()), True)
    assert_equal(is_last_question(test_quiz_state()), False)
    assert_equal(new_state().score, 0)
    assert_equal(new_state().flag_count, 0)

    _test = test_state()
    _test.flag_count = 100
    _test.regions = ["Oceania"]
    fix_count(_test)
    assert_equal(_test.flag_count, 0)
    assert_equal(apply_extras(_test, True, "3"), None)
    assert_equal(_test.num_choices, 3)
    assert_equal(_test.hard_mode, True)
    assert_equal(find_country("Zambia").region, "Africa")
    assert_equal(count_available(["Oceania"], 50), False)

    # Home, resume, and options routes.
    assert_equal(index(test_state()).state.fullscreen, False)
    assert_equal(resume_game(test_state()).state.quiz, [])
    assert_equal(resume_game(test_quiz_state()).state.position, 0)
    assert_equal(open_options(test_state(), False, "4").state.fullscreen,
                 True)
    _test = test_state()
    _test.fullscreen = True
    assert_equal(close_options(_test, False, "4").state.fullscreen,
                 False)

    # Every region toggle route is tested on an isolated state.
    assert_equal("Africa" in toggle_africa(test_state(), False, "4")
                 .state.regions, False)
    assert_equal("Asia" in toggle_asia(test_state(), False, "4")
                 .state.regions, False)
    assert_equal("Europe" in toggle_europe(test_state(), False, "4")
                 .state.regions, False)
    assert_equal("North America" in
                 toggle_north_america(test_state(), False, "4")
                 .state.regions, False)
    assert_equal("South America" in
                 toggle_south_america(test_state(), False, "4")
                 .state.regions, False)
    assert_equal("Oceania" in toggle_oceania(test_state(), False, "4")
                 .state.regions, False)

    # Each flag-count route is tested separately.
    assert_equal(set_count_all(test_state(), False, "4").state.flag_count,
                 0)
    assert_equal(set_count_100(test_state(), False, "4").state.flag_count,
                 100)
    assert_equal(set_count_50(test_state(), False, "4").state.flag_count,
                 50)
    assert_equal(set_count_10(test_state(), False, "4").state.flag_count,
                 10)

    # Answer routes use a fixed quiz instead of randomized questions.
    assert_equal(choose_0(test_quiz_state()).state.score, 1)
    assert_equal(choose_1(test_quiz_state()).state.score, 0)
    assert_equal(choose_2(test_quiz_state()).state.streak, 0)
    assert_equal(len(choose_3(test_quiz_state()).state.missed), 1)
    _test = test_quiz_state()
    _test.answered = True
    assert_equal(next_question(_test).state.position, 1)
    assert_equal(next_question(test_quiz_state()).state.position, 0)
    assert_equal(question(test_quiz_state()).state.position, 0)
    assert_equal(quit_game(test_quiz_state()).state.score, 0)
    assert_equal(len(quit_to_home(test_quiz_state()).state.quiz), 2)
    assert_equal(len(go_home(test_quiz_state()).state.quiz), 0)
    assert_equal(results(test_quiz_state()).state.position, 0)

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
# Checking files is optional and must never stop the quiz website.
check_flags()
start_server(new_state())
