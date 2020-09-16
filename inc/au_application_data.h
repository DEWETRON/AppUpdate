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
#include "au_update_json.h"

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

    Q_PROPERTY(QVariantList installedApps
                READ getInstalledApps
                NOTIFY installedAppsChanged)

    Q_PROPERTY(QVariantList updateableApps
                READ getUpdateableApps
                NOTIFY updateableAppsChanged)

public:
    AuApplicationData();
    ~AuApplicationData();

    QVariantList getInstalledSoftware();
    QVariantList getInstalledApps();
    QVariantList getUpdateableApps();

    void update();

Q_SIGNALS:
    void installedSoftwareChanged();
    void installedAppsChanged();
    void updateableAppsChanged();

private:
    std::string getBundleName(const std::string& sw_display_name) const;
    void addToSwList(const SwEntry& sw_entry, const QVersionNumber& latest_version);
    QVariantList toVariantList(const std::vector<SwComponent>& sw_list);
    QVersionNumber getHighestVersionNumber(const SwEntry& sw_entry);
    void updateBundleMap();

private:
    QVariantList m_installed_software;
    std::vector<SwComponent> m_installed_software_internal;
    AuSoftwareEnumerator m_sw_enumerator;
    std::map<std::string, std::string> m_bundle_map;
    au_doc::AuDoc m_au_doc;
};

