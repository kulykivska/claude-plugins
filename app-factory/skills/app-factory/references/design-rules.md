# Design rules every generated app starts with

These are not suggestions to apply at the end. They are constraints on the
first draft, because retrofitting good interaction onto a typed-in form is more
work than building it right once.

## 1. Pick, never type

Free text is the last resort, not the default. For every input, ask what the
user is actually choosing from:

| The user is choosing | Use | Never |
|---|---|---|
| A time | `DatePicker`, or tappable slot chips from real free/busy data | A text field asking for a time |
| A day | A horizontal week strip, today preselected | A date typed as text |
| A duration | Segmented chips: 30m · 1h · 90m · 2h | A number field |
| One of a known set | `Picker`, or a row of chips if fewer than six | A dropdown of forty items |
| A place | Recent locations first, then search | An empty address field |
| A person | Contacts, recents at the top | Typing a name |

Where free text is unavoidable, seed it. Show four tappable example phrases the
first time a screen is empty, the way Chip's chat does. An empty box with a
blinking cursor is a design failure.

## 2. Voice is a first-class input, not a feature

Any screen where the user would otherwise type a sentence gets a microphone.
Rules:

- One press to start, the button stays held down visually while recording.
- Show the live transcription as it comes in, so the user can see it is working.
- Let the user edit the transcript before it is sent. Never act on speech the
  user has not seen.
- Stop automatically after two seconds of silence.
- Never require voice. Everything reachable by voice is reachable by hand.

`SFSpeechRecognizer` with on-device recognition where the locale supports it,
so nothing is uploaded for transcription.

## 3. Nothing happens without a receipt

When the app changes something the user cares about, show what changed, in the
same place, immediately. Chip prints one line per calendar edit in the thread.

Every destructive or hard-to-reverse action gets an undo, not a confirmation
dialog. Undo respects the user's time; "Are you sure?" does not.

## 4. State is always visible

The user must never wonder whether the app is working. Chip does this with the
dog: idle, listening, thinking, speaking, failed are five visibly different
animations. Any app in this factory needs an equivalent, even if it is only a
status line. Rules:

- Never show a spinner with no text.
- Errors say what to do next, not what went wrong internally.
  "No API key set. Open Settings and paste a key" beats "401 Unauthorized".

## 5. One screen, one job

Three tabs is usually right. If a fourth is needed, something belongs inside
another screen. Settings is always the last tab and always contains the boring
things: accounts, keys, defaults.

## 6. Platform-native, both themes, all sizes

- SwiftUI system components unless there is a reason not to. A custom control
  costs accessibility, Dynamic Type and dark mode by default.
- Every colour from a semantic token or the asset catalog, never a literal that
  only works on white.
- Test at the smallest Dynamic Type size and the largest. Text truncating at
  accessibility sizes is the most common rejection-worthy bug.
- Nothing smaller than 44×44 points is tappable.

## 7. Draw, do not ship, the artwork

Chip is drawn with SwiftUI shapes: no image assets, crisp at any size, tintable
per state, and it animates without a library. Prefer this for mascots, icons
and illustrations. Reach for Lottie only when the motion is genuinely beyond
shapes and springs.

## 8. Build for the triad from day one

An app that will later exist on iPhone, Mac and Watch is split at the start,
because splitting it later means rewriting the views:

```
<Name>Core/          Swift package: models, services, agent, networking.
                     No SwiftUI. No UIKit. Compiles for iOS, macOS, watchOS.
<Name>/              iPhone app: full interface.
<Name>Mac/           Mac app: same core, wider layout, menu bar item.
<Name>Watch/         Watch app: one glance, one action, complications.
<Name>Widget/        Widgets and Live Activities, shared with the watch.
```

State that has to be the same everywhere goes through one store in the core,
backed by CloudKit or an App Group, never copied between targets.

The Watch app is not a small phone app. It answers exactly one question and
offers exactly one action. For a schedule assistant that is: what is next, and
a microphone to change it.

## 9. Accessibility is part of the first draft

Every control gets a label. Every animation respects
`accessibilityReduceMotion`. Every colour pairing clears 4.5:1. This is fifteen
minutes during the build and a week after.
