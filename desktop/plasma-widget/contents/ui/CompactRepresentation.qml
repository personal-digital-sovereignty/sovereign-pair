import QtQuick
import org.kde.plasma.plasmoid
import org.kde.plasma.components as PlasmaComponents
import org.kde.kirigami as Kirigami

Item {
    id: compactRoot
    
    // We get properties from parent `main.qml` via implicit contextual resolution
    // `root.quarantineCount` and `root.activeModels`

    width: Kirigami.Units.iconSizes.small
    height: Kirigami.Units.iconSizes.small

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        onClicked: Plasmoid.expanded = !Plasmoid.expanded
        
        PlasmaComponents.ToolTip {
            visible: mouseArea.containsMouse
            text: "Sovereign Pair\n" + (root.activeModels > 0 ? "AI Online (" + root.avgTps.toFixed(1) + " T/s)" : "Modo O.S (Standby)")
        }
    }

    Image {
        id: icon
        anchors.centerIn: parent
        width: Math.min(parent.width, parent.height) * 0.9
        height: width
        // The beautiful layered SVG instead of a simple monochrome mask
        source: "app-icon.svg"
        sourceSize.width: 128
        sourceSize.height: 128
        fillMode: Image.PreserveAspectFit
    }
    
    // Notification Badge for Pending Vault Actions
    Rectangle {
        visible: root.tasksToday > 0 || root.quarantineCount > 0
        width: 12
        height: 12
        radius: 6
        color: root.quarantineCount > 0 ? Kirigami.Theme.negativeTextColor : Kirigami.Theme.highlightColor
        anchors.right: icon.right
        anchors.top: icon.top
        anchors.margins: -2

        PlasmaComponents.Label {
            anchors.centerIn: parent
            text: root.quarantineCount > 0 ? root.quarantineCount : root.tasksToday
            font.pixelSize: 8
            font.weight: Font.Bold
            color: Kirigami.Theme.backgroundColor
        }
    }
}
