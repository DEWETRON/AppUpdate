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
import QtQuick.Layouts 1.12

Rectangle {
    id: page
    width: 320; height: 480
    color: "lightgray"

    // Text {
    //     id: helloText
    //     text: "*Hello world!!!!!" + app.installedSoftware
    //     y: 30
    //     anchors.horizontalCenter: page.horizontalCenter
    //     font.pointSize: 24; font.bold: true
    // }

    GridLayout {
        columns: 2

        Repeater {
            model: app.installedSoftware

            Repeater {

                model: modelData
                            
                Text {
                    text: modelData
                    font.pointSize: 24; font.bold: true
                }
            }
        }
    }

}
