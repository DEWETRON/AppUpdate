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
    auto all_sw_entries = m_sw_enumerator.enumerate();

    for (const auto& sw_entry : all_sw_entries)
    {
        QStringList one_entry{sw_entry.m_sw_display_name.c_str(), 
            sw_entry.m_sw_version.c_str()};
        
        m_installed_software.push_back(one_entry);
    }

}