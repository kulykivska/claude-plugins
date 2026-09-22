# Shipping an iOS app to the App Store

## One-time setup per machine

```bash
brew install fastlane xcodegen
```

Ruby 2.6 ships with macOS and fastlane will complain. Install a newer one:

```bash
brew install ruby
echo 'export PATH="/opt/homebrew/opt/ruby/bin:$PATH"' >> ~/.zshrc
```

## Credentials

An **App Store Connect API key** replaces the Apple ID password and 2FA, which
is what makes unattended submission possible.

1. App Store Connect → Users and Access → Integrations → App Store Connect API
2. Generate a key with the **App Manager** role. Anything less cannot create a
   new app record.
3. Download the `.p8` once. It cannot be downloaded again.
4. Store it outside the repo, for example `~/.appstoreconnect/AuthKey_XXXX.p8`.

Three values are needed: key id, issuer id, and the path to the `.p8`.
Put them in the environment, never in a committed file:

```bash
export ASC_KEY_ID=XXXXXXXXXX
export ASC_ISSUER_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
export ASC_KEY_PATH=~/.appstoreconnect/AuthKey_XXXXXXXXXX.p8
export FASTLANE_TEAM_ID=XXXXXXXXXX
```

## Fastfile

```ruby
default_platform(:ios)

platform :ios do
  before_all do
    app_store_connect_api_key(
      key_id: ENV["ASC_KEY_ID"],
      issuer_id: ENV["ASC_ISSUER_ID"],
      key_filepath: ENV["ASC_KEY_PATH"],
      in_house: false
    )
  end

  desc "Build and push to TestFlight"
  lane :beta do
    increment_build_number(xcodeproj: "App.xcodeproj")
    sync_code_signing(type: "appstore", readonly: false)
    build_app(scheme: "App", export_method: "app-store")
    upload_to_testflight(skip_waiting_for_build_processing: true)
  end

  desc "Upload metadata and screenshots, then submit for review"
  lane :release do
    sync_code_signing(type: "appstore", readonly: false)
    build_app(scheme: "App", export_method: "app-store")
    upload_to_app_store(
      submit_for_review: true,
      automatic_release: false,
      force: true,
      precheck_include_in_app_purchases: false,
      submission_information: {
        add_id_info_uses_idfa: false,
        export_compliance_uses_encryption: false
      }
    )
  end

  desc "Capture App Store screenshots from the simulator"
  lane :shots do
    capture_screenshots
    frame_screenshots(white: true)
  end
end
```

## Metadata that Apple rejects builds over

- **Screenshots** are mandatory for 6.9" and 6.5" iPhone. Generate them with
  the app's `_UI_PREVIEW=1` flag so no permission dialog is in frame.
- **Privacy policy URL** is required for any app that touches personal data.
  A calendar or mail app always needs one.
- **App privacy** answers in App Store Connect must match reality. An app that
  keeps the API key on device and sends calendar text to a third-party model
  endpoint *is* sharing data with a third party; say so.
- **Sign in with Apple** is required only if the app offers other third-party
  logins. Google OAuth for Gmail alone does not trigger it, but adding a
  "Sign in with Google" account system does.
- **Encryption** — set `ITSAppUsesNonExemptEncryption` to `false` in Info.plist
  unless doing custom crypto. Otherwise every upload asks about it.
- **Demo account** in App Review notes for anything behind a login. Reviewers
  reject rather than sign up.
- **Purpose strings** must say why, not what. "Chip reads your calendars so it
  can plan your day" passes; "This app uses calendars" gets rejected.

## Third-party model endpoints

An app that lets the user paste any API key and endpoint is fine, but App
Review will ask what it connects to. In the review notes, state that the user
supplies their own key, no key ships in the binary, and the default endpoint is
whichever provider is preselected.

## Sequence for a brand-new app

```bash
fastlane produce -a io.racemodel.chip -q "Chip" --skip_itc false   # create records
fastlane beta                                                       # TestFlight
fastlane shots                                                      # screenshots
fastlane release                                                    # submit
```

## What cannot be automated

- Apple's review decision, one to three days.
- The Apple Developer Program enrolment itself.
- Anything requiring a human to accept a new agreement in App Store Connect;
  uploads fail with a vague error until the agreement is accepted in the UI.
