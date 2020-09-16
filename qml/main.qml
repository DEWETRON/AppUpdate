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
    width: 550; height: 300




    Tab {
        title: "Updates"

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 10

            Text {
                text: "New versions of your software have been released!"
                font.pointSize: 14; font.bold: false
            }


            ColumnLayout {
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
                            text: "DEWETRON OXYGEN 6.0"
                            font.pointSize: 14; font.bold: false
                        }
                        Text {
                            text: "Installed version: 3.l.0"
                            font.pointSize: 12; font.bold: false
                        }
                    }

                    // HorizontalSpacer
                    Item {
                        Layout.fillWidth: true
                    }

                    ColumnLayout {
                        Text {
                            Layout.alignment: Qt.AlignRight
                            text: "Download"
                            color: "blue"
                            font.pointSize: 12; font.bold: false; font.underline: true
                        }
                    }

                    // HorizontalSpacer (fixed)
                    Item {
                        Layout.minimumWidth: 20
                    }

                }

                RowLayout {
                    spacing: 10
                    Rectangle{
                        width: 64
                        height: 64
                        color: "blue"
                    }
                    Text {
                        Layout.alignment: Qt.AlignTop | Qt.AlignLeft
                        text: "Changes:"
                        font.pointSize: 12; font.bold: false;

                    }
                }

                // VerticalSpacer
                Item {
                    Layout.fillHeight: true
                }

            }

            // VerticalSpacer
            Item {
                Layout.fillHeight: true
            }
        }
    }

    Tab {
        title: "Installed Apps"

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 10

            Text {
                text: "Currently installed applications:"
                font.pointSize: 14; font.bold: false
            }

            ListView {
                model: app.installedApps
                Layout.fillWidth: true
                Layout.fillHeight: true
                boundsBehavior: Flickable.StopAtBounds
                ScrollBar.vertical: ScrollBar {}
                clip: true

                delegate:
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
                                font.pointSize: 14; font.bold: false
                            }
                            Text {
                                text: modelData["version"]
                                font.pointSize: 12; font.bold: false
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


    Tab {
        title: "Installed Apps (old)"

        Rectangle {
            id: page

            color: "white"

            ColumnLayout {
                id: mainColumn
                anchors.fill: parent
                anchors.margins: 20


                ColumnLayout {
                    Repeater {
                        model: app.installedSoftware

                        RowLayout {
                            spacing: 10

                            Rectangle {
                                color: "blue"
                                width: 20; height: 20
                            }
                            Text {
                                Layout.minimumWidth: 250
                                Layout.preferredWidth: 250
                                text: modelData[0]
                                font.pointSize: 12; font.bold: false
                            }
                            Text {
                                Layout.minimumWidth: 100
                                Layout.preferredWidth: 100
                                text: modelData[1]
                                font.pointSize: 12; font.bold: false
                            }
                            Text {
                                Layout.minimumWidth: 100
                                Layout.preferredWidth: 100
                                text: modelData[2]
                                font.pointSize: 12; font.bold: false
                            }
                        }
                    }
                }
            }
        }

    }
}
