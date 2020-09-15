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

#pragma once

#include "au_software_enumerator.h"

#include <QObject>
#include <QStringList>
#include <QVariant>

 /**
  * Application main model
  */
class AuApplicationData : public QObject
{
    Q_OBJECT

    Q_PROPERTY(QVariantList installedSoftware
                READ getInstalledSoftware
                NOTIFY installedSoftwareChanged)

public:
    AuApplicationData();
    ~AuApplicationData();

    QVariantList getInstalledSoftware();

    void update();

Q_SIGNALS:
    void blaChanged();
    void installedSoftwareChanged();

private:
    QVariantList m_installed_software;

    AuSoftwareEnumerator m_sw_enumerator;
};

