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
#include <QJsonDocument>
#include <QFile>


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
