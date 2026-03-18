import QtQuick
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.components as PlasmaComponents
import org.kde.kirigami as Kirigami

Item {
    id: compactRoot
    
    // We get properties from parent `main.qml` via implicit contextual resolution
    // `root.quarantineCount` and `root.activeModels`

    width: PlasmaCore.Units.iconSizes.small
    height: PlasmaCore.Units.iconSizes.small

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        onClicked: Plasmoid.expanded = !Plasmoid.expanded
    }

    PlasmaCore.IconItem {
        id: icon
        anchors.centerIn: parent
        width: Math.min(parent.width, parent.height) * 0.9
        height: width
        // Troca de cor/icone caso haja algo na quarentena ou modelos ativos
        source: root.quarantineCount > 0 ? "security-high" : (root.activeModels > 0 ? "cpu" : "brain")
        colorGroup: root.quarantineCount > 0 ? PlasmaCore.Theme.NegativeTextColor : PlasmaCore.Theme.NormalTextColor
    }
    
    // Notification Badge for Pending Vault Actions
    Rectangle {
        visible: root.tasksToday > 0 || root.quarantineCount > 0
        width: 12
        height: 12
        radius: 6
        color: root.quarantineCount > 0 ? PlasmaCore.Theme.negativeTextColor : PlasmaCore.Theme.highlightColor
        anchors.right: icon.right
        anchors.top: icon.top
        anchors.margins: -2

        PlasmaComponents.Label {
            anchors.centerIn: parent
            text: root.quarantineCount > 0 ? root.quarantineCount : root.tasksToday
            font.pixelSize: 8
            font.weight: Font.Bold
            color: "white"
        }
    }
    
    PlasmaCore.ToolTipArea {
        anchors.fill: parent
        mainText: "Sovereign Pair"
        subText: root.activeModels > 0 ? "AI Online (" + root.avgTps.toFixed(1) + " T/s)" : "Modo O.S (Standby)"
    }
}
