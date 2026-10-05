"""CS 1430 Betweener checker.

Run this file to check your work:   python check.py

Fix the FIRST line that says FAIL, save, and run this file again.
You do not need to read or change anything in this file.
"""

import ast
import copy
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN = HERE / "main.py"
TEMPLATE_URL = "github.com/CS1430/betweener-lab/blob/main/main.py"

MARKERS = [
    "--- Part 1: given ---",
    "--- Part 1: yours ---",
    "--- Part 2: given ---",
    "--- Part 2: yours ---",
]

# Ages typed into main.py. Every age right at the edges, plus a few far away.
TEST_AGES = [0, 10, 16, 17, 18, 19, 20, 21, 22, 30, 65, 100]

# The code you were given, exactly as it shipped. Comments and blank lines
# don't matter; the code itself must stay the same.
ORIGINAL = '''
LOW_AGE = 18
HIGH_AGE = 21
AGE_PROMPT = "Please enter an age --> "

user_age = int(input(AGE_PROMPT))

print("--- Part 1: given ---")
if user_age >= LOW_AGE:
    if user_age < HIGH_AGE:
        print("BETWEENER")

print("--- Part 1: yours ---")

print("--- Part 2: given ---")
if user_age < LOW_AGE:
    print("NOT BETWEENER")
else:
    if user_age >= HIGH_AGE:
        print("NOT BETWEENER")

print("--- Part 2: yours ---")
'''

PARTS = [
    {
        "name": "Part 1",
        "word_op": ast.And,
        "word_label": "uses the strict parents' word",
        "word_hint": ("Back to the dinner plate. The strict parents need EVERY item\n"
                      "eaten, and Python has a word for that."),
    },
    {
        "name": "Part 2",
        "word_op": ast.Or,
        "word_label": "uses Grandma's word",
        "word_hint": ("Back to the dinner plate. Grandma only needs ONE item eaten,\n"
                      "and Python has a word for that."),
    },
]


# ---------------------------------------------------------------- output

def _use_color():
    if not sys.stdout.isatty() or os.environ.get("NO_COLOR"):
        return False
    if os.name == "nt":
        os.system("")  # turns on color codes in the Windows terminal
    return True


COLOR = _use_color()


def _paint(text, code):
    return f"\033[{code}m{text}\033[0m" if COLOR else text


LABELS = {
    "PASS": _paint("[PASS]", "32"),
    "FAIL": _paint("[FAIL]", "31"),
    "SKIP": _paint("[ -- ]", "90"),
}


class Report:
    def __init__(self):
        self.first_fail_shown = False
        self.failed = False

    def heading(self, text):
        print()
        print(_paint(text, "1"))

    def line(self, status, text, hint=""):
        print(f"  {LABELS[status]} {text}")
        if status == "FAIL":
            self.failed = True
            if hint and not self.first_fail_shown:
                for hint_line in hint.strip().splitlines():
                    print(_paint(f"         > {hint_line}", "33"))
            self.first_fail_shown = True

    def skip(self, *texts):
        for text in texts:
            self.line("SKIP", text)


def part_labels(part):
    p = f"{part['name']}, yours"
    return [
        f"{p}: has code",
        f"{p}: one if statement, nothing nested",
        f"{p}: {part['word_label']}",
        f"{p}: uses LOW_AGE and HIGH_AGE, no bare numbers",
        f"{p}: prints the same as given for {len(TEST_AGES)} different ages",
    ]


# ---------------------------------------------------------------- helpers

def run_git(*args, timeout=20):
    """Run a git command in this folder. Returns (ok, output)."""
    try:
        result = subprocess.run(
            ["git", *args], cwd=HERE, capture_output=True, text=True,
            timeout=timeout, encoding="utf-8", errors="replace",
        )
    except (OSError, subprocess.TimeoutExpired) as err:
        return False, str(err)
    return result.returncode == 0, (result.stdout + result.stderr).strip()


def run_main(age):
    """Run main.py, typing one age. Returns (returncode, stdout, stderr)."""
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    try:
        result = subprocess.run(
            [sys.executable, str(MAIN)], cwd=HERE, input=f"{age}\n",
            capture_output=True, text=True, timeout=10, env=env,
            encoding="utf-8", errors="replace",
        )
    except subprocess.TimeoutExpired:
        return None, "", "timeout"
    return result.returncode, result.stdout, result.stderr


