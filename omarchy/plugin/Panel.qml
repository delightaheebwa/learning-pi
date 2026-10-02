import QtQuick
import Quickshell
import Quickshell.Io
import qs.Commons
import qs.Ui

// Pi review status bar widget.
//
// Reads `pi-review-status --json` and shows, only in the evening window
// (phase != "day"):
//   evening, pending  -> dim  "R"
//   evening/catchup, done -> "R✓"  (normal foreground)
//   catchup, missed   -> "R✗"  (urgent color)
//
// Left click launches pi in the learning-system checkout; right/middle click
// refreshes. State comes from a session-note filename match, so no sentinel
// bookkeeping is needed here.
BarWidget {
  id: root
  moduleName: "local.pi-review"

  property string reviewDate: ""
  property bool reviewDone: false
  property string phase: "day"
  property string lastError: ""

  readonly property bool inWindow: phase !== "day"
  readonly property bool missed: phase === "catchup" && !reviewDone
  readonly property string glyph: reviewDone ? "R✓" : (missed ? "R✗" : "R")
  readonly property string tooltip: {
    if (!inWindow) return ""
    if (reviewDone) return "Review done — " + reviewDate
    if (missed) return "No review for " + reviewDate + " — click to start"
    return "Review pending — click to start"
  }

  readonly property string home: Quickshell.env("HOME") || ""
  readonly property string statusBin: home + "/.local/bin/pi-review-status"
  readonly property string learningRoot: Quickshell.env("LEARNING_SYSTEM_ROOT") || (home + "/learning-system")
  readonly property int refreshIntervalSec: {
    var value = parseInt(String(setting("refreshIntervalSec", 60)), 10)
    if (!isFinite(value)) value = 60
    return Math.max(30, Math.min(600, value))
  }

  visible: inWindow
  implicitWidth: button.implicitWidth
  implicitHeight: button.implicitHeight

  function refresh() {
    if (!statusProc.running) statusProc.running = true
  }

  function update(raw) {
    try {
      var data = JSON.parse(String(raw || "").trim())
      reviewDate = String(data.date || "")
      reviewDone = data.done === true
      phase = String(data.phase || "day")
      lastError = ""
    } catch (error) {
      lastError = "could not parse pi-review-status output"
    }
  }

  function launchReview() {
    if (!root.bar) return
    var inner = "cd " + root.bar.shellQuote(root.learningRoot) + " && exec pi"
    root.bar.run("omarchy-launch-tui --app-id=org.learning-pi.review bash -lc " + root.bar.shellQuote(inner))
  }

  Timer {
    interval: root.refreshIntervalSec * 1000
    repeat: true
    running: true
    triggeredOnStart: true
    onTriggered: root.refresh()
  }

  Process {
    id: statusProc
    command: [root.statusBin, "--json"]
    stdout: StdioCollector {
      waitForEnd: true
      onStreamFinished: root.update(text)
    }
    stderr: StdioCollector { waitForEnd: true }
  }

  WidgetButton {
    id: button
    anchors.fill: parent
    bar: root.bar
    text: root.glyph
    active: root.missed
    dimmed: !root.reviewDone && !root.missed
    tooltipText: root.tooltip
    fontSize: Style.font.caption
    horizontalMargin: 5
    fixedWidth: vertical ? -1 : Style.bar.statusSlot
    onPressed: function(buttonCode) {
      if (buttonCode === Qt.RightButton || buttonCode === Qt.MiddleButton) root.refresh()
      else root.launchReview()
    }
  }
}
