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

#include "au_software_enumerator.h"

#ifdef WIN32
#include "au_registry_win.h"
#else
#include "au_dpkg_lin.h"
#endif

class AuTestSource : public AuSoftwareEnumeratorSource
{
public:
    AuTestSource()
    {}

    ~AuTestSource() = default;


    std::vector<SwEntry> enumerate() override
    {
        return { { "Sparta",  "1.0.0", "Helenas Inc" },
                {"Troja",  "1.0.0", "Helenas Inc" },
                {"Athen",  "2.0.0", "Helenas Inc" },
                };
    }
};


AuSoftwareEnumerator::AuSoftwareEnumerator()
    : m_sw_sources()
{

#ifdef WIN32
    //m_sw_sources.push_back(std::make_shared<AuRegistry>());
    m_sw_sources.push_back(std::make_shared<AuTestSource>());
#else
    //m_sw_sources.push_back(std::make_shared<AuTestSource>());
    m_sw_sources.push_back(std::make_shared<AuDpkg>());
#endif

}

std::vector<SwEntry> AuSoftwareEnumerator::enumerate()
{
    std::vector<SwEntry> all_installed_sw;

    for (auto source : m_sw_sources)
    {
        auto sw_from_source = source->enumerate();
        all_installed_sw.insert(all_installed_sw.end(), sw_from_source.begin(), sw_from_source.end());
    }
    return all_installed_sw;
}
