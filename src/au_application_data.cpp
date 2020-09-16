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

#include "au_application_data.h"
#include "au_update_json.h"
#include <QVersionNumber>

AuApplicationData::AuApplicationData()
    : m_installed_software{}
    , m_sw_enumerator()
{
    update();
}

AuApplicationData::~AuApplicationData()
{
}

QVariantList AuApplicationData::getInstalledSoftware()
{
    return m_installed_software;
}

void AuApplicationData::update()
{
    // get update json document
    AuUpdateJson au_json;
    QVariantMap update_map;

    // TODO get remote json document
    if (au_json.update(QUrl{ "..." }))
    {
        update_map = au_json.getVariantMap();
    }

    // add a custom filter to display only relevant software packages
    m_sw_enumerator.addFilter([](const SwEntry& sw) { return sw.m_publisher.find("DEWETRON") != std::string::npos; });

    auto sw_entries = m_sw_enumerator.enumerate();

    for (const auto& sw_entry : sw_entries)
    {
        QVersionNumber latest_version;
        
        auto it = update_map.find(sw_entry.m_sw_display_name.c_str());
        if (it != update_map.end())
        {
            auto avail_versions = qvariant_cast<QVariantMap>(*it);
            for (auto version_it = avail_versions.begin(); version_it != avail_versions.end(); version_it++)
            {
                auto qver = QVersionNumber::fromString(version_it.key());
                if (qver > latest_version) latest_version = qver;
            }
        }


        QStringList one_entry{ sw_entry.m_sw_display_name.c_str(),
            sw_entry.m_sw_version.c_str(),
            latest_version.toString()
        };

        m_installed_software.push_back(one_entry);
    }


}