def explain_crash(stderr, age):
    last = stderr.strip().splitlines()[-1] if stderr.strip() else "(no message)"
    if last.startswith("NameError"):
        return (f"Typed {age} and main.py crashed on a name Python doesn't know.\n"
                "Check the spelling and capitals of every name you used.\n"
                f"Python said: {last}")
    if last.startswith("EOFError"):
        return (f"Typed {age} and main.py asked for input again.\n"
                "The program should ask for an age only once. Don't add input().")
    return f"Typed {age} and main.py crashed. The last line of the error was:\n{last}"


def is_marker(stmt):
    """True if this line is one of the print("--- Part ...") lines."""
    return (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call)
            and isinstance(stmt.value.func, ast.Name) and stmt.value.func.id == "print"
            and len(stmt.value.args) == 1 and isinstance(stmt.value.args[0], ast.Constant)
            and stmt.value.args[0].value in MARKERS)


def find_markers(tree):
    """Find the four marker lines. Returns their positions in the file, or None."""
    spots = [i for i, stmt in enumerate(tree.body) if is_marker(stmt)]
    found = [tree.body[i].value.args[0].value for i in spots]
    if found != MARKERS:
        return None
    return spots


def is_constant(stmt):
    """True if this line sets an ALL_CAPS name, like LOW_AGE = 18."""
    return (isinstance(stmt, ast.Assign)
            and all(isinstance(t, ast.Name) and t.id.isupper() for t in stmt.targets))


def without_yours(tree):
    """A copy of the program with both 'yours' sections removed."""
    tree = copy.deepcopy(tree)
    m1, m2, m3, m4 = find_markers(tree)
    body = tree.body
    tree.body = body[:m2 + 1] + body[m3:m4 + 1]
    return tree


def dump(nodes):
    return "\n".join(ast.dump(n) for n in nodes)


def given_sections(tree):
    """Break the given code into named pieces so a change can be located."""
    m1, m2, m3, m4 = find_markers(tree)
    body = tree.body
    top = body[:m1]
    return {
        "the CONSTANTS": dump([n for n in top if is_constant(n)]),
        "the input line": dump([n for n in top if not is_constant(n)]),
        "the Part 1 given code": dump(body[m1:m2 + 1]),
        "the Part 2 given code": dump(body[m3:m4 + 1]),
    }


def section_output(stdout, which):
    """Text printed between marker number `which` and the next marker."""
    start = stdout.find(MARKERS[which])
    if start == -1:
        return None
    start += len(MARKERS[which])
    end = stdout.find(MARKERS[which + 1], start) if which + 1 < len(MARKERS) else len(stdout)
    if end == -1:
        return None
    lines = [ln.rstrip() for ln in stdout[start:end].replace("\r\n", "\n").split("\n")]
    return "\n".join(ln for ln in lines if ln)


def show(text):
    return "(nothing)" if not text else " / ".join(text.splitlines())


# ---------------------------------------------------------------- checks

