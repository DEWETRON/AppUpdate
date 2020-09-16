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
    , m_installed_software_internal{}
    , m_sw_enumerator()
    , m_bundle_map()
{
    // predefine bundles, which are only shown once
    m_bundle_map = std::map<std::string, std::string>
    {
        { "DEWETRON TRION Driver", "DEWETRON TRION Applications" },
        { "DEWETRON DEWE2 Driver", "DEWETRON TRION Applications" },
        { "DEWETRON Explorer",     "DEWETRON TRION Applications" },
        { "DEWETRON TRIONCAL",     "DEWETRON TRION Applications" }
    };

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
        au_json.getDocument();
    }

    // add a custom filter to display only relevant software packages
    m_sw_enumerator.addFilter([](const SwEntry& sw) { return sw.m_publisher.find("DEWETRON") != std::string::npos; });

    auto sw_entries = m_sw_enumerator.enumerate();

    // create list of installed sw
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

        addToSwList(sw_entry, latest_version);
    }

    m_installed_software = toVariantList(m_installed_software_internal);

}


std::string AuApplicationData::getBundleName(const std::string& sw_display_name) const
{
    auto it = m_bundle_map.find(sw_display_name);
    if (it != m_bundle_map.end())
    {
        return it->second;
    }
    return {};
}

void AuApplicationData::addToSwList(const SwEntry& sw_entry, const QVersionNumber& latest_version)
{
    auto bundle_name = getBundleName(sw_entry.m_sw_display_name);

    std::string app_name = bundle_name.empty() ? sw_entry.m_sw_display_name : bundle_name;

    if (std::none_of(m_installed_software_internal.begin(), m_installed_software_internal.end(),
        [app_name](SwEntry sw_entry) {
            return sw_entry.m_sw_display_name == app_name;
        }))
    {
        SwEntry one_entry{ app_name.c_str(),
            sw_entry.m_sw_version.c_str(),
            latest_version.toString().toStdString()
        };

        m_installed_software_internal.push_back(one_entry);
    }
}

QVariantList AuApplicationData::toVariantList(const std::vector<SwEntry>& sw_list)
{
    QVariantList v_list;

    for (const auto& sw_entry : sw_list)
    {
        QVariantList entry;
        entry.push_back(sw_entry.m_sw_display_name.c_str());
        entry.push_back(sw_entry.m_sw_version.c_str());
        entry.push_back("");

        v_list.push_back(entry);
    }

    return v_list;
}
