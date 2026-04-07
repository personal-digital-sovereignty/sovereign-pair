import QtQuick
import org.kde.plasma.plasmoid
import org.kde.plasma.components as PlasmaComponents
import QtQuick.Controls as QQC2
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
        onClicked: root.expanded = !root.expanded
        
        QQC2.ToolTip.visible: containsMouse
        QQC2.ToolTip.text: "Sovereign Pair\n" + (root.activeModels > 0 ? "AI Online (" + root.avgTps.toFixed(1) + " T/s)" : "Modo O.S (Standby)")
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
    
}