def check_part(report, part, region, runs, runs_ok):
    """All the checks for one 'yours' section."""
    labels = part_labels(part)
    region_mod = ast.Module(body=region, type_ignores=[])

    if not region:
        report.line("FAIL", labels[0],
                    f"There's no code under the \"{MARKERS[1] if part['name'] == 'Part 1' else MARKERS[3]}\" line yet.\n"
                    "Your code goes there, starting at the left edge, lined up with\n"
                    "the print above it.")
        report.skip(*labels[1:])
        return
    report.line("PASS", labels[0])

    ifs = [n for n in ast.walk(region_mod) if isinstance(n, ast.If)]
    if len(ifs) != 1:
        lines = ", ".join(str(n.lineno) for n in ifs)
        if not ifs:
            hint = (f"{part['name']} needs an if statement that makes the decision.")
        else:
            hint = (f"Found {len(ifs)} if statements (lines {lines}). That counts every elif\n"
                    "and every if tucked inside another one.\n"
                    f"{part['name']} should make its whole decision with ONE if.")
        report.line("FAIL", labels[1], hint)
    else:
        report.line("PASS", labels[1])

    chained = [n for n in ast.walk(region_mod)
               if isinstance(n, ast.Compare) and len(n.ops) > 1]
    has_word = any(isinstance(n, ast.BoolOp) and isinstance(n.op, part["word_op"])
                   for n in ast.walk(region_mod))
    if chained:
        report.line("FAIL", labels[2],
                    f"Line {chained[0].lineno} chains comparisons, like a < b < c.\n"
                    "That's legal Python, but this lab practices writing two separate\n"
                    "comparisons and joining them with a word.")
    elif not has_word:
        report.line("FAIL", labels[2], part["word_hint"])
    else:
        report.line("PASS", labels[2])

    numbers = [n for n in ast.walk(region_mod)
               if isinstance(n, ast.Constant) and isinstance(n.value, (int, float))
               and not isinstance(n.value, bool)]
    names = {n.id for n in ast.walk(region_mod) if isinstance(n, ast.Name)}
    if numbers:
        report.line("FAIL", labels[3],
                    f"Line {numbers[0].lineno} has the number {numbers[0].value} typed in.\n"
                    "Use the constants at the top of the file instead of typing numbers.")
    elif not {"LOW_AGE", "HIGH_AGE"} <= names:
        missing = " and ".join(sorted({"LOW_AGE", "HIGH_AGE"} - names))
        report.line("FAIL", labels[3],
                    f"Your {part['name']} code never uses {missing}.\n"
                    "Both ends of the age range matter here.")
    else:
        report.line("PASS", labels[3])

    if not runs_ok:
        report.skip(labels[4])
        return
    which = 0 if part["name"] == "Part 1" else 2
    for age, out in runs:
        given = section_output(out, which)
        yours = section_output(out, which + 1)
        if given != yours:
            report.line("FAIL", labels[4],
                        f"Typed {age}.\n"
                        f"  given printed: {show(given)}\n"
                        f"  yours printed: {show(yours)}\n"
                        "Run main.py yourself, type that age, and compare.")
            return
    report.line("PASS", labels[4])


def check_code(report):
    report.heading("Toolchain")
    version = ".".join(str(p) for p in sys.version_info[:3])
    report.line("PASS", f"Python is installed ({version})")

    if not MAIN.exists():
        report.line("FAIL", "main.py is in this folder",
                    "Use File > Open Folder and open the whole Betweener folder,\n"
                    "not a single file.")
        return
    report.line("PASS", "main.py is in this folder")

    report.heading("Your code")
    all_part_labels = part_labels(PARTS[0]) + part_labels(PARTS[1])
    later = ["The given code is unchanged", "main.py runs"] + all_part_labels

    source = MAIN.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(source)
    except SyntaxError as err:
        report.line("FAIL", "main.py has no syntax errors",
                    f"Python can't read line {err.lineno}: {err.msg}\n"
                    "Look for a missing colon, parenthesis, or quote.\n"
                    "Your if starts at the left edge, like the given code. Only the\n"
                    "lines INSIDE the if are indented one step.")
        report.skip(*later)
        return
    report.line("PASS", "main.py has no syntax errors")

    original = ast.parse(ORIGINAL)
    restore = (f"Undo with Ctrl+Z, or copy that part back from the class template:\n"
               f"{TEMPLATE_URL}")
    if find_markers(tree) is None:
        report.line("FAIL", "The given code is unchanged",
                    "One of the four  print(\"--- Part ...\")  lines was changed, moved,\n"
                    "indented, or deleted.\n" + restore)
        report.skip(*later[1:])
        return
    mine, theirs = given_sections(without_yours(tree)), given_sections(original)
    changed = [name for name in theirs if mine[name] != theirs[name]]
    if changed:
        report.line("FAIL", "The given code is unchanged",
                    f"Something changed in {changed[0]}.\n"
                    "Only add code under the two \"yours\" lines.\n" + restore)
        report.skip(*later[1:])
        return
    report.line("PASS", "The given code is unchanged")

    runs, runs_ok = [], True
    for age in TEST_AGES:
        code, out, err = run_main(age)
        if code is None:
            report.line("FAIL", "main.py runs",
                        f"Typed {age} and main.py was still running after 10 seconds.")
            runs_ok = False
            break
        if code != 0:
            report.line("FAIL", "main.py runs", explain_crash(err, age))
            runs_ok = False
            break
        runs.append((age, out))
    if runs_ok:
        report.line("PASS", f"main.py runs (typed {len(TEST_AGES)} different ages)")

    m1, m2, m3, m4 = find_markers(tree)
    regions = [tree.body[m2 + 1:m3], tree.body[m4 + 1:]]
    for part, region in zip(PARTS, regions):
        check_part(report, part, region, runs, runs_ok)


