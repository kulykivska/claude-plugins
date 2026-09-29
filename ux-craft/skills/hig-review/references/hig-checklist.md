# HIG checklist with values

Reference values for the `hig-review` pass. Where Apple states a
recommendation rather than a rule, it is marked "guideline"; where the value
is common practice rather than Apple's text, it is marked "practice".

## Navigation

- Tab bar (iPhone): 3 to 5 tabs (guideline); labels always shown; icon plus
  a one-word label; selected state uses the filled symbol and the tint.
- Tab bar never hides on scroll in a way that loses the user's place; it
  hides only for immersive or modal content.
- Sidebar (iPad, Mac): for more than five sections, user-created
  collections, or deep hierarchies. Sidebar items are destinations, not
  actions.
- Back button shows the previous screen's title (or "Back" when long).
- Deep links land on a screen with a working back path.

RaceModel example: Home, Races, Drivers, Leagues, Settings is five tabs.
Adding "Pro" as a sixth tab is a finding; Pro belongs in the screens it
unlocks and in Settings.

## Titles and bars

- Large title on root screens of each tab; collapses to inline on scroll.
- Detail screens: inline title.
- Navigation bar trailing: one primary action (Add, Edit, Done). Leading:
  back or Cancel.
- Search in the navigation bar (searchable) for lists users filter.

## Controls

| Need | Use | Avoid |
|------|-----|-------|
| 2 to 5 views of the same content | Segmented control | Tabs inside tabs, custom pill rows |
| On or off | Toggle | Checkbox styles on iOS |
| Pick one of many | Menu or picker (inline or navigation style) | Custom dropdowns |
| Pick a date or time | DatePicker | Free text |
| Range value | Slider or stepper | Text field |
| Destructive action | Button with destructive role, confirmation for irreversible | Red text links |

## Modality

- Sheet: self-contained task; medium and large detents when content allows
  a glance; grabber when resizable; Cancel leading, Done or the action
  trailing; swipe-to-dismiss guarded when there are unsaved changes.
- Popover: iPad and Mac, anchored to its source; adapts to a sheet on
  iPhone.
- Alert: title that is the question, optional one-line message, 2 buttons
  (3 at most), the destructive one marked; no alerts for information that
  could be inline.
- Confirmation dialog (action sheet) for choosing among actions from a
  source element.

## Typography (default Large content size, iOS)

| Style | Size (pt) | Weight |
|-------|-----------|--------|
| Large Title | 34 | Regular |
| Title 1 | 28 | Regular |
| Title 2 | 22 | Regular |
| Title 3 | 20 | Regular |
| Headline | 17 | Semibold |
| Body | 17 | Regular |
| Callout | 16 | Regular |
| Subheadline | 15 | Regular |
| Footnote | 13 | Regular |
| Caption 1 | 12 | Regular |
| Caption 2 | 11 | Regular |

- Custom fonts: map each role to a text style with `relativeTo:` (SwiftUI
  `.custom(_:size:relativeTo:)`) so they scale.
- At accessibility sizes, horizontal layouts stack vertically; numbers in
  tables may use monospaced digits.
- Minimum 11 pt at the default size.

## Layout

- 8 pt grid for spacing (practice); 4 pt for tight internal padding.
- Margins: system layout margins or readable content guide; typically 16 pt
  on compact width, 20 pt on regular width.
- Safe areas respected; nothing interactive under the Dynamic Island or the
  home indicator.
- Lists: standard row height at least 44 pt; insets aligned to the title.

## Targets

- At least 44x44 pt hit area (guideline), even when the visible glyph is
  smaller: extend with padding or `contentShape`.
- At least 8 pt between adjacent targets (practice).

## Colour and appearance

- Semantic colours: `label`, `secondaryLabel`, `tertiaryLabel`,
  `systemBackground`, `secondarySystemBackground`, `separator`, the app tint.
- Dark mode is designed, not inverted: elevated surfaces lighter, shadows
  replaced by surface contrast, vivid colours desaturated slightly.
- Increase Contrast variants for custom colours.
- Meaning never carried by colour alone: add a symbol, label or shape
  (RaceModel: gains and losses in places use an arrow as well as green and
  red).

## Contrast (WCAG 2.x AA)

- Body text: 4.5:1.
- Large text (at least 18 pt regular or 14 pt bold): 3:1.
- Non-text essentials (icons that carry meaning, control borders, focus
  indicators): 3:1 against adjacent colours.
- Check in both appearances and over images (use a scrim).

## Iconography

- SF Symbols first; custom symbols built on the SF Symbols template.
- Symbol weight matches the adjacent text weight; scale small, medium or
  large to match context.
- One rendering mode per context (monochrome in bars, hierarchical or
  palette in content).
- Filled variant for selected tab items.

## States

- Empty: explains and offers one action.
- Loading: skeleton or progress with context; never a blank screen.
- Error: inline, recoverable, keeps the user's input.
- Offline: shows cached content with its age.

## Accessibility

- VoiceOver: label (purpose), value (current state), hint only when the
  result is not obvious, traits (button, header, selected, adjustable).
- Grouping: a row reads as one element ("Leclerc, Ferrari, 34% chance to
  win, button").
- Focus order matches reading order; modal content traps focus; dismissing
  returns focus to the source.
- Custom gestures have an accessible action (accessibilityAction) or a
  visible control.
- Honour Reduce Motion, Reduce Transparency, Bold Text, Increase Contrast,
  Button Shapes, and Differentiate Without Colour.
- Web: semantic elements, visible focus, `aria-label` where text is absent,
  respects the browser font size, `prefers-color-scheme`,
  `prefers-reduced-motion`, `prefers-contrast`.
