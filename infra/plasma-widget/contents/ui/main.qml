import QtQuick
import org.kde.plasma.plasmoid
import org.kde.kirigami as Kirigami
import QtQuick.Layouts

PlasmoidItem {
    id: root

    // Compatibility mode for Plasma 6 (Removed deprecated KDE5 Enums)
    // Core state properties mapped from Rust Telemetry
    property int totalTokens: 0
    property real avgTps: 0.0
    property int activeModels: 0
    property int tasksToday: 0
    property int quarantineCount: 0

    // Fetch Telemetry from Rust Core
    Timer {
        interval: 2000 // Poll every 2 seconds
        running: root.expanded || true // Keep polling even compact to update systray icon styles
        repeat: true
        onTriggered: fetchTelemetry()
    }

    function fetchTelemetry() {
        var req = new XMLHttpRequest();
        req.onreadystatechange = function() {
            if (req.readyState === XMLHttpRequest.DONE) {
                if (req.status === 200 && req.responseText) {
                    try {
                        var data = JSON.parse(req.responseText);
                        root.totalTokens = data.total_tokens || 0;
                        root.avgTps = data.avg_tps || 0.0;
                        root.activeModels = data.active_models || 0;
                        if (data.cronos) {
                            root.tasksToday = data.cronos.tasks_today || 0;
                            root.quarantineCount = data.cronos.gaps || 0;
                        }
                    } catch (e) {
                        console.log("Sovereign Plasmoid JSON error: " + e + ". Text: " + req.responseText);
                    }
                }
            }
        };
        req.open("GET", "http://127.0.0.1:38001/v1/analytics/telemetry");
        req.send();
    }

    Component.onCompleted: {
        fetchTelemetry(); // Force sync on mount
    }

    Plasmoid.icon: Qt.resolvedUrl("app-icon.svg")

    fullRepresentation: FullRepresentation {}
}
