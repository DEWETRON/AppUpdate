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

#include "au_update_json.h"
#include <algorithm>
#include <QJsonDocument>
#include <QFile>

using namespace au_doc;

AuUpdateJson::AuUpdateJson(const QByteArray& byte_array)
    : m_byte_array(byte_array)
    , m_update_doc()
    , m_update_map()
{
}

bool AuUpdateJson::update()
{
    QJsonParseError err;
    m_update_doc = QJsonDocument::fromJson(m_byte_array, &err);

    auto debug = m_update_doc.toJson();

    m_update_map = qvariant_cast<QVariantMap>(m_update_doc.toVariant());

    return true;
}


QVariantMap AuUpdateJson::getVariantMap() const
{
    return m_update_map;
}

au_doc::AuDoc AuUpdateJson::getDocument() const
{
    au_doc::AuDoc doc;

    for (auto app_it = m_update_map.begin(); app_it != m_update_map.end(); ++app_it)
    {
        AuApp au_app;

        QVariantMap ver_map = qvariant_cast<QVariantMap>(app_it.value());

        for (auto ver_it = ver_map.begin(); ver_it != ver_map.end(); ++ver_it)
        {
            AuAppVersion au_ver;
            QVariantMap ver_val = qvariant_cast<QVariantMap>(ver_it.value());
            au_ver.beta = ver_val["beta"].toString().toStdString();
            au_ver.version = ver_val["version"].toString().toStdString();
            au_ver.release_note_url = ver_val["release_note_url"].toString().toStdString();
            au_ver.release_date = ver_val["release_date"].toString().toStdString();
            au_ver.license = ver_val["license"].toString().toStdString();
            au_ver.url = ver_val["url"].toString().toStdString();
            au_ver.md5 = ver_val["md5"].toString().toStdString();
            au_ver.sha1 = ver_val["sha1"].toString().toStdString();
            au_ver.notify = ver_val["notify"].toString().toStdString();

            auto bundle = ver_val["bundle"].toStringList();
            au_ver.bundle.resize(bundle.size());
            std::transform(bundle.begin(), bundle.end(), au_ver.bundle.begin(),
                [](QString entry) {
                    return entry.toStdString();
                }
                );

            auto changes = ver_val["changes"].toStringList();
            au_ver.changes.resize(changes.size());
            std::transform(changes.begin(), changes.end(), au_ver.changes.begin(),
                [](QString entry) {
                return entry.toStdString();
            }
            );


            au_app.m_app_versions.insert({ ver_it.key().toStdString(), au_ver});
        }

        doc.m_apps.insert({ app_it.key().toStdString(), au_app });
    }

    return doc;
}
