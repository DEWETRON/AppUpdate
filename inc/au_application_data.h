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

#include <map>
#include <QObject>
#include <QStringList>
#include <QVariant>

class QVersionNumber;

struct SwComponent
{
    std::string package_name;
    std::string package_version;
    std::string publisher;
    std::string latest_package_version;
};


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
    void installedSoftwareChanged();

private:
    std::string getBundleName(const std::string& sw_display_name) const;
    void addToSwList(const SwEntry& sw_entry, const QVersionNumber& latest_version);
    QVariantList toVariantList(const std::vector<SwEntry>& sw_list);

private:
    QVariantList m_installed_software;
    std::vector<SwEntry> m_installed_software_internal;
    AuSoftwareEnumerator m_sw_enumerator;
    std::map<std::string, std::string> m_bundle_map;
};

