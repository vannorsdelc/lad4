# CS 1430 · Betweener

`main.py` already works. It asks for an age and makes two decisions about it. Your job is to write each of those two decisions **again, in a different shape**, under the lines marked `yours`. Your instructor explains the task in class.

**You're done when** `check.py` shows PASS on every line. After that, your instructor will give you the reflection.

---

## Before you start

You need the Assignment 1 toolchain: Python, Git, VS Code with the Python extension, and a GitHub account you're signed in to.

---

## Step 1: Make your own copy

1. On this page, click the green **Use this template** button (top right) → **Create a new repository**.
2. **Owner:** your own account, not CS1430.
3. **Repository name:** `Betweener`
4. **Visibility:** Public
5. Click **Create repository**.

> **Do NOT click Fork.** Use this template only.

---

## Step 2: Clone it to your computer

1. On **your** new repo's page, click the green **Code** button and copy the HTTPS URL.
2. Open VS Code. Open a terminal: **Terminal → New Terminal**.
3. Type this, using **your** URL (not CS1430's), and press Enter:

```
git clone https://github.com/YOUR-USERNAME/Betweener.git C:\CS1430\Betweener
```

Keep your work out of Documents, Desktop, and OneDrive.

---

## Step 3: Open the folder in VS Code

1. **File → Open Folder…** and choose `C:\CS1430\Betweener`. Pick the **whole folder**, not a single file.
2. If VS Code asks whether you trust the authors, click **Yes, I trust the authors**.
3. In the Explorer panel you should see `README.md`, `main.py`, `check.py`, and a few items that start with a dot.

---

## Step 4: Copilot stays quiet in this folder

This folder includes a settings file that turns off Copilot's typing suggestions here, and only here. Leave it that way.

- Don't ask Copilot Chat (or any other AI) to write the `yours` code. The point is for **you** to work out the new shape.
- Asking an AI to explain an error message in plain words is fine.

---

## Step 5: Run it first

Open `main.py` and click **▷ Run** (top right). Type an age and press Enter. Run it several more times with different ages. Try ages right at the edges, not just easy ones.

Notice what each `given` part prints, and when it prints nothing at all.

---

## Step 6: Write your code

Write your code under each `yours` line in `main.py`, indented to line up with the `print` above it.

| Rule | |
|---|---|
| Each `yours` part prints **exactly** what the `given` part above it prints, for **every** age | Including printing nothing when the given part prints nothing |
| Don't change the given code, the constants, or the four `--- Part ---` lines | `check.py` compares them to the original |
| `check.py` lists the rest | Read its output. It's your to-do list |

Save the file: **Ctrl + S**.

---

## Step 7: Run the checker

Type this in the terminal:

```
python check.py
```

Under **Git and GitHub**, `Your code is committed` will say **FAIL** until you commit. **That's expected.**

> **Rule of thumb:** fix only the **first** FAIL line, save, and run the checker again.

---

## Step 8: Commit and push

| Save | Where it lives |
|---|---|
| **Saved** (Ctrl + S) | Only this computer |
| **Committed** (a labeled snapshot) | Still only this computer |
| **Pushed** | On GitHub |

**In VS Code:**

1. Click the **Source Control** icon in the left sidebar.
2. Type a short message, like `wrote betweener`.
3. Click **✓ Commit**. If VS Code asks about staging changes, click **Yes**.
4. Click **Sync Changes** (or **Push**).

**Prefer the terminal?**

```
git add .
git commit -m "wrote betweener"
git push
```

---

## Step 9: Run the checker again

```
python check.py
```

Every line should say **PASS**.

---

## If something breaks

| You see | Fix |
|---|---|
| `'git' is not recognized` | Close every terminal, then close and reopen VS Code |
| `main.py is in this folder` FAIL | **File → Open Folder** and pick `C:\CS1430\Betweener` |
| `The given code is unchanged` FAIL | Undo with Ctrl + Z, or copy the original `main.py` from the class template on GitHub and add your code back |
| `expected an indented block` or `unindent does not match` | Line your code up with the `print` above it; code inside an `if` goes one step further in |
| `prints the same as given` FAIL | Run `main.py`, type the age the checker names, and compare the two parts yourself |
| `Your copy is on your own GitHub account` FAIL | You cloned the class template. Go back to Step 1 |
| `Your code is committed` FAIL | Step 8, parts 1 to 3 |
| `Your commit is pushed to GitHub` FAIL | Click **Sync Changes**, or run `git push` |
| `python` opens the Microsoft Store | Try `py check.py` instead, then ask your instructor |
