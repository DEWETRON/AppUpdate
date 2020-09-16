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

AuUpdateJson::AuUpdateJson()
{
}


bool AuUpdateJson::update(QUrl remote_url)
{
    QFile update_file("../examples/update.json");

    if (!update_file.open(QIODevice::ReadOnly)) {
        qWarning("Couldn't open save file.");
        return false;
    }

    QByteArray json_data = update_file.readAll();
    QJsonParseError err;
    m_update_doc = QJsonDocument::fromJson(json_data, &err);

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
            au_ver.version = ver_val["version"].toString().toStdString();
            au_ver.release_note_url = ver_val["release_note_url"].toString().toStdString();
            au_ver.release_date = ver_val["release_date"].toString().toStdString();
            au_ver.license = ver_val["license"].toString().toStdString();
            au_ver.url = ver_val["url"].toString().toStdString();
            au_ver.signature = ver_val["signature"].toString().toStdString();
            
            auto bundle = ver_val["bundle"].toStringList();
            au_ver.bundle.resize(bundle.size());
            std::transform(bundle.begin(), bundle.end(), au_ver.bundle.begin(),
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
