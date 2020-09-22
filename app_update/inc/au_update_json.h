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

#include <map>
#include <string>
#include <vector>

#include <QUrl>
#include <QJsonDocument>
#include <QVariant>


namespace au_doc
{
    struct AuAppVersion
    {
        std::string version;
        std::string release_note_url;
        std::string release_date;
        std::string license;
        std::string url;
        std::string md5;
        std::string sha1;
        std::vector<std::string> bundle;
        std::vector<std::string> changes;
    };

    struct AuApp
    {
        std::map<std::string, AuAppVersion> m_app_versions;
    };

    struct AuDoc
    {
        std::map<std::string, AuApp> m_apps;
    };
}



class AuUpdateJson
{
public:
    AuUpdateJson(const QByteArray& byte_array);
    ~AuUpdateJson() = default;

    bool update();

    QVariantMap getVariantMap() const;
    au_doc::AuDoc getDocument() const;

private:
    QByteArray m_byte_array;
    QJsonDocument m_update_doc;
    QVariantMap   m_update_map;
};
