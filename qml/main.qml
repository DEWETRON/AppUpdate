/*
 * This file is part of the AppUpdate (https://github.com/DEWETRON/AppUpdate)
 * Copyright (c) DEWETRON GmbH 2020.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, version 3.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <http://www.gnu.org/licenses/>.
 */

import QtQuick 2.0
import QtQuick.Controls 1.0
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12


TabView {
    id: root
    width: 500; height: 440

    property var show_older_versions : false
    property var show_updates_only : true
    property var model: getModel(app.updateableApps)

    function getModel(data) {
        return getShowOlderVersions(getUpdatesOnly(data));
    }

    function getUpdatesOnly(data) {
        if (!root.show_updates_only) return data

        var filteredApps = []
        var entry
        for (entry of data) {
            if (entry["has_update"] == true) {
                filteredApps.push(entry)
            }
        }
        return filteredApps
    }

    function getShowOlderVersions(data) {
        if (show_older_versions) return data

        var filteredApps = []
        var entry
        for (entry of data) {
            if (entry["is_older_version"] != true) {
                filteredApps.push(entry)
            }
        }
        return filteredApps
    }

    Tab {
        title: qsTr("Updates")
        
        ColumnLayout {
            anchors.fill: parent
            spacing: 10

            Text {
                Layout.topMargin: 10
                Layout.leftMargin: 10
                text: root.model.length > 0 ? qsTr("New versions of your software have been released!") : qsTr("Everything is up to date!")
                font.pointSize: 12; font.bold: false
            }

            ListView {
                model: root.model
                Layout.fillWidth: true
                Layout.fillHeight: true
                boundsBehavior: Flickable.StopAtBounds
                ScrollBar.vertical: ScrollBar { }
                clip: true

                delegate:
                ColumnLayout {
                    x:10
                    width: parent.width - 20


                    Rectangle {
                        Layout.fillWidth: true
                        height: 1
                        color: "darkgrey"
                    }

                    RowLayout {

                        spacing: 10
                        Rectangle{
                            width: 64
                            height: 64
                            //color: "red"
                            Image {
                                anchors.fill: parent
                                fillMode: Image.PreserveAspectFit
                                source: "../res/dewetron.ico"
                            }
                        }

                        ColumnLayout {
                            Text {
                                text: modelData["name"]
                                font.pointSize: 12; font.bold: false
                            }
                            RowLayout {
                                Text {
                                    text: modelData["version"]
                                    font.pointSize: 10; font.bold: false
                                }
                                Text {
                                    text: modelData["has_update"] ? qsTr("New!") : ""
                                    font.pointSize: 10; font.bold: false
                                    color: "red"
                                }
                            }
                        }

                        // HorizontalSpacer
                        Item {
                            Layout.fillWidth: true
                        }

                        ColumnLayout {
                            Text {
                                Layout.alignment: Qt.AlignRight
                                text: qsTr("Download")
                                color: "blue"
                                font.pointSize: 12; font.bold: false; font.underline: true
                                visible: modelData["url"] != null ? modelData["url"].length > 0 : false
                                
                                MouseArea {
                                    anchors.fill: parent
                                    onClicked: { 
                                        app.download(modelData["url"])
                                    }
                                }
                            }
                        }

                    }

                    RowLayout {
                        spacing: 10
                        Rectangle{
                            width: 64
                            //height: 64
                            //color: "blue"
                        }
                        Text {
                            Layout.alignment: Qt.AlignTop | Qt.AlignLeft
                            text: modelData["changes"]
                            font.pointSize: 12; font.bold: false;

                        }

                        // HorizontalSpacer
                        Item {
                            Layout.fillWidth: true
                        }

                    }

                }
    

                // VerticalSpacer
                Item {
                    Layout.fillHeight: true
                }

            }


            ColumnLayout {

                // Text {
                //     text: app.downloadProgress
                // }
                ProgressBar {
                    Layout.fillWidth: true
                    from: 0
                    to: 100
                    value: app.downloadProgress
                    visible: app.downloadProgress > 0
                }


                Text {
                    text: app.message
                }

                RowLayout {
                    spacing: 10

                    ColumnLayout {
                        CheckBox {
                            id: showUpdatesOnly
                            text: qsTr("Show updates only")
                            checked: root.show_updates_only
                            onClicked: {
                                root.show_updates_only = checked
                            }
                        }
                        CheckBox {
                            id: showOlderVersions
                            text: qsTr("Show older versions")
                            checked: root.show_older_versions
                            onClicked: {
                                root.show_older_versions = checked
                            }
                        }
                    }

                    // HorizontalSpacer
                    Item {
                        Layout.fillWidth: true
                    }

                    Button {
                        text: qsTr("Check for Updates")
                        onClicked: {
                            app.checkForUpdates()
                        }
                    }

                    Button {
                        enabled: root.model.length > 0
                        text: qsTr("Update All")
                        onClicked: {
                            app.updateAll()
                        }
                    }

                }
            }

        }
    }
    Tab {
        title: qsTr("Installed Apps")

        ColumnLayout {
            anchors.fill: parent
            spacing: 10

            Text {
                Layout.topMargin: 10
                Layout.leftMargin: 10
                text: qsTr("Currently installed applications:")
                font.pointSize: 12; font.bold: false
            }

            ListView {
                model: app.installedApps
                Layout.fillWidth: true
                Layout.fillHeight: true
                boundsBehavior: Flickable.StopAtBounds
                ScrollBar.vertical: ScrollBar { }
                clip: true

                delegate: 
                ColumnLayout {
                    x:10
                    width: parent.width - 20

                    Rectangle {
                        Layout.fillWidth: true
                        height: 1
                        color: "darkgrey"
                    }

                    RowLayout {
                        x:10
                        width: parent.width - 20
                        spacing: 10
                        Rectangle{
                            width: 64
                            height: 64
                            //color: "red"
                            Image {
                                anchors.fill: parent
                                fillMode: Image.PreserveAspectFit
                                source: "../res/dewetron.ico"
                            }
                        }

                        ColumnLayout {
                            Text {
                                text: modelData["name"]
                                font.pointSize: 12; font.bold: false
                            }
                            Text {
                                text: modelData["version"]
                                font.pointSize: 10; font.bold: false
                            }
                        }

                        // HorizontalSpacer
                        Item {
                            Layout.fillWidth: true
                        }

                        // HorizontalSpacer (fixed)
                        Item {
                            Layout.minimumWidth: 20
                        }

                    }
                }

            }

        }
    }
}
