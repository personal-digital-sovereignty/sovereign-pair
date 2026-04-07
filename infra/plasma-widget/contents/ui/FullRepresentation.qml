import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.components as PlasmaComponents
import org.kde.kirigami as Kirigami

Item {
    id: fullRoot
    
    width: 320
    height: 380

    Rectangle {
        anchors.fill: parent
        color: Kirigami.Theme.backgroundColor
        radius: 8

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 16
            spacing: 12

            // Header
            RowLayout {
                spacing: 8
                Image {
                    source: "app-icon.svg"
                    sourceSize.width: 32
                    sourceSize.height: 32
                    Layout.preferredWidth: 32
                    Layout.preferredHeight: 32
                }
                ColumnLayout {
                    spacing: 0
                    PlasmaComponents.Label {
                        text: "Sovereign Pair"
                        font.weight: Font.Bold
                        font.pixelSize: 16
                        color: Kirigami.Theme.textColor
                    }
                    PlasmaComponents.Label {
                        text: root.activeModels > 0 ? "Core LLM Ativo" : "Em Espera (Desidratado)"
                        font.pixelSize: 11
                        opacity: 0.7
                        color: root.activeModels > 0 ? Kirigami.Theme.highlightColor : Kirigami.Theme.textColor
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: Kirigami.Theme.textColor
                opacity: 0.1
            }

            // Telemetry Grid
            GridLayout {
                columns: 2
                rowSpacing: 16
                columnSpacing: 16
                Layout.fillWidth: true

                // Tokens Processados
                ColumnLayout {
                    spacing: 2
                    PlasmaComponents.Label {
                        text: "TOKENS (TOTAL)"
                        font.pixelSize: 10
                        font.weight: Font.Bold
                        opacity: 0.5
                    }
                    PlasmaComponents.Label {
                        text: root.totalTokens.toLocaleString()
                        font.pixelSize: 20
                        font.family: "monospace"
                        color: Kirigami.Theme.textColor
                    }
                }

                // TPS
                ColumnLayout {
                    spacing: 2
                    PlasmaComponents.Label {
                        text: "VELOCIDADE (T/s)"
                        font.pixelSize: 10
                        font.weight: Font.Bold
                        opacity: 0.5
                    }
                    RowLayout {
                        spacing: 4
                        PlasmaComponents.Label {
                            text: root.avgTps.toFixed(1)
                            font.pixelSize: 20
                            font.family: "monospace"
                            color: Kirigami.Theme.highlightColor
                        }
                        Kirigami.Icon {
                            source: "lightning"
                            implicitWidth: 16
                            implicitHeight: 16
                            isMask: true
                            color: Kirigami.Theme.highlightColor
                            visible: root.avgTps > 0
                        }
                    }
                }
                
                // Tasks
                ColumnLayout {
                    spacing: 2
                    PlasmaComponents.Label {
                        text: "TAREFAS HOJE"
                        font.pixelSize: 10
                        font.weight: Font.Bold
                        opacity: 0.5
                    }
                    PlasmaComponents.Label {
                        text: root.tasksToday.toString()
                        font.pixelSize: 20
                        font.family: "monospace"
                        color: Kirigami.Theme.textColor
                    }
                }

                // Quarantine
                ColumnLayout {
                    spacing: 2
                    PlasmaComponents.Label {
                        text: "QUARENTENA"
                        font.pixelSize: 10
                        font.weight: Font.Bold
                        opacity: 0.5
                    }
                    PlasmaComponents.Label {
                        text: root.quarantineCount.toString()
                        font.pixelSize: 20
                        font.family: "monospace"
                        color: root.quarantineCount > 0 ? Kirigami.Theme.negativeTextColor : Kirigami.Theme.textColor
                    }
                }
            }

            Item { Layout.fillHeight: true } // Spacer

            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: Kirigami.Theme.textColor
                opacity: 0.1
            }

            // Quick Actions
            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                PlasmaComponents.Button {
                    Layout.fillWidth: true
                    text: "Abrir Dashboard"
                    icon.name: "window-new"
                    onClicked: {
                        var req = new XMLHttpRequest();
                        req.open("POST", "http://127.0.0.1:38001/v1/system/launch-gui");
                        req.send();
                        root.expanded = false;
                    }
                }
            }
        }
    }
}