def check_git(report):
    report.heading("Git and GitHub")

    if not shutil.which("git"):
        report.line("FAIL", "Git is installed",
                    "Close every terminal, then close and reopen VS Code.\n"
                    "If that doesn't fix it, reinstall Git from Assignment 1.")
        report.skip("This folder is a Git repository", "Your copy is on your own GitHub account",
                    "Your code is committed", "Your commit is pushed to GitHub")
        return
    report.line("PASS", "Git is installed")

    ok, _ = run_git("rev-parse", "--is-inside-work-tree")
    if not ok:
        report.line("FAIL", "This folder is a Git repository",
                    "This folder wasn't cloned with git clone.\n"
                    "Did you download the ZIP? Go back to step 2 in README.md.")
        report.skip("Your copy is on your own GitHub account",
                    "Your code is committed", "Your commit is pushed to GitHub")
        return
    report.line("PASS", "This folder is a Git repository")

    ok, url = run_git("config", "--get", "remote.origin.url")
    if not ok or "github.com" not in url.lower():
        report.line("FAIL", "Your copy is on your own GitHub account",
                    "This folder isn't connected to GitHub.\n"
                    "Go back to step 2 in README.md and clone YOUR copy.")
        report.skip("Your code is committed", "Your commit is pushed to GitHub")
        return
    if "github.com/cs1430/" in url.lower() or "github.com:cs1430/" in url.lower():
        report.line("FAIL", "Your copy is on your own GitHub account",
                    "You cloned the CLASS template, not your own copy.\n"
                    "Go back to step 1 in README.md: Use this template > Create a new repository.")
        report.skip("Your code is committed", "Your commit is pushed to GitHub")
        return
    report.line("PASS", "Your copy is on your own GitHub account")

    ok_root, roots = run_git("rev-list", "--max-parents=0", "HEAD")
    ok_status, status = run_git("status", "--porcelain", "--", "main.py")
    changed_since_template = False
    if ok_root and roots:
        root = roots.splitlines()[0]
        same, _ = run_git("diff", "--quiet", root, "HEAD", "--", "main.py")
        changed_since_template = not same
    if ok_status and status:
        report.line("FAIL", "Your code is committed",
                    "main.py has changes that aren't committed yet.\n"
                    "Save (Ctrl+S), then in Source Control type a message and click Commit.")
        report.skip("Your commit is pushed to GitHub")
        return
    if not changed_since_template:
        report.line("FAIL", "Your code is committed",
                    "Your code isn't in a commit yet. Save (Ctrl+S), then in\n"
                    "Source Control type a message and click Commit.")
        report.skip("Your commit is pushed to GitHub")
        return
    report.line("PASS", "Your code is committed")

    ok_local, local = run_git("rev-parse", "HEAD")
    ok_remote, remote = run_git("ls-remote", "origin", "HEAD", timeout=30)
    if not ok_remote:
        report.line("FAIL", "Your commit is pushed to GitHub",
                    "Could not reach GitHub to check. Make sure you're online,\n"
                    "then run this file again.")
        return
    remote_sha = remote.split()[0] if remote else ""
    if ok_local and local == remote_sha:
        report.line("PASS", "Your commit is pushed to GitHub")
    else:
        report.line("FAIL", "Your commit is pushed to GitHub",
                    "Committing saves your work on this computer. PUSH sends it\n"
                    "to GitHub. Click Sync Changes (or run git push), then run this file again.")


def main():
    print(_paint("CS 1430 Betweener checker", "1"))
    report = Report()
    check_code(report)
    check_git(report)
    print()
    if report.failed:
        print("Fix the FIRST line that says FAIL, save, and run this file again.")
    else:
        print(_paint("All checks passed. The Betweener code is done.", "32"))


if __name__ == "__main__":
    main()
