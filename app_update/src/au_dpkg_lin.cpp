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

#include "au_dpkg_lin.h"

#include <boost/tokenizer.hpp>

#include <array>
#include <cstdio>
#include <cstring>
#include <memory>

static const std::vector<std::string> VISIBLE_ITEMS = { "dewetron-explorer", "dewetron-oxygen", "dewetron-trion-api" };

namespace
{
    std::string exec(const char* cmd)
    {
        std::array<char, 128> buffer = { 0 };
        std::string result;
        std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(cmd, "r"), pclose);
        if (!pipe)
        {
            throw std::runtime_error("popen() failed!");
        }
        while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr)
        {
            result += buffer.data();
        }
        return result;
    }
}

AuDpkg::AuDpkg()
{
}

AuDpkg::~AuDpkg()
{
}

std::vector<SwEntry> AuDpkg::enumerate()
{
    typedef boost::tokenizer<boost::char_separator<char>> tokenizer;

    std::vector<SwEntry> entries;

    const auto cmd = "dpkg --list | grep dewetron";
    auto ret = exec(cmd);

    if (!ret.empty())
    {
        boost::char_separator<char> br {"\n"};
        tokenizer lines {ret, br};

        for (const auto& line : lines)
        {
            boost::char_separator<char> space {" "};
            tokenizer columns {line, space};

            std::vector<std::string> infos;

            std::copy(columns.begin(), columns.end(), std::back_inserter(infos));

            auto sw_name = infos.at(1);

            auto iter = std::find_if(VISIBLE_ITEMS.begin(), VISIBLE_ITEMS.end(), [&sw_name](const std::string& entry)
            {
                return std::strncmp(sw_name.c_str(), entry.c_str(), entry.size()) == 0;
            });

            if (iter != VISIBLE_ITEMS.end())
            {
                SwEntry entry;
                {
                    sw_name = sw_name.substr(9);
                    auto pos = sw_name.find_first_of(':');
                    if (pos != std::string::npos)
                    {
                        sw_name = sw_name.substr(0, pos);
                    }
                    entry.m_sw_display_name = sw_name;
                }
                {
                    auto version = infos.at(2);
                    auto pos = version.find_last_of('.');
                    if (pos != std::string::npos)
                    {
                        version = version.substr(0, pos);
                    }
                    entry.m_sw_version = version;
                    entry.m_publisher = "DEWETRON";
                    entries.push_back(entry);
                }
            }
        }
    }
    return entries;
}
