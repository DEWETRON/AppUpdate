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

#include <memory>
#include <string>
#include <vector>


struct SwEntry
{
    std::string m_sw_display_name;
    std::string m_sw_version;
    std::string m_publisher;
};


class AuSoftwareEnumeratorSource
{
public:
    virtual ~AuSoftwareEnumeratorSource() = default;
    virtual std::vector<SwEntry> enumerate() = 0;
};


class AuSoftwareEnumerator
{
public:
    AuSoftwareEnumerator();

    std::vector<SwEntry> enumerate();

private:
    std::vector<std::shared_ptr<AuSoftwareEnumeratorSource>> m_sw_sources;
};
